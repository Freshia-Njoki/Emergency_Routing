"""
td_astar.py  — Time-Dependent A* + all baseline algorithms
"""

import heapq
import math
import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

STEP_S     = 300
N_FUTURE   = 6
_FREE_FLOW_MPS = 13.4   # ~30 mph


@dataclass
class RoutingResult:
    path:            List[int]
    total_time_s:    float
    latency_ms:      float
    nodes_expanded:  int
    feasible:        bool = True
    fallback:        bool = False


def _time_slot(elapsed_s: float, _: int) -> int:
    return min(int(elapsed_s // STEP_S), N_FUTURE - 1)


def _get_edge_travel_time(travel_time_fn, free_flow_tt, u, v, elapsed_s):
    edge = (u, v)
    if edge in travel_time_fn:
        val = travel_time_fn[edge]
        if isinstance(val, (int, float)):
            return float(max(val, 1.0))
        try:
            slot = min(_time_slot(elapsed_s, 0), len(val) - 1)
            return float(max(val[slot], 1.0))
        except Exception:
            return float(max(val[0], 1.0))
    ff = free_flow_tt.get(edge, STEP_S)
    return float(max(ff, 1.0))


def _haversine(lat1, lon1, lat2, lon2):
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def _heuristic(graph, node, goal):
    try:
        n_data = graph.nodes[node]
        g_data = graph.nodes[goal]
        dist_m = _haversine(n_data['y'], n_data['x'],
                            g_data['y'], g_data['x'])
        return dist_m / _FREE_FLOW_MPS
    except (KeyError, TypeError):
        return 0.0


def td_astar(graph, origin, destination, departure_time,
             travel_time_fn, free_flow_tt, step_seconds=STEP_S):
    t_wall_start = _time.perf_counter()

    if origin == destination:
        return RoutingResult(path=[origin], total_time_s=0.0,
                             latency_ms=0.0, nodes_expanded=0)

    open_heap = []
    g_score   = {origin: 0.0}
    came_from = {origin: None}
    nodes_expanded = 0

    h0 = _heuristic(graph, origin, destination)
    heapq.heappush(open_heap, (h0, 0.0, origin))

    while open_heap:
        f, g, current = heapq.heappop(open_heap)
        nodes_expanded += 1

        if g > g_score.get(current, math.inf) + 1e-9:
            continue

        if current == destination:
            path = _reconstruct(came_from, destination)
            latency_ms = (_time.perf_counter() - t_wall_start) * 1000
            return RoutingResult(path=path, total_time_s=g,
                                 latency_ms=latency_ms,
                                 nodes_expanded=nodes_expanded)

        for neighbour in graph.successors(current):
            tt = _get_edge_travel_time(travel_time_fn, free_flow_tt,
                                       current, neighbour, g)
            tentative_g = g + tt
            if tentative_g < g_score.get(neighbour, math.inf):
                g_score[neighbour]   = tentative_g
                came_from[neighbour] = current
                h = _heuristic(graph, neighbour, destination)
                heapq.heappush(open_heap,
                               (tentative_g + h, tentative_g, neighbour))

    latency_ms = (_time.perf_counter() - t_wall_start) * 1000
    best_node  = min(g_score, key=lambda n: g_score[n] +
                    _heuristic(graph, n, destination))
    return RoutingResult(path=[origin, best_node],
                         total_time_s=g_score[best_node],
                         latency_ms=latency_ms,
                         nodes_expanded=nodes_expanded,
                         feasible=False, fallback=True)


# ── Baselines ─────────────────────────────────────────────────────────────────

def dijkstra_current(graph, origin, destination, current_tt):
    """Baseline 1: Dijkstra with current conditions only."""
    t0 = _time.perf_counter()
    dist = {origin: 0.0}
    prev = {origin: None}
    heap = [(0.0, origin)]
    expanded = 0

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, math.inf) + 1e-9:
            continue
        expanded += 1
        if u == destination:
            return RoutingResult(
                path=_reconstruct(prev, destination),
                total_time_s=d,
                latency_ms=(_time.perf_counter() - t0) * 1000,
                nodes_expanded=expanded)
        for v in graph.successors(u):
            tt = float(current_tt.get((u, v),
                       free_flow_from_graph(graph, u, v)))
            nd = d + max(tt, 1.0)
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    return RoutingResult(path=[origin], total_time_s=math.inf,
                         latency_ms=(_time.perf_counter()-t0)*1000,
                         nodes_expanded=expanded, feasible=False)


def static_astar_historical(graph, origin, destination, hist_avg_tt):
    """Baseline 2: Static A* with historical average speeds."""
    t0 = _time.perf_counter()
    g_score = {origin: 0.0}
    prev    = {origin: None}
    heap    = [(_heuristic(graph, origin, destination), 0.0, origin)]
    expanded = 0

    while heap:
        f, g, u = heapq.heappop(heap)
        if g > g_score.get(u, math.inf) + 1e-9:
            continue
        expanded += 1
        if u == destination:
            return RoutingResult(
                path=_reconstruct(prev, destination),
                total_time_s=g,
                latency_ms=(_time.perf_counter() - t0) * 1000,
                nodes_expanded=expanded)
        for v in graph.successors(u):
            tt = float(hist_avg_tt.get((u, v),
                       free_flow_from_graph(graph, u, v)))
            ng = g + max(tt, 1.0)
            if ng < g_score.get(v, math.inf):
                g_score[v] = ng
                prev[v]    = u
                h = _heuristic(graph, v, destination)
                heapq.heappush(heap, (ng + h, ng, v))

    return RoutingResult(path=[origin], total_time_s=math.inf,
                         latency_ms=(_time.perf_counter()-t0)*1000,
                         nodes_expanded=expanded, feasible=False)


def oracle_astar(graph, origin, destination, actual_tt):
    """Baseline 4: Oracle A* — perfect future knowledge (upper bound)."""
    return static_astar_historical(graph, origin, destination, actual_tt)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _reconstruct(prev, dest):
    path, node = [], dest
    while node is not None:
        path.append(node)
        node = prev[node]
    return list(reversed(path))


def free_flow_from_graph(graph, u, v):
    data = graph.get_edge_data(u, v, default={})
    length_m = data.get('length', 500.0)
    return length_m / _FREE_FLOW_MPS