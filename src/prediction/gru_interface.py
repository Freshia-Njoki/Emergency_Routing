"""
gru_interface.py
----------------
Loads your trained GRU model (gru_best.h5 / gru_improved_best.h5) and
scaler.pkl, then exposes a single function:

    predict_travel_times(sensor_speeds, edge_sensor_map, road_graph)
        -> dict  {(u, v): [tt_t0, tt_t1, ..., tt_t5]}   (6 steps x 5 min)

This is the ONLY file the routing module ever calls.  It is a wrapper
around whatever model you already trained — zero changes needed there.
"""

import os
import pickle
import numpy as np

# ── constants (match your training setup) ────────────────────────────────────
SEQUENCE_LEN   = 12          # input time-steps fed to GRU
N_FUTURE_STEPS = 6           # 6 x 5 min = 30-min horizon
SPEED_UNIT_MPH_TO_MPS = 0.44704
FREE_FLOW_SPEED_MPS   = 30 * SPEED_UNIT_MPH_TO_MPS   # ~13.4 m/s  (30 mph)


def load_model_and_scaler(model_dir: str):
    """
    Loads gru_improved_best.h5 (preferred) or gru_best.h5 from model_dir,
    plus scaler.pkl.  Returns (model, scaler).
    """
    try:
        import tensorflow as tf
    except ImportError:
        raise ImportError("TensorFlow not installed. Run: pip install tensorflow")

    # prefer the improved model if it exists
    for fname in ("gru_improved_best.h5", "gru_best.h5"):
        path = os.path.join(model_dir, fname)
        if os.path.exists(path):
            model = tf.keras.models.load_model(path, compile=False)
            print(f"[GRU Interface] Loaded model: {path}")
            break
    else:
        raise FileNotFoundError(
            f"No GRU model found in {model_dir}. "
            "Expected gru_best.h5 or gru_improved_best.h5"
        )

    scaler_path = os.path.join(model_dir, "scaler.pkl")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"scaler.pkl not found at {scaler_path}")
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    print(f"[GRU Interface] Loaded scaler: {scaler_path}")
    return model, scaler


def predict_speeds(model, scaler, recent_speeds: np.ndarray) -> np.ndarray:
    """
    Parameters:  recent_speeds shape (207, 12)
    Returns:     predicted speeds shape (207, 6)
    """
    n_sensors, seq_len = recent_speeds.shape   # 207, 12
    n_feat = scaler.n_features_in_

    # ── Step 1: Scale input ───────────────────────────────────────────────────
    if n_feat == n_sensors:                    # scaler fitted on (T, 207)
        ts_scaled = scaler.transform(recent_speeds.T)   # (12, 207)
        scaled    = ts_scaled.T                          # (207, 12)
    elif n_feat == 1:
        flat   = recent_speeds.reshape(-1, 1)
        scaled = scaler.transform(flat).reshape(n_sensors, seq_len)
    else:
        mu    = recent_speeds.mean()
        sigma = recent_speeds.std() + 1e-8
        scaled = (recent_speeds - mu) / sigma

    # ── Step 2: Build model input ─────────────────────────────────────────────
    in_shape = model.input_shape               # e.g. (None, 12, 1) or (None, 12, 207)
    n_in_feat = in_shape[-1]

    if n_in_feat == 1:
        X = scaled.reshape(n_sensors, seq_len, 1)      # (207, 12, 1)
    elif n_in_feat == n_sensors:
        X = scaled.T[np.newaxis, :, :]                  # (1, 12, 207)
    else:
        X = scaled.reshape(n_sensors, seq_len, 1)

    # ── Step 3: Predict ───────────────────────────────────────────────────────
    raw = model.predict(X, verbose=0)          # unknown shape — handle all cases

    # ── Step 4: Force output to (207, 6) ─────────────────────────────────────
    raw = np.array(raw)

    if raw.ndim == 1:
        # (207*6,) → (207, 6)
        raw = raw.reshape(n_sensors, -1)

    elif raw.ndim == 2:
        # Could be (207, 6), (6, 207), (1, 207*6), (207, 1) etc.
        if raw.shape == (n_sensors, 6):
            pass                                         # already correct
        elif raw.shape == (6, n_sensors):
            raw = raw.T                                  # (207, 6)
        elif raw.shape[0] == 1:
            raw = raw.reshape(n_sensors, -1)             # (1, X) → (207, 6)
        elif raw.shape[1] == 1:
            raw = np.repeat(raw, 6, axis=1)              # (207, 1) → (207, 6)

    elif raw.ndim == 3:
        # Could be (207, 6, 1), (1, 6, 207), (1, 207, 6) etc.
        if raw.shape[0] == 1 and raw.shape[1] == seq_len:
            raw = raw[0].T                               # (1,12,207)→(207,12) wrong
        elif raw.shape[0] == 1:
            raw = raw[0]                                 # (1, 6, 207) → (6, 207)
            if raw.shape[0] != n_sensors:
                raw = raw.T                              # → (207, 6)
        elif raw.shape[-1] == 1:
            raw = raw[:, :, 0]                           # (207, 6, 1) → (207, 6)
        else:
            raw = raw.reshape(n_sensors, -1)

    # Final safety check
    if raw.shape[0] != n_sensors:
        raw = raw.T
    if raw.ndim != 2 or raw.shape[1] < 1:
        raw = np.full((n_sensors, 6), recent_speeds.mean())

    # ── Step 5: Inverse scale ─────────────────────────────────────────────────
    if n_feat == n_sensors:
        pred_mph = scaler.inverse_transform(raw.T).T    # (207, 6)
    elif n_feat == 1:
        pred_mph = scaler.inverse_transform(
            raw.reshape(-1, 1)).reshape(n_sensors, -1)
    else:
        pred_mph = raw * sigma + mu

    return np.clip(pred_mph.astype(np.float64), 1.0, None)

def speeds_to_travel_times(pred_speeds_mph: np.ndarray,
                           edge_lengths_m: dict,
                           edge_sensor_map: dict) -> dict:
    """
    Converts sensor speed predictions to per-edge travel time functions.

    Parameters
    ----------
    pred_speeds_mph : (n_sensors, N_FUTURE_STEPS)
    edge_lengths_m  : {(u,v): length_in_metres}
    edge_sensor_map : {(u,v): sensor_index}  — which sensor governs this edge

    Returns
    -------
    travel_time_fn  : {(u,v): np.ndarray shape (N_FUTURE_STEPS,)}
                      travel time in seconds for each future 5-min slot
    """
    travel_time_fn = {}
    for edge, sensor_idx in edge_sensor_map.items():
        speeds_mps = pred_speeds_mph[sensor_idx] * SPEED_UNIT_MPH_TO_MPS
        length_m   = float(edge_lengths_m.get(edge, 500.0))
        tt_seconds = [float(length_m / max(float(s), 0.1)) for s in speeds_mps]
        travel_time_fn[edge] = tt_seconds
    return travel_time_fn


def get_free_flow_travel_time(edge_lengths_m: dict) -> dict:
    """Baseline: free-flow travel time (lower bound heuristic)."""
    return {e: L / FREE_FLOW_SPEED_MPS for e, L in edge_lengths_m.items()}