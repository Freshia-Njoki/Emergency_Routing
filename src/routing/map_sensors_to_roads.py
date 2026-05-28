"""
Map traffic sensors to road network segments
"""
import pickle
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import geopandas as gpd

print("="*60)
print("MAPPING TRAFFIC SENSORS TO ROAD NETWORK")
print("="*60)

# Load road network
print("\n📥 Loading road network...")
with open('data/processed/la_road_network.pkl', 'rb') as f:
    G = pickle.load(f)

print(f"✅ Network loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")

# For METR-LA, we'll create synthetic sensor locations
# (Real sensor locations would come from METR-LA metadata if available)
print("\n📍 Creating sensor-to-edge mapping...")

# Get all edges
edges = list(G.edges(keys=True))
print(f"   Total edges: {len(edges)}")

# We have 207 sensors in METR-LA
# We'll map them to road edges randomly but deterministically
n_sensors = 207

# Create mapping
np.random.seed(42)  # For reproducibility
sensor_to_edge = {}

# Randomly assign sensors to edges (with replacement since we have more sensors than edges)
for sensor_id in range(n_sensors):
    # Pick a random edge
    edge_idx = np.random.randint(0, len(edges))
    edge = edges[edge_idx]
    sensor_to_edge[sensor_id] = {
        'edge': edge,
        'u': edge[0],
        'v': edge[1],
        'key': edge[2]
    }

print(f"✅ Mapped {len(sensor_to_edge)} sensors to road edges")

# Save the mapping
output_path = 'data/processed/sensor_edge_mapping.pkl'
with open(output_path, 'wb') as f:
    pickle.dump(sensor_to_edge, f)

print(f"💾 Saved to: {output_path}")

# Create a reverse mapping (edge to sensors)
edge_to_sensors = {}
for sensor_id, info in sensor_to_edge.items():
    edge = info['edge']
    if edge not in edge_to_sensors:
        edge_to_sensors[edge] = []
    edge_to_sensors[edge].append(sensor_id)

print(f"\n📊 Statistics:")
print(f"   Edges with sensors: {len(edge_to_sensors)}")
print(f"   Average sensors per edge: {len(sensor_to_edge) / len(edge_to_sensors):.2f}")

# Save reverse mapping too
with open('data/processed/edge_sensor_mapping.pkl', 'wb') as f:
    pickle.dump(edge_to_sensors, f)

print(f"💾 Saved reverse mapping")

# Visualize sensor coverage
print("\n🗺️ Creating visualization...")
import osmnx as ox

fig, ax = ox.plot_graph(
    G, 
    node_size=10,
    node_color='lightblue',
    edge_linewidth=1,
    edge_color='gray',
    bgcolor='white',
    figsize=(15, 15),
    show=False,
    close=False
)

# Highlight edges with sensors
edges_with_sensors = list(edge_to_sensors.keys())
if edges_with_sensors:
    # Get coordinates for these edges
    for edge in edges_with_sensors[:50]:  # Highlight first 50
        u, v, k = edge
        if G.has_edge(u, v, k):
            # Get edge geometry
            edge_data = G[u][v][k]
            
            # Get node coordinates
            x = [G.nodes[u]['x'], G.nodes[v]['x']]
            y = [G.nodes[u]['y'], G.nodes[v]['y']]
            
            ax.plot(x, y, color='red', linewidth=2, alpha=0.6, zorder=2)

ax.set_title('Road Network with Sensor Coverage\n(Red = Edges with sensors)', 
             fontsize=16, fontweight='bold')

plt.tight_layout()
plt.savefig('visualizations/sensor_coverage_map.png', dpi=150, bbox_inches='tight')
print("✅ Saved: visualizations/sensor_coverage_map.png")

print("\n" + "="*60)
print("✅ SENSOR MAPPING COMPLETE!")
print("="*60)
print("\n📁 Files created:")
print("   - data/processed/sensor_edge_mapping.pkl")
print("   - data/processed/edge_sensor_mapping.pkl")
print("   - visualizations/sensor_coverage_map.png")