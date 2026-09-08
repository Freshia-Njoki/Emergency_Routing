See RUN_LOCALLY.md for the full improved pipeline.

Quick start (Git Bash, after pulling branch cursor/improve-ev-routing-framework-c48b):

```
cd "/d/MSc - Route optimisation for road traffic evasion/Routing App"
source venv/Scripts/activate
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
bash run_improved_pipeline.sh
```

Or step by step:

```
python -m src.prediction.data_preprocessing
python -m src.prediction.train_improved_gru
python -m src.routing.map_sensors_to_roads
python -m src.evaluation.run_simulation --quick
python -m src.evaluation.evaluate_framework --results-dir results/sliding
python -m src.evaluation.run_simulation
python run_full_framework.py
```
