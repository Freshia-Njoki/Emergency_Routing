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
    Predicts future speeds for all sensors.

    Parameters
    ----------
    model        : loaded Keras model
    scaler       : fitted MinMaxScaler / StandardScaler
    recent_speeds: np.ndarray shape (n_sensors, SEQUENCE_LEN)
                   last 12 x 5-min speed readings per sensor (mph)

    Returns
    -------
    predicted    : np.ndarray shape (n_sensors, N_FUTURE_STEPS)
                   predicted speeds in mph
    """
    n_sensors = recent_speeds.shape[0]

    # scale each sensor's sequence
    flat = recent_speeds.reshape(-1, 1)
    flat_scaled = scaler.transform(flat)
    scaled = flat_scaled.reshape(n_sensors, SEQUENCE_LEN, 1)

    # model expects (batch, timesteps, features)
    raw_pred = model.predict(scaled, verbose=0)   # (n_sensors, N_FUTURE_STEPS)

    # inverse-scale
    pred_flat = raw_pred.reshape(-1, 1)
    pred_mph  = scaler.inverse_transform(pred_flat).reshape(n_sensors, -1)

    # clip to safe minimum (avoid divide-by-zero in travel time)
    pred_mph = np.clip(pred_mph, 1.0, None)
    return pred_mph


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