"""
Predictor-accuracy ablation (paper part A).

Question: does a MORE accurate traffic forecast produce a BETTER ambulance route?

We hold the graph (100% coverage), the router, the controller (delta=0.20), and
the ground-truth speeds fixed, and vary ONLY the fidelity of the forecast the
framework routes on:
  * a spectrum from the raw GRU forecast, blended toward the true future
    (oracle) at fractions alpha in {0, .25, .5, .75, 1.0}, tracing MAE 3.5 -> 0;
  * a degraded branch (Gaussian noise added to the GRU forecast) tracing MAE
    above the GRU;
  * a real alternative architecture: a trained LSTM (lstm_best.keras) if present;
  * a naive historical-mean forecast (high MAE).
For each variant we record the effective forecast MAE (mph) and the resulting
incident travel-time reduction vs Dijkstra.  A flat curve => accuracy is not the
routing bottleneck.
"""
from __future__ import annotations
import os, sys, time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.evaluation.simulation_core import (
    STEP_S, N_FUTURE,
    load_keras_model, load_scaler, load_graph_and_costs, load_test_arrays,
    make_od_pairs, pick_test_indices, apply_path_incident,
    astar_route, remaining_on_path, tt_from_speeds, gru_predict_mph,
    actual_edge_seconds, should_accept_replan, fuse_forecast, _inject_into_window,
)
from src.utils.console import safe_print

MODEL_DIR, PROCESSED_DIR = "models/saved", "data/processed"
RESULTS = "results/accuracy"; os.makedirs(RESULTS, exist_ok=True)
DELTA, N_OD, N_SENSORS = 0.20, 50, 207


def simulate_framework_pred(G, o, d, transform, scaler, x_window_scaled, actual_mph,
                            weights, lengths, ff_mph, ff_tt, delta,
                            affected, x_future_scaled, t_inc, actual_inc, gru_fn):
    """transform(gru_pred (6,N)) -> variant forecast (6,N). gru_fn(window)->gru_pred."""
    affected = np.asarray(affected, dtype=int)
    current_obs = np.asarray(actual_mph[0], dtype=np.float64).copy()

    def fused(window, persist):
        pred = transform(gru_fn(window))
        pidx = affected if persist and affected.size else None
        prow = current_obs if pidx is not None else None
        return fuse_forecast(pred, current_obs, pidx, prow)

    window = x_window_scaled.copy()
    pred_tt = tt_from_speeds(fused(window, False), weights, lengths, ff_mph)
    path, _ = astar_route(G, o, d, pred_tt, ff_tt)
    n_rep = 0; elapsed = 0.0; current = o; last_slot = 0; revealed = False
    T_old = remaining_on_path(path, pred_tt, ff_tt, elapsed)

    def live(t):
        return (actual_inc, t) if (actual_inc is not None and t_inc is not None and t >= t_inc) else (actual_mph, t)

    while current != d:
        if len(path) < 2: break
        nxt = path[1]
        speeds_now, t_used = live(elapsed)
        si = min(int(t_used // STEP_S), max(speeds_now.shape[0]-1, 0))
        current_obs = np.asarray(speeds_now[si], dtype=np.float64)
        elapsed += actual_edge_seconds(current, nxt, t_used, speeds_now, weights, lengths, ff_mph)
        current = nxt; path = path[1:]
        if current == d: break
        slot = min(int(elapsed // STEP_S), N_FUTURE - 1)
        refresh = slot > last_slot
        if (not revealed) and affected.size and t_inc is not None and elapsed >= t_inc:
            refresh = True; revealed = True
            row = actual_inc[0] if actual_inc is not None else actual_mph[0]
            current_obs = np.asarray(row, dtype=np.float64)
            window = _inject_into_window(x_window_scaled, scaler, row, affected, n_steps=6)
        elif slot > last_slot and x_future_scaled is not None:
            window = x_future_scaled[min(slot, len(x_future_scaled)-1)]
            if revealed and affected.size:
                row = actual_inc[0] if actual_inc is not None else actual_mph[0]
                window = _inject_into_window(window, scaler, row, affected, n_steps=6)
        if refresh:
            last_slot = slot
            pred_tt_new = tt_from_speeds(fused(window, revealed), weights, lengths, ff_mph)
            T_new = remaining_on_path(path, pred_tt_new, ff_tt, elapsed)
            new_path, _ = astar_route(G, current, d, pred_tt_new, ff_tt)
            T_alt = remaining_on_path(new_path, pred_tt_new, ff_tt, elapsed) if new_path and len(new_path) >= 2 else T_new
            if should_accept_replan(T_old, T_new, T_alt, delta, bool(new_path) and new_path != path):
                path = new_path; n_rep += 1; pred_tt = pred_tt_new
            T_old = remaining_on_path(path, pred_tt, ff_tt, elapsed)
    return elapsed, n_rep


def simulate_path(path, actual_mph, weights, lengths, ff_mph, t_inc, actual_inc):
    e = 0.0
    for i in range(len(path)-1):
        s = actual_inc if (actual_inc is not None and t_inc is not None and e >= t_inc) else actual_mph
        e += actual_edge_seconds(path[i], path[i+1], e, s, weights, lengths, ff_mph)
    return e


def main():
    model = load_keras_model(MODEL_DIR)
    scaler = load_scaler(MODEL_DIR, PROCESSED_DIR)
    G, esm, weights, ff_mph, lengths, ff_tt = load_graph_and_costs(PROCESSED_DIR, remap=False, graph_mode="sensor")
    X_test_seq, X_last, y_test_mph, hist_mph, _ = load_test_arrays(PROCESSED_DIR, scaler)

    lstm = None
    if os.path.exists(os.path.join(MODEL_DIR, "lstm_best.keras")):
        import tensorflow as tf
        lstm = tf.keras.models.load_model(os.path.join(MODEL_DIR, "lstm_best.keras"), compile=False)
        safe_print("  [OK] loaded LSTM alternative")

    rng_noise = np.random.default_rng(7)
    # variant: (name, kind, param)
    variants = [
        ("oracle", "blend", 1.0), ("blend75", "blend", 0.75), ("blend50", "blend", 0.5),
        ("blend25", "blend", 0.25), ("gru", "blend", 0.0),
        ("gru_noise4", "noise", 4.0), ("gru_noise8", "noise", 8.0),
        ("historical", "hist", None),
    ]
    if lstm is not None:
        variants.insert(5, ("lstm", "lstm", None))

    pairs = make_od_pairs(G, N_OD, min_hops=8, ff_tt=ff_tt, min_tt_s=300.0)
    rng = np.random.default_rng(42)
    idx_inc = pick_test_indices(y_test_mph, "incident")
    rows = []

    def gru_fn(w):
        return gru_predict_mph(model, scaler, w)

    for (name, kind, param) in variants:
        red = []; maes = []; reps = []
        for (o, d) in pairs:
            t_idx = int(idx_inc[int(rng.integers(0, len(idx_inc)))])
            actual = y_test_mph[t_idx]
            curr_tt = tt_from_speeds(X_last[t_idx], weights, lengths, ff_mph)
            b1_path, _ = astar_route(G, o, d, curr_tt, ff_tt)
            actual_inc, affected = apply_path_incident(actual, b1_path, weights, severity=0.60, start_slot=0)
            t_inc = max(20.0, 0.20 * remaining_on_path(b1_path, curr_tt, ff_tt, 0.0))
            oracle_future = actual_inc  # (6,N) true future incl. incident

            def transform(gp, _name=name, _kind=kind, _param=param, _of=oracle_future):
                if _kind == "blend":
                    out = (1 - _param) * gp + _param * _of[:gp.shape[0]]
                elif _kind == "noise":
                    out = gp + rng_noise.normal(0, _param, size=gp.shape)
                elif _kind == "hist":
                    out = np.tile(hist_mph[:gp.shape[1]], (gp.shape[0], 1))
                elif _kind == "lstm":
                    out = gp  # placeholder; replaced below via lstm_fn
                return np.clip(out, 1.0, 90.0)

            if kind == "lstm":
                def lstm_transform(gp, _of=oracle_future):
                    x = X_test_seq[t_idx].reshape(1, 12, N_SENSORS).astype(np.float32)
                    raw = np.asarray(lstm.predict(x, verbose=0)).reshape(N_FUTURE, N_SENSORS)
                    from src.evaluation.simulation_core import inverse_speed
                    return np.clip(inverse_speed(scaler, raw), 1.0, 90.0)
                tfun = lstm_transform
            else:
                tfun = transform

            # effective MAE of this predictor vs true future
            base_pred = tfun(gru_predict_mph(model, scaler, X_test_seq[t_idx]))
            maes.append(float(np.mean(np.abs(base_pred - oracle_future[:base_pred.shape[0]]))))

            b1 = simulate_path(b1_path, actual, weights, lengths, ff_mph, t_inc, actual_inc)
            horizon = min(N_FUTURE, len(X_test_seq) - t_idx)
            fw, n_rep = simulate_framework_pred(
                G, o, d, tfun, scaler, X_test_seq[t_idx], actual, weights, lengths, ff_mph, ff_tt,
                DELTA, affected, X_test_seq[t_idx:t_idx+horizon], t_inc, actual_inc, gru_fn)
            red.append((b1 - fw) / b1 * 100.0 if b1 > 0 else 0.0)
            reps.append(n_rep)
        rows.append(dict(variant=name, pred_mae_mph=round(float(np.mean(maes)), 2),
                         incident_red_pct=round(float(np.mean(red)), 2),
                         red_sd=round(float(np.std(red)), 2), replans=round(float(np.mean(reps)), 2)))
        safe_print(f"  {name:12s} MAE={rows[-1]['pred_mae_mph']:5.2f} mph  reduction={rows[-1]['incident_red_pct']:6.2f}%")
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "accuracy_results.csv"), index=False)
    safe_print("\nDONE -> results/accuracy/accuracy_results.csv")


if __name__ == "__main__":
    main()
