"""
Threshold-based adaptive route recommendation controller.

This is Component 3 of my framework

Core logic

    Trigger a new route recommendation when:

        [T_new(current→dest) − T_old(current→dest)]
        ─────────────────────────────────────────── > δ
                  T_old(current→dest)

Where:
    T_new = estimated remaining time using LATEST GRU predictions
    T_old = remaining time from the currently recommended route
    δ     ∈ {0.05, 0.10, 0.15, 0.20}

The controller also tracks:
    - total replanning events per journey
    - time stamps of each replanning event
    - which δ triggered each replan
    - final journey travel time

Public API
----------
    sim = JourneySimulator(graph, travel_time_fn_series, free_flow_tt,
                           delta=0.10, policy='threshold')
    result = sim.run(origin, destination, departure_slot)

    result.total_time_s      : actual simulated travel time
    result.n_replannings     : number of route updates issued
    result.replan_timestamps : list of elapsed seconds when replanning fired
    result.path_segments     : list of path segments (one per leg)
    result.policy            : policy name used
    result.delta             : δ value used
"""

import time as _wall_time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from src.routing.td_astar import (
    td_astar, RoutingResult, STEP_S, N_FUTURE
)


# ── update policies ───────────────────────────────────────────────────────────
POLICIES = ('threshold', 'fixed_interval', 'hybrid', 'event_driven')


@dataclass
class SimulationResult:
    total_time_s:      float
    n_replannings:     int
    replan_timestamps: List[float]          # elapsed seconds at each replan
    path_segments:     List[List[int]]      # path used in each leg
    policy:            str
    delta:             float
    latency_ms_list:   List[float]          # per-replan routing latency
    feasible:          bool = True

    @property
    def avg_latency_ms(self) -> float:
        return float(np.mean(self.latency_ms_list)) if self.latency_ms_list else 0.0

    @property
    def update_frequency(self) -> float:
        """replannings per journey"""
        return self.n_replannings


class JourneySimulator:
    """
    Simulates a single emergency vehicle journey through the road network,
    replanning according to the chosen policy.

    Parameters
    ----------
    graph              : NetworkX DiGraph
    tt_fn_series       : list of travel_time_fn dicts, one per 5-min slot.
                         tt_fn_series[t][(u,v)] = travel time at slot t.
                         In the experiment harness this corresponds to
                         successive GRU prediction windows.
    free_flow_tt       : {(u,v): float}  lower-bound travel times
    delta              : replanning threshold (0.05 / 0.10 / 0.15 / 0.20)
    policy             : one of POLICIES
    fixed_interval_s   : for 'fixed_interval' policy — replan every N seconds
    """

    def __init__(self,
                 graph,
                 tt_fn_series:    List[Dict],
                 free_flow_tt:    Dict,
                 delta:           float = 0.10,
                 policy:          str   = 'threshold',
                 fixed_interval_s: float = 300.0):

        assert policy in POLICIES, f"policy must be one of {POLICIES}"
        assert 0 < delta < 1,      "delta must be between 0 and 1"

        self.graph             = graph
        self.tt_fn_series      = tt_fn_series   # list of dicts, indexed by slot
        self.free_flow_tt      = free_flow_tt
        self.delta             = delta
        self.policy            = policy
        self.fixed_interval_s  = fixed_interval_s

    # ── main entry point ──────────────────────────────────────────────────────

    def run(self,
            origin:          int,
            destination:     int,
            departure_slot:  int = 0
            ) -> SimulationResult:
        """
        Simulate full journey origin→destination.

        The simulation advances in discrete 5-second micro-steps along the
        currently recommended path, updating elapsed time and checking
        replanning triggers at every full STEP_S boundary.
        """
        elapsed_s        = 0.0
        current_node     = origin
        current_slot     = departure_slot

        # initial route
        init_tt_fn = self._get_tt_fn(current_slot)
        route      = td_astar(self.graph, current_node, destination,
                               elapsed_s, init_tt_fn, self.free_flow_tt)

        path_segments      = [route.path[:]]
        replan_timestamps  = []
        latency_list       = [route.latency_ms]
        n_replannings      = 0

        T_old = route.total_time_s    # remaining time under current route
        last_replan_s = 0.0

        # ── traverse the route segment by segment ─────────────────────────────
        while current_node != destination:
            if len(route.path) < 2:
                break   # destination reached or stuck

            # next edge to traverse
            next_node = route.path[1] if len(route.path) > 1 else destination

            # travel time for this single edge at current elapsed time
            edge_tt = self._edge_tt(init_tt_fn, current_node, next_node, elapsed_s)
            elapsed_s  += edge_tt
            current_slot = min(int(elapsed_s // STEP_S), len(self.tt_fn_series) - 1)
            current_node = next_node

            # advance route pointer (remove head)
            route.path.pop(0)

            # ── check replanning trigger ───────────────────────────────────
            if current_node == destination:
                break

            new_tt_fn = self._get_tt_fn(current_slot)

            should_replan = False

            if self.policy == 'threshold':
                should_replan = self._threshold_check(
                    current_node, destination, new_tt_fn, T_old)

            elif self.policy == 'fixed_interval':
                should_replan = (elapsed_s - last_replan_s) >= self.fixed_interval_s

            elif self.policy == 'hybrid':
                # both conditions must be met
                interval_ok = (elapsed_s - last_replan_s) >= self.fixed_interval_s
                thresh_ok   = self._threshold_check(
                    current_node, destination, new_tt_fn, T_old)
                should_replan = interval_ok and thresh_ok

            elif self.policy == 'event_driven':
                # replan when predicted speed drops below 50 % of free-flow
                should_replan = self._event_check(current_node, new_tt_fn)

            if should_replan:
                new_route = td_astar(
                    self.graph, current_node, destination,
                    elapsed_s, new_tt_fn, self.free_flow_tt)

                # update state
                T_old          = new_route.total_time_s
                init_tt_fn     = new_tt_fn
                route          = new_route
                n_replannings += 1
                replan_timestamps.append(elapsed_s)
                latency_list.append(new_route.latency_ms)
                last_replan_s  = elapsed_s
                path_segments.append(new_route.path[:])

        return SimulationResult(
            total_time_s      = elapsed_s,
            n_replannings     = n_replannings,
            replan_timestamps = replan_timestamps,
            path_segments     = path_segments,
            policy            = self.policy,
            delta             = self.delta,
            latency_ms_list   = latency_list,
            feasible          = current_node == destination
        )

    # ── private helpers ───────────────────────────────────────────────────────

    def _get_tt_fn(self, slot: int) -> Dict:
        idx = min(slot, len(self.tt_fn_series) - 1)
        return self.tt_fn_series[idx]

    def _edge_tt(self, tt_fn: Dict, u: int, v: int, elapsed_s: float) -> float:
        from src.routing.td_astar import _get_edge_travel_time
        return _get_edge_travel_time(tt_fn, self.free_flow_tt, u, v, elapsed_s)

    def _threshold_check(self,
                          current:     int,
                          destination: int,
                          new_tt_fn:   Dict,
                          T_old:       float) -> bool:
        """
        Core replanning condition from proposal Section 3.8:
            (T_new - T_old) / T_old > delta
        """
        if T_old <= 0:
            return False
        new_route = td_astar(self.graph, current, destination,
                              0.0, new_tt_fn, self.free_flow_tt)
        T_new = new_route.total_time_s
        deviation = (T_new - T_old) / T_old
        return deviation > self.delta

    def _event_check(self, current_node: int, new_tt_fn: Dict) -> bool:
        """
        Event-driven trigger: any outgoing edge from current node has
        travel time > 2x its free-flow time (incident proxy).
        """
        for v in self.graph.successors(current_node):
            edge = (current_node, v)
            if edge in new_tt_fn and edge in self.free_flow_tt:
                ratio = new_tt_fn[edge][0] / max(self.free_flow_tt[edge], 1.0)
                if ratio > 2.0:
                    return True
        return False