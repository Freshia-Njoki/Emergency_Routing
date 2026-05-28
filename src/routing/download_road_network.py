"""
Download Los Angeles road network from OpenStreetMap
"""
import osmnx as ox
import pickle
import os

os.makedirs('data/processed', exist_ok=True)

print("="*60)
print("DOWNLOADING LOS ANGELES ROAD NETWORK")
print("="*60)

# Configure OSMnx
ox.settings.use_cache = True
ox.settings.log_console = True

print("\n📍 Downloading road network...")
print("   Location: Los Angeles, California")
print("   Network type: Drivable streets")
print("   This may take 5-10 minutes...")

try:
    # Download LA road network
    # Using a smaller area first (downtown LA) to make it manageable
    place_name = "Downtown Los Angeles, Los Angeles, California, USA"
    
    G = ox.graph_from_place(
        place_name,
        network_type='drive',
        simplify=True
    )
    
    print(f"\n✅ Network downloaded!")
    print(f"   Nodes (intersections): {len(G.nodes):,}")
    print(f"   Edges (road segments): {len(G.edges):,}")
    
    # Save the network
    output_path = 'data/processed/la_road_network.pkl'
    with open(output_path, 'wb') as f:
        pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"\n💾 Saved to: {output_path}")
    
    # Get basic statistics
    print("\n📊 Network Statistics:")
    print(f"   Total nodes: {len(G.nodes):,}")
    print(f"   Total edges: {len(G.edges):,}")
    
    # Get bounding box
    nodes = ox.graph_to_gdfs(G, edges=False)
    print(f"\n📍 Bounding Box:")
    print(f"   Latitude: {nodes.y.min():.4f} to {nodes.y.max():.4f}")
    print(f"   Longitude: {nodes.x.min():.4f} to {nodes.x.max():.4f}")
    
    # Visualize and save
    print("\n🗺️ Creating visualization...")
    fig, ax = ox.plot_graph(
        G, 
        node_size=0, 
        edge_linewidth=0.5,
        edge_color='#2563eb',
        bgcolor='white',
        figsize=(15, 15),
        show=False,
        close=False
    )
    
    fig.savefig('visualizations/la_road_network.png', dpi=150, bbox_inches='tight')
    print("✅ Saved: visualizations/la_road_network.png")
    
    print("\n" + "="*60)
    print("✅ ROAD NETWORK DOWNLOAD COMPLETE!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTrying alternative method with smaller area...")
    
    # Fallback: smaller bounding box
    north, south, east, west = 34.0522, 34.0322, -118.2437, -118.2737
    
    G = ox.graph_from_bbox(
        north, south, east, west,
        network_type='drive',
        simplify=True
    )
    
    print(f"✅ Smaller network downloaded: {len(G.nodes)} nodes")
    
    with open('data/processed/la_road_network.pkl', 'wb') as f:
        pickle.dump(G, f)
    
    print("✅ Network saved!")