# Pull and run the improved emergency-routing framework
# Branch: cursor/improve-ev-routing-framework-c48b
#
# Git Bash (recommended, matches your previous workflow):
#   cd "/d/MSc - Route optimisation for road traffic evasion/Routing App"
#   bash run_improved_pipeline.sh
#
# Do NOT train one multivariate GRU on both datasets at once.

$ErrorActionPreference = "Stop"
git fetch origin
git checkout cursor/improve-ev-routing-framework-c48b
git pull origin cursor/improve-ev-routing-framework-c48b

& .\venv\Scripts\Activate.ps1
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

python -c "from download_data import download_sensor_graph; download_sensor_graph()"
python -m src.prediction.data_preprocessing
python -m src.prediction.train_improved_gru
python -m src.evaluation.run_simulation --quick --graph sensor
python -m src.evaluation.evaluate_framework --results-dir results/sliding --graph sensor
python -m src.evaluation.run_simulation --graph sensor
python run_full_framework.py
