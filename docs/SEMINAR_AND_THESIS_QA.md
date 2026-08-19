# Seminar, local run, 18.6%, appendix, APA, comments

Work in Word on the thesis. **GET THIS / REPLACE WITH** is for the document. **For you only** is not.

The seminar file is still `docs/Freshia_Njoki_Obj34_Findings_Presentation.pptx` (updated in place, 12 slides, 15 minutes).

---

## 1. Slide 11 — what changed

The old slide 11 listed internal mistakes (“do not say”, GitHub branch, retired numbers). That is not a seminar slide.

**New slide 11** is Limitations and further research: US freeways; 100% detector graph; PEMS-BAY is prediction-only; sparse 10–30% not run; next work starts from **100% → 10–30%**.

Foundation is now in the same deck: problem (slide 2), purpose / RQs / objectives (slide 3), framework (slide 4), data and 900-run design (slide 5).

---

## 2. Local `bash run_improved_pipeline.sh` — did you do the right thing?

**Branch, preprocess, and architecture: yes.**

You were on `cursor/improve-ev-routing-framework-c48b`. METR-LA loaded as **(34272, 207)**. Train-only scaler. Windows **23973 / 5123 / 5125**. GRU **2 × 64, dropout 0.2**. That matches Chapter 3.

**Retrain: you created a new checkpoint. Do not mix it with the GitHub 900-run tables.**

| | GitHub / thesis (keep this) | Your laptop retrain |
|---|---|---|
| Early stop | 27 epochs | 24 epochs; best weights from epoch **14** |
| Test MAE | **3.48 mph** | **3.46 mph** |
| Test RMSE | 6.04 | 6.04 |
| Routing tables | 900-run in `results/full_report.txt` | **Did not run** (graph pickle crashed) |

**Simulation: not completed.** `adj_mx.pkl` is a Python 2 pickle. Git on Windows often stores it with CRLF, which raises `UnpicklingError: the STRING opcode argument must be quoted`. So you do **not** yet have a new 900-run.

**What to do on the laptop (do not retrain again):**

```bash
git pull origin cursor/improve-ev-routing-framework-c48b

# Keep the GitHub GRU if you still have it; if you overwrote it, either
# restore from git or accept that a new 900-run is required before changing MAE.

export PYTHONUTF8=1
python -m src.evaluation.run_simulation --graph sensor
python run_full_framework.py
```

After `git pull`, adjacency loads from `data/raw/sensor_graph/adj_mx.npz` (Python 3), with a CRLF-safe pickle fallback.

**Thesis numbers stay 3.48 / 27 epochs / +16.19% until a full 900-run with the new weights finishes and you replace every table.** Do not write 3.46 in Chapter 4 while routing tables still come from the 3.48 model.

---

## 3. Section 5.5 — the purple 18.6% → 10 and 5% sentence

**Do not only delete 18.6%.** Replace it. Silent delete leaves “this study demonstrated that coverage constrained peak hour” with no graph attached.

**GET THIS**

```
Nairobi sparse-sensor deployment study: This study demonstrated that 18.6 percent sensor coverage constrained route differentiation in peak-hour conditions. A systematic study progressively reducing sensor coverage from 18.6 percent to 10 and 5 percent of road edges should be conducted to simulate the infrastructure density of Nairobi's road network, identifying the minimum viable sensor density at which the framework maintains statistically significant routing improvements over reactive baselines.
```

**REPLACE WITH**

```
Sparse-sensor Nairobi analogue: A future experiment should downsample the present 100% detector graph to 10 to 30% coverage and repeat the 900-run. That experiment was not part of this study.
```

**GET THIS** (duplicate grey bullet, if both remain)

```
Sparse-sensor sensitivity analysis: A systematic study reducing
```

**REPLACE WITH**  
Delete the duplicate. Keep **one** sparse-sensor bullet.

**GET THIS** (the bullet that *increases* 18.6% toward 100% — this is the yellow highlight on page 83)

```
Sensor coverage density study: This study demonstrated that 18.6 percent sensor coverage constrained the framework's ability to differentiate routing paths in peak-hour conditions. A systematic study increasing sensor coverage from 18.6 percent to 50, 75, and 100 percent
```

**REPLACE WITH**

```
The 100% detector-coverage experiment is already the reported 900-run. No further increase from 18.6% is required for this thesis.
```

**For you only.** 18.6% = 190 / 1,024 edges on the **unused** downtown OpenStreetMap extract. The defended 900-run is **207 nodes, 1,515 edges, 100% instrumented**. Reducing 18.6% to 5% would shrink a map you are not defending. 10–30% is the Nairobi analogue on the **detector** graph, and you have **not** run it — so it belongs in 5.5, not in Chapter 4 as a completed result.

Same replacement belongs in **1.7** and **4.6.4** if those sentences still treat 18.6% as a property of the reported tables (`docs/REPLACE_46_55_CITATIONS.md`).

---

## 4. Can remaining Word balloons just be deleted?

**No — not until the highlighted sentence is already correct.**

| Balloon type | Direction |
|---|---|
| Old number (`+0.17%`, `123 s`, `0.315 ms`, `17 epochs`, `3.42`, `δ = 0.10` as default, `397-node` as the 900-run) | **Replace** the sentence, then delete the balloon. |
| `18.6%` | **Replace** (unused OSM vs 100% detector graph). Do not mute-delete. |
| `Meaning?` / jargon | Add one plain sentence (δ vs α; MAE; remaining time), then delete. |
| `Include PEMS-BAY?` | One sentence: second GRU for prediction; routing is METR-LA only. Then delete. |
| `Remove?` on Dijkstra, Cho, Li 2018, Peffers, WHO | **Keep** the cite; delete only the balloon. |
| `Perfect for Nairobi?` / WHO 8 minutes | Keep the limitation; do not convert +16% into CBD minutes. Then delete the balloon. |

After replacements, strip balloons before printing (Review → Delete all comments). The edit sheets are `docs/CHAPTER1_EDIT_GUIDE.md`, `CHAPTER23_EDIT_GUIDE.md`, `CHAPTER45_EDIT_GUIDE.md`, `REPLACE_46_55_CITATIONS.md`.

The GitHub **DOCX is not fully corrected** unless you have pasted those GET/REPLACE blocks. Code and `full_report.txt` are the source of truth; Word still needs your paste.

---

## 5. Figures and tables — are they accurate now?

**Accurate if you paste KEEP files from the improved branch. Inaccurate if old PNGs or old table cells remain.**

**KEEP** (from `docs/FIGURE_AND_TABLE_MAP.md`)

| File | Use |
|---|---|
| `visualizations/improved_gru_training.png` | Fig. 4.1 — 27 epochs, train-only scaler |
| `visualizations/improved_gru_predictions.png` | Optional Fig. 4.2 |
| `results/simulation/figures/fig3_delta_sensitivity.png` | Obj. 3 / Fig. 4.4 |
| `results/simulation/figures/fig1_travel_time_comparison.png` | Fig. 4.5 |
| `results/simulation/figures/fig2_reduction_by_scenario.png` | Fig. 4.6 |
| `results/simulation/figures/fig4_computational_performance.png` | Fig. 4.7 |
| `results/full_report.txt` | Every table number |

**IGNORE** (do not paste even if prettier)

- `sensor_coverage_map.png` (18.6% OSM)
- `gru_training_history.png` / `gru_predictions.png` (old 3.42 / 17 epochs)
- `prediction_comparison_both_datasets.png` (broken / scaled MAE)
- `results/figures/` without `simulation`

**Table cells that must match `full_report.txt`**

| Table | Defended values |
|---|---|
| 4.3 | 27 epochs, MAE 3.48, RMSE 6.04, GRU 39.3 ms |
| 4.4 | 207 nodes, 1,515 edges, 100% mapped |
| 4.4c | METR-LA 3.48 / 6.04; PEMS-BAY 79 epochs, 2.38 / 4.49 |
| 4.5 | Incident 599 s vs 728 s; peak 506 vs 513; off-peak ≈ 403 vs 403 |
| 4.6 | +16.19% (*p* < .001); +1.03% (*p* = .0002); +0.01% (n.s.); overall +5.74% |
| 4.7 | Recommend δ = 0.20; ANOVA *F* ≈ 0.001, *p* = 1.00; replans not 0 |
| 4.8 | TD-A* 0.37 ms, GRU 39.3 ms, combined ~40 ms |
| 5.1 | Same as 4.6–4.8 |

If your laptop overwrote `improved_gru_training.png` during the new 24-epoch train, **do not replace Fig. 4.1 with that PNG** unless you also replace MAE with 3.46 *and* rerun the 900 journeys. Prefer the GitHub figure that matches 27 epochs / 3.48.

---

## 6. Appendix A — source files (paste this table)

KyU: short description, past tense, no new citations in Chapter 5; the appendix may name files.

**GET THIS** any appendix list that headlines `evaluate_framework.py` as the 900-run, or that lists `la_road_network.pkl` as the result graph.

**REPLACE WITH**

### Appendix A: Implementation artefacts

The framework was implemented in Python. The files below correspond to the defended evaluation (METR-LA detector graph; ground-truth traversal).

| File | Role |
|---|---|
| `src/prediction/data_preprocessing.py` | Built METR-LA sequences (12-step input, 6-step horizon) and the train-only StandardScaler. |
| `src/prediction/train_improved_gru.py` | Trained the routing GRU (two layers, 64 units, dropout 0.2, MSE). Checkpoint `models/saved/gru_improved_best.keras`. |
| `src/prediction/preprocess_pems_bay.py` | Built the separate PEMS-BAY sequences. |
| `src/prediction/train_pems_bay.py` | Trained the second-city GRU used only for prediction metrics (MAE 2.38 mph). |
| `src/prediction/gru_interface.py` | Loaded the scaler and returned inverse-scaled miles-per-hour forecasts. |
| `src/routing/graph_builder.py` | Built the 207-node, 1,515-edge detector graph from the DCRNN adjacency. |
| `src/routing/travel_times.py` | Converted speeds to edge travel times and collapsed parallel OSM edges when that mode was used. |
| `src/routing/td_astar.py` | Time-dependent A* search. |
| `src/controller/adaptive_controller.py` | Remaining-time threshold δ (accept a new path if remaining time grows by more than δ). |
| `src/evaluation/simulation_core.py` | Ground-truth walk, path-targeted incidents, nowcast fusion, four baselines. |
| `src/evaluation/run_simulation.py` | 900-run harness (75 pairs × 3 scenarios × 4 δ). |
| `src/evaluation/analyse_results.py` | Tables, *t*-tests, ANOVA, and figures `fig1`–`fig4`. |
| `run_full_framework.py` | Wrote `results/full_report.txt` from the simulation CSV. |
| `run_improved_pipeline.sh` / `run_improved_pipeline.ps1` | End-to-end preprocess, train, and evaluate entry points. |

**Not the headline 900-run.** `src/evaluation/evaluate_framework.py` is the older sliding-window evaluator; reported travel-time tables come from `run_simulation.py`. `src/routing/download_road_network.py` and `map_sensors_to_roads.py` support the unused downtown OSM mode. `src/prediction/train_gru_model.py` is the earlier training script; the defended METR-LA model is `train_improved_gru.py`.

Optional Appendix B: `results/full_report.txt` (verbatim metrics). Optional Appendix C: `tests/test_framework_logic.py` (controller and remaining-time tests).

---

## 7. APA references — eight papers, alphabetical

Merge into the existing list (Dijkstra, Cho, Li, Werner, …). APA 7, hanging indent, alphabetical by first author. Two Zhangs: use `Zhang, Gao, et al. (2025)` vs `Zhang, Khalgui, and Li (2021)` in text.

**GET THIS** Abdullah `5716` / `Alhussan`; distillation `Wang et al. (2025)` / arXiv line.

**REPLACE WITH** (paste these eight; keep your other correct entries)

```
Abdullah, S. M., Periyasamy, M., Kamaludeen, N. A., Towfek, S. K., Marappan, R., Kidambi Raju, S., Alharbi, A. H., & Khafaga, D. S. (2023). Optimizing traffic flow in smart cities: Soft GRU-based recurrent neural networks for enhanced congestion prediction using deep learning. Sustainability, 15(7), 5949. https://doi.org/10.3390/su15075949

Chowdhury, A., Kaisar, S., Khoda, M. E., Naha, R., Khoshkholghi, M. A., & Aiash, M. (2023). IoT-based emergency vehicle services in intelligent transportation system. Sensors, 23(11), 5324. https://doi.org/10.3390/s23115324

Jiang, W., & Luo, J. (2022). Graph neural network for traffic forecasting: A survey. Expert Systems with Applications, 207, 117921. https://doi.org/10.1016/j.eswa.2022.117921

Lan, S., Ma, Y., Huang, W., Wang, W., Yang, H., & Li, P. (2022). DSTAGNN: Dynamic spatial-temporal aware graph neural network for traffic flow forecasting. In Proceedings of the 39th International Conference on Machine Learning (pp. 11906–11917). PMLR.

Shao, Z., Zhang, Z., Wang, F., & Xu, Y. (2022). Pre-training enhanced spatial-temporal graph neural network for multivariate time series forecasting. In Proceedings of the 28th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (pp. 1567–1577). https://doi.org/10.1145/3534678.3539396

Yin, X., Wu, G., Wei, J., Shen, Y., Qi, H., & Yin, B. (2022). Deep learning on traffic prediction: Methods, analysis, and future directions. IEEE Transactions on Intelligent Transportation Systems, 23(6), 4927–4943. https://doi.org/10.1109/TITS.2021.3054840

Zhang, Q., Gao, X., Wang, H., Yiu, S. M., & Yin, H. (2025). Efficient traffic prediction through spatio-temporal distillation. Proceedings of the AAAI Conference on Artificial Intelligence, 39(1), 1093–1101. https://doi.org/10.1609/aaai.v39i1.32096

Zhang, L., Khalgui, M., & Li, Z. (2021). Predictive intelligent transportation: Alleviating traffic congestion in the Internet of Vehicles. Sensors, 21(21), 7330. https://doi.org/10.3390/s21217330
```

**In-text (APA 7, three or more authors → et al. from the first cite)**

- (Abdullah et al., 2023)
- (Chowdhury et al., 2023)
- (Jiang & Luo, 2022)
- (Lan et al., 2022)
- (Shao et al., 2022)
- (Yin et al., 2022)
- (Zhang, Gao, et al., 2025)  ← distillation paper; you did **not** distill
- (Zhang, Khalgui, & Li, 2021) first cite; later (Zhang, Khalgui, et al., 2021)

Chapter 5: **no new citations** (KyU). These belong in Chapter 2 and the reference list only.

If Word still has `su15075716` or `Alhussan`, that is a different MDPI article — use **5949** / **Alharbi**.

---

## 8. Is the thesis “okay”?

**The science on this branch is okay. The Word file is okay only after you paste the replacements.**

Already true in `results/full_report.txt` and the article draft `docs/research_article_v0.3.md`: 3.48 / 2.38; 34,272; 207 / 1,515 / 100%; +16.19% incidents; +5.74% overall; ~1 incident replan; δ = 0.20; ~40 ms.

Still your job in Word:

1. Abstract and Chapters 4–5 numbers (see `REPLACE_46_55_CITATIONS.md`).
2. 1.7 / 4.6.4 / 5.5 graph wording (18.6% unused OSM).
3. Appendix file list above.
4. Reference list alphabetical, Abdullah 5949, Zhang, Gao, et al. (2025).
5. Word count toward 20,000 if the body is still ~14,500 (`THESIS_COMMENTS_AND_EXPANSION.md` INSERT blocks).
6. Delete balloons **after** the text is correct.

Ctrl+F before print: `0.17` `123.` `588` `0.315` `69.1` `3,175` `17 epochs` `3.42` `34,254` `MinMax` `δ = 0.10` as **recommended** default `397-node` as the result graph `18.6` as the 900-run.
