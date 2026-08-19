"""
graph_builder.py
----------------
Builds a NetworkX DiGraph from METR-LA / PEMS-BAY sensor data.

Since METR-LA sensors sit on LA County highways, we construct the graph
using the sensor adjacency matrix (distances.csv / adj_mx.pkl) that ships
with the DCRNN / Li et al. 2018 data release.

Output graph node attributes: 'x' (lon), 'y' (lat), 'sensor_id'
Output graph edge attributes: 'length' (metres), 'sensor_pair'

Also exports:
    edge_sensor_map  : {(u,v): sensor_index}
    edge_lengths_m   : {(u,v): float}
    hist_avg_tt      : {(u,v): float}  — time-of-day historical averages
    node_positions   : {node_id: (lat, lon)}
"""

import os
import pickle
from typing import Dict, List, Optional, Tuple

import networkx as nx
import numpy as np


# ── METR-LA sensor metadata ───────────────────────────────────────────────────
# These are approximate centroids for LA county loop detectors.
# Replace with my actual sensor_locations.csv if available.
METR_LA_N_SENSORS = 207
PEMS_BAY_N_SENSORS = 325

# default speed for edge length estimation (mph → m/s)
AVG_HIGHWAY_SPEED_MPS = 25 * 0.44704   # 25 mph ≈ 11.2 m/s
SENSOR_SPACING_M      = 1000.0         # ~1 km between adjacent sensors


def _unpickle_bytes(raw: bytes):
    """Load a DCRNN Python-2 protocol-0 pickle, including Windows CRLF checkouts."""
    blobs = [raw, raw.replace(b"\r\n", b"\n"), raw.replace(b"\r", b"\n")]
    encodings = ("latin1", "bytes")
    last_err = None
    for blob in blobs:
        for encoding in encodings:
            try:
                return pickle.loads(blob, encoding=encoding)
            except Exception as exc:
                last_err = exc
        try:
            return pickle.loads(blob)
        except Exception as exc:
            last_err = exc
    raise last_err


def _from_npz(path: str) -> Tuple[List, np.ndarray]:
    z = np.load(path, allow_pickle=True)
    adj_mx = np.asarray(z["adj_mx"])
    if "sensor_ids" in z.files:
        sensor_ids = [str(s) for s in z["sensor_ids"].tolist()]
    else:
        sensor_ids = list(range(adj_mx.shape[0]))
    return sensor_ids, adj_mx


def _reconstruct_from_distances(adj_dir: str, normalized_k: float = 0.1
                                ) -> Tuple[List, np.ndarray]:
    """DCRNN Gaussian kernel on distances_la_2012.csv when the pickle cannot be read."""
    import pandas as pd

    loc_path = os.path.join(adj_dir, "graph_sensor_locations.csv")
    dist_path = os.path.join(adj_dir, "distances_la_2012.csv")
    if not (os.path.exists(loc_path) and os.path.exists(dist_path)):
        raise FileNotFoundError(
            "Need graph_sensor_locations.csv and distances_la_2012.csv to rebuild adjacency"
        )
    locs = pd.read_csv(loc_path)
    id_col = "sensor_id" if "sensor_id" in locs.columns else locs.columns[1]
    sensor_ids = [str(s) for s in locs[id_col].tolist()]
    id_to_ind = {sid: i for i, sid in enumerate(sensor_ids)}
    n = len(sensor_ids)
    dist_mx = np.full((n, n), np.inf, dtype=np.float64)
    dist_df = pd.read_csv(dist_path)
    for row in dist_df.itertuples(index=False):
        frm, to, cost = str(row[0]), str(row[1]), float(row[2])
        if frm in id_to_ind and to in id_to_ind:
            dist_mx[id_to_ind[frm], id_to_ind[to]] = cost
    finite = dist_mx[np.isfinite(dist_mx)]
    std = float(finite.std()) if finite.size else 1.0
    std = max(std, 1e-6)
    adj_mx = np.exp(-np.square(dist_mx / std))
    adj_mx[adj_mx < normalized_k] = 0.0
    np.fill_diagonal(adj_mx, 0.0)
    return sensor_ids, adj_mx


def load_adjacency_matrix(adj_mx_path: str) -> Tuple[List, np.ndarray]:
    """
    Load DCRNN (sensor_ids, adj_mx).

    Accepts .pkl (Python 2), .npz, or .npy. A sibling adj_mx.npz is preferred
    because Git on Windows often converts protocol-0 pickles to CRLF, which
    raises UnpicklingError: the STRING opcode argument must be quoted.
    """
    base, ext = os.path.splitext(adj_mx_path)
    adj_dir = os.path.dirname(adj_mx_path) or "."
    npz_path = base + ".npz"
    npy_path = base + ".npy"

    if ext.lower() == ".npz" and os.path.exists(adj_mx_path):
        return _from_npz(adj_mx_path)
    if os.path.exists(npz_path):
        return _from_npz(npz_path)
    if ext.lower() == ".npy" and os.path.exists(adj_mx_path):
        adj_mx = np.load(adj_mx_path)
        return list(range(adj_mx.shape[0])), np.asarray(adj_mx)
    if os.path.exists(npy_path):
        adj_mx = np.load(npy_path)
        return list(range(adj_mx.shape[0])), np.asarray(adj_mx)

    last_err = None
    if ext.lower() == ".pkl" and os.path.exists(adj_mx_path):
        try:
            with open(adj_mx_path, "rb") as f:
                data = _unpickle_bytes(f.read())
            if isinstance(data, (list, tuple)) and len(data) == 3:
                sensor_ids, _, adj_mx = data
                return list(sensor_ids), np.asarray(adj_mx)
            adj_mx = np.asarray(data)
            return list(range(adj_mx.shape[0])), adj_mx
        except Exception as exc:
            last_err = exc

    try:
        return _reconstruct_from_distances(adj_dir)
    except Exception as exc:
        detail = f"{last_err}; then {exc}" if last_err else str(exc)
        raise ValueError(
            f"Could not load adjacency from {adj_mx_path} ({detail})"
        ) from exc


def export_adjacency_npz(adj_mx_path: str, npz_path: Optional[str] = None) -> str:
    """Write a Python-3 npz next to the DCRNN pickle so Windows does not need it."""
    sensor_ids, adj_mx = load_adjacency_matrix(adj_mx_path)
    npz_path = npz_path or os.path.splitext(adj_mx_path)[0] + ".npz"
    np.savez_compressed(
        npz_path,
        adj_mx=np.asarray(adj_mx),
        sensor_ids=np.array(sensor_ids, dtype=object),
    )
    return npz_path


def build_graph_from_adjacency(adj_mx_path: str,
                                sensor_locs_path: Optional[str] = None,
                                threshold: float = 0.1
                                ) -> Tuple[nx.DiGraph, Dict, Dict]:
    """
    Build DiGraph from METR-LA/PEMS-BAY adjacency matrix.

    Parameters
    ----------
    adj_mx_path      : path to adj_mx.pkl  (from DCRNN data release)
                       OR adj_mx.npz / a numpy .npy file of shape (N, N)
    sensor_locs_path : optional CSV with columns: sensor_id, lat, lon
    threshold        : edges where adj_mx[i,j] > threshold are included

    Returns
    -------
    graph           : nx.DiGraph
    edge_sensor_map : {(u,v): sensor_index_of_u}
    edge_lengths_m  : {(u,v): float metres}
    """
    sensor_ids, adj_mx = load_adjacency_matrix(adj_mx_path)
    adj_mx = np.asarray(adj_mx)
    n = adj_mx.shape[0]

    # ── load sensor locations (optional) ─────────────────────────────────────
    locs = _load_sensor_locations(sensor_locs_path, n)

    # ── build graph ───────────────────────────────────────────────────────────
    G = nx.DiGraph()

    for i in range(n):
        G.add_node(i,
                   sensor_id=sensor_ids[i] if i < len(sensor_ids) else i,
                   y=locs[i][0],    # lat
                   x=locs[i][1])    # lon

    edge_sensor_map = {}
    edge_lengths_m  = {}

    for i in range(n):
        for j in range(n):
            if i != j and adj_mx[i, j] > threshold:
                # edge weight stored as distance proxy
                weight = adj_mx[i, j]
                # invert normalised weight to approximate distance
                # DCRNN uses Gaussian kernel: w_ij = exp(-dist²/σ²)
                # → dist ≈ σ * sqrt(-ln(w))  where σ ≈ 1000 m
                if weight < 1.0:
                    dist_m = max(100.0,
                                 1000.0 * np.sqrt(-np.log(weight + 1e-10)))
                else:
                    dist_m = SENSOR_SPACING_M

                G.add_edge(i, j, length=dist_m)
                edge_sensor_map[(i, j)] = i     # source sensor governs edge
                edge_lengths_m[(i, j)]  = dist_m

    print(f"[GraphBuilder] Graph: {G.number_of_nodes()} nodes, "
          f"{G.number_of_edges()} edges")
    return G, edge_sensor_map, edge_lengths_m


def build_synthetic_graph(n_sensors: int = METR_LA_N_SENSORS,
                           grid_cols: int = 23
                           ) -> Tuple[nx.DiGraph, Dict, Dict]:
    """
    Synthetic grid graph for testing when adj_mx is not available.
    Creates a grid-like sensor network with lat/lon coordinates near LA.

    n_sensors : number of sensor nodes
    grid_cols : sensors per row
    """
    G = nx.DiGraph()
    edge_sensor_map = {}
    edge_lengths_m  = {}

    # LA bounding box approximate
    lat_min, lat_max = 33.7, 34.4
    lon_min, lon_max = -118.7, -117.8

    grid_rows = (n_sensors + grid_cols - 1) // grid_cols

    for i in range(n_sensors):
        row = i // grid_cols
        col = i %  grid_cols
        lat = lat_min + (lat_max - lat_min) * row / max(grid_rows - 1, 1)
        lon = lon_min + (lon_max - lon_min) * col / max(grid_cols - 1, 1)
        G.add_node(i, y=lat, x=lon, sensor_id=i)

    # connect grid neighbours (4-directional + diagonals)
    for i in range(n_sensors):
        row_i, col_i = i // grid_cols, i % grid_cols
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            row_j = row_i + di
            col_j = col_i + dj
            j = row_j * grid_cols + col_j
            if 0 <= j < n_sensors and 0 <= row_j < grid_rows \
               and 0 <= col_j < grid_cols:
                dist_m = SENSOR_SPACING_M
                G.add_edge(i, j, length=dist_m)
                edge_sensor_map[(i, j)] = i
                edge_lengths_m[(i, j)]  = dist_m

    print(f"[GraphBuilder] Synthetic graph: {G.number_of_nodes()} nodes, "
          f"{G.number_of_edges()} edges")
    return G, edge_sensor_map, edge_lengths_m


def compute_historical_avg_tt(speed_data: np.ndarray,
                               edge_lengths_m: Dict,
                               edge_sensor_map: Dict,
                               n_slots_per_day: int = 288
                               ) -> Dict:
    """
    Computes time-of-day average travel times from historical speed data.

    Parameters
    ----------
    speed_data     : np.ndarray shape (T, N)  — T time steps, N sensors
    edge_lengths_m : {(u,v): float}
    edge_sensor_map: {(u,v): sensor_index}
    n_slots_per_day: 288 for 5-min intervals

    Returns
    -------
    hist_avg_tt    : {(u,v): float seconds}  — simple overall mean
    """
    avg_speed_mph = np.nanmean(speed_data, axis=0)   # (N,)
    avg_speed_mps = np.clip(avg_speed_mph * 0.44704, 0.5, None)

    hist_avg_tt = {}
    for edge, sensor_idx in edge_sensor_map.items():
        idx = int(np.array(sensor_idx).flat[0])
        if idx < 0 or idx >= len(avg_speed_mps):
            continue
        length_m = edge_lengths_m.get(edge, SENSOR_SPACING_M)
        hist_avg_tt[edge] = length_m / avg_speed_mps[idx]
    return hist_avg_tt


def compute_current_tt(current_speeds_mph: np.ndarray,
                       edge_lengths_m:     Dict,
                       edge_sensor_map:    Dict) -> Dict:
    """Travel times from current (departure-time) snapshot."""
    speeds_mps = np.clip(current_speeds_mph * 0.44704, 0.5, None)
    current_tt = {}
    for edge, sensor_idx in edge_sensor_map.items():
        idx = int(np.array(sensor_idx).flat[0])
        if idx < 0 or idx >= len(speeds_mps):
            continue
        length_m = edge_lengths_m.get(edge, SENSOR_SPACING_M)
        current_tt[edge] = float(length_m) / float(speeds_mps[idx])
    return current_tt


# ── helpers ───────────────────────────────────────────────────────────────────

def _load_sensor_locations(path: Optional[str], n: int):
    """Returns list of (lat, lon) for each sensor index."""
    if path and os.path.exists(path):
        import pandas as pd
        df = pd.read_csv(path)
        # expect columns: index/sensor_id, latitude/lat, longitude/lon
        lat_col = [c for c in df.columns if 'lat' in c.lower()][0]
        lon_col = [c for c in df.columns if 'lon' in c.lower()][0]
        locs = list(zip(df[lat_col], df[lon_col]))
        return locs[:n] if len(locs) >= n else \
               locs + [(34.0, -118.2)] * (n - len(locs))
    else:
        # generate synthetic spread around LA
        np.random.seed(42)
        lats = np.random.uniform(33.7, 34.4, n)
        lons = np.random.uniform(-118.7, -117.8, n)
        return list(zip(lats, lons))
    
def load_from_processed(processed_dir: str = 'data/processed'):
    """
    Loads the OSM road network and sensor map, collapsing MultiDiGraph
    parallel edges to a simple DiGraph with (u, v) keys.
    """
    import pickle
    from src.routing.travel_times import (
        to_simple_digraph, normalize_edge_sensor_map,
    )

    graph_path = os.path.join(processed_dir, 'la_road_network.pkl')
    esm_path   = os.path.join(processed_dir, 'edge_sensor_mapping.pkl')

    with open(graph_path, 'rb') as f:
        graph = to_simple_digraph(pickle.load(f))
    print(f"[GraphBuilder] Graph: "
          f"{graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

    with open(esm_path, 'rb') as f:
        edge_sensor_map = normalize_edge_sensor_map(pickle.load(f))

    print(f"[GraphBuilder] edge_sensor_map: "
          f"{len(edge_sensor_map)} edges, "
          f"sensor range 0-{max(edge_sensor_map.values()) if edge_sensor_map else 0}")

    edge_lengths_m = {}
    for u, v, data in graph.edges(data=True):
        edge_lengths_m[(int(u), int(v))] = float(data.get('length', 500.0))

    return graph, edge_sensor_map, edge_lengths_m 