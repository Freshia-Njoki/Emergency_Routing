"""
METR-LA preprocessing (thesis Section 3.4 / 3.6).

Fixes vs the original script:
  * StandardScaler is fitted on the TRAINING partition only (no leakage).
  * Chronological split is applied on raw time steps BEFORE windowing,
    so validation/test windows never contain training observations.
  * Raw mph series is saved for evaluation (evaluate_framework used to
    treat scaled npz values as mph, which produced the fake ~78% reduction).
  * Module import no longer writes training_data.npz as a side effect.
"""
from __future__ import annotations

import os
import pickle

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def load_metr_la_frame(path: str = "data/raw/metr-la.h5") -> pd.DataFrame:
    """Load METR-LA whether stored as a pandas table or a raw h5py frame."""
    try:
        df = pd.read_hdf(path)
        if getattr(df, "shape", (0, 0))[1] >= 100:
            return df
    except Exception:
        pass
    import h5py
    with h5py.File(path, "r") as f:
        if "df/block0_values" in f:
            arr = f["df/block0_values"][:]
        else:
            key = list(f.keys())[0]
            node = f[key]
            arr = node["block0_values"][:] if "block0_values" in node else node[()]
    return pd.DataFrame(np.asarray(arr, dtype=np.float32))


class TrafficDataPreprocessor:
    def __init__(self, sequence_length=12, horizon=6):
        self.sequence_length = sequence_length
        self.horizon = horizon
        self.scaler = StandardScaler()
        print("Preprocessor initialized:")
        print(f"   - Input sequence: {sequence_length} steps ({sequence_length * 5} min)")
        print(f"   - Prediction horizon: {horizon} steps ({horizon * 5} min)")

    def impute(self, data: np.ndarray) -> np.ndarray:
        out = data.astype(np.float32).copy()
        for col in range(out.shape[1]):
            col_data = out[:, col]
            non_zero = col_data[col_data > 0]
            mean_val = float(non_zero.mean()) if len(non_zero) else 30.0
            col_data[col_data <= 0] = mean_val
            out[:, col] = col_data
        return out

    def make_sequences(self, data: np.ndarray):
        seq, hor = self.sequence_length, self.horizon
        X, y = [], []
        for i in range(len(data) - seq - hor + 1):
            X.append(data[i:i + seq])
            y.append(data[i + seq:i + seq + hor])
        return np.asarray(X, dtype=np.float32), np.asarray(y, dtype=np.float32)

    def prepare_data(self, df, train_ratio=0.7, val_ratio=0.15):
        print("\n" + "=" * 60)
        print("DATA PREPROCESSING PIPELINE (train-only scaler)")
        print("=" * 60)

        data = self.impute(df.values if hasattr(df, "values") else np.asarray(df))
        T, N = data.shape
        print(f"\nInput data shape: {data.shape}  (timesteps x sensors)")

        n_train = int(T * train_ratio)
        n_val = int(T * val_ratio)
        train_raw = data[:n_train]
        val_raw = data[n_train:n_train + n_val]
        test_raw = data[n_train + n_val:]
        print(f"Split (raw steps): train={len(train_raw)}  val={len(val_raw)}  test={len(test_raw)}")

        # Per-sensor StandardScaler on training rows only (thesis 3.4).
        self.scaler = StandardScaler()
        self.scaler.fit(train_raw)

        train_s = self.scaler.transform(train_raw)
        val_s = self.scaler.transform(val_raw)
        test_s = self.scaler.transform(test_raw)

        X_train, y_train = self.make_sequences(train_s)
        X_val, y_val = self.make_sequences(val_s)
        X_test, y_test = self.make_sequences(test_s)

        print("Sequences:")
        print(f"   Training:   {X_train.shape}")
        print(f"   Validation: {X_val.shape}")
        print(f"   Test:       {X_test.shape}")

        os.makedirs("models/saved", exist_ok=True)
        os.makedirs("data/processed", exist_ok=True)
        with open("models/saved/scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)
        with open("data/processed/scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)
        np.save("data/processed/speed_data_raw.npy", data)
        print("Saved scaler.pkl and speed_data_raw.npy")

        return (X_train, y_train), (X_val, y_val), (X_test, y_test)


def save_npz(train, val, test, path="data/processed/training_data.npz"):
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = train, val, test
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.savez(
        path,
        X_train=X_train, y_train=y_train,
        X_val=X_val, y_val=y_val,
        X_test=X_test, y_test=y_test,
    )
    print(f"Saved: {path}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PREPROCESSING METR-LA")
    print("=" * 60)
    df = load_metr_la_frame("data/raw/metr-la.h5")
    print(f"Loaded: {df.shape}")
    preprocessor = TrafficDataPreprocessor(sequence_length=12, horizon=6)
    train, val, test = preprocessor.prepare_data(df)
    save_npz(train, val, test)
    print("PREPROCESSING COMPLETE")
