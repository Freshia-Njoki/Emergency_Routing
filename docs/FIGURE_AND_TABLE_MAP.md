# Figures and tables — keep vs replace

**Final results branch:** `cursor/improve-ev-routing-framework-c48b`  
**Not** `main` (main still has the old evaluator).

Seminar PPT (same file, 12 slides): `docs/Freshia_Njoki_Obj34_Findings_Presentation.pptx`.  
Local run, 18.6%, APA, appendix: `docs/SEMINAR_AND_THESIS_QA.md`.

After you pull that branch, use **only** the files listed under KEEP. Ignore the rest even if they look prettier.

---

## KEEP (paste these)

| File | Goes in | Caption |
|---|---|---|
| `visualizations/improved_gru_training.png` | Thesis Fig 4.1; article Fig 2 | GRU training history on METR-LA (27 epochs, train-only StandardScaler). |
| `visualizations/improved_gru_predictions.png` | Thesis Fig 4.2 (optional) | Sample METR-LA test predictions vs actual (mph). Predictions are smoother than raw loops; MAE 3.48 mph is the defended metric, not this plot. |
| `visualizations/obj3_delta_sensitivity.png` **or** `results/simulation/figures/fig3_delta_sensitivity.png` | Thesis Fig 4.4; article Fig 5; PPT slide 5 | Prefer **fig3** (has peak / off-peak / incident). Threshold δ vs reduction and replans. |
| `results/simulation/figures/fig1_travel_time_comparison.png` | Thesis Fig 4.5; article Fig 3; PPT slide 7 | Mean travel time (s): framework vs B1–B4. |
| `results/simulation/figures/fig2_reduction_by_scenario.png` | Thesis Fig 4.6; article Fig 4; PPT slide 8 | Reduction (%) vs Dijkstra / static A* / reactive A*. |
| `results/simulation/figures/fig4_computational_performance.png` | Thesis Fig 4.7; article Fig 6; PPT slide 9 | TD-A* ~0.37 ms; GRU ~39 ms. |
| `results/simulation/figures/fig5_summary_poster.png` | PPT backup / poster only | Four-panel summary. Too dense for the article. |
| `results/full_report.txt` | Source of every table number | Not a figure. |

`obj4_travel_time_reduction.png` is a simpler bar chart of the same % as fig2. Use **fig2** in the document (it has error bars). Use obj4 only if fig2 is too wide.

---

## IGNORE (do not paste; old or broken)

| File | Why |
|---|---|
| `visualizations/gru_training_history.png` | Old 17-epoch run (MAE 3.42). |
| `visualizations/gru_predictions.png` | Same old checkpoint. |
| `visualizations/sensor_coverage_map.png` | Downtown OSM, 18.6% red edges. **Not** the 900-run graph. |
| `visualizations/prediction_comparison_both_datasets.png` | METR-LA says “Not trained yet”; PEMS MAE 0.18 is **scaled**, not 2.38 mph. |
| `visualizations/traffic_heatmap.png` | Exploratory; not a result. |
| `visualizations/traffic_patterns.png` | Exploratory. |
| `visualizations/training_history_comparison.png` | Likely old METR vs Bay mix. |
| `results/figures/fig1`–`fig5` | Older copy. Prefer `results/simulation/figures/`. |
| `results/sliding/figures/*` | Duplicate harness; use `simulation/figures` so numbers match `full_report.txt`. |

You do **not** need to delete them from Git. Just do not put them in the thesis, article, or PPT.

---

## Thesis tables — replace contents (improved run)

| Table | Action |
|---|---|
| 4.2 | Keep architecture. Note two models (207 and 325), not one. File `gru_improved_best.keras`. |
| 4.3 | Epochs **27**, MAE **3.48**, RMSE **6.04**, GRU **39.3 ms**. Not 17 / 3.42 / 6.14 / 69.1. |
| 4.4 | **207 nodes, 1,515 edges, 100% mapped.** Not 397 / 1,024 / 190 (18.6%). |
| 4.4c | METR-LA column: 27 epochs, 3.48 / 6.04. PEMS: 79, 2.38 / 4.49. |
| 4.7 | See `full_report.txt` δ rows. Replans **not** 0. Recommend **δ = 0.20**. ANOVA *F* ≈ 0.001, *p* = 1.00. |
| 4.5 | Seconds: peak 506 vs 513; off-peak 403 vs 403; incident **599 vs 728**. Not 123 vs 588. |
| 4.6 | +1.03% (*p* = .0002); +0.01% (n.s.); **+16.19%** (*p* < .001). N = 300 per row. |
| 4.8 | TD-A* **0.37 ms**, GRU **39.3 ms**, combined **~40 ms**. Not 0.315 / 69.1 / 3,175×. |
| 5.1 | Same numbers as 4.6–4.8. δ = 0.20. No 18.6% as the cause of the defending tables. |

Ctrl+F in the thesis Word file: `0.315` `3.42` `34,254` `123.09` `588.3` `+0.17` `17 epochs` `69.1` `3,175` `δ = 0.10` as the **recommended** default.

Replace `34,254` with **`34,272`** everywhere.

---

## Research article v0.3 — what to change for submission

v0.3 **already has** 3.48, 2.38, +16.19%, 207 nodes, 34,272, δ = 0.20, ~40 ms.

Still do this before submit:

1. Paste the KEEP figures above (the markdown has no embedded images).
2. Do **not** add the 18.6% OSM map. Methods now say the detector graph only.
3. Do **not** add 0.315, 3.42, 123 s, or 0.17% as results.
4. Abdullah article number **5949**; distillation paper **Zhang, Gao, Wang, Yiu, and Yin (2025)**.
5. Gap 1 in §2.3 is the short version (already in the file).
6. Journal template + keywords + ethics statement as the venue requires.

---

## 4.6 and 5.5 in one screen (improved results only)

**4.6 — say this:**

When the planned road was jammed, the framework cut Dijkstra time by **16.19%** (about 599 s vs 728 s), with about **one** replan. Peak hour: **+1.03%**. Off-peak: **no gain** (empty roads). δ did not change travel time, so **δ = 0.20**. Combined wait **~40 ms**.

**4.6 — do not say:** 18.6% caused peak-hour loss; zero replans; +0.17%; 123 s.

**5.5 — say this:** Next study: downsample the **100%** detector graph to 10–30% (Nairobi analogue). Also: PEMS-BAY **routing** 900-run; field trial.

**5.5 — do not say:** cut coverage from 18.6% down to 5%. That is shrinking the unused OSM map.

---

## Pull and run (Windows Git Bash)

```bash
cd "/d/MSc - Route optimisation for road traffic evasion/Routing App"

git fetch origin
git checkout cursor/improve-ev-routing-framework-c48b
git pull origin cursor/improve-ev-routing-framework-c48b

export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# If the venv exists:
source venv/Scripts/activate
pip install -r requirements.txt

# Skip retrain if models/saved/gru_improved_best.keras (or .h5) already exists.
# If adj_mx.pkl failed with STRING opcode / quoted, pull this branch first
# (adj_mx.npz is Windows-safe). Do not mix a new MAE with the old 900-run tables.
python -m src.evaluation.run_simulation --graph sensor
python run_full_framework.py
```

Full retrain (optional, 10–40 min CPU; overwrites the 3.48 mph checkpoint):

```bash
bash run_improved_pipeline.sh
```

PowerShell: `.\run_improved_pipeline.ps1`

Open after the run:

- `results/full_report.txt`
- `results/simulation/figures/fig1_travel_time_comparison.png` … `fig4_computational_performance.png`
- `docs/Freshia_Njoki_Obj34_Findings_Presentation.pptx`
