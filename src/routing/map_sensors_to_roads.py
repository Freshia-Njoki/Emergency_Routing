"""
Map METR-LA sensors onto major OSM edges (loop-detector realism)
and write interpolation-friendly (u, v) keys.
"""
from __future__ import annotations

import os
import pickle

from src.utils.console import configure_utf8, safe_print
from src.routing.travel_times import (
    remap_sensors_to_major_roads,
    to_simple_digraph,
    build_interpolator,
)

configure_utf8()


def main():
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("visualizations", exist_ok=True)

    safe_print("=" * 60)
    safe_print("MAPPING TRAFFIC SENSORS TO ROAD NETWORK")
    safe_print("=" * 60)

    with open("data/processed/la_road_network.pkl", "rb") as f:
        G_raw = pickle.load(f)
    G = to_simple_digraph(G_raw)
    safe_print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    edge_sensor_map, sensor_to_edge = remap_sensors_to_major_roads(G, n_sensors=207, seed=42)
    safe_print(f"Mapped {len(edge_sensor_map)} sensors onto unique major-road edges")

    with open("data/processed/edge_sensor_mapping.pkl", "wb") as f:
        pickle.dump(edge_sensor_map, f)
    with open("data/processed/sensor_edge_mapping.pkl", "wb") as f:
        pickle.dump(sensor_to_edge, f)

    weights, ff_mph, lengths = build_interpolator(G, edge_sensor_map, n_sensors=207)
    with open("data/processed/edge_speed_weights.pkl", "wb") as f:
        pickle.dump({"weights": weights, "free_flow_mph": ff_mph, "lengths": lengths}, f)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import osmnx as ox

        fig, ax = ox.plot_graph(
            G_raw, node_size=8, node_color="lightblue",
            edge_linewidth=0.6, edge_color="gray", bgcolor="white",
            figsize=(12, 12), show=False, close=False,
        )
        for (u, v) in list(edge_sensor_map.keys())[:80]:
            if u in G.nodes and v in G.nodes:
                ax.plot(
                    [G.nodes[u]["x"], G.nodes[v]["x"]],
                    [G.nodes[u]["y"], G.nodes[v]["y"]],
                    color="red", linewidth=2, alpha=0.7, zorder=2,
                )
        ax.set_title("Major-road sensor mapping (red = directly mapped)")
        plt.tight_layout()
        plt.savefig("visualizations/sensor_coverage_map.png", dpi=150, bbox_inches="tight")
        plt.close()
        safe_print("Saved visualizations/sensor_coverage_map.png")
    except Exception as exc:
        safe_print(f"[WARN] coverage plot skipped: {exc}")

    safe_print("SENSOR MAPPING COMPLETE")


if __name__ == "__main__":
    main()
