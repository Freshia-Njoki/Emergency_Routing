"""
Train GRU Model for Traffic Prediction
"""
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import pickle
import os

print("="*60)
print("TRAFFIC PREDICTION MODEL TRAINING")
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

print(f"✅ Data loaded!")
print(f"   Training: {X_train.shape}")
print(f"   Validation: {X_val.shape}")
print(f"   Test: {X_test.shape}")

# Build GRU Model
print("\n🧠 Building GRU model...")

model = keras.Sequential([
    # Input layer
    layers.Input(shape=(X_train.shape[1], X_train.shape[2])),
    
    # First GRU layer
    layers.GRU(64, return_sequences=True, name='gru_1'),
    layers.Dropout(0.2),
    
    # Second GRU layer
    layers.GRU(64, return_sequences=False, name='gru_2'),
    layers.Dropout(0.2),
    
    # Output layer
    layers.Dense(y_train.shape[1] * y_train.shape[2], name='output'),
    layers.Reshape((y_train.shape[1], y_train.shape[2]))
])

model.compile(
    optimizer='adam',
    loss='mse',
    metrics=['mae']
)

print(model.summary())

# Callbacks
callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=0.00001,
        verbose=1
    ),
    keras.callbacks.ModelCheckpoint(
        'models/saved/gru_best.h5',
        monitor='val_loss',
        save_best_only=True,
        verbose=1
    )
]

# Train the model
print("\n🚀 Training model...")
print("This may take 10-20 minutes depending on your computer...")

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

# Save final model
model.save('models/saved/gru_traffic_model.h5')
print("\n✅ Model saved to: models/saved/gru_traffic_model.h5")

# Save training history
with open('models/saved/training_history.pkl', 'wb') as f:
    pickle.dump(history.history, f)

# Evaluate on test set
print("\n📊 Evaluating on test set...")
test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Loss (MSE): {test_loss:.4f}")
print(f"Test MAE: {test_mae:.4f}")

# Plot training history
print("\n📈 Creating training visualizations...")
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Loss
axes[0].plot(history.history['loss'], label='Training Loss', linewidth=2)
axes[0].plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
axes[0].set_title('Model Loss Over Epochs', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Loss (MSE)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# MAE
axes[1].plot(history.history['mae'], label='Training MAE', linewidth=2)
axes[1].plot(history.history['val_mae'], label='Validation MAE', linewidth=2)
axes[1].set_title('Model MAE Over Epochs', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('MAE')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/gru_training_history.png', dpi=150)
print("✅ Saved: visualizations/gru_training_history.png")

# Make predictions on test set
print("\n🔮 Making predictions on test set...")
y_pred = model.predict(X_test[:100], verbose=0)

# Plot predictions vs actual
fig, axes = plt.subplots(3, 1, figsize=(15, 12))

for i in range(3):
    # Select one sensor
    sensor_idx = i * 50
    
    axes[i].plot(y_test[i, :, sensor_idx], label='Actual', linewidth=2, marker='o')
    axes[i].plot(y_pred[i, :, sensor_idx], label='Predicted', linewidth=2, marker='s', alpha=0.7)
    axes[i].set_title(f'Prediction vs Actual - Sample {i+1}, Sensor {sensor_idx}', fontsize=12, fontweight='bold')
    axes[i].set_xlabel('Time Step (5-min intervals)')
    axes[i].set_ylabel('Normalized Speed')
    axes[i].legend()
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/gru_predictions.png', dpi=150)
print("✅ Saved: visualizations/gru_predictions.png")

print("\n" + "="*60)
print("✅ TRAINING COMPLETE!")
print("="*60)
print("\n📁 Files created:")
print("   - models/saved/gru_traffic_model.keras (final model)")
print("   - models/saved/gru_best.keras (best checkpoint)")
print("   - models/saved/training_history.pkl (training metrics)")
print("   - visualizations/gru_training_history.png")
print("   - visualizations/gru_predictions.png")
print("\n🎉 Your traffic prediction model is ready!")