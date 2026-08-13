"""
src/prediction/train_pems_bay.py
---------------------------------
Trains a GRU model on the PEMS-BAY dataset.

Uses identical architecture to the METR-LA model so results
are directly comparable.

Output:
  models/saved/gru_bay_best.h5     — best model by validation loss
  models/saved/training_history_bay.pkl

Run from project root:
  python src/prediction/train_pems_bay.py
"""

import os
import pickle
import numpy as np

PROCESSED_DIR = os.path.join("data", "processed")
MODEL_DIR     = os.path.join("models", "saved")
os.makedirs(MODEL_DIR, exist_ok=True)

# ── CONFIG — identical to METR-LA training ───────────────────────────────────
SEQUENCE_LEN   = 12
N_FUTURE_STEPS = 6
HIDDEN_UNITS   = 64
N_LAYERS       = 2
DROPOUT_RATE   = 0.2
BATCH_SIZE     = 64
MAX_EPOCHS     = 100
PATIENCE       = 10      # early stopping patience
LEARNING_RATE  = 0.001


def build_gru_model(n_sensors: int):
    """Builds the same GRU architecture used for METR-LA."""
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import GRU, Dense, Dropout

    model = Sequential(name="GRU_PEMS_BAY")

    model.add(GRU(
        units=HIDDEN_UNITS,
        return_sequences=True,
        input_shape=(SEQUENCE_LEN, n_sensors),
        name="gru_layer_1"
    ))
    model.add(Dropout(DROPOUT_RATE))

    model.add(GRU(
        units=HIDDEN_UNITS,
        return_sequences=False,
        name="gru_layer_2"
    ))
    model.add(Dropout(DROPOUT_RATE))

    # Output: N_FUTURE_STEPS × n_sensors flattened, then reshape in loss
    model.add(Dense(N_FUTURE_STEPS * n_sensors, name="output_dense"))

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="mse",
        metrics=["mae"]
    )
    return model


def reshape_for_model(X, y):
    """
    X shape: (samples, SEQUENCE_LEN, N_sensors)
    y shape: (samples, N_FUTURE_STEPS, N_sensors)
    → y_flat: (samples, N_FUTURE_STEPS * N_sensors) for Dense output
    """
    samples = X.shape[0]
    y_flat = y.reshape(samples, -1)
    return X, y_flat


def compute_metrics(y_true_flat, y_pred_flat, scaler, n_sensors):
    """
    Inverse-scale predictions and ground truth, then compute MAE and RMSE.
    Both arrays shape: (samples, N_FUTURE * N_sensors)
    """
    samples = y_true_flat.shape[0]

    # reshape to (samples * N_future * N_sensors, 1) for inverse_transform
    y_true_inv = scaler.inverse_transform(
        y_true_flat.reshape(-1, 1)
    ).reshape(samples, N_FUTURE_STEPS, n_sensors)

    y_pred_inv = scaler.inverse_transform(
        y_pred_flat.reshape(-1, 1)
    ).reshape(samples, N_FUTURE_STEPS, n_sensors)

    mae  = float(np.mean(np.abs(y_true_inv - y_pred_inv)))
    rmse = float(np.sqrt(np.mean((y_true_inv - y_pred_inv) ** 2)))
    return mae, rmse, y_true_inv, y_pred_inv


def train():
    import tensorflow as tf

    # ── Load processed data ─────────────────────────────────────────────────
    npz_path = os.path.join(PROCESSED_DIR, "pems_bay_training_data.npz")
    if not os.path.exists(npz_path):
        raise FileNotFoundError(
            f"{npz_path} not found. "
            "Run: python src/prediction/preprocess_pems_bay.py"
        )

    print("Loading PEMS-BAY processed data...")
    data = np.load(npz_path)
    X_train, y_train = data["X_train"], data["y_train"]
    X_val,   y_val   = data["X_val"],   data["y_val"]
    X_test,  y_test  = data["X_test"],  data["y_test"]

    # Load scaler
    scaler_path = os.path.join(PROCESSED_DIR, "scaler_bay.pkl")
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    n_sensors = X_train.shape[2]
    print(f"  Sensors: {n_sensors}  "
          f"Train: {len(X_train)}  Val: {len(X_val)}  Test: {len(X_test)}")

    # ── Reshape y for Dense output ──────────────────────────────────────────
    X_train_r, y_train_r = reshape_for_model(X_train, y_train)
    X_val_r,   y_val_r   = reshape_for_model(X_val,   y_val)
    X_test_r,  y_test_r  = reshape_for_model(X_test,  y_test)

    # ── Build model ─────────────────────────────────────────────────────────
    print("\nBuilding GRU model (same architecture as METR-LA)...")
    model = build_gru_model(n_sensors)
    model.summary()

    # ── Callbacks ───────────────────────────────────────────────────────────
    model_path = os.path.join(MODEL_DIR, "gru_bay_best.h5")
    callbacks  = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=PATIENCE,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ModelCheckpoint(
            model_path,
            monitor="val_loss",
            save_best_only=True,
            verbose=0
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        ),
    ]

    # ── Train ────────────────────────────────────────────────────────────────
    print(f"\nTraining on PEMS-BAY ({n_sensors} sensors)...")
    history = model.fit(
        X_train_r, y_train_r,
        validation_data=(X_val_r, y_val_r),
        epochs=MAX_EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1
    )

    # ── Save training history ────────────────────────────────────────────────
    hist_path = os.path.join(MODEL_DIR, "training_history_bay.pkl")
    with open(hist_path, "wb") as f:
        pickle.dump(history.history, f)
    print(f"\n[OK] Training history saved to {hist_path}")

    # ── Evaluate on test set ─────────────────────────────────────────────────
    print("\nEvaluating on PEMS-BAY test set...")
    y_pred_flat = model.predict(X_test_r, verbose=0)
    mae, rmse, y_true_inv, y_pred_inv = compute_metrics(
        y_test_r, y_pred_flat, scaler, n_sensors
    )

    n_epochs = len(history.history["loss"])
    best_val = min(history.history["val_loss"])
    final_train = history.history["loss"][-1]

    print("\n" + "=" * 50)
    print("PEMS-BAY GRU TRAINING RESULTS")
    print("=" * 50)
    print(f"  Epochs trained:       {n_epochs}")
    print(f"  Final training loss:  {final_train:.4f}")
    print(f"  Best validation loss: {best_val:.4f}")
    print(f"  Test set MAE:         {mae:.2f} mph")
    print(f"  Test set RMSE:        {rmse:.2f} mph")
    print("=" * 50)

    # Save metrics for comparison
    metrics = {
        "dataset": "PEMS-BAY",
        "n_sensors": n_sensors,
        "epochs": n_epochs,
        "final_train_loss": final_train,
        "best_val_loss": best_val,
        "test_mae_mph": mae,
        "test_rmse_mph": rmse,
    }
    metrics_path = os.path.join(MODEL_DIR, "pems_bay_metrics.pkl")
    with open(metrics_path, "wb") as f:
        pickle.dump(metrics, f)
    print(f"\n[OK] Model saved to {model_path}")
    print("Run next: python src/evaluation/cross_validate.py")


if __name__ == "__main__":
    train()