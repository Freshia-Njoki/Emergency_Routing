"""
Shared ground-truth simulation used by run_simulation.py and evaluate_framework.py.

Design (thesis Sections 3.7-3.9):
  * Routing decisions use each method's own information
    (GRU forecasts / current snapshot / historical mean / oracle future).
  * Every method is then TRAVERSED with actual future speeds (ground truth).
  * Sliding-window GRU advances as the vehicle moves; an incident that
    starts mid-journey is revealed in later observations so the threshold
    controller can replan, while Dijkstra never replans.
  * Incidents are placed on the Dijkstra path (not random sensors) so there
    is a genuine alternative to avoid.
"""
from __future__ import annotations

import heapq
import math
import os
import pickle
import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from src.routing.travel_times import (
    MPS_PER_MPH,
    build_interpolator,
    edge_speeds_to_tt,
    free_flow_tt_seconds,
    remap_sensors_to_major_roads,
    sensors_on_path,
    speeds_to_edge_speeds,
    to_simple_digraph,
    normalize_edge_sensor_map,
)
from src.utils.console import ascii_safe, configure_utf8, safe_print

STEP_S = 300.0
SEQUENCE_LEN = 12
N_FUTURE = 6
N_SENSORS_LA = 207
RANDOM_SEED = 42


# ── model I/O ─────────────────────────────────────────────────────────────────

def load_keras_model(model_dir: str, n_sensors: int = N_SENSORS_LA):
    import tensorflow as tf

    dummy = np.zeros((1, SEQUENCE_LEN, n_sensors), dtype=np.float32)
    for fname in (
        "gru_improved_best.keras", "gru_improved_best.h5",
        "gru_best.keras", "gru_best.h5", "gru_traffic_model.h5",
    ):
        path = os.path.join(model_dir, fname)
        if not os.path.exists(path):
            continue
        try:
            m = tf.keras.models.load_model(path, compile=False)
            m.predict(dummy, verbose=0)
            safe_print(f"  [OK] Loaded model: {path}")
            return m
        except Exception:
            pass
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import GRU, Dropout, Dense, Input, Reshape

            m = Sequential([
                Input(shape=(SEQUENCE_LEN, n_sensors)),
                GRU(64, return_sequences=True),
                Dropout(0.2),
                GRU(64, return_sequences=False),
                Dropout(0.2),
                Dense(N_FUTURE * n_sensors),
                Reshape((N_FUTURE, n_sensors)),
            ])
            m.predict(dummy, verbose=0)
            m.load_weights(path, by_name=True, skip_mismatch=True)
            m.predict(dummy, verbose=0)
            safe_print(f"  [OK] Loaded weights: {path}")
            return m
        except Exception as exc:
            safe_print(f"  [WARN] {fname}: {exc}")
    raise RuntimeError(f"No GRU model found in {model_dir}")


def load_scaler(model_dir: str, processed_dir: str):
    for path in (
        os.path.join(processed_dir, "scaler.pkl"),
        os.path.join(model_dir, "scaler.pkl"),
    ):
        if os.path.exists(path):
            with open(path, "rb") as f:
                scaler = pickle.load(f)
            safe_print(f"  [OK] Loaded scaler: {path} (n_features={getattr(scaler, 'n_features_in_', '?')})")
            return scaler
    raise FileNotFoundError("scaler.pkl not found")


def inverse_speed(scaler, values: np.ndarray) -> np.ndarray:
    """Inverse-transform scaled speeds regardless of scaler n_features."""
    arr = np.asarray(values, dtype=np.float64)
    shape = arr.shape
    n_feat = int(getattr(scaler, "n_features_in_", 1))
    if n_feat == 1:
        out = scaler.inverse_transform(arr.reshape(-1, 1)).reshape(shape)
    else:
        # per-sensor scaler: last axis must be n_feat
        if arr.ndim == 1:
            out = scaler.inverse_transform(arr.reshape(1, -1)).reshape(shape)
        elif arr.shape[-1] == n_feat:
            out = scaler.inverse_transform(arr.reshape(-1, n_feat)).reshape(shape)
        else:
            out = scaler.inverse_transform(arr.reshape(-1, 1)).reshape(shape)
    return np.clip(out, 1.0, 90.0)


def scale_speed(scaler, values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    shape = arr.shape
    n_feat = int(getattr(scaler, "n_features_in_", 1))
    if n_feat == 1:
        return scaler.transform(arr.reshape(-1, 1)).reshape(shape)
    if arr.ndim >= 1 and arr.shape[-1] == n_feat:
        return scaler.transform(arr.reshape(-1, n_feat)).reshape(shape)
    return scaler.transform(arr.reshape(-1, 1)).reshape(shape)


def fuse_forecast(
    pred_mph: np.ndarray,
    current_mph: np.ndarray,
    persist_idx=None,
    persist_row=None,
    n_nowcast: int = 1,
) -> np.ndarray:
    """Blend a current speed snapshot into the GRU horizon.

    Slot 0 (and optionally a half-blend of slot 1) uses what the vehicle
    can actually observe *now*.  Later slots keep the GRU forecast.
    If an incident has been observed, affected sensors are clamped to the
    observed slow speed for the whole horizon (persistence nowcast).
    """
    out = np.asarray(pred_mph, dtype=np.float64).copy()
    cur = np.asarray(current_mph, dtype=np.float64).reshape(-1)
    n_sensors = min(out.shape[-1], cur.shape[0])
    n = min(int(n_nowcast), out.shape[0])
    for i in range(n):
        out[i, :n_sensors] = cur[:n_sensors]
    if out.shape[0] > n:
        out[n, :n_sensors] = 0.5 * cur[:n_sensors] + 0.5 * out[n, :n_sensors]
    if persist_idx is not None and persist_row is not None:
        idx = np.asarray(persist_idx, dtype=int)
        idx = idx[(idx >= 0) & (idx < n_sensors)]
        if idx.size:
            obs = np.asarray(persist_row, dtype=np.float64).reshape(-1)
            out[:, idx] = np.minimum(out[:, idx], obs[idx])
    return np.clip(out, 1.0, 90.0)


def remaining_deteriorated(T_new: float, T_old: float, delta: float) -> bool:
    """Thesis Section 3.8: (T_new - T_old) / T_old > delta."""
    return T_old > 1.0 and (T_new - T_old) / T_old > float(delta)


def should_accept_replan(
    T_old: float,
    T_new: float,
    T_alt: float,
    delta: float,
    paths_differ: bool,
) -> bool:
    """Take the new TD-A* path if the current plan got worse *or* a
    substantially better alternative appeared (opportunity replan)."""
    if not paths_differ or T_alt is None:
        return False
    deteriorated = remaining_deteriorated(T_new, T_old, delta)
    if deteriorated and T_alt < T_new - 1.0:
        return True
    if T_old > 1.0 and (T_old - T_alt) / T_old > float(delta):
        return True
    return False


def gru_predict_mph(model, scaler, x_window_scaled: np.ndarray) -> np.ndarray:
    """
    x_window_scaled: (SEQUENCE_LEN, N) scaled
    returns (N_FUTURE, N) mph
    """
    n_sensors = x_window_scaled.shape[-1]
    x = x_window_scaled.reshape(1, SEQUENCE_LEN, n_sensors).astype(np.float32)
    raw = np.asarray(model.predict(x, verbose=0))
    if raw.ndim == 2 and raw.shape[-1] == n_sensors * N_FUTURE:
        raw = raw.reshape(1, N_FUTURE, n_sensors)
    elif raw.ndim == 2 and raw.shape == (1, n_sensors):
        raw = np.repeat(raw[:, None, :], N_FUTURE, axis=1)
    elif raw.ndim == 3:
        if raw.shape[1] == n_sensors and raw.shape[2] == N_FUTURE:
            raw = np.transpose(raw, (0, 2, 1))
        raw = raw.reshape(1, raw.shape[1], raw.shape[2])
    else:
        raw = raw.reshape(1, N_FUTURE, n_sensors)
    pred = inverse_speed(scaler, raw[0])
    return np.clip(pred.astype(np.float64), 1.0, 90.0)


def load_graph_and_costs(
    processed_dir: str,
    n_sensors: int = N_SENSORS_LA,
    remap: bool = True,
    graph_mode: str = "sensor",
):
    """
    graph_mode:
      'sensor' — METR-LA detector adjacency (207 nodes, every edge instrumented)
      'osm'    — downtown OSM graph with interpolated speeds
    """
    adj_path = os.path.join("data", "raw", "sensor_graph", "adj_mx.pkl")
    npz_path = os.path.join("data", "raw", "sensor_graph", "adj_mx.npz")
    loc_path = os.path.join("data", "raw", "sensor_graph", "graph_sensor_locations.csv")

    if graph_mode == "sensor":
        if not os.path.exists(adj_path) and not os.path.exists(npz_path):
            try:
                from download_data import download_sensor_graph
                download_sensor_graph()
            except Exception as exc:
                safe_print(f"  [WARN] Could not auto-download sensor graph: {exc}")
    sensor_graph_path = adj_path if os.path.exists(adj_path) else npz_path
    if graph_mode == "sensor" and os.path.exists(sensor_graph_path):
        from src.routing.graph_builder import build_graph_from_adjacency
        G, esm, lengths = build_graph_from_adjacency(
            sensor_graph_path, loc_path if os.path.exists(loc_path) else None, threshold=0.1
        )
        for u, v, data in G.edges(data=True):
            data.setdefault("highway", "motorway")
            data.setdefault("maxspeed", "65 mph")
        safe_print(
            f"  [OK] METR-LA sensor graph: {G.number_of_nodes()} nodes, "
            f"{G.number_of_edges()} edges, {len(esm)} fully instrumented"
        )
        weights, ff_mph, lengths = build_interpolator(
            G, esm, n_sensors=n_sensors, max_dist_m=2500.0
        )
        ff_tt = free_flow_tt_seconds(lengths, ff_mph)
        return G, esm, weights, ff_mph, lengths, ff_tt

    net_path = os.path.join(processed_dir, "la_road_network.pkl")
    esm_path = os.path.join(processed_dir, "edge_sensor_mapping.pkl")
    with open(net_path, "rb") as f:
        G_raw = pickle.load(f)
    G = to_simple_digraph(G_raw)

    if remap:
        esm, _ = remap_sensors_to_major_roads(G, n_sensors=n_sensors, seed=RANDOM_SEED)
        safe_print(
            f"  [OK] Remapped {len(esm)} sensors onto major-road edges "
            f"({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)"
        )
    else:
        with open(esm_path, "rb") as f:
            esm = normalize_edge_sensor_map(pickle.load(f))
        safe_print(f"  [OK] Loaded existing mapping: {len(esm)} sensor-mapped edges")

    weights, ff_mph, lengths = build_interpolator(G, esm, n_sensors=n_sensors)
    ff_tt = free_flow_tt_seconds(lengths, ff_mph)
    return G, esm, weights, ff_mph, lengths, ff_tt


def load_test_arrays(processed_dir: str, scaler, n_sensors: int = N_SENSORS_LA):
    """
    Returns mph arrays for routing + scaled windows for GRU.

    Also returns full-history mph (T, N) reconstructed from the npz so
    evaluate_framework no longer treats *scaled* values as miles per hour
    (that bug produced the fake ~78% sliding-window reduction).
    """
    npz = os.path.join(processed_dir, "training_data.npz")
    raw_path = os.path.join(processed_dir, "speed_data_raw.npy")
    d = np.load(npz)

    X_test_scaled = d["X_test"]
    y_test_scaled = d["y_test"]
    T, NF, NS = y_test_scaled.shape
    NS = min(NS, n_sensors)

    y_test_mph = inverse_speed(scaler, y_test_scaled[..., :NS]).astype(np.float32)
    X_last_mph = inverse_speed(scaler, X_test_scaled[:, -1, :NS]).astype(np.float32)

    X_train_scaled = d["X_train"]
    hist_mph = inverse_speed(
        scaler, X_train_scaled[..., :NS]
    ).reshape(-1, NS).mean(axis=0)
    hist_mph = np.clip(hist_mph, 1.0, 90.0).astype(np.float32)

    if os.path.exists(raw_path):
        speed_hist = np.load(raw_path).astype(np.float32)
        if speed_hist.ndim == 2:
            speed_hist = np.clip(speed_hist[:, :NS], 1.0, 90.0)
        else:
            speed_hist = None
    else:
        # Reconstruct an approximate full series from window starts (already mph
        # if inverse-transformed).  Used only for scenario slot picking.
        parts = []
        for split in ("X_train", "X_val", "X_test"):
            if split in d.files:
                parts.append(inverse_speed(scaler, d[split][:, 0, :NS]))
        speed_hist = np.vstack(parts).astype(np.float32) if parts else X_last_mph

    safe_print(
        f"  [OK] Test windows={T}  future={y_test_mph.shape}  "
        f"hist_mean={float(hist_mph.mean()):.1f} mph"
    )
    return (
        X_test_scaled[..., :NS].astype(np.float32),
        X_last_mph[:, :NS],
        y_test_mph[..., :NS],
        hist_mph[:NS],
        speed_hist,
    )


# ── routing ───────────────────────────────────────────────────────────────────

def heuristic(G, n, goal, ff_tt) -> float:
    try:
        d1, d2 = G.nodes[n], G.nodes[goal]
        dist = 2 * 6_371_000 * math.asin(
            math.sqrt(
                min(
                    1.0,
                    math.sin(math.radians(d2["y"] - d1["y"]) / 2) ** 2
                    + math.cos(math.radians(d1["y"]))
                    * math.cos(math.radians(d2["y"]))
                    * math.sin(math.radians(d2["x"] - d1["x"]) / 2) ** 2,
                )
            )
        )
        return dist / (65.0 * MPS_PER_MPH)
    except Exception:
        return 0.0


def _edge_cost(tt_dict, ff_tt, u, v, elapsed: float) -> float:
    val = tt_dict.get((u, v), ff_tt.get((u, v), 300.0))
    if hasattr(val, "__len__") and not isinstance(val, (str, bytes)):
        slot = min(int(elapsed // STEP_S), len(val) - 1)
        return float(max(val[slot], 1.0))
    return float(max(val, 1.0))


def astar_route(G, origin, dest, tt_dict, ff_tt):
    t0 = time.perf_counter()
    if origin == dest:
        return [origin], 0.0
    g_sc = {origin: 0.0}
    prev = {origin: None}
    heap = [(heuristic(G, origin, dest, ff_tt), 0.0, origin)]
    while heap:
        _, g, u = heapq.heappop(heap)
        if g > g_sc.get(u, math.inf) + 1e-9:
            continue
        if u == dest:
            path, node = [], dest
            while node is not None:
                path.append(node)
                node = prev[node]
            path.reverse()
            return path, (time.perf_counter() - t0) * 1000.0
        for v in G.successors(u):
            ng = g + _edge_cost(tt_dict, ff_tt, u, v, g)
            if ng < g_sc.get(v, math.inf):
                g_sc[v] = ng
                prev[v] = u
                heapq.heappush(heap, (ng + heuristic(G, v, dest, ff_tt), ng, v))
    return [origin], (time.perf_counter() - t0) * 1000.0


def remaining_on_path(path, tt_dict, ff_tt, elapsed: float) -> float:
    total = 0.0
    t = elapsed
    for i in range(len(path) - 1):
        dt = _edge_cost(tt_dict, ff_tt, path[i], path[i + 1], t)
        total += dt
        t += dt
    return total


def actual_edge_seconds(u, v, elapsed, actual_mph, weights, lengths, ff_mph) -> float:
    slot = min(int(elapsed // STEP_S), max(actual_mph.shape[0] - 1, 0))
    wts = weights.get((u, v), [])
    length = float(lengths.get((u, v), 500.0))
    if wts:
        spd = 0.0
        for sidx, w in wts:
            if sidx < actual_mph.shape[1]:
                spd += w * float(actual_mph[slot, sidx])
        spd = max(spd, 3.0)
    else:
        spd = float(ff_mph.get((u, v), 30.0))
    return length / max(spd * MPS_PER_MPH, 0.5)


def simulate_path(
    path,
    actual_mph,
    weights,
    lengths,
    ff_mph,
    t_inc: float = None,
    actual_inc: np.ndarray = None,
) -> float:
    """Traverse `path`. After wall-clock t_inc, switch to incident speeds.

    Timeline stays aligned with the original 5-minute slots (do not restart
    the slot index at t_inc — that used to sample the wrong future).
    """
    elapsed = 0.0
    for i in range(len(path) - 1):
        speeds = actual_mph
        if actual_inc is not None and t_inc is not None and elapsed >= t_inc:
            speeds = actual_inc
        elapsed += actual_edge_seconds(
            path[i], path[i + 1], elapsed, speeds, weights, lengths, ff_mph
        )
    return elapsed


def simulate_reactive(
    G,
    origin,
    dest,
    curr_tt,
    ff_tt,
    actual_mph,
    weights,
    lengths,
    ff_mph,
    t_inc: float = None,
    actual_inc: np.ndarray = None,
) -> float:
    """B3: reactive A* — same as Dijkstra until current speeds change,
    then one replan on the latest snapshot (no GRU horizon)."""
    path, _ = astar_route(G, origin, dest, curr_tt, ff_tt)
    elapsed = 0.0
    current = origin
    replanned = False
    while current != dest:
        if (
            (not replanned)
            and actual_inc is not None
            and t_inc is not None
            and elapsed >= t_inc
        ):
            inc_tt = tt_from_speeds(actual_inc[0], weights, lengths, ff_mph)
            new_path, _ = astar_route(G, current, dest, inc_tt, ff_tt)
            if len(new_path) >= 2:
                path = new_path
            replanned = True
        if len(path) < 2:
            break
        nxt = path[1]
        speeds = actual_mph
        if actual_inc is not None and t_inc is not None and elapsed >= t_inc:
            speeds = actual_inc
        elapsed += actual_edge_seconds(
            current, nxt, elapsed, speeds, weights, lengths, ff_mph
        )
        current = nxt
        path = path[1:]
    return elapsed


def tt_from_speeds(speeds_mph, weights, lengths, ff_mph) -> dict:
    edge_spd = speeds_to_edge_speeds(speeds_mph, weights, ff_mph)
    return edge_speeds_to_tt(edge_spd, lengths)


# ── framework journey with sliding window + threshold ─────────────────────────

def _inject_into_window(x_scaled, scaler, observed_mph_row, affected, n_steps=6):
    """Copy already-observed (possibly incident) mph into the last n window steps."""
    window = x_scaled.copy()
    mph = inverse_speed(scaler, window)
    k = min(int(n_steps), mph.shape[0])
    idx = np.asarray(affected, dtype=int)
    row = np.asarray(observed_mph_row)
    mph[-k:, idx] = row[idx]
    return scale_speed(scaler, mph)


def simulate_framework(
    G,
    origin,
    dest,
    model,
    scaler,
    x_window_scaled,
    actual_mph,
    weights,
    lengths,
    ff_mph,
    ff_tt,
    delta: float,
    affected=None,
    severity: float = 0.4,
    x_future_scaled: Optional[np.ndarray] = None,
    t_inc: float = None,
    actual_inc: np.ndarray = None,
):
    """
    Adaptive controller (thesis 3.8):

        (T_new - T_old) / T_old  >  delta

    T_old = remaining time on the CURRENT path under the predictions used
            when that path was last issued.
    T_new = remaining time on that SAME path under the LATEST predictions.

    Predictions refresh when a 5-minute slot advances or when an incident
    becomes visible in the observation window (sliding window, 3.8).

    Costs fuse the current snapshot (nowcast) with the GRU horizon, and an
    observed incident is persisted on the affected sensors so the controller
    can actually see the slowdown.  A replan is accepted if the current path
    deteriorated by delta *or* a new TD-A* path is better by delta.

    Journey time is always accumulated from actual_mph (ground truth).
    """
    affected = np.asarray(affected if affected is not None else [], dtype=int)
    pred_cache = {}
    current_obs = np.asarray(actual_mph[0], dtype=np.float64).copy()

    def predict(window):
        key = window.tobytes()
        if key not in pred_cache:
            pred_cache[key] = gru_predict_mph(model, scaler, window)
        return pred_cache[key]

    def fused(window, persist: bool):
        pred = predict(window)
        persist_idx = affected if persist and affected.size else None
        persist_row = current_obs if persist_idx is not None else None
        return fuse_forecast(pred, current_obs, persist_idx, persist_row)

    window = x_window_scaled.copy()
    pred = fused(window, persist=False)
    pred_tt = tt_from_speeds(pred, weights, lengths, ff_mph)
    path, lat = astar_route(G, origin, dest, pred_tt, ff_tt)
    lats = [lat]
    n_rep = 0
    elapsed = 0.0
    current = origin
    last_slot = 0
    incident_revealed = False

    T_old = remaining_on_path(path, pred_tt, ff_tt, elapsed)

    def live_speeds(t):
        if actual_inc is not None and t_inc is not None and t >= t_inc:
            return actual_inc, t
        return actual_mph, t

    while current != dest:
        if len(path) < 2:
            break
        nxt = path[1]
        speeds_now, t_used = live_speeds(elapsed)
        slot_i = min(int(t_used // STEP_S), max(speeds_now.shape[0] - 1, 0))
        current_obs = np.asarray(speeds_now[slot_i], dtype=np.float64)
        elapsed += actual_edge_seconds(
            current, nxt, t_used, speeds_now, weights, lengths, ff_mph
        )
        current = nxt
        path = path[1:]
        if current == dest:
            break

        slot = min(int(elapsed // STEP_S), N_FUTURE - 1)
        should_refresh = slot > last_slot
        if (
            (not incident_revealed)
            and affected.size
            and t_inc is not None
            and elapsed >= t_inc
        ):
            should_refresh = True
            incident_revealed = True
            row = actual_inc[0] if actual_inc is not None else actual_mph[0]
            current_obs = np.asarray(row, dtype=np.float64)
            window = _inject_into_window(
                x_window_scaled, scaler, row, affected, n_steps=6,
            )
        elif slot > last_slot and x_future_scaled is not None:
            nxt_idx = min(slot, len(x_future_scaled) - 1)
            window = x_future_scaled[nxt_idx]
            if incident_revealed and affected.size:
                row = actual_inc[0] if actual_inc is not None else actual_mph[0]
                current_obs = np.asarray(row, dtype=np.float64)
                window = _inject_into_window(
                    window, scaler, row, affected, n_steps=6,
                )

        if should_refresh:
            last_slot = slot
            pred_new = fused(window, persist=incident_revealed)
            pred_tt_new = tt_from_speeds(pred_new, weights, lengths, ff_mph)
            T_new = remaining_on_path(path, pred_tt_new, ff_tt, elapsed)
            new_path, replan_lat = astar_route(G, current, dest, pred_tt_new, ff_tt)
            T_alt = (
                remaining_on_path(new_path, pred_tt_new, ff_tt, elapsed)
                if new_path and len(new_path) >= 2
                else T_new
            )
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


# ── OD pairs / scenarios ──────────────────────────────────────────────────────

def make_od_pairs(G, n_pairs: int, min_hops: int = 8, ff_tt=None, min_tt_s: float = 300.0):
    """Sample OD pairs long enough to span at least one 5-minute prediction slot."""
    import networkx as nx

    rng = np.random.default_rng(RANDOM_SEED)
    nodes = list(G.nodes())
    pairs = []
    attempts = 0
    limit = n_pairs * 200
    while len(pairs) < n_pairs and attempts < limit:
        attempts += 1
        o = int(nodes[int(rng.integers(0, len(nodes)))])
        d = int(nodes[int(rng.integers(0, len(nodes)))])
        if o == d:
            continue
        try:
            hops = nx.shortest_path_length(G, o, d)
            if hops < min_hops:
                continue
            if ff_tt is not None and min_tt_s:
                sp = nx.shortest_path(G, o, d)
                if remaining_on_path(sp, ff_tt, ff_tt, 0.0) < min_tt_s:
                    continue
        except Exception:
            continue
        pairs.append((o, d))
    seen = set()
    uniq = []
    for p in pairs:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    safe_print(
        f"  [OK] Generated {len(uniq)} OD pairs (min hops={min_hops}, "
        f"min free-flow {min_tt_s:.0f}s)"
    )
    return uniq[:n_pairs]


def pick_test_indices(y_test_mph, scenario, n=8):
    mean_speed = y_test_mph.mean(axis=(1, 2))
    if scenario == "peak_hour":
        cands = np.where(mean_speed <= np.percentile(mean_speed, 25))[0]
    elif scenario == "off_peak":
        cands = np.where(mean_speed >= np.percentile(mean_speed, 75))[0]
    else:
        cands = np.arange(len(mean_speed))
    rng = np.random.default_rng(RANDOM_SEED)
    return rng.choice(cands, size=min(n, len(cands)), replace=False).astype(int).tolist()


def apply_path_incident(
    actual_mph,
    path,
    weights,
    severity=0.60,
    start_slot=1,
    n_sensors_hit=None,
):
    """Corridor incident: 40% speed drop (severity=0.60) on path sensors.

    Thesis Section 3.9 specifies a 40% mid-journey speed reduction.  Applying
    it to the sensors that govern the current Dijkstra route (rather than a
    random 15% of the whole network) is what makes avoidance possible.
    """
    out = actual_mph.copy()
    affected = sensors_on_path(path, weights, top_n=n_sensors_hit)
    if not affected:
        n = out.shape[1]
        rng = np.random.default_rng(RANDOM_SEED)
        affected = rng.choice(n, size=max(1, int(n * 0.15)), replace=False).tolist()
    aff = np.array(affected, dtype=int)
    out[start_slot:, aff] *= float(severity)
    return out, aff


# ── experiment loop ───────────────────────────────────────────────────────────

def run_experiments(
    model,
    scaler,
    G,
    weights,
    lengths,
    ff_mph,
    ff_tt,
    X_test_seq,
    X_last,
    y_test_mph,
    hist_mph,
    n_od: int = 75,
    deltas: Sequence[float] = (0.05, 0.10, 0.15, 0.20),
    scenarios: Sequence[str] = ("peak_hour", "off_peak", "incident"),
    min_hops: int = 8,
    incident_severity: float = 0.60,
    min_tt_s: float = 300.0,
):
    configure_utf8()
    pairs = make_od_pairs(G, n_od, min_hops=min_hops, ff_tt=ff_tt, min_tt_s=min_tt_s)
    hist_tt = tt_from_speeds(hist_mph, weights, lengths, ff_mph)
    rng = np.random.default_rng(RANDOM_SEED)
    rows = []
    total = len(pairs) * len(scenarios) * len(deltas)
    safe_print(
        f"\n  {len(pairs)} OD x {len(scenarios)} scenarios x {len(deltas)} delta "
        f"= {total} runs\n"
    )
    count = 0
    gru_ms_acc = []

    for scenario in scenarios:
        indices = pick_test_indices(y_test_mph, scenario)
        for origin, dest in pairs:
            t_idx = int(indices[int(rng.integers(0, len(indices)))])
            actual = y_test_mph[t_idx]
            curr_mph = X_last[t_idx]
            curr_tt = tt_from_speeds(curr_mph, weights, lengths, ff_mph)

            b1_path, b1_lat = astar_route(G, origin, dest, curr_tt, ff_tt)
            affected = np.array([], dtype=int)
            actual_inc = None
            t_inc = None
            if scenario == "incident":
                actual_inc, affected = apply_path_incident(
                    actual, b1_path, weights, severity=incident_severity,
                    start_slot=0, n_sensors_hit=None,
                )
                t_inc = max(20.0, 0.20 * remaining_on_path(b1_path, curr_tt, ff_tt, 0.0))

            oracle_src = actual_inc if actual_inc is not None else actual
            oracle_tt = tt_from_speeds(oracle_src, weights, lengths, ff_mph)
            t_gru = time.perf_counter()
            pred_mph = gru_predict_mph(model, scaler, X_test_seq[t_idx])
            gru_ms = (time.perf_counter() - t_gru) * 1000.0
            gru_ms_acc.append(gru_ms)

            b2_path, b2_lat = astar_route(G, origin, dest, hist_tt, ff_tt)
            b4_path, b4_lat = astar_route(G, origin, dest, oracle_tt, ff_tt)

            b1_tt = simulate_path(b1_path, actual, weights, lengths, ff_mph, t_inc, actual_inc)
            b2_tt = simulate_path(b2_path, actual, weights, lengths, ff_mph, t_inc, actual_inc)
            b3_tt = simulate_reactive(
                G, origin, dest, curr_tt, ff_tt, actual, weights, lengths, ff_mph,
                t_inc, actual_inc,
            )
            b4_tt = simulate_path(b4_path, actual, weights, lengths, ff_mph, t_inc, actual_inc)

            # future scaled windows for sliding (next test samples, if any)
            horizon = min(N_FUTURE, len(X_test_seq) - t_idx)
            x_future = X_test_seq[t_idx: t_idx + horizon]

            for delta in deltas:
                count += 1
                if count % 50 == 0 or count == total:
                    safe_print(f"  Progress: {count}/{total} ({100 * count // total}%)")
                try:
                    fw_tt, n_rep, fw_lat = simulate_framework(
                        G, origin, dest, model, scaler,
                        X_test_seq[t_idx], actual, weights, lengths, ff_mph, ff_tt,
                        delta=float(delta),
                        affected=affected,
                        severity=incident_severity,
                        x_future_scaled=x_future,
                        t_inc=t_inc,
                        actual_inc=actual_inc,
                    )
                except Exception as exc:
                    safe_print(f"  [WARN] ({origin},{dest}) delta={delta}: {exc}")
                    continue

                def red(base):
                    if base > 0 and 0 < fw_tt < math.inf:
                        return (base - fw_tt) / base * 100.0
                    return 0.0

                rows.append({
                    "origin": origin,
                    "destination": dest,
                    "scenario": scenario,
                    "delta": float(delta),
                    "gru_ms": gru_ms,
                    "b1_tt_s": b1_tt,
                    "b2_tt_s": b2_tt,
                    "b3_tt_s": b3_tt,
                    "b4_tt_s": b4_tt,
                    "fw_tt_s": fw_tt,
                    "fw_lat_ms": fw_lat,
                    "n_replannings": n_rep,
                    "red_vs_b1": red(b1_tt),
                    "red_vs_b2": red(b2_tt),
                    "red_vs_b3": red(b3_tt),
                    "red_vs_b4": red(b4_tt),
                    # aliases used by analyse_results.py
                    "framework_tt_s": fw_tt,
                    "b1_dijkstra_tt_s": b1_tt,
                    "b2_static_astar_tt_s": b2_tt,
                    "b3_reactive_astar_tt_s": b3_tt,
                    "b4_oracle_tt_s": b4_tt,
                    "framework_lat_ms": fw_lat,
                    "framework_n_replannings": n_rep,
                    "gru_inference_ms": gru_ms,
                    "reduction_vs_dijkstra_pct": red(b1_tt),
                    "reduction_vs_static_astar_pct": red(b2_tt),
                    "reduction_vs_reactive_astar_pct": red(b3_tt),
                    "reduction_vs_oracle_pct": red(b4_tt),
                })
    return rows
