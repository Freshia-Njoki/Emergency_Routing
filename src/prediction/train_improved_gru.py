"""
Train the thesis GRU (Section 3.6):

  2 stacked GRU layers, 64 hidden units, dropout 0.2
  input  12 steps (60 min)
  output  6 steps (30 min) x N sensors
  Adam + MSE, early stopping patience=10 on val_loss
  chronological 70/15/15 split (already applied in preprocessing)

This replaces the 3-layer/128-unit network that contradicted Chapter 3
while still writing gru_improved_best.h5 so the rest of the pipeline
keeps working.

Usage (from project root):
    python -m src.prediction.train_improved_gru
"""
from __future__ import annotations

import os
import pickle

import numpy as np

from src.utils.console import configure_utf8, safe_print

configure_utf8()

os.makedirs("models/saved", exist_ok=True)
os.makedirs("visualizations", exist_ok=True)


def build_model(n_steps, n_sensors, n_future, hidden=64, dropout=0.2):
    from tensorflow import keras
    from tensorflow.keras import layers

    model = keras.Sequential([
        layers.Input(shape=(n_steps, n_sensors)),
        layers.GRU(hidden, return_sequences=True, name="gru_1"),
        layers.Dropout(dropout),
        layers.GRU(hidden, return_sequences=False, name="gru_2"),
        layers.Dropout(dropout),
        layers.Dense(n_future * n_sensors, name="output"),
        layers.Reshape((n_future, n_sensors)),
    ])
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="mse",
        metrics=["mae"],
    )
    return model


def mph_metrics(y_true_scaled, y_pred_scaled, scaler):
    n_feat = int(getattr(scaler, "n_features_in_", 1))
    shape = y_true_scaled.shape  # (B, H, N)

    def inv(arr):
        if n_feat == 1:
            return scaler.inverse_transform(arr.reshape(-1, 1)).reshape(shape)
        return scaler.inverse_transform(arr.reshape(-1, n_feat)).reshape(shape)

    yt = inv(y_true_scaled)
    yp = inv(y_pred_scaled)
    mae = float(np.mean(np.abs(yt - yp)))
    rmse = float(np.sqrt(np.mean((yt - yp) ** 2)))
    return mae, rmse


def main():
    from tensorflow import keras
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    safe_print("=" * 60)
    safe_print("THESIS GRU TRAINING (2 x 64, dropout 0.2, MSE)")
    safe_print("=" * 60)

    data = np.load("data/processed/training_data.npz")
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    X_test, y_test = data["X_test"], data["y_test"]
    safe_print(f"Training {X_train.shape}  val {X_val.shape}  test {X_test.shape}")

    scaler_path = "data/processed/scaler.pkl"
    if not os.path.exists(scaler_path):
        scaler_path = "models/saved/scaler.pkl"
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    n_steps, n_sensors = X_train.shape[1], X_train.shape[2]
    n_future = y_train.shape[1]
    model = build_model(n_steps, n_sensors, n_future)
    model.summary()

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=10, restore_best_weights=True, verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6, verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            "models/saved/gru_improved_best.h5",
            monitor="val_loss", save_best_only=True, verbose=1,
        ),
    ]

    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=64,
        callbacks=callbacks,
        verbose=1,
    )

    model.save("models/saved/gru_improved_final.h5")
    with open("models/saved/training_history.pkl", "wb") as f:
        pickle.dump(history.history, f)

    y_pred = model.predict(X_test, verbose=0)
    mae, rmse = mph_metrics(y_test, y_pred, scaler)
    test_loss, test_mae_scaled = model.evaluate(X_test, y_test, verbose=0)

    metrics = {
        "dataset": "METR-LA",
        "n_sensors": int(n_sensors),
        "epochs": len(history.history["loss"]),
        "final_train_loss": float(history.history["loss"][-1]),
        "best_val_loss": float(min(history.history["val_loss"])),
        "test_mae_scaled": float(test_mae_scaled),
        "test_loss": float(test_loss),
        "test_mae_mph": mae,
        "test_rmse_mph": rmse,
    }
    with open("models/saved/metr_la_metrics.pkl", "wb") as f:
        pickle.dump(metrics, f)

    safe_print("\nMETR-LA TEST METRICS (inverse-scaled mph)")
    safe_print(f"  Epochs:        {metrics['epochs']}")
    safe_print(f"  Train loss:    {metrics['final_train_loss']:.4f}")
    safe_print(f"  Best val loss: {metrics['best_val_loss']:.4f}")
    safe_print(f"  Test MAE:      {mae:.2f} mph")
    safe_print(f"  Test RMSE:     {rmse:.2f} mph")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    axes[0].plot(history.history["loss"], label="Training")
    axes[0].plot(history.history["val_loss"], label="Validation")
    axes[0].set_title("MSE loss")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(history.history["mae"], label="Training")
    axes[1].plot(history.history["val_mae"], label="Validation")
    axes[1].set_title("MAE (scaled)")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("visualizations/improved_gru_training.png", dpi=150)
    plt.close()

    fig, axes = plt.subplots(3, 1, figsize=(15, 12))
    n_feat = int(getattr(scaler, "n_features_in_", 1))
    yt = y_test[:8]
    yp = y_pred[:8]
    if n_feat == 1:
        yt_m = scaler.inverse_transform(yt.reshape(-1, 1)).reshape(yt.shape)
        yp_m = scaler.inverse_transform(yp.reshape(-1, 1)).reshape(yp.shape)
    else:
        yt_m = scaler.inverse_transform(yt.reshape(-1, n_feat)).reshape(yt.shape)
        yp_m = scaler.inverse_transform(yp.reshape(-1, n_feat)).reshape(yp.shape)
    for i in range(3):
        sidx = min(i * 50, n_sensors - 1)
        axes[i].plot(yt_m[i, :, sidx], label="Actual", marker="o")
        axes[i].plot(yp_m[i, :, sidx], label="Predicted", marker="s")
        axes[i].set_title(f"Sample {i+1}, sensor {sidx}")
        axes[i].set_ylabel("Speed (mph)")
        axes[i].legend()
        axes[i].grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("visualizations/improved_gru_predictions.png", dpi=150)
    plt.close()
    safe_print("Saved visualizations/improved_gru_training.png")
    safe_print("TRAINING COMPLETE")


if __name__ == "__main__":
    main()
