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
import numpy as np
import networkx as nx
from typing import Dict, Tuple, Optional


# ── METR-LA sensor metadata ───────────────────────────────────────────────────
# These are approximate centroids for LA county loop detectors.
# Replace with your actual sensor_locations.csv if available.
METR_LA_N_SENSORS = 207
PEMS_BAY_N_SENSORS = 325

# default speed for edge length estimation (mph → m/s)
AVG_HIGHWAY_SPEED_MPS = 25 * 0.44704   # 25 mph ≈ 11.2 m/s
SENSOR_SPACING_M      = 1000.0         # ~1 km between adjacent sensors


def build_graph_from_adjacency(adj_mx_path: str,
                                sensor_locs_path: Optional[str] = None,
                                threshold: float = 0.1
                                ) -> Tuple[nx.DiGraph, Dict, Dict]:
    """
    Build DiGraph from METR-LA/PEMS-BAY adjacency matrix.

    Parameters
    ----------
    adj_mx_path      : path to adj_mx.pkl  (from DCRNN data release)
                       OR a numpy .npy file of shape (N, N)
    sensor_locs_path : optional CSV with columns: sensor_id, lat, lon
    threshold        : edges where adj_mx[i,j] > threshold are included

    Returns
    -------
    graph           : nx.DiGraph
    edge_sensor_map : {(u,v): sensor_index_of_u}
    edge_lengths_m  : {(u,v): float metres}
    """
    # ── load adjacency matrix ─────────────────────────────────────────────────
    if adj_mx_path.endswith('.pkl'):
        with open(adj_mx_path, 'rb') as f:
            data = pickle.load(f)
        # DCRNN format: (sensor_ids, sensor_id_to_ind, adj_mx)
        if isinstance(data, (list, tuple)) and len(data) == 3:
            sensor_ids, _, adj_mx = data
        else:
            adj_mx = np.array(data)
            sensor_ids = list(range(adj_mx.shape[0]))
    elif adj_mx_path.endswith('.npy'):
        adj_mx   = np.load(adj_mx_path)
        sensor_ids = list(range(adj_mx.shape[0]))
    else:
        raise ValueError("adj_mx_path must be .pkl or .npy")

    n = adj_mx.shape[0]
    adj_mx = np.array(adj_mx)

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
        length_m = edge_lengths_m.get(edge, SENSOR_SPACING_M)
        hist_avg_tt[edge] = length_m / avg_speed_mps[sensor_idx]
    return hist_avg_tt


def compute_current_tt(current_speeds_mph: np.ndarray,
                       edge_lengths_m:     Dict,
                       edge_sensor_map:    Dict) -> Dict:
    """Travel times from current (departure-time) snapshot."""
    speeds_mps = np.clip(current_speeds_mph * 0.44704, 0.5, None)
    current_tt = {}
    for edge, sensor_idx in edge_sensor_map.items():
        length_m = edge_lengths_m.get(edge, SENSOR_SPACING_M)
        current_tt[edge] = float(length_m) / float(speeds_mps[sensor_idx])
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
    Loads your existing preprocessed road network files.
    Normalises edge keys from (u, v, 0) → (u, v)
    Normalises sensor values from [0] → 0
    """
    import pickle

    graph_path = os.path.join(processed_dir, 'la_road_network.pkl')
    esm_path   = os.path.join(processed_dir, 'edge_sensor_mapping.pkl')

    # ── Load graph ────────────────────────────────────────────────────────────
    with open(graph_path, 'rb') as f:
        graph = pickle.load(f)
    print(f"[GraphBuilder] Real graph: "
          f"{graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

    # ── Load raw edge→sensor map ──────────────────────────────────────────────
    with open(esm_path, 'rb') as f:
        raw_esm = pickle.load(f)

    # ── Normalise keys and values ─────────────────────────────────────────────
    # Keys:   (u, v, 0)  →  (u, v)       [OSM multigraph key stripped]
    # Values: [0]        →  0             [list unwrapped to int]
    edge_sensor_map = {}
    for key, val in raw_esm.items():

        # normalise key to 2-tuple
        if isinstance(key, (tuple, list)) and len(key) >= 2:
            edge = (int(key[0]), int(key[1]))
        else:
            edge = key

        # normalise value to plain int
        if isinstance(val, (list, tuple)):
            sensor_idx = int(val[0])
        elif hasattr(val, 'flat'):          # numpy array
            sensor_idx = int(val.flat[0])
        else:
            sensor_idx = int(val)

        edge_sensor_map[edge] = sensor_idx

    print(f"[GraphBuilder] edge_sensor_map: "
          f"{len(edge_sensor_map)} edges, "
          f"sensor range 0–{max(edge_sensor_map.values())}")

    # ── Build edge lengths from graph ─────────────────────────────────────────
    edge_lengths_m = {}
    for u, v, data in graph.edges(data=True):
        edge_lengths_m[(int(u), int(v))] = float(data.get('length', 500.0))

    return graph, edge_sensor_map, edge_lengths_m 