"""
src/prediction/preprocess_pems_bay.py
--------------------------------------
Preprocesses the PEMS-BAY dataset using the same pipeline as METR-LA.

PEMS-BAY specs:
  - 325 sensors on San Francisco Bay Area road network
  - 6 months: January – May 2017
  - 5-minute resolution speed readings (mph)

Output: data/processed/pems_bay_training_data.npz
  X_train, X_val, X_test  — shape (N_samples, SEQUENCE_LEN, N_sensors)
  y_train, y_val, y_test  — shape (N_samples, N_future, N_sensors)
  scaler_bay.pkl           — fitted MinMaxScaler

Run from project root:
  python src/prediction/preprocess_pems_bay.py
"""

import os
import pickle
import numpy as np
import h5py
from sklearn.preprocessing import MinMaxScaler

# ── CONFIG ────────────────────────────────────────────────────────────────────
RAW_DIR       = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
H5_PATH       = os.path.join(RAW_DIR, "pems-bay.h5")

SEQUENCE_LEN   = 12    # 12 × 5 min = 60 min input
N_FUTURE_STEPS = 6     # 6 × 5 min = 30 min prediction horizon
TRAIN_RATIO    = 0.70
VAL_RATIO      = 0.15
# TEST_RATIO   = 0.15 (remainder)

N_SENSORS_EXPECTED = 325
os.makedirs(PROCESSED_DIR, exist_ok=True)


# ── LOAD ──────────────────────────────────────────────────────────────────────
def load_pems_bay(h5_path: str) -> np.ndarray:
    if not os.path.exists(h5_path):
        raise FileNotFoundError(f"Not found: {h5_path}")
    print(f"Loading {h5_path} ...")
    with h5py.File(h5_path, "r") as f:
        data = np.array(f["speed/block0_values"])
    print(f"  Shape: {data.shape}  (time steps x sensors)")
    return data.astype(np.float32)
    
# ── IMPUTE ────────────────────────────────────────────────────────────────────
def impute_missing(data: np.ndarray, max_gap: int = 6) -> np.ndarray:
    """
    Forward-fill gaps shorter than max_gap time steps.
    Gaps longer than max_gap are filled with sensor column mean.
    """
    out = data.copy()
    T, N = out.shape

    for n in range(N):
        col = out[:, n]
        zero_mask = col <= 0.0
        if not zero_mask.any():
            continue

        # forward fill
        for t in range(1, T):
            if zero_mask[t] and not zero_mask[t - 1]:
                out[t, n] = out[t - 1, n]
            zero_mask[t] = out[t, n] <= 0.0

        # remaining zeros → column mean
        col_mean = np.nanmean(out[:, n][out[:, n] > 0])
        out[zero_mask, n] = col_mean if not np.isnan(col_mean) else 30.0

    zeros_remaining = (out <= 0).sum()
    print(f"  After imputation — zeros remaining: {zeros_remaining}")
    return out


# ── SLIDING WINDOW ────────────────────────────────────────────────────────────
def make_sequences(data_scaled: np.ndarray):
    """
    Create overlapping windows from (T, N) scaled data.
    Returns X of shape (samples, SEQUENCE_LEN, N)
            y of shape (samples, N_FUTURE_STEPS, N)
    """
    T, N = data_scaled.shape
    X_list, y_list = [], []

    for t in range(SEQUENCE_LEN, T - N_FUTURE_STEPS + 1):
        X_list.append(data_scaled[t - SEQUENCE_LEN: t, :])        # (12, N)
        y_list.append(data_scaled[t: t + N_FUTURE_STEPS, :])      # (6, N)

    X = np.stack(X_list, axis=0)   # (samples, 12, N)
    y = np.stack(y_list, axis=0)   # (samples, 6, N)
    return X, y


# ── MAIN ──────────────────────────────────────────────────────────────────────
def preprocess():
    # 1. Load raw data
    data = load_pems_bay(H5_PATH)
    T, N = data.shape
    print(f"  Shape: {T} time steps × {N} sensors")

    if N != N_SENSORS_EXPECTED:
        print(f"  [WARNING] Expected {N_SENSORS_EXPECTED} sensors, got {N}. "
              "Continuing — check your h5 file.")

    # 2. Impute missing values
    print("\nImputing missing values...")
    data = impute_missing(data)

    # 3. Chronological split BEFORE fitting scaler
    n_train = int(T * TRAIN_RATIO)
    n_val   = int(T * VAL_RATIO)

    train_raw = data[:n_train]
    val_raw   = data[n_train: n_train + n_val]
    test_raw  = data[n_train + n_val:]

    print(f"\nSplit: train={len(train_raw)} | "
          f"val={len(val_raw)} | "
          f"test={len(test_raw)} time steps")

    # 4. Fit scaler on TRAINING data only (prevent data leakage)
    print("\nFitting MinMaxScaler on training data...")
    scaler = MinMaxScaler(feature_range=(0, 1))
    # scaler expects (samples, features) — reshape to (T*N, 1)
    scaler.fit(train_raw.reshape(-1, 1))

    train_scaled = scaler.transform(train_raw.reshape(-1, 1)).reshape(
        len(train_raw), N)
    val_scaled   = scaler.transform(val_raw.reshape(-1, 1)).reshape(
        len(val_raw), N)
    test_scaled  = scaler.transform(test_raw.reshape(-1, 1)).reshape(
        len(test_raw), N)

    # 5. Create sliding window sequences
    print("Creating sliding window sequences...")
    X_train, y_train = make_sequences(train_scaled)
    X_val,   y_val   = make_sequences(val_scaled)
    X_test,  y_test  = make_sequences(test_scaled)

    print(f"  X_train: {X_train.shape}  y_train: {y_train.shape}")
    print(f"  X_val:   {X_val.shape}    y_val:   {y_val.shape}")
    print(f"  X_test:  {X_test.shape}   y_test:  {y_test.shape}")

    # 6. Save processed arrays
    out_path = os.path.join(PROCESSED_DIR, "pems_bay_training_data.npz")
    np.savez(
        out_path,
        X_train=X_train, y_train=y_train,
        X_val=X_val,     y_val=y_val,
        X_test=X_test,   y_test=y_test,
    )
    print(f"\n[OK] Saved sequences to {out_path}")

    # 7. Save scaler
    scaler_path = os.path.join(PROCESSED_DIR, "scaler_bay.pkl")
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    print(f"[OK] Saved scaler to {scaler_path}")

    print("\nRun next: python src/prediction/train_pems_bay.py")


if __name__ == "__main__":
    preprocess()