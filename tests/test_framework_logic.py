"""Lightweight tests that do not require TensorFlow or METR-LA raw files."""
from __future__ import annotations

import math
import os
import sys
import unittest

import numpy as np
import networkx as nx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.console import ascii_safe
from src.routing.travel_times import (
    build_interpolator,
    remap_sensors_to_major_roads,
    speeds_to_edge_speeds,
    to_simple_digraph,
    edge_speeds_to_tt,
)
from src.evaluation.simulation_core import (
    apply_path_incident,
    astar_route,
    remaining_on_path,
    simulate_path,
    tt_from_speeds,
)


def _toy_graph():
    G = nx.MultiDiGraph()
    coords = {
        0: (34.05, -118.27),
        1: (34.05, -118.26),
        2: (34.05, -118.25),
        3: (34.04, -118.26),
    }
    for n, (y, x) in coords.items():
        G.add_node(n, y=y, x=x)
    # two routes 0->1->2 and 0->3->2
    G.add_edge(0, 1, key=0, length=400.0, highway="motorway", maxspeed="65 mph")
    G.add_edge(1, 2, key=0, length=400.0, highway="motorway", maxspeed="65 mph")
    G.add_edge(0, 3, key=0, length=500.0, highway="primary", maxspeed="35 mph")
    G.add_edge(3, 2, key=0, length=500.0, highway="primary", maxspeed="35 mph")
    return G


class EncodingTests(unittest.TestCase):
    def test_ascii_safe_arrows(self):
        self.assertEqual(ascii_safe("results \u2192 file"), "results -> file")
        self.assertEqual(ascii_safe("train \u2248 val"), "train ~ val")
        encoded = ascii_safe("Raw results \u2192 file  (~900 records)")
        encoded.encode("cp1252")


class GraphTests(unittest.TestCase):
    def test_multigraph_collapse(self):
        G = _toy_graph()
        H = to_simple_digraph(G)
        self.assertFalse(H.is_multigraph())
        self.assertEqual(H.number_of_edges(), 4)

    def test_major_road_mapping_and_interpolation(self):
        H = to_simple_digraph(_toy_graph())
        esm, _ = remap_sensors_to_major_roads(H, n_sensors=2, seed=42)
        self.assertGreaterEqual(len(esm), 1)
        weights, ff_mph, lengths = build_interpolator(H, esm, n_sensors=2, max_dist_m=5000)
        self.assertEqual(len(weights), H.number_of_edges())
        speeds = np.array([10.0, 60.0])
        edge_spd = speeds_to_edge_speeds(speeds, weights, ff_mph)
        self.assertTrue(all(np.ndim(v) == 0 for v in edge_spd.values()))


class RoutingLogicTests(unittest.TestCase):
    def setUp(self):
        self.G = to_simple_digraph(_toy_graph())
        self.esm, _ = remap_sensors_to_major_roads(self.G, n_sensors=2, seed=0)
        self.weights, self.ff_mph, self.lengths = build_interpolator(
            self.G, self.esm, n_sensors=2, max_dist_m=8000
        )
        self.ff_tt = {e: l / (mph * 0.44704) for e, l in self.lengths.items()
                      for mph in [self.ff_mph[e]]}

    def test_path_incident_slows_dijkstra_more_than_alternate(self):
        curr = np.array([55.0, 55.0])
        curr_tt = tt_from_speeds(curr, self.weights, self.lengths, self.ff_mph)
        b1_path, _ = astar_route(self.G, 0, 2, curr_tt, self.ff_tt)
        self.assertGreaterEqual(len(b1_path), 3)

        actual = np.tile(curr, (6, 1))
        actual_inc, affected = apply_path_incident(
            actual, b1_path, self.weights, severity=0.3, start_slot=0, n_sensors_hit=2
        )
        self.assertTrue(affected.size >= 1)
        t_inc = 5.0
        b1_tt = simulate_path(b1_path, actual, self.weights, self.lengths, self.ff_mph,
                              t_inc, actual_inc)
        b1_clear = simulate_path(b1_path, actual, self.weights, self.lengths, self.ff_mph)
        self.assertGreater(b1_tt, b1_clear)

    def test_threshold_formula_uses_remaining_not_original_total(self):
        curr = np.array([50.0, 50.0])
        tt = tt_from_speeds(curr, self.weights, self.lengths, self.ff_mph)
        path, _ = astar_route(self.G, 0, 2, tt, self.ff_tt)
        full = remaining_on_path(path, tt, self.ff_tt, 0.0)
        rest = remaining_on_path(path[1:], tt, self.ff_tt, 20.0)
        self.assertLess(rest, full)
        # Old bug: T_old stayed equal to the original full journey time, so
        # (T_new - T_old)/T_old was always negative and never replanned.
        self.assertGreater(full - rest, 1.0)


if __name__ == "__main__":
    unittest.main()
