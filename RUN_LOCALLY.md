# Improved GRU emergency-routing framework

**Final accurate results live on** `cursor/improve-ev-routing-framework-c48b` (not `main`).

Pull, run, and figure-to-caption map: `docs/FIGURE_AND_TABLE_MAP.md`.  
Obj 3–4 15-minute deck: `docs/Freshia_Njoki_Obj34_Findings_Presentation.pptx` (notes under each slide).

This branch is **not** merged into `main`. Pull it locally, run the scripts, then copy the new tables into Chapters 4–5.

## Recommendation: do **not** train both datasets as one model

METR-LA has **207** sensors and PEMS-BAY has **325**. A multivariate GRU cannot take both as a single input tensor. Chapter 3 is correct: train METR-LA for routing, and train a **separate** PEMS-BAY model only for cross-dataset MAE/RMSE (Section 4.3.4). `train_joint_per_sensor.py` exists as an optional experiment; it is **not** the routing model.

## Why the old numbers contradicted each other

Two evaluators were measuring different things:

| Script | What it actually measured | What you saw |
|---|---|---|
| `evaluate_framework.py --sliding-window` | Framework time from **GRU-predicted** costs vs baselines from **scaled** npz values treated as mph | ~78% “reduction”, identical across every delta |
| `run_simulation.py` | Ground-truth traversal, but 81% of OSM edges used a constant 30 mph, incidents were random, `T_old` never updated | ~0% vs Dijkstra, 0 replannings, ANOVA p = 1.000 |

Chapter 4 Table 4.5 (framework ~123 s vs baselines ~588 s) came from the first script. Table 4.6 (+0.17% incident) came from the second. Both cannot be true at once. **Drop the 78% / 123 s vs 588 s table.**

## What this branch changes (aligned with Chapters 1–3)

1. **Ground-truth evaluation everywhere** — Dijkstra, Static A*, Reactive A*, Oracle, and the framework are all traversed with actual future speeds (Section 3.9).
2. **Train-only StandardScaler** — matches Section 3.4.
3. **Thesis GRU** — 2×64, dropout 0.2, MSE, patience 10 (`train_improved_gru.py`).
4. **Default routing graph = METR-LA detector adjacency** (207 nodes, 100% instrumented). Downtown OSM (397 nodes / 18.6% mapped) is still available with `--graph osm`, but the sensor graph is the accurate choice for this dataset. Update Chapter 3 if you adopt it.
5. **Nowcast + GRU forecast fusion** — slot 0 of the horizon is the current snapshot; later slots are GRU. Stops peak-hour detours caused by a slightly wrong first-slot forecast.
6. **Incident persistence** — once a corridor slowdown is observed, those sensors stay slow in the predicted costs so the threshold controller can fire (Objective 3).
7. **Replan if the current path deteriorated by δ *or* a new TD-A* path is better by δ** (opportunity replan). Update Section 3.8 if you keep this.
8. **B3 is reactive A*** — one replan on the current snapshot when the incident starts; it is no longer a copy of Dijkstra.
9. **Incidents on the Dijkstra corridor**, 40% speed drop (`severity=0.60`), starting after 20% of B1 travel time.
10. **Windows cp1252-safe logging**.

## Commands to run on your machine (Git Bash)

```bash
cd "/d/MSc - Route optimisation for road traffic evasion/Routing App"
source venv/Scripts/activate

git fetch origin
git checkout cursor/improve-ev-routing-framework-c48b
git pull origin cursor/improve-ev-routing-framework-c48b

export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# Sensor adjacency (skip if data/raw/sensor_graph/adj_mx.pkl is already there)
python -c "from download_data import download_sensor_graph; download_sensor_graph()"

# 1) Re-build sequences with a train-only scaler
python -m src.prediction.data_preprocessing

# 2) Retrain the Chapter-3 GRU  (10–30 min on CPU)
python -m src.prediction.train_improved_gru

# 3) Quick smoke test (~15 OD pairs)
python -m src.evaluation.run_simulation --quick --graph sensor

# 4) Full 900 experiments (75 OD x 3 scenarios x 4 delta)
python -m src.evaluation.evaluate_framework --results-dir results/sliding --graph sensor
python -m src.evaluation.run_simulation --graph sensor

# 5) One report, UTF-8, numbers taken from the CSV (not hard-coded)
python run_full_framework.py

# 6) Optional: separate PEMS-BAY model + plots (not joint training)
python -m src.prediction.preprocess_pems_bay
python -m src.prediction.train_pems_bay
python -m src.evaluation.cross_validate
```

Or: `bash run_improved_pipeline.sh`  
PowerShell: `.\run_improved_pipeline.ps1`

## Outputs to paste into Chapter 4

- `results/full_report.txt`
- `results/simulation/simulation_results.csv`
- `results/simulation/summary_statistics.csv`
- `results/sliding/evaluation_results.csv`  (same harness as simulation — numbers will now agree)
- `results/statistical_tests.csv`
- `visualizations/obj3_delta_sensitivity.png`
- `visualizations/obj4_travel_time_reduction.png`
- `models/saved/metr_la_metrics.pkl`  (test MAE/RMSE in mph)

## Switching back to main

```bash
git checkout main
```
