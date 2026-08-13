"""
download_pems_bay.py
--------------------
Downloads the PEMS-BAY dataset.
Run this from your project root:  python download_pems_bay.py
"""

import os
import urllib.request

DATA_DIR = os.path.join("data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)


def download_with_progress(url, dest):
    """Download a file showing progress."""
    print(f"Downloading to {dest} ...")

    def progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            pct = min(100, downloaded * 100 // total_size)
            mb = downloaded / 1_048_576
            print(f"\r  {pct:3d}%  {mb:.1f} MB", end="", flush=True)

    urllib.request.urlretrieve(url, dest, reporthook=progress)
    print()


def download_pems_bay():
    # ── Method 1: try gdown (Google Drive) ──────────────────────────────────
    pems_path = os.path.join(DATA_DIR, "pems-bay.h5")

    if os.path.exists(pems_path):
        print(f"[OK] pems-bay.h5 already exists at {pems_path}")
        return pems_path

    print("Attempting download via gdown (Google Drive)...")
    try:
        import gdown
        # Official DCRNN release file ID
        gdown.download(
            "https://drive.google.com/uc?id=1wD-mHlqAb2mtHOe_68fZvDh1LpDegMMq",
            pems_path,
            quiet=False,
        )
        if os.path.exists(pems_path):
            print(f"[OK] Downloaded pems-bay.h5")
            return pems_path
    except Exception as e:
        print(f"  gdown failed: {e}")

    # ── Method 2: adjacency matrix from DCRNN GitHub ─────────────────────────
    print("\nDownloading PEMS-BAY adjacency matrix from GitHub...")
    adj_url = (
        "https://raw.githubusercontent.com/liyaguang/DCRNN/"
        "master/data/sensor_graph/adj_mx_bay.pkl"
    )
    adj_path = os.path.join(DATA_DIR, "adj_mx_bay.pkl")
    try:
        download_with_progress(adj_url, adj_path)
        print(f"[OK] Downloaded adj_mx_bay.pkl")
    except Exception as e:
        print(f"  adj matrix download failed: {e}")

    print(
        "\n[ACTION REQUIRED] pems-bay.h5 must be downloaded manually.\n"
        "  1. Go to: https://drive.google.com/drive/folders/"
        "10FOTa6HXPqX8Pf5WRoRwcFnW9BrNZEIX\n"
        "  2. Download  pems-bay.h5\n"
        f"  3. Place it in: {os.path.abspath(DATA_DIR)}\n"
    )
    return None


if __name__ == "__main__":
    # Install gdown if missing
    try:
        import gdown
    except ImportError:
        print("Installing gdown...")
        os.system("pip install gdown -q")

    result = download_pems_bay()
    if result:
        size_mb = os.path.getsize(result) / 1_048_576
        print(f"\nFile size: {size_mb:.1f} MB")
        print("Run next:  python src/prediction/preprocess_pems_bay.py")