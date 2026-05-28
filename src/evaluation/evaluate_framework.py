"""
evaluate_framework.py
---------------------
Objective 4: Evaluate framework performance against baselines.

Runs 50–100 origin-destination pairs across three traffic scenarios:
    - peak_hour     : worst congestion (top 25 % speed-drop slots)
    - off_peak      : free-flow conditions (top 25 % speed slots)
    - incident      : sudden speed drop ≥ 40 % mid-journey

Baselines:
    B1  Dijkstra + current conditions   (status quo in most dispatch centres)
    B2  Static A* + historical average  (time-of-day averages only)
    B3  Static A* + current conditions  (reactive, no prediction)
    B4  Oracle A* + actual future tt    (theoretical maximum — upper bound)
    F   TD-A* + GRU prediction + δ controller  (YOUR FRAMEWORK)

Metrics captured per run:
    travel_time_s, latency_ms, n_replannings, update_frequency,
    path_length_nodes, feasible

All results saved to  results/evaluation_results.csv
Summary statistics to results/summary_stats.csv
"""

import os
import time
import random
import warnings
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

warnings.filterwarnings('ignore')

# ── local imports ─────────────────────────────────────────────────────────────
from src.routing.td_astar import (
    td_astar, dijkstra_current, static_astar_historical,
    oracle_astar, free_flow_from_graph
)
from src.routing.graph_builder import (
    build_synthetic_graph, compute_historical_avg_tt, compute_current_tt
)
from src.controller.adaptive_controller import JourneySimulator
from src.prediction.gru_interface import (
    load_model_and_scaler, predict_speeds, speeds_to_travel_times,
    get_free_flow_travel_time
)

# ── configuration ─────────────────────────────────────────────────────────────
N_OD_PAIRS       = 75       # number of origin-destination pairs per scenario
DELTA_VALUES     = [0.05, 0.10, 0.15, 0.20]
SCENARIOS        = ['peak_hour', 'off_peak', 'incident']
POLICIES         = ['threshold', 'fixed_interval', 'hybrid', 'event_driven']
RANDOM_SEED      = 42
SEQUENCE_LEN     = 12       # must match your GRU training
N_FUTURE_STEPS   = 6


def load_metr_la_data(data_dir: str) -> Optional[np.ndarray]:
    npz_path = os.path.join(data_dir, 'processed', 'training_data.npz')
    if os.path.exists(npz_path):
        data     = np.load(npz_path)
        # X_train shape: (23977, 12, 207) — take first timestep of each window
        speed_data = np.vstack([
            data['X_train'][:, 0, :],   # (23977, 207)
            data['X_val'][:, 0, :],     # ( 5138, 207)
            data['X_test'][:, 0, :]     # ( 5139, 207)
        ])                              # → (34254, 207)
        print(f"[Eval] Loaded training_data.npz: shape {speed_data.shape}")
        return speed_data.astype(np.float32)
    return None

def generate_od_pairs(graph, n: int = N_OD_PAIRS,
                      min_hops: int = 3) -> List[Tuple[int, int]]:
    """Generate random OD pairs with minimum path length."""
    import networkx as nx
    rng    = random.Random(RANDOM_SEED)
    nodes  = list(graph.nodes())
    pairs  = []
    attempts = 0
    while len(pairs) < n and attempts < n * 20:
        o = rng.choice(nodes)
        d = rng.choice(nodes)
        attempts += 1
        if o == d:
            continue
        try:
            hops = nx.shortest_path_length(graph, o, d)
            if hops >= min_hops:
                pairs.append((o, d))
        except nx.NetworkXNoPath:
            continue
    print(f"[Eval] Generated {len(pairs)} OD pairs")
    return pairs


def select_scenario_slots(speed_data: np.ndarray,
                           scenario: str,
                           n_slots: int = 5) -> List[int]:
    """
    Select representative departure time slots for each scenario.

    peak_hour  : slots where mean speed is lowest (bottom 25 %)
    off_peak   : slots where mean speed is highest (top 25 %)
    incident   : random slots (incident injected synthetically)
    """
    mean_speed = speed_data.mean(axis=1)   # (T,)
    T = len(mean_speed)

    if scenario == 'peak_hour':
        threshold = np.percentile(mean_speed, 25)
        candidates = np.where(mean_speed <= threshold)[0]
    elif scenario == 'off_peak':
        threshold = np.percentile(mean_speed, 75)
        candidates = np.where(mean_speed >= threshold)[0]
    else:   # incident
        candidates = np.arange(SEQUENCE_LEN, T - N_FUTURE_STEPS - 10)

    rng = np.random.default_rng(RANDOM_SEED)
    chosen = rng.choice(candidates, size=min(n_slots, len(candidates)),
                        replace=False)
    return chosen.tolist()


def inject_incident(speed_window: np.ndarray,
                    severity: float = 0.4) -> np.ndarray:
    """
    Simulate a traffic incident by dropping speeds on random sensors by
    severity fraction mid-journey.
    incident speed_window shape: (N_sensors, SEQUENCE_LEN)
    """
    rng = np.random.default_rng()
    n_affected = max(1, int(speed_window.shape[0] * 0.15))
    affected   = rng.choice(speed_window.shape[0], n_affected, replace=False)
    modified   = speed_window.copy()
    modified[affected, SEQUENCE_LEN // 2:] *= (1 - severity)
    return modified


def run_single_od(graph,
                  origin:       int,
                  destination:  int,
                  speed_window: np.ndarray,    # (N, SEQUENCE_LEN)
                  model,
                  scaler,
                  edge_sensor_map: Dict,
                  edge_lengths_m:  Dict,
                  hist_avg_tt:     Dict,
                  free_flow_tt:    Dict,
                  scenario:        str,
                  delta:           float,
                  policy:          str
                  ) -> Dict:
    """
    Run all baselines + framework for one OD pair.
    Returns dict of metrics.
    """
    record = {
        'origin': origin, 'destination': destination,
        'scenario': scenario, 'delta': delta, 'policy': policy
    }

    # ── GRU prediction ────────────────────────────────────────────────────────
    t_pred_start = time.perf_counter()
    if scenario == 'incident':
        speed_window = inject_incident(speed_window)

    pred_speeds = predict_speeds(model, scaler, speed_window)  # (N, N_FUTURE)
    pred_tt_fn  = speeds_to_travel_times(pred_speeds, edge_lengths_m,
                                          edge_sensor_map)
    record['gru_inference_ms'] = (time.perf_counter() - t_pred_start) * 1000

    # current conditions (departure-time snapshot)
    current_speeds = speed_window[:, -1]   # most recent reading
    current_tt     = compute_current_tt(current_speeds, edge_lengths_m,
                                         edge_sensor_map)

    # Oracle uses current_tt as a scalar-valued baseline (best achievable
    # given current conditions — replace with held-out future data in real exp)
    actual_tt = current_tt

    # ── BASELINE 1: Dijkstra + current conditions ─────────────────────────────
    r_b1 = dijkstra_current(graph, origin, destination, current_tt)
    record['b1_dijkstra_tt_s']     = r_b1.total_time_s
    record['b1_dijkstra_lat_ms']   = r_b1.latency_ms
    record['b1_dijkstra_feasible'] = r_b1.feasible

    # ── BASELINE 2: Static A* + historical average ────────────────────────────
    r_b2 = static_astar_historical(graph, origin, destination, hist_avg_tt)
    record['b2_static_astar_tt_s']   = r_b2.total_time_s
    record['b2_static_astar_lat_ms'] = r_b2.latency_ms

    # ── BASELINE 3: Static A* + current conditions ────────────────────────────
    r_b3 = static_astar_historical(graph, origin, destination, current_tt)
    record['b3_reactive_astar_tt_s']   = r_b3.total_time_s
    record['b3_reactive_astar_lat_ms'] = r_b3.latency_ms

    # ── BASELINE 4: Oracle A* (upper bound) ──────────────────────────────────
    r_b4 = oracle_astar(graph, origin, destination, actual_tt)
    record['b4_oracle_tt_s']   = r_b4.total_time_s
    record['b4_oracle_lat_ms'] = r_b4.latency_ms

    # ── FRAMEWORK: TD-A* + GRU + adaptive controller ─────────────────────────
    # Build a series of tt_fns (one per future slot window)
    # For the simulation we use the same pred_tt_fn for all slots
    # In full experiment: slide the window forward for each replan
    tt_fn_series = [pred_tt_fn] * (N_FUTURE_STEPS + 2)

    sim = JourneySimulator(
        graph=graph,
        tt_fn_series=tt_fn_series,
        free_flow_tt=free_flow_tt,
        delta=delta,
        policy=policy
    )
    sim_result = sim.run(origin, destination)

    record['framework_tt_s']         = sim_result.total_time_s
    record['framework_lat_ms']       = sim_result.avg_latency_ms
    record['framework_n_replannings']= sim_result.n_replannings
    record['framework_feasible']     = sim_result.feasible

    # ── travel time reduction vs each baseline ────────────────────────────────
    fw_tt = sim_result.total_time_s
    for key, baseline_tt in [
        ('vs_dijkstra',      r_b1.total_time_s),
        ('vs_static_astar',  r_b2.total_time_s),
        ('vs_reactive_astar',r_b3.total_time_s),
        ('vs_oracle',        r_b4.total_time_s),
    ]:
        if baseline_tt > 0:
            record[f'reduction_{key}_pct'] = \
                (baseline_tt - fw_tt) / baseline_tt * 100
        else:
            record[f'reduction_{key}_pct'] = 0.0

    return record


def run_evaluation(model_dir:  str = 'models/saved',
                   data_dir:   str = 'data',
                   results_dir:str = 'results',
                   use_synthetic: bool = False) -> pd.DataFrame:
    """
    Master evaluation loop.

    Parameters
    ----------
    model_dir     : path to your saved GRU models + scaler
    data_dir      : path to METR-LA / PEMS-BAY data files
    results_dir   : where to write CSV outputs
    use_synthetic : True = skip data loading, use synthetic speeds (for testing)
    """
    os.makedirs(results_dir, exist_ok=True)
    rng = np.random.default_rng(RANDOM_SEED)

    # ── 1. Load GRU model ─────────────────────────────────────────────────────
    print("\n[Phase 1] Loading GRU model...")
    model, scaler = load_model_and_scaler(model_dir)

    # ── 2. Build graph ────────────────────────────────────────────────────────
    print("[Phase 2] Building road graph...")
    processed_dir   = os.path.join(data_dir, 'processed')
    la_network_path = os.path.join(processed_dir, 'la_road_network.pkl')

    if os.path.exists(la_network_path) and not use_synthetic:
        from src.routing.graph_builder import load_from_processed
        graph, edge_sensor_map, edge_lengths_m = load_from_processed(processed_dir)
        print("[Phase 2] ✓ Real OSM road network loaded")
    else:
        graph, edge_sensor_map, edge_lengths_m = build_synthetic_graph()
        print("[Phase 2] Synthetic graph used")

    # ── 3. Load speed data ────────────────────────────────────────────────────
    print("[Phase 3] Loading speed data...")
    speed_data = None
    if not use_synthetic:
        speed_data = load_metr_la_data(data_dir)

    if speed_data is None:
        print("[Phase 3] Using synthetic speed data")
        T = 34272    # METR-LA length
        N = graph.number_of_nodes()
        speed_data = rng.normal(loc=45, scale=15, size=(T, N)).clip(5, 80)
        speed_data = speed_data.astype(np.float32)

    N = min(speed_data.shape[1], graph.number_of_nodes())
    speed_data = speed_data[:, :N]

    # ── 4. Pre-compute baseline travel-time tables ────────────────────────────
    print("[Phase 4] Pre-computing historical averages...")
    hist_avg_tt = compute_historical_avg_tt(
        speed_data, edge_lengths_m, edge_sensor_map)
    free_flow_tt = get_free_flow_travel_time(edge_lengths_m)

    # ── 5. Generate OD pairs ──────────────────────────────────────────────────
    print("[Phase 5] Generating OD pairs...")
    od_pairs = generate_od_pairs(graph, N_OD_PAIRS)

    # ── 6. Main experiment loop ───────────────────────────────────────────────
    print(f"\n[Phase 6] Running experiments: "
          f"{len(od_pairs)} OD × {len(SCENARIOS)} scenarios × "
          f"{len(DELTA_VALUES)} δ values\n")

    all_records = []
    total = len(od_pairs) * len(SCENARIOS) * len(DELTA_VALUES)
    count = 0

    for scenario in SCENARIOS:
        depart_slots = select_scenario_slots(speed_data, scenario, n_slots=5)

        for origin, destination in od_pairs:
            slot = int(rng.choice(depart_slots))
            # extract speed window ending at departure slot
            start = max(0, slot - SEQUENCE_LEN)
            speed_window = speed_data[start:slot, :N].T   # (N, SEQUENCE_LEN)
            if speed_window.shape[1] < SEQUENCE_LEN:
                pad = SEQUENCE_LEN - speed_window.shape[1]
                speed_window = np.pad(speed_window, ((0,0),(pad,0)),
                                      mode='edge')

            for delta in DELTA_VALUES:
                count += 1
                if count % 50 == 0:
                    print(f"  Progress: {count}/{total} "
                          f"({100*count//total}%)", flush=True)
                try:
                    rec = run_single_od(
                        graph, origin, destination,
                        speed_window, model, scaler,
                        edge_sensor_map, edge_lengths_m,
                        hist_avg_tt, free_flow_tt,
                        scenario, delta, policy='threshold'
                    )
                    all_records.append(rec)
                except Exception as e:
                    print(f"  [WARN] OD ({origin}→{destination}) "
                          f"scenario={scenario} δ={delta}: {e}")
                    continue

    # ── 7. Save raw results ───────────────────────────────────────────────────
    df = pd.DataFrame(all_records)
    raw_path = os.path.join(results_dir, 'evaluation_results.csv')
    df.to_csv(raw_path, index=False)
    print(f"\n[Phase 7] Raw results saved → {raw_path}")

    # ── 8. Summary statistics ─────────────────────────────────────────────────
    summary = _compute_summary(df)
    summ_path = os.path.join(results_dir, 'summary_stats.csv')
    summary.to_csv(summ_path, index=True)
    print(f"[Phase 8] Summary stats saved → {summ_path}")
    print("\n" + "="*60)
    print(summary.to_string())
    print("="*60)

    return df


def _compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute summary statistics grouped by scenario + delta."""
    metrics = [
        'framework_tt_s', 'b1_dijkstra_tt_s', 'b2_static_astar_tt_s',
        'framework_lat_ms', 'framework_n_replannings',
        'reduction_vs_dijkstra_pct', 'reduction_vs_static_astar_pct',
        'reduction_vs_oracle_pct', 'gru_inference_ms'
    ]
    available = [m for m in metrics if m in df.columns]
    if df.empty or 'scenario' not in df.columns:
        return pd.DataFrame()
    summary = df.groupby(['scenario', 'delta'])[available].agg(
        ['mean', 'std', 'median']).round(3)
    return summary


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run framework evaluation')
    parser.add_argument('--model-dir',   default='models/saved')
    parser.add_argument('--data-dir',    default='data')
    parser.add_argument('--results-dir', default='results')
    parser.add_argument('--synthetic',   action='store_true',
                        help='Use synthetic data (no METR-LA required)')
    args = parser.parse_args()

    run_evaluation(
        model_dir    = args.model_dir,
        data_dir     = args.data_dir,
        results_dir  = args.results_dir,
        use_synthetic= args.synthetic
    )