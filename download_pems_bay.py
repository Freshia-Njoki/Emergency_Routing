"""
download_pems_bay.py
--------------------
Downloads and processes the PEMS-BAY dataset to match your
existing METR-LA processed format exactly.

Run once:
    python download_pems_bay.py

Produces:
    data/pems_bay/processed/training_data.npz   shape (T, 325)
    data/pems_bay/processed/adj_mx_bay.pkl      adjacency matrix
    data/pems_bay/processed/sensor_ids_bay.txt  sensor IDs

PEMS-BAY specs:
    325 sensors on San Francisco Bay Area road network
    6 months: Jan–May 2017
    5-minute resolution, speed in mph
"""

import os
import sys
import pickle
import numpy as np

DATA_DIR    = 'data/pems_bay'
PROC_DIR    = os.path.join(DATA_DIR, 'processed')
RAW_DIR     = os.path.join(DATA_DIR, 'raw')
SEQUENCE_LEN   = 12
N_FUTURE_STEPS = 6
TRAIN_RATIO    = 0.70
VAL_RATIO      = 0.15


def download_pems_bay():
    os.makedirs(RAW_DIR,  exist_ok=True)
    os.makedirs(PROC_DIR, exist_ok=True)

    h5_path  = os.path.join(RAW_DIR, 'pems-bay.h5')
    adj_path = os.path.join(RAW_DIR, 'adj_mx_bay.pkl')

    # ── Download .h5 speed data ───────────────────────────────────────────────
    if not os.path.exists(h5_path):
        print("[Download] Fetching pems-bay.h5 from Google Drive...")
        try:
            import gdown
            gdown.download(
                'https://drive.google.com/uc?id=1wD-mHlqAb2mtHOe_68fZvDh1LpDegMMq',
                h5_path, quiet=False
            )
            print(f"[Download] Saved → {h5_path}")
        except Exception as e:
            print(f"[Download] gdown failed: {e}")
            print("\nManual download instructions:")
            print("1. Open: https://github.com/liyaguang/DCRNN")
            print("2. Click the Google Drive link in the README")
            print(f"3. Download pems-bay.h5 → save to {h5_path}")
            sys.exit(1)
    else:
        print(f"[Download] pems-bay.h5 already exists at {h5_path}")

    # ── Download adjacency matrix ─────────────────────────────────────────────
    if not os.path.exists(adj_path):
        print("[Download] Fetching adj_mx_bay.pkl...")
        try:
            import urllib.request
            url = 'https://github.com/liyaguang/DCRNN/raw/master/data/sensor_graph/adj_mx_bay.pkl'
            urllib.request.urlretrieve(url, adj_path)
            print(f"[Download] Saved → {adj_path}")
        except Exception as e:
            print(f"[Download] Could not download adj_mx_bay.pkl: {e}")
            print(f"Download manually from the DCRNN repo → save to {adj_path}")

    return h5_path, adj_path


def load_pems_bay_speeds(h5_path: str) -> np.ndarray:
    """Load pems-bay.h5 → np.ndarray shape (T, 325), speeds in mph."""
    try:
        import h5py
        with h5py.File(h5_path, 'r') as f:
            key = list(f.keys())[0]
            data = f[key][:]
        # ensure (T, N)
        if data.ndim == 3:
            data = data[:, :, 0]          # take speed channel
        if data.shape[0] < data.shape[1]:
            data = data.T
        print(f"[Process] pems-bay raw shape: {data.shape}")
        return data.astype(np.float32)
    except Exception as e:
        raise RuntimeError(f"Could not read pems-bay.h5: {e}\n"
                           "Ensure h5py is installed: pip install h5py")


def create_sequences(data: np.ndarray,
                     seq_len:     int = SEQUENCE_LEN,
                     horizon:     int = N_FUTURE_STEPS,
                     stride:      int = 1):
    """
    Slide windows over (T, N) speed data.
    Returns X: (samples, seq_len, N), y: (samples, horizon, N)
    Identical to your METR-LA preprocessing in data_preprocessing.py.
    """
    T, N   = data.shape
    X_list = []
    y_list = []
    for t in range(0, T - seq_len - horizon + 1, stride):
        X_list.append(data[t           : t + seq_len])
        y_list.append(data[t + seq_len : t + seq_len + horizon])
    X = np.array(X_list)   # (samples, seq_len, N)
    y = np.array(y_list)   # (samples, horizon, N)
    print(f"[Process] Sequences: X={X.shape}, y={y.shape}")
    return X, y


def chronological_split(X: np.ndarray, y: np.ndarray,
                         train_r=TRAIN_RATIO, val_r=VAL_RATIO):
    """Chronological 70/15/15 split — same as your METR-LA split."""
    n     = len(X)
    t_end = int(n * train_r)
    v_end = int(n * (train_r + val_r))
    return (X[:t_end], y[:t_end],
            X[t_end:v_end], y[t_end:v_end],
            X[v_end:], y[v_end:])


def scale_data(X_train, X_val, X_test, y_train, y_val, y_test):
    """
    MinMax scale using only training statistics — prevents data leakage.
    Matches your existing scaler approach in data_preprocessing.py.
    """
    from sklearn.preprocessing import MinMaxScaler
    import pickle

    n_tr, seq, N = X_train.shape
    flat_train = X_train.reshape(-1, N)

    scaler = MinMaxScaler()
    scaler.fit(flat_train)

    def scale(arr):
        s, n = arr.shape[1], arr.shape[2]
        return scaler.transform(arr.reshape(-1, n)).reshape(-1, s, n)

    X_tr_s = scale(X_train)
    X_v_s  = scale(X_val)
    X_te_s = scale(X_test)
    y_tr_s = scale(y_train)
    y_v_s  = scale(y_val)
    y_te_s = scale(y_test)

    scaler_path = os.path.join(PROC_DIR, 'scaler_bay.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"[Process] Scaler saved → {scaler_path}")

    return X_tr_s, X_v_s, X_te_s, y_tr_s, y_v_s, y_te_s, scaler


def process_pems_bay(h5_path: str):
    print("\n[Process] Processing PEMS-BAY dataset...")

    # ── load raw ──────────────────────────────────────────────────────────────
    speeds = load_pems_bay_speeds(h5_path)

    # ── handle missing values (same as METR-LA) ───────────────────────────────
    # interpolate gaps shorter than 30 min (6 steps), exclude longer
    mask = (speeds == 0) | np.isnan(speeds)
    if mask.any():
        n_missing = mask.sum()
        print(f"[Process] Imputing {n_missing} missing values (<= 30 min gaps)...")
        for i in range(speeds.shape[1]):
            col = speeds[:, i].copy()
            col_mask = (col == 0) | np.isnan(col)
            if col_mask.any():
                idx = np.where(~col_mask)[0]
                if len(idx) > 1:
                    speeds[:, i] = np.interp(np.arange(len(col)), idx, col[idx])

    # ── create sequences ──────────────────────────────────────────────────────
    X, y = create_sequences(speeds)

    # ── split ─────────────────────────────────────────────────────────────────
    X_train, y_train, X_val, y_val, X_test, y_test = chronological_split(X, y)
    print(f"[Process] Split: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")

    # ── scale ─────────────────────────────────────────────────────────────────
    X_tr_s, X_v_s, X_te_s, y_tr_s, y_v_s, y_te_s, scaler = \
        scale_data(X_train, X_val, X_test, y_train, y_val, y_test)

    # ── save ──────────────────────────────────────────────────────────────────
    npz_path = os.path.join(PROC_DIR, 'training_data.npz')
    np.savez(npz_path,
             X_train=X_tr_s, y_train=y_tr_s,
             X_val=X_v_s,   y_val=y_v_s,
             X_test=X_te_s, y_test=y_te_s)
    print(f"[Process] Saved → {npz_path}")

    # also save raw speed array for evaluation use
    raw_path = os.path.join(PROC_DIR, 'speed_data_raw.npy')
    np.save(raw_path, speeds)
    print(f"[Process] Raw speeds saved → {raw_path}")

    return npz_path, scaler


if __name__ == '__main__':
    h5_path, adj_path = download_pems_bay()
    process_pems_bay(h5_path)
    print("\n[Done] PEMS-BAY ready.")
    print(f"  Processed data → {PROC_DIR}/")
    print("  Next: run the evaluation on PEMS-BAY:")
    print("  python -m src.evaluation.evaluate_framework "
          "--data-dir data/pems_bay --dataset pems_bay "
          "--model-dir models/saved --results-dir results/pems_bay")
