"""
Loads preprocessed traffic time-series data

Builds a deep GRU-based neural network

Trains it with smart training strategies

Evaluates performance on test data

Saves the model

Plots training results and predictions
"""
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import pickle

print("="*60)
print("TRAFFIC PREDICTION MODEL")
print("="*60)

# Load preprocessed data
print("\n📥 Loading preprocessed data...")
data = np.load('data/processed/training_data.npz')
X_train = data['X_train']
y_train = data['y_train']
X_val = data['X_val']
y_val = data['y_val']
X_test = data['X_test']
y_test = data['y_test']

print(f"✅ Data loaded: Training {X_train.shape}")

# Build GRU Model
print("\n🧠 Building GRU model...")

model = keras.Sequential([
    # Input layer
    layers.Input(shape=(X_train.shape[1], X_train.shape[2])),
    
    # First GRU layer - MORE UNITS
    layers.GRU(128, return_sequences=True, name='gru_1'),
    layers.Dropout(0.3),
    
    # Second GRU layer - MORE UNITS
    layers.GRU(128, return_sequences=True, name='gru_2'),
    layers.Dropout(0.3),
    
    # Third GRU layer - ADDED!
    layers.GRU(64, return_sequences=False, name='gru_3'),
    layers.Dropout(0.2),
    
    # Dense layer before output - ADDED!
    layers.Dense(256, activation='relu', name='dense_1'),
    layers.Dropout(0.2),
    
    # Output layer
    layers.Dense(y_train.shape[1] * y_train.shape[2], name='output'),
    layers.Reshape((y_train.shape[1], y_train.shape[2]))
])

# Custom learning rate schedule
initial_learning_rate = 0.001
lr_schedule = keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate,
    decay_steps=1000,
    decay_rate=0.96,
    staircase=True
)

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=lr_schedule),
    loss='mse',
    metrics=['mae']
)

print(model.summary())

# Callbacks
callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=15,  # Increased patience
        restore_best_weights=True,
        verbose=1
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=7,  # Increased patience
        min_lr=0.00001,
        verbose=1
    ),
    keras.callbacks.ModelCheckpoint(
        'models/saved/gru_improved_best.h5',
        monitor='val_loss',
        save_best_only=True,
        verbose=1
    )
]

# Train
print("\n🚀 Training model...")
print("This will take 15-30 minutes...")

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=100,  # More epochs
    batch_size=64,  # Larger batch size
    callbacks=callbacks,
    verbose=1
)

# Save
model.save('models/saved/gru_improved_final.h5')
print("\n✅ Model saved!")

# Evaluate
print("\n📊 Evaluating...")
test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Loss: {test_loss:.4f}")
print(f"Test MAE: {test_mae:.4f}")

# Plot training
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

axes[0].plot(history.history['loss'], label='Training', linewidth=2)
axes[0].plot(history.history['val_loss'], label='Validation', linewidth=2)
axes[0].set_title('Model Loss Over Epochs', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Loss')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(history.history['mae'], label='Training', linewidth=2)
axes[1].plot(history.history['val_mae'], label='Validation', linewidth=2)
axes[1].set_title('Model MAE Over Epochs', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('MAE')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/improved_gru_training.png', dpi=150)
print("✅ Saved: visualizations/improved_gru_training.png")

# Better predictions visualization
print("\n🔮 Making predictions...")
y_pred = model.predict(X_test[:100], verbose=0)

fig, axes = plt.subplots(3, 1, figsize=(15, 12))

for i in range(3):
    sensor_idx = i * 50
    
    axes[i].plot(y_test[i, :, sensor_idx], label='Actual', 
                linewidth=2.5, marker='o', markersize=6, color='#2563eb')
    axes[i].plot(y_pred[i, :, sensor_idx], label='Predicted', 
                linewidth=2.5, marker='s', markersize=6, alpha=0.8, color='#dc2626')
    axes[i].fill_between(range(6), 
                         y_test[i, :, sensor_idx], 
                         y_pred[i, :, sensor_idx], 
                         alpha=0.2)
    axes[i].set_title(f'Sample {i+1}, Sensor {sensor_idx}', fontsize=12, fontweight='bold')
    axes[i].set_xlabel('Time Step (5-min)')
    axes[i].set_ylabel('Normalized Speed')
    axes[i].legend()
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/improved_gru_predictions.png', dpi=150)
print("✅ Saved: visualizations/improved_gru_predictions.png")

print("\n" + "="*60)
print("✅ MODEL TRAINING COMPLETE!")
print("="*60)
print(f"\nImprovement over baseline:")
print(f"  Baseline MAE: 0.3718")
print(f"  Improved MAE: {test_mae:.4f}")
print(f"  Reduction: {((0.3718 - test_mae) / 0.3718 * 100):.1f}%")