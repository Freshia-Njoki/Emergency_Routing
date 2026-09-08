"""
Joint per-sensor GRU trained on METR-LA and PEMS-BAY together.

A single multivariate network cannot consume both datasets at once:
METR-LA has 207 sensors and PEMS-BAY has 325, so the input width differs.
This script instead trains one *shared* sensor-level GRU:

    input  (12, 1)   -- 60 minutes of one detector
    output (6,)      -- 30-minute speed forecast for that detector

Every detector from both cities becomes a training sample, which is the
correct way to "train on both datasets at a go" (thesis abstract / Obj 2).

The METR-LA *multivariate* model (train_improved_gru.py) remains the
routing model, because spatial correlation across the 207 LA sensors
matters for TD-A*.  This joint model is the cross-city generalisation
check and can optionally be used as a drop-in fallback.

Usage:
    python -m src.prediction.train_joint_per_sensor
"""
from __future__ import annotations

import os
import pickle

import numpy as np

from src.utils.console import configure_utf8, safe_print

configure_utf8()


def _inv(arr, scaler):
    n_feat = int(getattr(scaler, "n_features_in_", 1))
    shape = arr.shape
    if n_feat == 1:
        return scaler.inverse_transform(arr.reshape(-1, 1)).reshape(shape)
    return scaler.inverse_transform(arr.reshape(-1, n_feat)).reshape(shape)


def _sensor_samples(X, y):
    """(B, 12, N), (B, 6, N) -> (B*N, 12, 1), (B*N, 6)."""
    b, t, n = X.shape
    h = y.shape[1]
    Xs = X.transpose(0, 2, 1).reshape(b * n, t, 1)
    ys = y.transpose(0, 2, 1).reshape(b * n, h)
    return Xs.astype(np.float32), ys.astype(np.float32)


def _load_mph(npz_path, scaler_path):
    if not os.path.exists(npz_path) or not os.path.exists(scaler_path):
        return None
    data = np.load(npz_path)
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    out = {}
    for split in ("train", "val", "test"):
        X = _inv(data[f"X_{split}"], scaler)
        y = _inv(data[f"y_{split}"], scaler)
        out[split] = (X, y)
    out["name"] = os.path.basename(npz_path)
    return out


def main():
    from tensorflow import keras
    from tensorflow.keras import layers
    from sklearn.preprocessing import StandardScaler

    os.makedirs("models/saved", exist_ok=True)

    sets = []
    la = _load_mph("data/processed/training_data.npz", "data/processed/scaler.pkl")
    bay = _load_mph(
        "data/processed/pems_bay_training_data.npz", "data/processed/scaler_bay.pkl"
    )
    if la is None:
        raise FileNotFoundError("METR-LA processed data missing. Run data_preprocessing.py")
    sets.append(("METR-LA", la))
    if bay is None:
        safe_print("[WARN] PEMS-BAY processed data missing -- training METR-LA sensors only.")
    else:
        sets.append(("PEMS-BAY", bay))

    scaler = StandardScaler()
    Xtr, ytr = _sensor_samples(*la["train"])
    if bay is not None:
        xb, yb = _sensor_samples(*bay["train"])
        Xtr = np.concatenate([Xtr, xb], axis=0)
        ytr = np.concatenate([ytr, yb], axis=0)
    scaler.fit(Xtr.reshape(-1, 1))

    def pack(pair):
        X, y = _sensor_samples(*pair)
        Xs = scaler.transform(X.reshape(-1, 1)).reshape(X.shape)
        ys = scaler.transform(y.reshape(-1, 1)).reshape(y.shape)
        return Xs, ys

    X_train, y_train = pack(la["train"]) if bay is None else (
        scaler.transform(Xtr.reshape(-1, 1)).reshape(Xtr.shape),
        scaler.transform(ytr.reshape(-1, 1)).reshape(ytr.shape),
    )
    X_val, y_val = pack(la["val"])
    if bay is not None:
        xv, yv = pack(bay["val"])
        X_val = np.concatenate([X_val, xv], axis=0)
        y_val = np.concatenate([y_val, yv], axis=0)

    safe_print(f"Joint train samples: {X_train.shape}  val: {X_val.shape}")

    model = keras.Sequential([
        layers.Input(shape=(12, 1)),
        layers.GRU(64, return_sequences=True),
        layers.Dropout(0.2),
        layers.GRU(64, return_sequences=False),
        layers.Dropout(0.2),
        layers.Dense(6),
    ])
    model.compile(optimizer=keras.optimizers.Adam(0.001), loss="mse", metrics=["mae"])
    model.summary()

    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=40,
        batch_size=256,
        callbacks=[
            keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=8, restore_best_weights=True, verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=4, min_lr=1e-6, verbose=1
            ),
        ],
        verbose=1,
    )

    model.save("models/saved/gru_joint_per_sensor.h5")
    with open("models/saved/scaler_joint.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open("models/saved/training_history_joint.pkl", "wb") as f:
        pickle.dump(history.history, f)

    results = {}
    for name, ds in sets:
        Xt, yt = pack(ds["test"])
        pred = model.predict(Xt, verbose=0)
        yt_m = scaler.inverse_transform(yt.reshape(-1, 1)).reshape(yt.shape)
        yp_m = scaler.inverse_transform(pred.reshape(-1, 1)).reshape(pred.shape)
        mae = float(np.mean(np.abs(yt_m - yp_m)))
        rmse = float(np.sqrt(np.mean((yt_m - yp_m) ** 2)))
        results[name] = {"mae_mph": mae, "rmse_mph": rmse}
        safe_print(f"  {name:12s}  joint-GRU MAE={mae:.2f} mph  RMSE={rmse:.2f} mph")

    with open("models/saved/joint_metrics.pkl", "wb") as f:
        pickle.dump(results, f)
    safe_print("Saved models/saved/gru_joint_per_sensor.h5")
    safe_print("JOINT TRAINING COMPLETE")


if __name__ == "__main__":
    main()
