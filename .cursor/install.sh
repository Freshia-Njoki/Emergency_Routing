#!/usr/bin/env bash
#
# Cloud Agent install hook for the GRU emergency-routing framework.
#
# Idempotent: provisions an isolated Python 3.11 virtualenv (required by the
# pinned tensorflow==2.13.0 stack, which has no cp312 wheels), installs the
# pinned dependencies plus the two helpers needed to rebuild the dataset, and
# best-effort prepares the METR-LA tensors so the full pipeline runs offline.
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# ── 1. Ensure uv is available (fast, reproducible Python + venv manager) ──────
if ! command -v uv >/dev/null 2>&1; then
  echo "[install] Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

# ── 2. Create the Python 3.11 virtualenv (uv downloads 3.11 if needed) ────────
echo "[install] Creating Python 3.11 virtualenv at ./venv"
uv venv --python 3.11 venv
export VIRTUAL_ENV="$REPO_ROOT/venv"

# ── 3. Install pinned dependencies + dataset-prep helpers ─────────────────────
# gdown (Google Drive download) and tables (pandas.read_hdf backend) are only
# needed to rebuild the dataset; they are intentionally kept out of the
# training requirements.txt.
echo "[install] Installing pinned requirements..."
uv pip install -r requirements.txt
uv pip install gdown tables

# ── 4. Prepare the METR-LA dataset (idempotent, best-effort) ──────────────────
# Produces data/processed/training_data.npz so run_full_framework.py and
# run_simulation.py work end to end. A network/quota failure here is
# non-fatal: the shipped models, graph and scalers still allow
# evaluate_framework.py --synthetic to run.
if [ ! -f data/processed/training_data.npz ]; then
  echo "[install] Preparing METR-LA dataset..."
  ./venv/bin/python scripts/prepare_metr_la.py \
    || echo "[install] WARNING: dataset prep failed (offline?); continuing."
else
  echo "[install] data/processed/training_data.npz already present."
fi

echo "[install] Done. Activate with: source venv/bin/activate"
