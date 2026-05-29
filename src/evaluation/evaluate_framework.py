"""
evaluate_framework.py  -  FINAL VERSION with all fixes applied
"""
import os, time, random, warnings
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
warnings.filterwarnings('ignore')

from src.routing.td_astar import (td_astar, dijkstra_current,
    static_astar_historical, oracle_astar, free_flow_from_graph)
from src.routing.graph_builder import (build_synthetic_graph,
    compute_historical_avg_tt, compute_current_tt)
from src.controller.adaptive_controller import JourneySimulator
from src.prediction.gru_interface import (load_model_and_scaler,
    predict_speeds, speeds_to_travel_times, get_free_flow_travel_time)

N_OD_PAIRS     = 100
DELTA_VALUES   = [0.05, 0.10, 0.15, 0.20]
SCENARIOS      = ['peak_hour', 'off_peak', 'incident']
RANDOM_SEED    = 42
SEQUENCE_LEN   = 12
N_FUTURE_STEPS = 6
SENSOR_COUNTS  = {'metr_la': 207, 'pems_bay': 325}


def load_speed_data(data_dir, dataset='metr_la'):
    npz = os.path.join(data_dir, 'processed', 'training_data.npz')
    if os.path.exists(npz):
        d = np.load(npz)
        sd = np.vstack([d['X_train'][:,0,:], d['X_val'][:,0,:], d['X_test'][:,0,:]])
        print(f"[Eval] Loaded training_data.npz: shape {sd.shape}")
        return sd.astype(np.float32)
    raw = os.path.join(data_dir, 'processed', 'speed_data_raw.npy')
    if os.path.exists(raw):
        d = np.load(raw)
        print(f"[Eval] Loaded speed_data_raw.npy: shape {d.shape}")
        return d.astype(np.float32)
    for fname in ('metr-la.h5', 'pems-bay.h5'):
        fpath = os.path.join(data_dir, 'raw', fname)
        if os.path.exists(fpath):
            try:
                import h5py
                with h5py.File(fpath,'r') as f:
                    key = list(f.keys())[0]; d = f[key][:]
                if d.ndim==3: d=d[:,:,0]
                if d.shape[0]<d.shape[1]: d=d.T
                print(f"[Eval] Loaded {fname}: shape {d.shape}")
                return d.astype(np.float32)
            except Exception as e:
                print(f"[Eval] Cannot read {fname}: {e}")
    return None


def load_graph(data_dir, use_synthetic=False):
    processed = os.path.join(data_dir, 'processed')
    la_path   = os.path.join(processed, 'la_road_network.pkl')
    if not use_synthetic and os.path.exists(la_path):
        try:
            from src.routing.graph_builder import load_from_processed
            g, esm, elm = load_from_processed(processed)
            print(f"[Phase 2] Real OSM graph: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges")
            return g, esm, elm
        except Exception as e:
            print(f"[Phase 2] load_from_processed failed: {e}")
    n = 325 if 'pems_bay' in data_dir else 207
    print(f"[Phase 2] Synthetic graph ({n} sensors)")
    return build_synthetic_graph(n_sensors=n)


def build_tt_fn_series(speed_data, slot, model, scaler,
                       edge_lengths_m, edge_sensor_map, N, sliding=False):
    n_series = N_FUTURE_STEPS + 2
    if not sliding:
        start  = max(0, slot - SEQUENCE_LEN)
        window = speed_data[start:slot, :N].T
        if window.shape[1] < SEQUENCE_LEN:
            window = np.pad(window, ((0,0),(SEQUENCE_LEN-window.shape[1],0)), mode='edge')
        pred  = predict_speeds(model, scaler, window)
        tt_fn = speeds_to_travel_times(pred, edge_lengths_m, edge_sensor_map)
        return [tt_fn] * n_series
    series = []
    T = speed_data.shape[0]
    for step in range(n_series):
        s     = min(slot + step, T-1)
        start = max(0, s - SEQUENCE_LEN)
        w     = speed_data[start:s, :N].T
        if w.shape[1] < SEQUENCE_LEN:
            w = np.pad(w, ((0,0),(SEQUENCE_LEN-w.shape[1],0)), mode='edge')
        pred  = predict_speeds(model, scaler, w)
        tt_fn = speeds_to_travel_times(pred, edge_lengths_m, edge_sensor_map)
        series.append(tt_fn)
    return series


def generate_od_pairs(graph, n=N_OD_PAIRS, min_hops=3):
    import networkx as nx
    rng   = random.Random(RANDOM_SEED)
    nodes = [int(nd) for nd in graph.nodes()]
    pairs, attempts = [], 0
    while len(pairs) < n and attempts < n*30:
        o = rng.choice(nodes); d = rng.choice(nodes)
        attempts += 1
        if o == d: continue
        try:
            if nx.shortest_path_length(graph, o, d) >= min_hops:
                pairs.append((o, d))
        except nx.NetworkXNoPath:
            continue
    print(f"[Eval] Generated {len(pairs)} OD pairs")
    return pairs


def select_scenario_slots(speed_data, scenario, n_slots=5):
    ms = speed_data.mean(axis=1); T = len(ms)
    if scenario == 'peak_hour':
        cands = np.where(ms <= np.percentile(ms, 25))[0]
    elif scenario == 'off_peak':
        cands = np.where(ms >= np.percentile(ms, 75))[0]
    else:
        cands = np.arange(SEQUENCE_LEN, T - N_FUTURE_STEPS - 20)
    chosen = np.random.default_rng(RANDOM_SEED).choice(
        cands, size=min(n_slots, len(cands)), replace=False)
    return [int(c) for c in chosen]


def inject_incident(sw, severity=0.4):
    rng = np.random.default_rng()
    n_aff = max(1, int(sw.shape[0]*0.15))
    aff   = rng.choice(sw.shape[0], n_aff, replace=False)
    m = sw.copy(); m[aff, SEQUENCE_LEN//2:] *= (1-severity); return m


def run_single_od(graph, origin, destination, sw, tt_fn_series,
                  model, scaler, edge_sensor_map, edge_lengths_m,
                  hist_avg_tt, free_flow_tt, scenario, delta):
    rec = {'origin':origin,'destination':destination,'scenario':scenario,'delta':delta}
    t0 = time.perf_counter()
    pred_tt_fn = tt_fn_series[0]
    rec['gru_inference_ms'] = (time.perf_counter()-t0)*1000
    curr_tt = compute_current_tt(sw[:,-1], edge_lengths_m, edge_sensor_map)
    r1 = dijkstra_current(graph, origin, destination, curr_tt)
    r2 = static_astar_historical(graph, origin, destination, hist_avg_tt)
    r3 = static_astar_historical(graph, origin, destination, curr_tt)
    r4 = oracle_astar(graph, origin, destination, curr_tt)
    rec.update({'b1_dijkstra_tt_s':r1.total_time_s,'b1_dijkstra_lat_ms':r1.latency_ms,
                'b2_static_astar_tt_s':r2.total_time_s,'b2_static_astar_lat_ms':r2.latency_ms,
                'b3_reactive_astar_tt_s':r3.total_time_s,'b3_reactive_astar_lat_ms':r3.latency_ms,
                'b4_oracle_tt_s':r4.total_time_s,'b4_oracle_lat_ms':r4.latency_ms})
    sim = JourneySimulator(graph=graph, tt_fn_series=tt_fn_series,
                           free_flow_tt=free_flow_tt, delta=delta, policy='threshold')
    res = sim.run(origin, destination)
    rec.update({'framework_tt_s':res.total_time_s,'framework_lat_ms':res.avg_latency_ms,
                'framework_n_replannings':res.n_replannings,'framework_feasible':res.feasible})
    fw = res.total_time_s
    for key, btt in [('vs_dijkstra',r1.total_time_s),('vs_static_astar',r2.total_time_s),
                     ('vs_reactive_astar',r3.total_time_s),('vs_oracle',r4.total_time_s)]:
        rec[f'reduction_{key}_pct'] = (btt-fw)/btt*100 if btt>0 else 0.0
    return rec


def run_evaluation(model_dir='models/saved', data_dir='data',
                   results_dir='results', dataset='metr_la',
                   use_synthetic=False, sliding=False):
    os.makedirs(results_dir, exist_ok=True)
    rng = np.random.default_rng(RANDOM_SEED)
    print(f"\n{'='*60}")
    print(f"  Dataset: {dataset.upper().replace('_','-')}  |  Sliding: {'YES' if sliding else 'NO'}")
    print(f"{'='*60}\n")

    print("[Phase 1] Loading GRU model...")
    model, scaler = load_model_and_scaler(model_dir)

    print("[Phase 2] Building road graph...")
    graph, esm, elm = load_graph(data_dir, use_synthetic)
    N = min(graph.number_of_nodes(), SENSOR_COUNTS.get(dataset, 207))

    print("[Phase 3] Loading speed data...")
    sd = None if use_synthetic else load_speed_data(data_dir, dataset)
    if sd is None:
        T = 52128 if dataset=='pems_bay' else 34272
        sd = rng.normal(45,15,(T,N)).clip(5,80).astype(np.float32)
        print(f"[Phase 3] Synthetic speed data: ({T},{N})")
    N = min(sd.shape[1], N); sd = sd[:,:N]

    print("[Phase 4] Pre-computing historical averages...")
    hist_avg_tt = compute_historical_avg_tt(sd, elm, esm)
    free_flow_tt= get_free_flow_travel_time(elm)

    print("[Phase 5] Generating OD pairs...")
    od_pairs = generate_od_pairs(graph, N_OD_PAIRS)

    total = len(od_pairs)*len(SCENARIOS)*len(DELTA_VALUES)
    print(f"\n[Phase 6] {len(od_pairs)} OD × {len(SCENARIOS)} scenarios × {len(DELTA_VALUES)} δ = {total} experiments\n")

    all_records, count = [], 0
    for scenario in SCENARIOS:
        slots = select_scenario_slots(sd, scenario, n_slots=5)
        for origin, destination in od_pairs:
            slot  = int(rng.choice(slots))
            start = max(0, slot - SEQUENCE_LEN)
            sw    = sd[start:slot,:N].T
            if sw.shape[1] < SEQUENCE_LEN:
                sw = np.pad(sw,((0,0),(SEQUENCE_LEN-sw.shape[1],0)),mode='edge')
            if scenario == 'incident': sw = inject_incident(sw)
            tt_series = build_tt_fn_series(sd,slot,model,scaler,elm,esm,N,sliding)
            for delta in DELTA_VALUES:
                count += 1
                if count % 100 == 0:
                    print(f"  Progress: {count}/{total} ({100*count//total}%)", flush=True)
                try:
                    rec = run_single_od(graph,origin,destination,sw,tt_series,
                                        model,scaler,esm,elm,hist_avg_tt,free_flow_tt,
                                        scenario,delta)
                    rec['dataset'] = dataset; rec['sliding'] = sliding
                    all_records.append(rec)
                except Exception as e:
                    print(f"  [WARN] {origin}→{destination} s={scenario} δ={delta}: {e}")

    df = pd.DataFrame(all_records)
    raw = os.path.join(results_dir,'evaluation_results.csv')
    df.to_csv(raw,index=False)
    print(f"\n[Phase 7] Results → {raw}")

    summary = _compute_summary(df)
    summary.to_csv(os.path.join(results_dir,'summary_stats.csv'))
    print(f"[Phase 8] Summary → {results_dir}/summary_stats.csv")

    print("\n[Phase 9] Generating figures...")
    try:
        from src.evaluation.analyse_results import run_full_analysis
        run_full_analysis(raw, os.path.join(results_dir,'figures'))
        print(f"[Phase 9] Figures → {results_dir}/figures/")
    except Exception as e:
        print(f"[Phase 9] Error: {e}")

    return df


def _compute_summary(df):
    metrics = ['framework_tt_s','b1_dijkstra_tt_s','b2_static_astar_tt_s',
               'framework_lat_ms','framework_n_replannings',
               'reduction_vs_dijkstra_pct','reduction_vs_static_astar_pct',
               'reduction_vs_oracle_pct','gru_inference_ms']
    avail = [m for m in metrics if m in df.columns]
    if df.empty or 'scenario' not in df.columns: return pd.DataFrame()
    return df.groupby(['scenario','delta'])[avail].agg(['mean','std','median']).round(3)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--model-dir',    default='models/saved')
    p.add_argument('--data-dir',     default='data')
    p.add_argument('--results-dir',  default='results')
    p.add_argument('--dataset',      default='metr_la', choices=['metr_la','pems_bay'])
    p.add_argument('--synthetic',    action='store_true')
    p.add_argument('--sliding-window', action='store_true')
    args = p.parse_args()
    run_evaluation(model_dir=args.model_dir, data_dir=args.data_dir,
                   results_dir=args.results_dir, dataset=args.dataset,
                   use_synthetic=args.synthetic, sliding=args.sliding_window)