"""
Threshold-based adaptive route recommendation controller (thesis Section 3.8).

A new recommendation is issued when:

    [T_new(current -> dest) - T_old(current -> dest)] / T_old  >  delta

T_old = remaining time on the currently recommended path under the
        predictions used when that path was issued.
T_new = remaining time on that SAME path under the latest GRU predictions.

delta in {0.05, 0.10, 0.15, 0.20}
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from src.routing.td_astar import td_astar, STEP_S

POLICIES = ("threshold", "fixed_interval", "hybrid", "event_driven")


@dataclass
class SimulationResult:
    total_time_s: float
    n_replannings: int
    replan_timestamps: List[float]
    path_segments: List[List[int]]
    policy: str
    delta: float
    latency_ms_list: List[float]
    feasible: bool = True

    @property
    def avg_latency_ms(self) -> float:
        return float(np.mean(self.latency_ms_list)) if self.latency_ms_list else 0.0

    @property
    def update_frequency(self) -> float:
        return self.n_replannings


class JourneySimulator:
    def __init__(
        self,
        graph,
        tt_fn_series: List[Dict],
        free_flow_tt: Dict,
        delta: float = 0.10,
        policy: str = "threshold",
        fixed_interval_s: float = 300.0,
    ):
        assert policy in POLICIES, f"policy must be one of {POLICIES}"
        assert 0 < delta < 1, "delta must be between 0 and 1"
        self.graph = graph
        self.tt_fn_series = tt_fn_series
        self.free_flow_tt = free_flow_tt
        self.delta = delta
        self.policy = policy
        self.fixed_interval_s = fixed_interval_s

    def run(self, origin: int, destination: int, departure_slot: int = 0) -> SimulationResult:
        elapsed_s = 0.0
        current_node = origin
        current_slot = departure_slot

        init_tt_fn = self._get_tt_fn(current_slot)
        route = td_astar(
            self.graph, current_node, destination, elapsed_s, init_tt_fn, self.free_flow_tt
        )

        path_segments = [route.path[:]]
        replan_timestamps = []
        latency_list = [route.latency_ms]
        n_replannings = 0
        last_replan_s = 0.0
        current_path = route.path[:]
        T_old = self._path_remaining(current_path, init_tt_fn, elapsed_s)

        while current_node != destination:
            if len(current_path) < 2:
                break

            next_node = current_path[1]
            edge_tt = self._edge_tt(init_tt_fn, current_node, next_node, elapsed_s)
            elapsed_s += edge_tt
            current_slot = min(int(elapsed_s // STEP_S), len(self.tt_fn_series) - 1)
            current_node = next_node
            current_path = current_path[1:]

            if current_node == destination:
                break

            new_tt_fn = self._get_tt_fn(current_slot)
            T_old = self._path_remaining(current_path, init_tt_fn, elapsed_s)
            T_new = self._path_remaining(current_path, new_tt_fn, elapsed_s)

            should_replan = False
            if self.policy == "threshold":
                should_replan = T_old > 0 and (T_new - T_old) / T_old > self.delta
            elif self.policy == "fixed_interval":
                should_replan = (elapsed_s - last_replan_s) >= self.fixed_interval_s
            elif self.policy == "hybrid":
                interval_ok = (elapsed_s - last_replan_s) >= self.fixed_interval_s
                thresh_ok = T_old > 0 and (T_new - T_old) / T_old > self.delta
                should_replan = interval_ok and thresh_ok
            elif self.policy == "event_driven":
                should_replan = self._event_check(current_node, new_tt_fn)

            if should_replan:
                new_route = td_astar(
                    self.graph, current_node, destination,
                    elapsed_s, new_tt_fn, self.free_flow_tt,
                )
                init_tt_fn = new_tt_fn
                current_path = new_route.path[:]
                T_old = self._path_remaining(current_path, init_tt_fn, elapsed_s)
                n_replannings += 1
                replan_timestamps.append(elapsed_s)
                latency_list.append(new_route.latency_ms)
                last_replan_s = elapsed_s
                path_segments.append(new_route.path[:])

        return SimulationResult(
            total_time_s=elapsed_s,
            n_replannings=n_replannings,
            replan_timestamps=replan_timestamps,
            path_segments=path_segments,
            policy=self.policy,
            delta=self.delta,
            latency_ms_list=latency_list,
            feasible=current_node == destination,
        )

    def _get_tt_fn(self, slot: int) -> Dict:
        return self.tt_fn_series[min(slot, len(self.tt_fn_series) - 1)]

    def _edge_tt(self, tt_fn: Dict, u: int, v: int, elapsed_s: float) -> float:
        from src.routing.td_astar import _get_edge_travel_time
        return _get_edge_travel_time(tt_fn, self.free_flow_tt, u, v, elapsed_s)

    def _path_remaining(self, path, tt_fn, elapsed_s: float) -> float:
        total = 0.0
        t = elapsed_s
        for i in range(len(path) - 1):
            dt = self._edge_tt(tt_fn, path[i], path[i + 1], t)
            total += dt
            t += dt
        return total

    def _event_check(self, current_node: int, new_tt_fn: Dict) -> bool:
        for v in self.graph.successors(current_node):
            edge = (current_node, v)
            if edge in new_tt_fn and edge in self.free_flow_tt:
                val = new_tt_fn[edge]
                first = float(val[0] if hasattr(val, "__len__") else val)
                if first / max(self.free_flow_tt[edge], 1.0) > 2.0:
                    return True
        return False
