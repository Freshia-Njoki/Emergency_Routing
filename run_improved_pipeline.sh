# Pull and run the improved emergency-routing framework
#
# Branch: cursor/improve-ev-routing-framework-c48b
# Repo:   https://github.com/Freshia-Njoki/Emergency_Routing
#
# These commands are for Git Bash on Windows (your existing venv).
# Run them from:  D:\MSc - Route optimisation for road traffic evasion\Routing App
#
# Do NOT train one multivariate GRU on METR-LA + PEMS-BAY together
# (207 vs 325 sensors).  Routing uses METR-LA; PEMS-BAY is cross-validation.

set -e

echo "=== 1. Fetch the improvement branch (does NOT touch main) ==="
git fetch origin
git checkout cursor/improve-ev-routing-framework-c48b
git pull origin cursor/improve-ev-routing-framework-c48b

echo "=== 2. Activate venv ==="
# Git Bash:
source venv/Scripts/activate
# PowerShell equivalent:  .\venv\Scripts\Activate.ps1

export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

echo "=== 3. Sensor graph (METR-LA adjacency) if missing ==="
python -c "from download_data import download_sensor_graph; download_sensor_graph()"

echo "=== 4. Re-preprocess METR-LA (train-only scaler -- fixes data leakage) ==="
python -m src.prediction.data_preprocessing

echo "=== 5. Retrain thesis GRU (2 x 64 hidden, dropout 0.2) ==="
python -m src.prediction.train_improved_gru

echo "=== 6. Optional PEMS-BAY cross-val (separate model, NOT joint multivariate) ==="
# python -m src.prediction.preprocess_pems_bay
# python -m src.prediction.train_pems_bay
# python -m src.evaluation.cross_validate

echo "=== 7. Smoke-test simulation (15 OD pairs) ==="
python -m src.evaluation.run_simulation --quick --graph sensor

echo "=== 8. Full 900-experiment evaluation (75 OD x 3 scenarios x 4 delta) ==="
python -m src.evaluation.evaluate_framework --results-dir results/sliding --graph sensor
python -m src.evaluation.run_simulation --graph sensor

echo "=== 9. Full report (Windows-safe UTF-8) ==="
python run_full_framework.py

echo "DONE. Read results/full_report.txt and results/simulation/summary_statistics.csv"
