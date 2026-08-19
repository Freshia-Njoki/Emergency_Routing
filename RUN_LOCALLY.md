# Improved GRU emergency-routing framework

Branch: `cursor/improve-ev-routing-framework-c48b`  
This branch is **not** merged into `main`. Pull it locally, run the scripts, then copy the new tables into Chapters 4–5.

## Why the old numbers contradicted each other

Two evaluators were measuring different things:

| Script | What it actually measured | What you saw |
|---|---|---|
| `evaluate_framework.py --sliding-window` | Framework time from **GRU-predicted** costs vs baselines from **scaled** npz values treated as mph | ~78% “reduction”, identical across every delta |
| `run_simulation.py` | Ground-truth traversal, but 81% of edges used a constant 30 mph, incidents were random, `T_old` never updated | ~0% vs Dijkstra, 0 replannings, ANOVA p = 1.000 |

Chapter 4 Table 4.5 (framework ~123 s vs baselines ~588 s) came from the first script. Table 4.6 (+0.17% incident) came from the second. Both cannot be true at once.

Downtown journeys also finish in **under five minutes**, so a 5-minute incident slot never arrived during the trip. Replanning could not fire.

## What this branch changes (aligned with Chapters 1–3)

1. **Ground-truth evaluation everywhere** — Dijkstra, Static A*, Reactive A*, Oracle, and the framework are all traversed with actual future speeds (Section 3.9).
2. **Train-only StandardScaler** — matches Section 3.4; stops scaled values being used as mph.
3. **Thesis GRU** — `train_improved_gru.py` is now the specified 2×64, dropout 0.2, MSE, patience 10. The old 3-layer/128 network contradicted Section 3.6.
4. **Major-road sensor mapping + IDW interpolation** — unmapped edges inherit nearby detector speeds instead of fake 30 mph free-flow (this is what caused peak-hour *detours onto ‘empty’ streets* in Section 4.6.1).
5. **Incidents on the Dijkstra path**, starting after 25% of B1 travel time, not after 300 s and not on random sensors.
6. **Threshold uses remaining time** `T_old` on the current path (Section 3.8). The previous controller compared remaining time to the *original full-journey* time, so `(T_new − T_old)/T_old` was always negative and never replanned.
7. **Windows cp1252-safe logging** — the `UnicodeEncodeError` on `→` and `≈` is gone (`PYTHONUTF8=1` plus ASCII fallbacks).
8. **Joint training of both datasets** — a multivariate net cannot have 207 and 325 inputs. `train_joint_per_sensor.py` trains one shared per-detector GRU on METR-LA **and** PEMS-BAY together. Routing still uses the METR-LA multivariate model (Section 3.6). PEMS-BAY remains the cross-dataset check (Section 4.3.4).

## Commands to run on your machine (Git Bash)

```bash
cd "/d/MSc - Route optimisation for road traffic evasion/Routing App"
source venv/Scripts/activate

git fetch origin
git checkout cursor/improve-ev-routing-framework-c48b
git pull origin cursor/improve-ev-routing-framework-c48b

export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# 1) Re-build sequences with a train-only scaler (overwrites training_data.npz + scaler.pkl)
python -m src.prediction.data_preprocessing

# 2) Retrain the Chapter-3 GRU  (10–30 min on CPU)
python -m src.prediction.train_improved_gru

# 3) Optional: train one GRU on METR-LA + PEMS-BAY sensors together
python -m src.prediction.train_joint_per_sensor

# 4) Map sensors onto motorway/primary edges
python -m src.routing.map_sensors_to_roads

# 5) Quick smoke test (~15 OD pairs)
python -m src.evaluation.run_simulation --quick

# 6) Full 900 experiments (75 OD x 3 scenarios x 4 delta) — 10–20 min
python -m src.evaluation.evaluate_framework --results-dir results/sliding
python -m src.evaluation.run_simulation

# 7) One report, UTF-8, numbers taken from the CSV (not hard-coded)
python run_full_framework.py

# 8) METR-LA vs PEMS-BAY plots
python -m src.evaluation.cross_validate
```

Or run the whole sequence:

```bash
bash run_improved_pipeline.sh
```

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
- `models/saved/joint_metrics.pkl`    (if you ran joint training)

## Switching back to main

```bash
git checkout main
```
