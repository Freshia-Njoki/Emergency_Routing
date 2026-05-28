"""
Explore METR-LA Traffic Dataset
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*60)
print("LOADING DATA")
print("="*60)

# Load data
df = pd.read_hdf('data/raw/metr-la.h5')

print("\n✅ Data loaded successfully!")
print(f"\nShape: {df.shape}")
print(f"  - Rows (time observations): {df.shape[0]:,}")
print(f"  - Columns (sensors): {df.shape[1]}")
print(f"\nDate range: {df.index.min()} to {df.index.max()}")
print(f"Total data points: {df.shape[0] * df.shape[1]:,}")

print("\n" + "="*60)
print("FIRST FEW ROWS")
print("="*60)
print(df.head())

# Statistics
print("\n" + "="*60)
print("TRAFFIC STATISTICS - Sensor 1")
print("="*60)
print(f"Average speed: {df.iloc[:, 0].mean():.2f} mph")
print(f"Minimum speed: {df.iloc[:, 0].min():.2f} mph")
print(f"Maximum speed: {df.iloc[:, 0].max():.2f} mph")
print(f"Standard deviation: {df.iloc[:, 0].std():.2f} mph")

# Create visualizations
print("\n" + "="*60)
print("CREATING VISUALIZATIONS")
print("="*60)

# Plot 1: Traffic over time
fig, axes = plt.subplots(2, 1, figsize=(15, 10))

axes[0].plot(df.iloc[:2000, 0], linewidth=1, color='#667eea')
axes[0].set_title('Traffic Speed Over Time - Sensor 1', fontsize=16, fontweight='bold')
axes[0].set_xlabel('Time', fontsize=12)
axes[0].set_ylabel('Speed (mph)', fontsize=12)
axes[0].grid(True, alpha=0.3)

# Plot 2: Daily pattern
df_copy = df.copy()
df_copy['hour'] = df_copy.index.hour
hourly_avg = df_copy.groupby('hour').mean().iloc[:, 0]

axes[1].plot(hourly_avg.index, hourly_avg.values, marker='o', linewidth=2, 
             markersize=8, color='#764ba2')
axes[1].set_title('Average Traffic Speed by Hour of Day', fontsize=16, fontweight='bold')
axes[1].set_xlabel('Hour of Day', fontsize=12)
axes[1].set_ylabel('Average Speed (mph)', fontsize=12)
axes[1].set_xticks(range(0, 24))
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/traffic_patterns.png', dpi=150, bbox_inches='tight')
print("✅ Saved: visualizations/traffic_patterns.png")

# Plot 3: Heatmap
fig, ax = plt.subplots(figsize=(15, 8))
subset = df.iloc[:288, :50].T

sns.heatmap(subset, cmap='RdYlGn', center=50, cbar_kws={'label': 'Speed (mph)'}, ax=ax)
ax.set_title('Traffic Speed Heatmap - First 24 Hours, 50 Sensors', fontsize=16, fontweight='bold')
ax.set_xlabel('Time (5-minute intervals)', fontsize=12)
ax.set_ylabel('Sensor ID', fontsize=12)

plt.tight_layout()
plt.savefig('visualizations/traffic_heatmap.png', dpi=150, bbox_inches='tight')
print("✅ Saved: visualizations/traffic_heatmap.png")

print("\n" + "="*60)
print("✅ ANALYSIS COMPLETE!")
print("="*60)
print("\nCheck the 'visualizations' folder for graphs!")

plt.show()