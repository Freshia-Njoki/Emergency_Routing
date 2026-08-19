"""
Edge travel-time construction with spatial interpolation.

Chapter 3 maps only 190 of 1,024 OSM edges to METR-LA sensors.  The original
code assigned a constant 30 mph free-flow speed to the remaining 81.4% of
edges, so Dijkstra, TD-A*, and the oracle all saw almost the same costs and
produced ~0% travel-time reduction (and harmful peak-hour detours onto
'free-flow' unmapped streets).

This module:
  1. Converts the OSM MultiDiGraph to a simple DiGraph.
  2. Parses OSM maxspeed / highway type for a realistic free-flow fallback.
  3. Builds inverse-distance weights so unmapped edges inherit speeds from
     nearby mapped sensors (k-NN IDW), which is standard loop-detector
     spatial interpolation.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

MPS_PER_MPH = 0.44704
DEFAULT_FF_MPH = 30.0

HIGHWAY_FF_MPH = {
    "motorway": 65.0,
    "motorway_link": 45.0,
    "trunk": 55.0,
    "trunk_link": 40.0,
    "primary": 40.0,
    "primary_link": 35.0,
    "secondary": 35.0,
    "secondary_link": 30.0,
    "tertiary": 30.0,
    "tertiary_link": 25.0,
    "residential": 25.0,
    "unclassified": 25.0,
    "busway": 25.0,
}

HIGHWAY_PRIORITY = {
    "motorway": 0,
    "motorway_link": 1,
    "trunk": 2,
    "trunk_link": 3,
    "primary": 4,
    "primary_link": 5,
    "secondary": 6,
    "secondary_link": 7,
    "tertiary": 8,
    "tertiary_link": 9,
}


def _highway_key(value) -> str:
    if value is None:
        return "unclassified"
    if isinstance(value, (list, tuple)):
        value = value[0] if value else "unclassified"
    return str(value).split(".")[0].strip().lower()


def parse_maxspeed_mph(value, highway=None) -> float:
    """Parse OSM maxspeed (mph or km/h) to mph; fall back by highway type."""
    if value is not None:
        if isinstance(value, (list, tuple)):
            value = value[0] if value else None
        if value is not None:
            raw = str(value).strip().lower()
            numeric = "".join(ch if (ch.isdigit() or ch == ".") else " " for ch in raw)
            parts = [p for p in numeric.split() if p]
            if parts:
                try:
                    speed = float(parts[0])
                    if "km" in raw:
                        speed *= 0.621371
                    if 5.0 <= speed <= 90.0:
                        return float(speed)
                except ValueError:
                    pass
    return HIGHWAY_FF_MPH.get(_highway_key(highway), DEFAULT_FF_MPH)


def haversine_m(lat1, lon1, lat2, lon2) -> float:
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(min(1.0, a)))


def to_simple_digraph(graph):
    """Collapse OSM MultiDiGraph parallel edges, keeping the shortest length."""
    import networkx as nx

    if not graph.is_multigraph():
        return graph

    H = nx.DiGraph()
    for node, data in graph.nodes(data=True):
        H.add_node(int(node), **{k: v for k, v in data.items() if k != "geometry"})

    for u, v, _key, data in graph.edges(keys=True, data=True):
        u_i, v_i = int(u), int(v)
        length = float(data.get("length", 500.0))
        payload = {
            "length": length,
            "highway": data.get("highway"),
            "maxspeed": data.get("maxspeed"),
            "name": data.get("name"),
        }
        if H.has_edge(u_i, v_i):
            if length < float(H[u_i][v_i].get("length", 1e18)):
                H[u_i][v_i].update(payload)
        else:
            H.add_edge(u_i, v_i, **payload)
    return H


def _sensor_int(val) -> int:
    arr = np.array(val).reshape(-1)
    return int(arr[0])


def normalize_edge_sensor_map(raw_esm: dict) -> Dict[Tuple[int, int], int]:
    out = {}
    for key, val in raw_esm.items():
        if isinstance(key, (tuple, list)) and len(key) >= 2:
            edge = (int(key[0]), int(key[1]))
        else:
            continue
        out[edge] = _sensor_int(val)
    return out


def remap_sensors_to_major_roads(graph, n_sensors: int = 207, seed: int = 42):
    """
    Assign each METR-LA sensor to a unique major-road edge.

    Loop detectors sit on freeways and arterials, not random residential
    streets.  Prefer motorway > primary > secondary, then longer edges.
    """
    rng = np.random.default_rng(seed)
    candidates = []
    for u, v, data in graph.edges(data=True):
        hwy = _highway_key(data.get("highway"))
        pri = HIGHWAY_PRIORITY.get(hwy, 20)
        length = float(data.get("length", 0.0))
        candidates.append((pri, -length, int(u), int(v)))
    candidates.sort()
    ranked = [(u, v) for _p, _l, u, v in candidates]

    chosen = ranked[: min(n_sensors, len(ranked))]
    if len(chosen) < n_sensors:
        extras = list(graph.edges())
        rng.shuffle(extras)
        for u, v in extras:
            e = (int(u), int(v))
            if e not in chosen:
                chosen.append(e)
            if len(chosen) >= n_sensors:
                break

    edge_sensor_map = {}
    sensor_edge_map = {}
    for s, edge in enumerate(chosen[:n_sensors]):
        edge_sensor_map[edge] = s
        sensor_edge_map[s] = edge
    return edge_sensor_map, sensor_edge_map


def _edge_midpoint(graph, u, v) -> Optional[Tuple[float, float]]:
    try:
        du, dv = graph.nodes[u], graph.nodes[v]
        return ((du["y"] + dv["y"]) / 2.0, (du["x"] + dv["x"]) / 2.0)
    except Exception:
        return None


def build_interpolator(
    graph,
    edge_sensor_map: Dict[Tuple[int, int], int],
    n_sensors: int = 207,
    k: int = 4,
    max_dist_m: float = 450.0,
):
    """
    Returns:
      weights: {(u,v): [(sensor_idx, weight), ...]}  (empty => use free-flow)
      free_flow_mph: {(u,v): mph}
      edge_lengths: {(u,v): metres}
    """
    edge_lengths = {}
    free_flow_mph = {}
    for u, v, data in graph.edges(data=True):
        e = (int(u), int(v))
        edge_lengths[e] = float(data.get("length", 500.0))
        free_flow_mph[e] = parse_maxspeed_mph(data.get("maxspeed"), data.get("highway"))

    mapped = []
    for edge, sidx in edge_sensor_map.items():
        sidx = int(sidx)
        if sidx < 0 or sidx >= n_sensors:
            continue
        if edge not in edge_lengths:
            continue
        mid = _edge_midpoint(graph, edge[0], edge[1])
        if mid is None:
            continue
        mapped.append((edge, sidx, mid))

    weights = {}
    for e in edge_lengths:
        if e in edge_sensor_map:
            sidx = int(edge_sensor_map[e])
            if 0 <= sidx < n_sensors:
                weights[e] = [(sidx, 1.0)]
                continue

        mid = _edge_midpoint(graph, e[0], e[1])
        if mid is None or not mapped:
            weights[e] = []
            continue

        dists = []
        for _me, sidx, m2 in mapped:
            d = haversine_m(mid[0], mid[1], m2[0], m2[1])
            if d <= max_dist_m:
                dists.append((max(d, 15.0), sidx))
        dists.sort()
        dists = dists[:k]
        if not dists:
            weights[e] = []
            continue
        inv = [(sidx, 1.0 / d) for d, sidx in dists]
        tot = sum(w for _s, w in inv)
        weights[e] = [(s, w / tot) for s, w in inv]

    n_direct = sum(1 for w in weights.values() if len(w) == 1)
    n_interp = sum(1 for w in weights.values() if len(w) > 1)
    n_ff = sum(1 for w in weights.values() if len(w) == 0)
    print(
        f"[TravelTimes] edges={len(weights)}  direct={n_direct}  "
        f"interpolated={n_interp}  free-flow-fallback={n_ff}"
    )
    return weights, free_flow_mph, edge_lengths


def speeds_to_edge_speeds(
    speeds_mph: np.ndarray,
    weights: dict,
    free_flow_mph: dict,
    clip_min: float = 3.0,
    clip_max: float = 85.0,
) -> Dict[Tuple[int, int], np.ndarray]:
    """
    speeds_mph: (N,) or (T, N)
    Returns {(u,v): scalar or (T,) array of mph}
    """
    spd = np.asarray(speeds_mph, dtype=np.float64)
    vector = spd.ndim == 2
    out = {}
    for edge, wts in weights.items():
        ff = free_flow_mph.get(edge, DEFAULT_FF_MPH)
        if not wts:
            out[edge] = np.full(spd.shape[0], ff) if vector else float(ff)
            continue
        if vector:
            acc = np.zeros(spd.shape[0], dtype=np.float64)
            for sidx, w in wts:
                if sidx < spd.shape[1]:
                    acc += w * spd[:, sidx]
            out[edge] = np.clip(acc, clip_min, clip_max)
        else:
            acc = 0.0
            for sidx, w in wts:
                if sidx < spd.shape[0]:
                    acc += w * float(spd[sidx])
            out[edge] = float(np.clip(acc, clip_min, clip_max))
    return out


def edge_speeds_to_tt(
    edge_speeds: dict,
    edge_lengths: dict,
) -> dict:
    """Convert mph (scalar or array) to seconds."""
    tt = {}
    for edge, spd in edge_speeds.items():
        length = float(edge_lengths.get(edge, 500.0))
        if np.ndim(spd) == 0:
            tt[edge] = length / max(float(spd) * MPS_PER_MPH, 0.5)
        else:
            tt[edge] = length / np.maximum(np.asarray(spd, dtype=np.float64) * MPS_PER_MPH, 0.5)
    return tt


def free_flow_tt_seconds(edge_lengths: dict, free_flow_mph: dict) -> dict:
    out = {}
    for edge, length in edge_lengths.items():
        mph = free_flow_mph.get(edge, DEFAULT_FF_MPH)
        out[edge] = float(length) / max(mph * MPS_PER_MPH, 0.5)
    return out


def sensors_on_path(
    path: Sequence[int],
    weights: dict,
    top_n: int = 8,
) -> List[int]:
    """Sensors that most strongly influence the given node path."""
    scores: Dict[int, float] = {}
    for i in range(len(path) - 1):
        for sidx, w in weights.get((int(path[i]), int(path[i + 1])), []):
            scores[int(sidx)] = scores.get(int(sidx), 0.0) + float(w)
    ranked = sorted(scores, key=lambda s: scores[s], reverse=True)
    return ranked[:top_n]
