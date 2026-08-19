# Pull and run the improved emergency-routing framework
#
# Branch: cursor/improve-ev-routing-framework-c48b
# Repo:   https://github.com/Freshia-Njoki/Emergency_Routing
#
# These commands are for Git Bash on Windows (your existing venv).
# Run them from:  D:\MSc - Route optimisation for road traffic evasion\Routing App

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

echo "=== 3. Re-preprocess METR-LA (train-only scaler -- fixes data leakage) ==="
python -m src.prediction.data_preprocessing

echo "=== 4. Retrain thesis GRU (2 x 64 hidden, dropout 0.2) ==="
python -m src.prediction.train_improved_gru

echo "=== 5. Optional: joint per-sensor GRU on METR-LA + PEMS-BAY ==="
# Requires pems_bay_training_data.npz (run preprocess_pems_bay.py if missing)
python -m src.prediction.train_joint_per_sensor || echo "Joint training skipped"

echo "=== 6. Remap sensors onto major roads ==="
python -m src.routing.map_sensors_to_roads

echo "=== 7. Smoke-test simulation (15 OD pairs, a few minutes) ==="
python -m src.evaluation.run_simulation --quick

echo "=== 8. Full 900-experiment evaluation (75 OD x 3 scenarios x 4 delta) ==="
python -m src.evaluation.evaluate_framework --results-dir results/sliding
python -m src.evaluation.run_simulation

echo "=== 9. Full report (Windows-safe UTF-8) ==="
python run_full_framework.py

echo "=== 10. Cross-dataset plots ==="
python -m src.evaluation.cross_validate

echo "DONE. Read results/full_report.txt and results/simulation/summary_statistics.csv"
