"""
prepare_metr_la.py
------------------
Idempotent data bootstrap for the GRU emergency-routing framework.

Downloads the raw METR-LA speed dataset (if missing) and produces
``data/processed/training_data.npz`` (the scaled train/val/test tensors that
``run_full_framework.py`` and ``src/evaluation/run_simulation.py`` consume).

Safe to run repeatedly: any artifact that already exists is left untouched.

Usage:
    python scripts/prepare_metr_la.py
"""

import os
import sys

RAW_DIR = os.path.join("data", "raw")
PROC_DIR = os.path.join("data", "processed")
RAW_H5 = os.path.join(RAW_DIR, "metr-la.h5")
TRAINING_NPZ = os.path.join(PROC_DIR, "training_data.npz")

# Official DCRNN / Li et al. 2018 release file id (Google Drive).
METR_LA_GDRIVE_ID = "1pAGRfzMx6K9WWsfDcD1NMbIif0T0saFC"


def download_raw() -> bool:
    """Download metr-la.h5 into data/raw/ if it is not already present."""
    if os.path.exists(RAW_H5):
        print(f"[prepare] Raw dataset already present: {RAW_H5}")
        return True

    os.makedirs(RAW_DIR, exist_ok=True)
    try:
        import gdown
    except ImportError:
        print("[prepare] ERROR: gdown is not installed (pip install gdown).")
        return False

    url = f"https://drive.google.com/uc?id={METR_LA_GDRIVE_ID}"
    print(f"[prepare] Downloading METR-LA dataset from {url}")
    try:
        gdown.download(url, RAW_H5, quiet=False)
    except Exception as exc:  # network / quota failures are non-fatal
        print(f"[prepare] ERROR: download failed: {exc}")
        return False

    if not os.path.exists(RAW_H5):
        print("[prepare] ERROR: download did not produce a file.")
        return False

    size_mb = os.path.getsize(RAW_H5) / (1024 * 1024)
    print(f"[prepare] Downloaded {RAW_H5} ({size_mb:.1f} MB)")
    return True


def build_training_npz() -> bool:
    """Preprocess the raw HDF5 speeds into scaled train/val/test tensors."""
    if os.path.exists(TRAINING_NPZ):
        print(f"[prepare] Processed tensors already present: {TRAINING_NPZ}")
        return True

    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import StandardScaler

    os.makedirs(PROC_DIR, exist_ok=True)

    print(f"[prepare] Reading {RAW_H5}")
    df = pd.read_hdf(RAW_H5)
    data = df.values.astype(np.float64)
    print(f"[prepare] Raw speed matrix: {data.shape} (timesteps, sensors)")

    # Replace missing (0) readings with the per-sensor mean, matching
    # src/prediction/data_preprocessing.py.
    for col in range(data.shape[1]):
        col_data = data[:, col]
        non_zero = col_data[col_data > 0]
        if len(non_zero) > 0:
            data[col_data == 0, col] = non_zero.mean()

    sequence_length, horizon = 12, 6
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    X, y = [], []
    limit = len(data_scaled) - sequence_length - horizon
    for i in range(limit):
        X.append(data_scaled[i:i + sequence_length])
        y.append(data_scaled[i + sequence_length:i + sequence_length + horizon])
    X = np.asarray(X, dtype=np.float32)
    y = np.asarray(y, dtype=np.float32)
    print(f"[prepare] Sequences: X={X.shape} y={y.shape}")

    n = len(X)
    train_size = int(n * 0.70)
    val_size = int(n * 0.15)

    np.savez(
        TRAINING_NPZ,
        X_train=X[:train_size], y_train=y[:train_size],
        X_val=X[train_size:train_size + val_size],
        y_val=y[train_size:train_size + val_size],
        X_test=X[train_size + val_size:], y_test=y[train_size + val_size:],
    )
    print(f"[prepare] Wrote {TRAINING_NPZ}")
    return True


def main() -> int:
    if not download_raw():
        print("[prepare] Raw dataset unavailable; skipping tensor build.")
        return 1
    if not build_training_npz():
        return 1
    print("[prepare] METR-LA data is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
