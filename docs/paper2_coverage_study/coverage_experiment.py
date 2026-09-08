"""
Sensor-coverage degradation experiment (second paper).

Holds the trained GRU, the detector graph, and the ground-truth future speeds
FIXED, and varies only the fraction of sensors whose live speed the router can
observe.  Uncovered edges inherit speeds by inverse-distance interpolation from
the nearest covered sensors (the same k-NN IDW used for the OSM graph).

Two speed fields per run:
  * weights_true  (100% sensors)  -> ground-truth traversal (what the vehicle
                                     actually experiences, including incidents)
  * weights_obs   (k% sensors)     -> routing costs the system can see and the
                                     snapshot/forecast it plans on
The GRU is trained once on the full historical archive; at "dispatch" only k%
of sensors stream live data used to build edge costs.

Design: delta fixed at 0.20 (Paper 1 showed travel time is invariant to delta),
3 sensor-retention seeds per coverage level for error bars, all three scenarios.
"""
from __future__ import annotations

import math
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.evaluation.simulation_core import (
    STEP_S, N_FUTURE,
    load_keras_model, load_scaler, load_graph_and_costs, load_test_arrays,
    make_od_pairs, pick_test_indices, apply_path_incident,
    astar_route, remaining_on_path, tt_from_speeds, gru_predict_mph,
    actual_edge_seconds, should_accept_replan, fuse_forecast,
    _inject_into_window, inverse_speed,
)
from src.routing.travel_times import build_interpolator
from src.utils.console import safe_print

MODEL_DIR = os.path.join("models", "saved")
PROCESSED_DIR = os.path.join("data", "processed")
RESULTS = "results/coverage"
os.makedirs(RESULTS, exist_ok=True)

COVERAGE_LEVELS = [1.0, 0.70, 0.50, 0.30, 0.20, 0.10]
RETENTION_SEEDS = [0, 1, 2]
DELTA = 0.20
N_OD = 50
SCENARIOS = ("peak_hour", "off_peak", "incident")
N_SENSORS = 207
MAX_DIST_M = 2500.0


def build_observed_weights(G, esm, retained: set):
    """Interpolator that only trusts the retained sensors; dropped-sensor edges
    inherit speeds by IDW from the nearest retained sensors."""
    esm_obs = {edge: s for edge, s in esm.items() if int(s) in retained}
    weights_obs, _ff, _len = build_interpolator(
        G, esm_obs, n_sensors=N_SENSORS, max_dist_m=MAX_DIST_M
    )
    return weights_obs


def simulate_reactive_2w(G, o, d, curr_tt_obs, ff_tt, actual_mph, actual_inc,
                         t_inc, weights_obs, weights_true, lengths, ff_mph):
    """B3 reactive: plans/replans on the OBSERVED snapshot; travels on TRUE speeds."""
    path, _ = astar_route(G, o, d, curr_tt_obs, ff_tt)
    elapsed = 0.0
    current = o
    replanned = False
    while current != d:
        if (not replanned) and actual_inc is not None and t_inc is not None and elapsed >= t_inc:
            inc_tt_obs = tt_from_speeds(actual_inc[0], weights_obs, lengths, ff_mph)
            new_path, _ = astar_route(G, current, d, inc_tt_obs, ff_tt)
            if len(new_path) >= 2:
                path = new_path
            replanned = True
        if len(path) < 2:
            break
        nxt = path[1]
        speeds = actual_mph
        if actual_inc is not None and t_inc is not None and elapsed >= t_inc:
            speeds = actual_inc
        elapsed += actual_edge_seconds(current, nxt, elapsed, speeds, weights_true, lengths, ff_mph)
        current = nxt
        path = path[1:]
    return elapsed


def simulate_framework_2w(G, o, d, model, scaler, x_window_scaled, actual_mph,
                          weights_obs, weights_true, lengths, ff_mph, ff_tt, delta,
                          affected_obs, x_future_scaled, t_inc, actual_inc):
    """Framework: routes on OBSERVED (k%) costs, detects the incident only on
    covered sensors (affected_obs), and travels on TRUE speeds."""
    affected_obs = np.asarray(affected_obs, dtype=int)
    pred_cache = {}
    current_obs = np.asarray(actual_mph[0], dtype=np.float64).copy()

    def predict(window):
        key = window.tobytes()
        if key not in pred_cache:
            pred_cache[key] = gru_predict_mph(model, scaler, window)
        return pred_cache[key]

    def fused(window, persist):
        pred = predict(window)
        pidx = affected_obs if persist and affected_obs.size else None
        prow = current_obs if pidx is not None else None
        return fuse_forecast(pred, current_obs, pidx, prow)

    window = x_window_scaled.copy()
    pred = fused(window, False)
    pred_tt = tt_from_speeds(pred, weights_obs, lengths, ff_mph)   # OBSERVED costs
    path, lat = astar_route(G, o, d, pred_tt, ff_tt)
    lats = [lat]
    n_rep = 0
    elapsed = 0.0
    current = o
    last_slot = 0
    incident_revealed = False
    T_old = remaining_on_path(path, pred_tt, ff_tt, elapsed)

    def live_speeds(t):
        if actual_inc is not None and t_inc is not None and t >= t_inc:
            return actual_inc
        return actual_mph

    while current != d:
        if len(path) < 2:
            break
        nxt = path[1]
        speeds_now = live_speeds(elapsed)
        slot_i = min(int(elapsed // STEP_S), max(speeds_now.shape[0] - 1, 0))
        current_obs = np.asarray(speeds_now[slot_i], dtype=np.float64)
        # TRUE traversal
        elapsed += actual_edge_seconds(current, nxt, elapsed, speeds_now, weights_true, lengths, ff_mph)
        current = nxt
        path = path[1:]
        if current == d:
            break

        slot = min(int(elapsed // STEP_S), N_FUTURE - 1)
        should_refresh = slot > last_slot
        # incident becomes visible ONLY if it touches covered sensors
        if (not incident_revealed) and affected_obs.size and t_inc is not None and elapsed >= t_inc:
            should_refresh = True
            incident_revealed = True
            row = actual_inc[0] if actual_inc is not None else actual_mph[0]
            current_obs = np.asarray(row, dtype=np.float64)
            window = _inject_into_window(x_window_scaled, scaler, row, affected_obs, n_steps=6)
        elif slot > last_slot and x_future_scaled is not None:
            nxt_idx = min(slot, len(x_future_scaled) - 1)
            window = x_future_scaled[nxt_idx]
            if incident_revealed and affected_obs.size:
                row = actual_inc[0] if actual_inc is not None else actual_mph[0]
                current_obs = np.asarray(row, dtype=np.float64)
                window = _inject_into_window(window, scaler, row, affected_obs, n_steps=6)

        if should_refresh:
            last_slot = slot
            pred_new = fused(window, incident_revealed)
            pred_tt_new = tt_from_speeds(pred_new, weights_obs, lengths, ff_mph)
            T_new = remaining_on_path(path, pred_tt_new, ff_tt, elapsed)
            new_path, replan_lat = astar_route(G, current, d, pred_tt_new, ff_tt)
            T_alt = remaining_on_path(new_path, pred_tt_new, ff_tt, elapsed) if new_path and len(new_path) >= 2 else T_new
            paths_differ = bool(new_path) and new_path != path
            if should_accept_replan(T_old, T_new, T_alt, delta, paths_differ):
                path = new_path
                n_rep += 1
                lats.append(replan_lat)
                pred_tt = pred_tt_new
                T_old = remaining_on_path(path, pred_tt, ff_tt, elapsed)
            else:
                T_old = remaining_on_path(path, pred_tt, ff_tt, elapsed)
        else:
            T_old = remaining_on_path(path, pred_tt, ff_tt, elapsed)
    return elapsed, n_rep, float(np.mean(lats)) if lats else 0.0


def simulate_path_true(path, actual_mph, weights_true, lengths, ff_mph, t_inc, actual_inc):
    elapsed = 0.0
    for i in range(len(path) - 1):
        speeds = actual_mph
        if actual_inc is not None and t_inc is not None and elapsed >= t_inc:
            speeds = actual_inc
        elapsed += actual_edge_seconds(path[i], path[i + 1], elapsed, speeds, weights_true, lengths, ff_mph)
    return elapsed


def run_one(model, scaler, G, esm, weights_true, ff_mph, lengths, ff_tt,
            X_test_seq, X_last, y_test_mph, hist_mph, coverage, ret_seed):
    rng_ret = np.random.default_rng(1000 + ret_seed)
    n_keep = max(1, int(round(coverage * N_SENSORS)))
    retained = set(int(s) for s in rng_ret.choice(N_SENSORS, size=n_keep, replace=False))
    if coverage >= 0.999:
        weights_obs = weights_true
    else:
        weights_obs = build_observed_weights(G, esm, retained)

    pairs = make_od_pairs(G, N_OD, min_hops=8, ff_tt=ff_tt, min_tt_s=300.0)
    hist_tt = tt_from_speeds(hist_mph, weights_obs, lengths, ff_mph)
    rng = np.random.default_rng(42)
    rows = []
    for scenario in SCENARIOS:
        indices = pick_test_indices(y_test_mph, scenario)
        for (o, d) in pairs:
            t_idx = int(indices[int(rng.integers(0, len(indices)))])
            actual = y_test_mph[t_idx]
            curr_mph = X_last[t_idx]
            curr_tt_obs = tt_from_speeds(curr_mph, weights_obs, lengths, ff_mph)
            b1_path, _ = astar_route(G, o, d, curr_tt_obs, ff_tt)

            affected = np.array([], dtype=int)
            affected_obs = np.array([], dtype=int)
            actual_inc = None
            t_inc = None
            if scenario == "incident":
                actual_inc, affected = apply_path_incident(
                    actual, b1_path, weights_true, severity=0.60, start_slot=0, n_sensors_hit=None)
                affected_obs = np.array([s for s in affected if int(s) in retained], dtype=int)
                t_inc = max(20.0, 0.20 * remaining_on_path(b1_path, curr_tt_obs, ff_tt, 0.0))

            oracle_src = actual_inc if actual_inc is not None else actual
            oracle_tt_obs = tt_from_speeds(oracle_src, weights_obs, lengths, ff_mph)
            pred_mph = gru_predict_mph(model, scaler, X_test_seq[t_idx])

            b2_path, _ = astar_route(G, o, d, hist_tt, ff_tt)
            b4_path, _ = astar_route(G, o, d, oracle_tt_obs, ff_tt)

            b1 = simulate_path_true(b1_path, actual, weights_true, lengths, ff_mph, t_inc, actual_inc)
            b2 = simulate_path_true(b2_path, actual, weights_true, lengths, ff_mph, t_inc, actual_inc)
            b3 = simulate_reactive_2w(G, o, d, curr_tt_obs, ff_tt, actual, actual_inc, t_inc,
                                      weights_obs, weights_true, lengths, ff_mph)
            b4 = simulate_path_true(b4_path, actual, weights_true, lengths, ff_mph, t_inc, actual_inc)

            horizon = min(N_FUTURE, len(X_test_seq) - t_idx)
            x_future = X_test_seq[t_idx: t_idx + horizon]
            fw, n_rep, fw_lat = simulate_framework_2w(
                G, o, d, model, scaler, X_test_seq[t_idx], actual,
                weights_obs, weights_true, lengths, ff_mph, ff_tt, DELTA,
                affected_obs, x_future, t_inc, actual_inc)

            def red(base):
                return (base - fw) / base * 100.0 if base > 0 else 0.0
            inc_visible = (len(affected_obs) > 0) if scenario == "incident" else None
            rows.append(dict(
                coverage=coverage, ret_seed=ret_seed, scenario=scenario,
                origin=o, destination=d,
                b1_tt_s=b1, b2_tt_s=b2, b3_tt_s=b3, b4_tt_s=b4, fw_tt_s=fw,
                red_vs_b1=red(b1), red_vs_b3=red(b3), n_replannings=n_rep,
                fw_lat_ms=fw_lat, n_affected=len(affected), n_affected_obs=len(affected_obs),
                incident_visible=inc_visible,
            ))
    return rows


def main():
    safe_print("Loading model/scaler/graph/test data ...")
    model = load_keras_model(MODEL_DIR)
    scaler = load_scaler(MODEL_DIR, PROCESSED_DIR)
    G, esm, weights_true, ff_mph, lengths, ff_tt = load_graph_and_costs(
        PROCESSED_DIR, remap=False, graph_mode="sensor")
    X_test_seq, X_last, y_test_mph, hist_mph, _ = load_test_arrays(PROCESSED_DIR, scaler)

    all_rows = []
    t0 = time.time()
    for cov in COVERAGE_LEVELS:
        seeds = [0] if cov >= 0.999 else RETENTION_SEEDS
        for rs in seeds:
            safe_print(f"\n=== coverage={int(cov*100)}%  ret_seed={rs} ===")
            rows = run_one(model, scaler, G, esm, weights_true, ff_mph, lengths, ff_tt,
                           X_test_seq, X_last, y_test_mph, hist_mph, cov, rs)
            all_rows.extend(rows)
            df = pd.DataFrame(all_rows)
            df.to_csv(os.path.join(RESULTS, "coverage_results.csv"), index=False)
            sub = df[(df.coverage == cov) & (df.ret_seed == rs) & (df.scenario == "incident")]
            safe_print(f"  incident mean red_vs_b1={sub.red_vs_b1.mean():.2f}%  "
                       f"visible={sub.incident_visible.mean()*100:.0f}%  "
                       f"replans={sub.n_replannings.mean():.2f}  elapsed={time.time()-t0:.0f}s")
    safe_print("\nDONE coverage sweep -> results/coverage/coverage_results.csv")


if __name__ == "__main__":
    main()
