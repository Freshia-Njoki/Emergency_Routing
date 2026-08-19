# Thesis sweep: 18.6%, references, peers, 20k words, figures, tables, appendix

KyU in-text citations stay **APA (Author, year)**. The numbers below are a packing list only. Do **not** write `[17]` in Chapter 2.

Cut-off for “older than five years”: published **before 2021** (today is August 2026).

---

## 1. The yellow 18.6% on page 83 (Sensor coverage density study)

That bullet describes the **unused** downtown OSM map. The 900-run already used **100%** detector coverage. Do not increase 18.6% toward 100% as future work.

**GET THIS**

```
Sensor coverage density study: This study demonstrated that 18.6 percent sensor coverage constrained the framework's ability to differentiate routing paths in peak-hour conditions. A systematic study increasing sensor coverage from 18.6 percent to 50, 75, and 100 percent through simulated imputation or network densification should be conducted to identify the coverage threshold at which travel time reductions become statistically significant across all scenarios.
```

**REPLACE WITH** (past tense for what was done; “should” only for genuine future work)

```
Sparse-sensor Nairobi analogue: The reported 900 journeys used the METR-LA detector graph with 100% of edges instrumented (207 nodes, 1,515 edges). A future experiment should downsample that graph to 10 to 30% coverage and repeat the 900-run. That downsample was not conducted in this study.
```

Ctrl+F `18.6` in Word. Every hit is one of:

| Where | Action |
|---|---|
| 5.5 “increase 18.6% to 50, 75, 100%” | Replace with the paragraph above |
| 5.5 “reduce 18.6% to 10 and 5%” | Same paragraph; keep **one** sparse-sensor bullet only |
| 1.7 last sentence treating 18.6% as *this* study | `An earlier OpenStreetMap extract mapped sensors to only 18.6% of edges; that map was not used for the reported 900 journeys.` |
| 4.6.1 / 4.6.4 blaming 18.6% for peak-hour loss / “sparse-sensor was applied” | See `docs/REPLACE_46_55_CITATIONS.md` |
| Figure of red OSM edges | Remove from results (see figures below) |

Do not mute-delete 18.6% and leave “this study demonstrated that coverage constrained peak hour.”

---

## 2. References older than five years

### Keep (foundational — age is allowed)

| Paper | Why it stays |
|---|---|
| Dijkstra (1959) | B1 algorithm |
| Hart, Nilsson, and Raphael (1968) | A* |
| Dreyfus (1969) | Time-dependent shortest path / FIFO |
| Gorry and Scott Morton (1971); Keen and Scott Morton (1978) | DSS theory |
| Box and Jenkins (1976) | **One** ARIMA history mention only |
| Peffers et al. (2007); Hevner et al. (2004) if cited | DSRM |
| Delling and Wagner (2009) | TDSP chapter you actually use |
| Cho et al. (2014) | GRU |
| WHO (2015) | Eight-minute target in the problem statement |
| Li et al. (2018) | METR-LA / PEMS-BAY and DCRNN dataset paper |
| Creswell and Creswell (2018) | Research design textbook |

### Keep (2021 — treat as current enough)

Jeong et al. (2021); Zhang, Khalgui, and Li (2021); Golub et al. (2021); Chen et al. (2021); Jaballah et al. (2021).

### Remove from the list **if** you also delete every in-text cite (not foundational, not your method)

| Paper | Why drop |
|---|---|
| Geisberger et al. (2008) contraction hierarchies | You did **not** use CH |
| Goldberg and Harrelson (2005) ALT | You did **not** use ALT |
| Pohl bidirectional Dijkstra (if still listed as a live method) | Background only; one sentence in 2.2 is enough, then drop the extra cites |
| Ouyang et al. (2020) dynamic SP index | You did **not** build their index. Optional one clause in 2.5, then remove if the examiner is strict on five years |

**Mugeere et al. (2020)** is six years old but is East African EMS context. **Keep** unless the supervisor insists on a 2021+ replacement (Golub et al., 2021 and AfDB, 2022 already cover the region).

Do **not** delete Dijkstra, A*, GRU, DSRM, Li 2018, or WHO because they are old.

---

## 3. Did a peer already do this / does anyone nullify it?

**No.** Closest papers **bound** the contribution; they do not replace GRU + TD-A* + δ on 900 ground-truth METR-LA journeys.

Paste these distinctions in Chapter 2 (past tense). They match the published papers, not a paraphrase of the title.

**Werner et al. (2022)** — closest **router**. Combined live and predicted times with time-dependent A* potentials and reported large speed-ups on continental networks (SEA 2022). They did not train a GRU, they relied on preprocessing that sits poorly with a five-minute weight refresh, they targeted general navigation, and they did not sweep δ ∈ {0.05, 0.10, 0.15, 0.20} for an emergency dispatcher.

**Zhang, Khalgui, and Li (2021)** — closest **prediction-plus-routing** outside EMS. *Sensors* 21, 7330: predictive signal control and vehicle route guidance in an Internet-of-Vehicles congestion model. No emergency remaining-time controller, no METR-LA 900-run.

**Zhang, Sun, and Liu (2022)** — adaptive route planning for connected vehicles with incidents (*ISPRS IJGI*). Not this GRU–δ sweep.

**Abuaisha et al. (2025)** — closest **replanning** percentage (12–18%). That gain was on **fixed public-transport corridors** (IJCAI 2025), not unconstrained emergency paths. Same band as +16.19% is allowed; same problem is not.

**Chowdhury et al. (2023)** — *Sensors* 23, 5324. They **proposed** a UAV-assisted EV priority scheme and reported about **8%** lower response time and **12%** better incident-area clearance in simulation. They did not learn a 30-minute path with a GRU. Do not call this paper “a survey” as if that were the result.

**Hugar et al. (2025) / Sasikala et al. (2025)** — intersection / signal priority (YOLOv8 in Hugar). Not route choice. Sasikala’s ~35% (if you cite it) is a **signal** figure; do not compare it with +16.19% as if they measured the same thing.

**Abdullah et al. (2023)** — soft GRU for city congestion (*Sustainability* 15, **5949**). Prediction only.

**Jeong et al. (2021)** — highway speed GRU. Prediction only; your MAE 3.48 mph sits in their usable short-horizon band.

**Jiang and Luo (2022); Yin et al. (2022); Lan et al. (2022); Shao et al. (2022); Xu et al. (2022) if cited** — stronger spatial-temporal predictors on METR-LA. They do not route ambulances. Cite them to say the study **declined** SOTA MAE for a 40 ms loop.

**Zhang, Gao, Wang, Yiu, and Yin (2025)** — AAAI distillation. You **did not distill**. Cite only as an efficiency trend that supports a small GRU.

**GET THIS** (over-claim that makes Werner look fatal)

```
Existing studies addressed prediction and routing independently, leaving the integration challenge unresolved
```

**REPLACE WITH**

```
Prediction and routing were each studied in depth, and a few systems combined live or predicted times with time-dependent search (Werner et al., 2022; Zhang, Khalgui, & Li, 2021). What remained thin was an emergency dispatch loop that learned speeds with a GRU, routed on those costs, and exposed an empirically tested remaining-time threshold under a one-second recommendation budget.
```

---

## 4. Past tense

Chapters 1–5: what you **did** is past tense (`was trained`, `were compared`, `reduced`).

Ctrl+F and fix: `will`, `shall`, `is trained`, `will be conducted`, `this study aims` (except purpose can stay “was to”), `are presented` in results (`were presented`).

**Leave future tense only in 5.5** (`should downsample`). Do not write 5.5 as if the downsample already happened.

Chapter 5: **no new citations** (KyU).

---

## 5. 20,000 words

GitHub DOCX body was about **14,600 words**. KyU minimum is **20,000**. You are short by about **5,400 words** until the INSERT blocks are pasted.

| Paste | Where | Approx. words |
|---|---|---|
| INSERT 1 | Table 3.1 RQ1 cell | 40 |
| INSERT 2 | End of 3.6 | 900 |
| INSERT 3 | End of 3.4 | 500 |
| INSERT 4 | Replace 4.3–4.6 numbers | 2,200 (replaces wrong 78%/0.17% text) |
| INSERT 5 | 5.1–5.2 | 700 |
| INSERT 6 | Chapter 2 (eight papers, accurate peers) | 1,200 |
| INSERT 7 | 3.8–3.9 | 800 |
| INSERT 8 | Limitations 18.6% vs 100% | 400 |
| INSERT 9 | New 4.6.5 | 2,400 |
| INSERT 10 | 3.2 DSRM | 900 |

Full text: `docs/THESIS_COMMENTS_AND_EXPANSION.md` Section D. After pasting, Word → Review → Word Count. Target 20,200–21,000. Do not pad by repeating sentences.

If still short: one extra paragraph per Chapter 2 theme using Jiang and Luo (2022), Yin et al. (2022), or Chowdhury et al. (2023) **as published** (UAV 8%/12%, not “a survey”).

---

## 6. Figures — by file name

Thesis captions stay Figure 1.1, 2.1, 4.1… The **file** you paste is what matters.

### KEEP / REPLACE (paste these)

| Thesis caption (typical) | File to insert | Status |
|---|---|---|
| Figure 1.1 congestion / WHO illustration | existing INRIX/WHO graphic | **KEEP** (must stay labelled *illustrative*) |
| Figure 2.1 conceptual framework | existing loop diagram | **KEEP** (do not draw 10–30% coverage as already tested) |
| Figure 3.x artefact / DSRM flow | existing architecture | **KEEP** if it shows GRU + TD-A* + δ, two datasets, one routing graph |
| Figure 4.1 GRU training | `visualizations/improved_gru_training.png` | **REPLACE** old 17-epoch plot |
| Figure 4.2 sample predictions | `visualizations/improved_gru_predictions.png` | **REPLACE** old `gru_predictions.png` |
| Figure 4.4 δ sensitivity | `results/simulation/figures/fig3_delta_sensitivity.png` | **REPLACE** |
| Figure 4.5 travel times (s) | `results/simulation/figures/fig1_travel_time_comparison.png` | **REPLACE** |
| Figure 4.6 % vs baselines | `results/simulation/figures/fig2_reduction_by_scenario.png` | **REPLACE** |
| Figure 4.7 latency | `results/simulation/figures/fig4_computational_performance.png` | **REPLACE** |

Prefer `fig3` over `visualizations/obj3_delta_sensitivity.png` (fig3 has all three scenarios). Prefer `fig2` over `obj4_travel_time_reduction.png` (fig2 has error bars).

### REMOVE (do not paste; wrong graph or old run)

| File | Why |
|---|---|
| `visualizations/sensor_coverage_map.png` | 18.6% OSM. **Not** the 900-run |
| `visualizations/gru_training_history.png` | Old 17-epoch / MAE 3.42 |
| `visualizations/gru_predictions.png` | Same old checkpoint |
| `visualizations/prediction_comparison_both_datasets.png` | Broken / scaled MAE |
| `visualizations/training_history_comparison.png` | Old mix |
| `visualizations/traffic_heatmap.png` | Exploratory, not a result |
| `visualizations/traffic_patterns.png` | Exploratory |
| `results/figures/fig1`–`fig5` (no `simulation` in the path) | Older copy |
| `results/simulation/figures/fig5_summary_poster.png` | Poster only; too dense for the thesis |

If Figure 4.3 is the red-edge OSM coverage map, **remove it** or recaption: *Unused downtown OpenStreetMap extract; not the graph for Tables 4.5–4.8.* Do not add a new 18.6% map.

If the laptop retrain overwrote `improved_gru_training.png` with a 24-epoch curve, **do not** replace Figure 4.1 with that PNG unless MAE in Table 4.3 also becomes 3.46 **and** the 900-run is redone. Use the GitHub 27-epoch figure.

---

## 7. Tables — accurate cells (from `results/full_report.txt`)

**Yes, if you paste these. No, if Word still has 123 s, +0.17%, 0 replans, 17 epochs, 3.42, 0.315 ms, 397 nodes, 18.6% as the result graph.**

**Table 3.1** RQ1 cell: `RQ1: Gaps in EV routing, prediction, and time-dependent pathfinding`

**Table 4.2** architecture: 2 × 64 GRU, dropout 0.2. Note: two models (207 and 325), not one joint network.

**Table 4.3 METR-LA**

| Item | Value |
|---|---|
| Epochs | 27 |
| Train loss | 0.3847 |
| Best val loss | 0.4335 |
| Test MAE | 3.48 mph |
| Test RMSE | 6.04 mph |
| Scaler | StandardScaler, train split only |

**Table 4.4 graph:** 207 nodes, 1,515 edges, 100% instrumented. **Not** 397 / 1,024 / 190 (18.6%).

**Table 4.4c PEMS-BAY:** 79 epochs, MAE 2.38 mph, RMSE 4.49 mph.

**Table 4.7 (δ), N = 225 per row**

| δ | vs Dijkstra | Replans / journey | TD-A* ms |
|---|---|---|---|
| 0.05 | +5.726% | 0.45 | 0.370 |
| 0.10 | +5.748% | 0.44 | 0.367 |
| 0.15 | +5.726% | 0.43 | 0.368 |
| 0.20 | +5.767% | 0.39 | 0.373 |

ANOVA *F* = 0.001, *p* = 1.00. Recommend **δ = 0.20**.

**Table 4.5 seconds (N = 300 per row)**

| Scenario | B1 | B2 | B3 | B4 | Framework |
|---|---|---|---|---|---|
| Peak | 513.1 | 552.5 | 513.1 | 499.5 | 506.3 |
| Off-peak | 403.5 | 405.2 | 403.5 | 403.1 | 403.4 |
| Incident | 727.5 | 723.2 | 603.7 | 580.5 | 598.9 |

**Table 4.6 vs Dijkstra**

| Scenario | Mean | *t* | *p* |
|---|---|---|---|
| Peak | +1.03% | 3.81 | .0002 |
| Off-peak | +0.01% | 0.12 | .90 |
| Incident | +16.19% | 26.43 | < .001 |

Overall: vs B1 **+5.74%**, vs B2 **+7.39%**, vs B3 **+0.61%**, vs B4 **−1.69%**.

**Table 4.8:** TD-A* 0.37 ms; GRU 39.3 ms; combined ~40 ms. Not 0.315 / 69.1 / 3,175×.

**Table 5.1:** copy 4.6–4.8. No 18.6% as the cause.

---

## 8. Full appendix (paste)

KyU: appendix after references or as specified in the format PDF. Past tense. No new Chapter 5 citations; file names in the appendix are allowed.

### Appendix A: Implementation artefacts

The framework was implemented in Python 3. The files below produced the defended evaluation: METR-LA detector graph, train-only scaler, and ground-truth traversal of 900 journeys.

**A.1 Prediction**

`src/prediction/data_preprocessing.py` built METR-LA sequences with a 12-step (60-minute) input and a 6-step (30-minute) horizon. A StandardScaler was fitted on the training split only. `src/prediction/train_improved_gru.py` trained the routing GRU (two layers, 64 units, dropout 0.2, mean squared error, Adam, early stopping). The defended checkpoint was `models/saved/gru_improved_best.keras` (27 epochs, test MAE 3.48 mph). `src/prediction/preprocess_pems_bay.py` and `src/prediction/train_pems_bay.py` trained a **separate** PEMS-BAY GRU (test MAE 2.38 mph) used only as a second-city prediction check. `src/prediction/gru_interface.py` loaded the scaler and returned inverse-scaled miles per hour.

**A.2 Routing and control**

`src/routing/graph_builder.py` built the 207-node, 1,515-edge detector graph from the DCRNN adjacency (`data/raw/sensor_graph/adj_mx.npz`). `src/routing/travel_times.py` converted speeds to edge times. `src/routing/td_astar.py` ran time-dependent A*. `src/controller/adaptive_controller.py` applied the remaining-time threshold δ.

**A.3 Evaluation**

`src/evaluation/simulation_core.py` walked every method on actual future speeds, placed a 40% corridor slowdown on the planned path in the incident scenario, and fused nowcast with GRU forecasts. `src/evaluation/run_simulation.py` ran 75 origin–destination pairs × 3 scenarios × 4 δ values (900 journeys). `src/evaluation/analyse_results.py` wrote Tables 4.5–4.8 and Figures 4.4–4.7. `run_full_framework.py` wrote `results/full_report.txt`. `run_improved_pipeline.sh` (and `run_improved_pipeline.ps1`) were the end-to-end entry points.

**A.4 Files that were not the headline 900-run**

`src/evaluation/evaluate_framework.py` is the older sliding-window evaluator; reported travel-time tables came from `run_simulation.py`. `src/routing/download_road_network.py` and `src/routing/map_sensors_to_roads.py` supported the unused downtown OpenStreetMap mode. `src/prediction/train_gru_model.py` was an earlier training script.

### Appendix B: Defended metrics (verbatim source)

The numbers in Chapters 4 and 5 were taken from `results/full_report.txt` on branch `cursor/improve-ev-routing-framework-c48b`:

- METR-LA: 27 epochs; MAE 3.48 mph; RMSE 6.04 mph.
- PEMS-BAY: 79 epochs; MAE 2.38 mph; RMSE 4.49 mph.
- Graph: 207 nodes; 1,515 edges; 100.0% instrumented.
- δ = 0.05, 0.10, 0.15, 0.20 → +5.726%, +5.748%, +5.726%, +5.767% vs Dijkstra; ANOVA *F* = 0.001, *p* = 1.00.
- Overall vs B1 +5.741%; vs B2 +7.390%; vs B3 +0.606%; vs B4 −1.694%.
- Incident +16.19% (*t* = 26.43, *p* < .001); peak +1.03% (*t* = 3.81, *p* = .0002); off-peak +0.01% (*p* = .90).
- TD-A* 0.369 ms; GRU 39.3 ms; combined ~39.7 ms.

### Appendix C: Controller tests

`tests/test_framework_logic.py` checked remaining-time (not original full-trip) triggering, reactive-replan acceptance, nowcast fusion, and adjacency loading. Those tests did not replace the 900-run.

---

## 9. References (numbered packing list — paste into Word as APA, A–Z)

Hanging indent. Match every in-text cite. Delete list entries you do not cite. **In-text stays (Author, year), not [n].**

1. Abdullah, S. M., Periyasamy, M., Kamaludeen, N. A., Towfek, S. K., Marappan, R., Kidambi Raju, S., Alharbi, A. H., & Khafaga, D. S. (2023). Optimizing traffic flow in smart cities: Soft GRU-based recurrent neural networks for enhanced congestion prediction using deep learning. *Sustainability, 15*(7), 5949. https://doi.org/10.3390/su15075949

2. Abuaisha, A., Shen, B., Harabor, D., Stuckey, P., & Wallace, M. (2025). Dynamic replanning for improved public transport routing. In *Proceedings of the International Joint Conference on Artificial Intelligence*. https://www.ijcai.org/proceedings/2025/937

3. African Development Bank. (2022). *African economic outlook 2022*. AfDB.

4. Benarmas, A., & Bey, M. (2024). A deep learning-based framework for road traffic prediction. *The Journal of Supercomputing, 80*, 7337–7357. https://doi.org/10.1007/s11227-023-05718-x

5. Binshaflout, A., & Ahmad, B. (2023). Graph neural networks for traffic pattern recognition: An overview. *IEEE Access, 11*, 14890–15005.

6. Boeing, G. (2025). Modeling and analyzing urban networks and amenities with OSMnx. *Geographical Analysis*. https://doi.org/10.1111/gean.70009

7. Chen, D., Li, L., Wang, Y., & Zhou, X. (2021). Online route planning over time-dependent road networks. In *Proceedings of the 37th IEEE International Conference on Data Engineering* (pp. 1152–1163).

8. Cho, K., van Merriënboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., & Bengio, Y. (2014). Learning phrase representations using RNN encoder–decoder for statistical machine translation. In *Proceedings of EMNLP* (pp. 1724–1734).

9. Chowdhury, A., Kaisar, S., Khoda, M. E., Naha, R., Khoshkholghi, M. A., & Aiash, M. (2023). IoT-based emergency vehicle services in intelligent transportation system. *Sensors, 23*(11), 5324. https://doi.org/10.3390/s23115324

10. Creswell, J. W., & Creswell, J. D. (2018). *Research design* (5th ed.). SAGE.

11. Delling, D., & Wagner, D. (2009). Time-dependent route planning. In *Robust and online large-scale optimization* (pp. 207–230). Springer.

12. Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik, 1*, 269–271.

13. Dreyfus, S. E. (1969). An appraisal of some shortest-path algorithms. *Operations Research, 17*(3), 395–412.

14. Golub, A., Stevens, M., Klopp, J. M., & Martin, E. (2021). Addressing public transit challenges in Sub-Saharan African cities. *Transport Policy, 105*, 62–72.

15. Gong, Z., et al. (2023). Querying shortest path on large time-dependent road networks with shortcuts. In *IEEE ICDE*.

16. Gorry, G. A., & Scott Morton, M. S. (1971). A framework for management information systems. *Sloan Management Review, 13*(1), 55–70.

17. Hagberg, A. A., Schult, D. A., & Swart, P. J. (2024). *NetworkX* documentation. https://networkx.org

18. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. *IEEE Transactions on Systems Science and Cybernetics, 4*(2), 100–107.

19. Hugar, S. M., et al. (2025). Real-time adaptive traffic management system for emergency vehicle prioritisation. In *IEEE CNC*.

20. Ikram, T., Sultana, T., Nawaz, M., & Hassan, M. F. (2025). Digital twin assisted real-time emergency vehicle navigation. *International Journal of Parallel, Emergent and Distributed Systems*.

21. INRIX. (2024). *INRIX 2024 global traffic scorecard*.

22. Jaballah, R., et al. (2021). The time-dependent shortest path and vehicle routing problem. *INFOR, 59*(3), 386–413.

23. Jeong, M.-H., Lee, T.-Y., Jeon, S.-B., & Youm, M. (2021). Highway speed prediction using gated recurrent unit neural networks. *Applied Sciences, 11*(7), 3059. https://doi.org/10.3390/app11073059

24. Jiang, W., & Luo, J. (2022). Graph neural network for traffic forecasting: A survey. *Expert Systems with Applications, 207*, 117921. https://doi.org/10.1016/j.eswa.2022.117921

25. Keen, P. G. W., & Scott Morton, M. S. (1978). *Decision support systems: An organizational perspective*. Addison-Wesley.

26. Lan, S., Ma, Y., Huang, W., Wang, W., Yang, H., & Li, P. (2022). DSTAGNN: Dynamic spatial-temporal aware graph neural network for traffic flow forecasting. In *Proceedings of the 39th International Conference on Machine Learning* (pp. 11906–11917). PMLR.

27. Li, Y., Yu, R., Shahabi, C., & Liu, Y. (2018). Diffusion convolutional recurrent neural network: Data-driven traffic forecasting. In *Proceedings of ICLR*.

28. Ma, C., Dai, G., & Zhou, J. (2023). A novel STFSA-CNN-GRU hybrid model for short-term traffic speed prediction. *IEEE Transactions on Intelligent Transportation Systems, 24*(9), 9660–9673.

29. Mugeere, A., Munene, J., & Nsubuga, E. (2020). Emergency response systems in East African cities. *African Studies Quarterly, 19*(3–4), 35–52.

30. Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A design science research methodology for information systems research. *Journal of Management Information Systems, 24*(3), 45–77.

31. Qi, P., et al. (2025). A review of dynamic traffic flow prediction methods for global energy-efficient route planning. *Sensors*.

32. Reis, D., Odhiambo, L., Wachira, B., Kamau, N., & Temu, A. (2025). Leveraging innovative technology and health data to enhance access to emergency care in Kenya. *Oxford Open Digital Health, 3*(1).

33. Sahayaraj, K. K. A., Chodnekar, A., & Mishra, A. (2024). Optimizing urban traffic flow prediction. In *Smart data intelligence* (pp. 381–391). Springer.

34. Sasikala, N., et al. (2025). Emergency traffic prioritization system with priority-based dynamic route optimization. In *IEEE CONIT*.

35. Shao, Z., Zhang, Z., Wang, F., & Xu, Y. (2022). Pre-training enhanced spatial-temporal graph neural network for multivariate time series forecasting. In *Proceedings of the 28th ACM SIGKDD Conference on Knowledge Discovery and Data Mining* (pp. 1567–1577). https://doi.org/10.1145/3534678.3539396

36. Werner, N., Buchhold, M., Storandt, S., & Wagner, D. (2022). Combining predicted and live traffic with time-dependent A* potentials. In *Proceedings of SEA 2022*. https://doi.org/10.4230/LIPIcs.SEA.2022.18

37. World Health Organisation. (2015). *Health emergency and disaster risk management framework*. WHO Press.

38. Yildirim, U. M., & Catay, B. (2022). An enhanced network-consistent travel speed generation scheme. *IEEE Transactions on Intelligent Transportation Systems*.

39. Yin, X., Wu, G., Wei, J., Shen, Y., Qi, H., & Yin, B. (2022). Deep learning on traffic prediction: Methods, analysis, and future directions. *IEEE Transactions on Intelligent Transportation Systems, 23*(6), 4927–4943. https://doi.org/10.1109/TITS.2021.3054840

40. Zhang, L., Khalgui, M., & Li, Z. (2021). Predictive intelligent transportation: Alleviating traffic congestion in the Internet of Vehicles. *Sensors, 21*(21), 7330. https://doi.org/10.3390/s21217330

41. Zhang, Q., Gao, X., Wang, H., Yiu, S. M., & Yin, H. (2025). Efficient traffic prediction through spatio-temporal distillation. *Proceedings of the AAAI Conference on Artificial Intelligence, 39*(1), 1093–1101. https://doi.org/10.1609/aaai.v39i1.32096

42. Zhang, Z., Sun, Y., & Liu, Q. (2022). An adaptive route planning method of connected vehicles for improving the transport efficiency. *ISPRS International Journal of Geo-Information, 11*(1), 39.

43. Zohir, H. M., et al. (2025). Advancements in accident-aware traffic management. *Scientific Reports, 15*, 2847.

**Add if cited in your Word file:** Box and Jenkins (1976); Hevner et al. (2004); any Xu et al. (2022) METR-LA GNN you actually discuss.

**Delete if unused after Ctrl+F:** Geisberger et al. (2008); Goldberg and Harrelson (2005); Ouyang et al. (2020).

**Fixes:** Abdullah article **5949** (not 5716), author **Alharbi** (not Alhussan). Distillation in-text: **Zhang, Gao, et al. (2025)** (not Wang et al.). Two Zhangs: Gao 2025 vs Khalgui 2021.

Chapter 5: do not add these cites into the chapter prose; they belong in Chapter 2 and this list.
