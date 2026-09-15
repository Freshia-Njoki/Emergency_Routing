#!/usr/bin/env bash
#
# Idempotent Cloud Agent setup for the GRU emergency-routing framework.
#
# The project pins tensorflow==2.13.0, which supports Python 3.8-3.11 only,
# so we provision an isolated Python 3.11 interpreter with `uv` rather than
# relying on the system Python (3.12 on Ubuntu 24.04).
#
# Steps (each guarded so re-runs are cheap):
#   1. Ensure the `uv` package manager is installed.
#   2. Create a Python 3.11 virtualenv at .venv.
#   3. Install pinned Python dependencies from requirements.txt.
#   4. Fetch the METR-LA detector adjacency graph and the raw METR-LA dataset.
#   5. Preprocess METR-LA into data/processed/training_data.npz (train-only scaler).
set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
echo "== GRU Emergency Routing setup (repo: ${REPO_ROOT}) =="

# ---------------------------------------------------------------------------
# 1. uv package manager
# ---------------------------------------------------------------------------
export PATH="${HOME}/.local/bin:${PATH}"
if ! command -v uv >/dev/null 2>&1; then
  echo "== Installing uv =="
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
UV="$(command -v uv)"
echo "== Using $("$UV" --version) =="

# ---------------------------------------------------------------------------
# 2. Python 3.11 virtualenv
# ---------------------------------------------------------------------------
if [ ! -x ".venv/bin/python" ]; then
  echo "== Creating Python 3.11 virtualenv at .venv =="
  "$UV" venv --python 3.11 .venv
fi
VENV_PY="${REPO_ROOT}/.venv/bin/python"
echo "== Interpreter: $("$VENV_PY" --version) =="

# ---------------------------------------------------------------------------
# 3. Python dependencies
# ---------------------------------------------------------------------------
echo "== Installing Python dependencies (requirements.txt) =="
"$UV" pip install --python "$VENV_PY" -r requirements.txt

# ---------------------------------------------------------------------------
# 4. Datasets
# ---------------------------------------------------------------------------
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

echo "== Ensuring METR-LA sensor adjacency graph =="
"$VENV_PY" -c "from download_data import download_sensor_graph; download_sensor_graph()"

if [ ! -f "data/raw/metr-la.h5" ]; then
  echo "== Downloading raw METR-LA dataset =="
  "$VENV_PY" -c "from download_data import download_file; download_file('https://drive.google.com/uc?export=download&id=1pAGRfzMx6K9WWsfDcD1NMbIif0T0saFC', 'data/raw/metr-la.h5')"
else
  echo "== data/raw/metr-la.h5 already present =="
fi

# ---------------------------------------------------------------------------
# 5. Preprocess into training_data.npz (deterministic, train-only scaler)
# ---------------------------------------------------------------------------
echo "== Preprocessing METR-LA into data/processed/training_data.npz =="
"$VENV_PY" -m src.prediction.data_preprocessing

echo "== Setup complete. Activate with: source .venv/bin/activate =="
