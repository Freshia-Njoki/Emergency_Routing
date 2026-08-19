# GRU-Based Predictive Route Optimisation Framework for Emergency Vehicle Navigation: Integrating Short-Term Traffic Forecasting with Time-Dependent A* and Adaptive Replanning

Freshia Njoki Macharia¹*, Gilbert Langat², Stephen Mageto²

¹Department of Computer Science and Informatics, Kirinyaga University, Kerugoya, Kenya  
²School of Pure and Applied Sciences, Kirinyaga University, Kerugoya, Kenya  

*Corresponding author: fnjokimacharia@gmail.com | Co-authors: glangat@kyu.ac.ke; snyakiba@kyu.ac.ke

## Abstract

Emergency vehicle navigation in congested cities fails when a route that is shortest at dispatch becomes slow minutes later. This article reports a design-science artefact that closes that gap: a dispatcher decision-support framework that joins a Gated Recurrent Unit (GRU) speed predictor, Time-Dependent A* (TD-A*) routing, and a remaining-time threshold controller. Two identical two-layer GRUs (64 hidden units, dropout 0.2) were trained separately on METR-LA (207 sensors) and PEMS-BAY (325 sensors) with chronological 70/15/15 splits and a train-only scaler. METR-LA test mean absolute error was 3.48 mph (RMSE 6.04 mph); PEMS-BAY test MAE was 2.38 mph (RMSE 4.49 mph). Routing used the METR-LA detector graph (207 nodes, 1,515 fully instrumented edges). Nine hundred matched journeys (75 origin–destination pairs × three traffic scenarios × four δ values) were traversed with ground-truth future speeds. Versus Dijkstra with current speeds, mean travel-time reduction was +5.74% overall and **+16.19% in incident conditions** (*p* < .001), with +1.03% in peak hour (*p* = .0002) and a non-significant +0.01% off-peak. The framework sat 1.69% below an oracle with perfect future knowledge and 0.61% above a reactive A* baseline. Combined GRU plus routing latency was about 40 ms against a 1,000 ms dispatch cap. All four thresholds δ ∈ {0.05, 0.10, 0.15, 0.20} were tested; travel time was insensitive to δ (ANOVA *F* ≈ 0.001, *p* = 1.00) because corridor incidents exceeded 20% remaining-time increase, so δ = 0.20 is recommended as the operational default. The contribution is an integrated, latency-feasible emergency routing loop, not a new state-of-the-art spatial-temporal predictor.

**Keywords:** emergency vehicle routing; GRU; time-dependent A*; traffic prediction; adaptive replanning; design science

## 1. Introduction

### 1.1 Background of the Study

Intelligent transportation systems sit at the junction of computer science, urban operations, and public safety. Within that field, routing an ambulance, fire appliance, or police unit is among the highest-stakes uses of a shortest-path algorithm: each extra minute at a cardiac-arrest scene is associated with about a 10% rise in mortality (Zhang et al., 2022). Congestion still adds 30–50% to ambulance times in peak hours in many metropolitan areas, and commercial tools such as Google Maps and Waze remain largely snapshot-based (Binshaflout & Ahmad, 2023; Qi et al., 2025).

East African capitals illustrate the same failure at larger delay. African Development Bank assessments have placed emergency response well beyond recommended thresholds (AfDB, 2022). In Nairobi, peak-hour ambulance times of 18–25 minutes sit far above the World Health Organisation eight-minute target for life-threatening calls (WHO, 2015; INRIX, 2024). Mixed traffic, including matatus and motorcycles, is poorly captured by freeway-trained models (Golub et al., 2021; Mugeere et al., 2020). Recent Kenyan deployments show that better dispatch routing can cut delays dramatically when the organisational setting allows it (Reis et al., 2025), which makes a computationally light, predictive decision-support design a practical research target rather than a purely theoretical one.

### 1.2 Statement of the Problem

The ideal dispatch condition is a route that remains near-optimal as traffic evolves over the next 15–30 minutes, with a new recommendation issued only when remaining travel time has truly deteriorated, and with an answer returned well under one second. The present condition is a static or current-only path that ages as soon as a queue forms downstream. Machine-learning traffic prediction and time-dependent shortest paths exist as separate literatures (Li et al., 2018; Jaballah et al., 2021; Werner et al., 2022). What has been missing is a single emergency-oriented artefact that (a) learns short-horizon speeds, (b) routes on time-varying costs, (c) exposes a human-calibrated replanning threshold, and (d) reports travel time, latency, and update frequency together (Qi et al., 2025; Zohir et al., 2025).

### 1.3 Objective of the Study

The study designed, implemented, and evaluated an Intelligent Route Optimisation Framework for emergency vehicle navigation by integrating GRU forecasting with TD-A* and a threshold-based controller.

Specific objectives were: (1) to review literature and produce a structured gap analysis; (2) to develop the three-component recommendation system; (3) to determine an empirical replanning threshold δ ∈ {5%, 10%, 15%, 20%}; and (4) to evaluate travel-time reduction, computational latency, and update frequency against Dijkstra, static A*, reactive A*, and an oracle.

### 1.4 Justification and Scope

A design-science stance is appropriate because the object of inquiry is an artefact that must be built before its utility can be measured (Peffers et al., 2007). The knowledge sought is prescriptive: which configuration of predictor, router, and controller is accurate enough, fast enough, and stable enough for a dispatcher who retains final authority.

The study is delimited to 15–30 minute speed forecasts, simulation on METR-LA (routing) and PEMS-BAY (cross-dataset GRU checks), a single vehicle, and travel-time minimisation only. Live Nairobi sensors, multi-vehicle coordination, and signal pre-emption were out of scope. METR-LA and PEMS-BAY are United States freeway benchmarks; they do not reproduce matatu dynamics, and that limit is stated rather than hidden.

## 2. Literature Review and Conceptual Framework

### 2.1 Theoretical Framework

Three theories bound the artefact. **Time-dependent shortest path (TDSP)** theory (Dreyfus, 1969; Delling & Wagner, 2009) treats edge cost as a function of entry time. With the first-in-first-out (FIFO) property, later departure cannot produce earlier arrival, and label-setting search remains correct. **GRU sequence modelling** (Cho et al., 2014) captures daily and weekly speed cycles with fewer parameters than long short-term memory (LSTM), which matters when inference must share a one-second dispatch window (Jeong et al., 2021; Benarmas & Bey, 2024). **Decision support systems (DSS)** theory (Gorry & Scott Morton, 1971; Keen & Scott Morton, 1978) requires that recommendations be timely, sparse enough to avoid alert fatigue, and subordinate to the human dispatcher.

### 2.2 Review of Related Empirical Studies

**Classical pathfinding.** Dijkstra (1959) and A* (Hart et al., 1968) remain the operational standard in many computer-aided dispatch stacks (Hagberg et al., 2024). Contraction hierarchies and ALT accelerate static queries but assume weights that do not jump every five minutes (Geisberger et al., 2008; Goldberg & Harrelson, 2005). Gong et al. (2023) and Chen et al. (2021) show that fully online time-dependent planning is still demanding; they do not supply an emergency prediction module.

**Traffic prediction.** Li et al. (2018) released METR-LA and PEMS-BAY and the diffusion convolutional recurrent network (DCRNN). Subsequent surveys document a race among graph neural networks and transformers (Jiang & Luo, 2022; Yin et al., 2022). Hybrid GNN–GRU models can cut MAPE substantially (Sahayaraj et al., 2024; Ma et al., 2023) at higher inference cost. Distillation and “soft GRU” variants aim to keep accuracy while shrinking compute (Zhang, Gao, Wang, Yiu, & Yin, 2025; Abdullah et al., 2023). For a dispatch loop, Jeong et al. (2021) remains the relevant trade-off: stacked GRU is accurate enough on 15–30 minute highway speeds and cheap enough to call repeatedly.

**Time-dependent routing and integration.** Jaballah et al. (2021) and Yildirim and Catay (2022) operationalise time-varying speeds on real networks. Werner et al. (2022) combine live and predicted times inside TD-A* and obtain large speedups on continental graphs. That paper is the closest routing precedent. It does not train a GRU, it relies on preprocessing that sits uneasily with five-minute weight refresh, and it targets general navigation rather than emergency dispatch with a δ-controller. Zhang et al. (2022) couple incident awareness with adaptive planning for connected vehicles; Zhang, Khalgui and Li (2021) integrate prediction and routing in an Internet-of-Vehicles setting without an emergency threshold policy. Dynamic index maintenance on changing graphs (Ouyang et al., 2020) explains why a lightweight urban TD-A* without heavy preprocessing is attractive when weights update often.

**Emergency vehicle services.** Chowdhury et al. (2023) proposed a UAV-assisted emergency-vehicle priority scheme and reported about 8% lower response time and 12% better incident-area clearance in simulation; the literature they surveyed still concentrated on detection, green waves, and static routes rather than a learned 15–30 minute path. Hugar et al. (2025) and Sasikala et al. (2025) improve intersection priority; those gains are not interchangeable with predictive path choice. Abuaisha et al. (2025) report 12–18% reliability gains from replanning on **fixed public-transport corridors**. Ikram et al. (2025) explore digital-twin emergency navigation. Zohir et al. (2025) still list proactive predictive routing as an open EV direction. None of these papers evaluate GRU + TD-A* + δ on METR-LA with ground-truth traversal.

**African urban context.** Golub et al. (2021) and Mugeere et al. (2020) document institutional and mixed-traffic constraints that make a lightweight, open implementation more relevant than a continental preprocessor.

### 2.3 Identification of Research Gaps

Four gaps follow. Gap 1: prediction and time-dependent routing are often studied apart; a few systems combine live or predicted times with search, but not as an emergency GRU, time-dependent A*, and remaining-time threshold under a one-second dispatch budget (Qi et al., 2025; Werner et al., 2022; Chowdhury et al., 2023). Gap 2: threshold policies for mid-journey recommendations are not systematically swept over {5, 10, 15, 20}%. Gap 3: MAE and route time are usually reported in different papers, so prediction error never appears as travel-time regret. Gap 4: Sub-Saharan mixed-traffic deployment remains untested on local sensors; this study can only offer a transferable method, not Nairobi measurements.

### 2.4 Conceptual Framework

Independent variables are GRU depth and width, TD-A* heuristic, δ, and dataset. Dependent variables are journey time, gap to oracle, latency, and replans per trip. Moderators — congestion regime, time of day, path length, and sensor coverage — affect **all three** components, not only the controller. Component 1 maps a 60-minute window to a 30-minute speed forecast. Component 2 computes a time-dependent path. Component 3 issues a new path when remaining time on the current path rises by more than δ, or when a newly computed path is better by δ. Figure 1 (thesis Figure 2.1) shows that loop.

## 3. Methodology

### 3.1 Research Design

The study followed the six Design Science Research Methodology activities (Peffers et al., 2007): problem identification, objective definition, artefact design, demonstration on public benchmarks, evaluation against four baselines, and communication through an open repository (https://github.com/Freshia-Njoki/Emergency_Routing). Pragmatism justified simulation measurement rather than a claim of universal optimality (Creswell & Creswell, 2018). The whole account is in the past tense: the experiments were run.

### 3.2 Dataset Description and Preprocessing

METR-LA contains 207 loop detectors and 34,272 five-minute speed frames (March–June 2012). PEMS-BAY contains 325 detectors and 52,116 frames (January–May 2017, about five months). Cells at or below zero were treated as missing and imputed with the sensor mean. Splits were chronological: 70% train, 15% validation, 15% test. A **StandardScaler was fitted on the METR-LA training partition only** and applied to METR-LA validation and test windows (`src/prediction/data_preprocessing.py`). PEMS-BAY used its **own** scaler on its **own** training split (`src/prediction/preprocess_pems_bay.py`). Sequences were 12 steps in and six steps out.

A multivariate GRU cannot take 207 and 325 sensors in one tensor. The study therefore trained **two models**, not one joint city model. Routing used METR-LA because that is the graph on which vehicles were simulated. PEMS-BAY answered whether the same architecture still predicted speeds in another region.

### 3.3 GRU Traffic Prediction Module

The network was two stacked GRU layers of 64 units, dropout 0.2 after each, a dense projection, and a reshape to (6, N_sensors), trained with Adam (learning rate 0.001), mean squared error, batch size 64, early stopping patience 10, and learning-rate reduction on plateau (`src/prediction/train_improved_gru.py`, `train_pems_bay.py`). Inverse scaling recovered miles per hour. GRU was adopted from published LSTM comparisons (Jeong et al., 2021) rather than a fresh LSTM bake-off, because the dispatch constraint is latency.

### 3.4 Time-Dependent A* and Baselines

State was (vertex, arrival time). The priority key was *f* = *g* + *h*, with *h* equal to haversine distance over free-flow speed (admissible). Edge times came from the current forecast slot and were clipped to at least one second to protect FIFO. If the search found no path, the result was treated as infeasible: the dispatcher would be told that the modelled graph had no route, rather than inventing one. The 900 origin–destination pairs were sampled to be reachable (minimum eight hops and at least 300 s free-flow time so that at least one five-minute slot could elapse).

Training looked like this in ordinary language. Speeds arrived as a table: each row a clock time, each column a detector. Broken zeros were filled. The table was cut in time order so Monday never leaked into Friday’s test exam. The training slice taught a ruler (the scaler) what “typical” meant. Windows of one hour were cut like a moving photograph album. The GRU practised guessing the next half hour until validation error stopped improving for ten epochs, then the best weights were frozen. PEMS-BAY repeated the same school with a different city and its own ruler (`gru_bay_best.h5`). Code tags: `TrafficDataPreprocessor.prepare_data`, `build_model`, `EarlyStopping(patience=10)`.

Four baselines were required to avoid Dijkstra-only bias. **B1** Dijkstra / current snapshot is operational practice. **B2** static A* on historical mean tests whether an average day is enough. **B3** reactive A* replans once from the latest snapshot when an incident appears, with no GRU horizon. **B4** oracle A* uses actual future speeds and is an unreachable ceiling.

### 3.5 Adaptive Controller and Sliding Window

Let *T_old* be remaining time on the current path under the costs that issued that path, and *T_new* the remaining time on the same path under the latest fused forecast. A replan was accepted if (*T_new* − *T_old*) / *T_old* > δ, or if a new TD-A* path improved remaining time by more than δ. **δ = 0.05 is a 5% remaining-time threshold; it is not the statistical significance level.** Statistical tests used α = 0.05. The two 0.05 quantities must not be conflated.

A sliding window is not a desktop setting. At each five-minute advance the oldest speed vector is dropped and the newest observation is appended, so the GRU always sees the last 60 minutes. Observed incident speeds were persisted on the affected sensors so the controller could see a corridor slowdown (nowcast–forecast fusion in `src/evaluation/simulation_core.py`).

### 3.6 Road Graph

The routing graph was the METR-LA detector adjacency (207 nodes, 1,515 edges, every edge instrumented). Downtown OpenStreetMap extracts were not used for the reported journeys.

### 3.7 Evaluation Protocol and Analysis

Scenarios followed Chapter 3 of the parent thesis: peak hour (lowest 25% of test-window mean speed), off-peak (highest 25%), and incident (40% speed drop on Dijkstra-corridor sensors after 20% of planned B1 time). Design: 75 pairs × 3 × 4 = 900. Every method was **driven** with actual future speeds. Descriptive means, standard deviations and medians, one-sample *t*-tests versus zero reduction, and one-way ANOVA on δ used α = 0.05. Shapiro–Wilk statistics were reported; many reduction distributions were non-normal, so significance was interpreted cautiously and alongside medians. Random seed 42 was fixed.

## 4. Results and Discussion

### 4.1 Objective 1: Gap Analysis

Thirty-seven papers across five themes — classical pathfinding, TDSP, traffic prediction, prediction–routing integration, and emergency routing — confirmed Gap 1 as the primary hole. Werner et al. (2022) is the nearest integrator and still leaves ML prediction, five-minute refresh, emergency δ control, and matched ground-truth EV journeys unaddressed. Qi et al. (2025) independently named the prediction–planning disconnect.

### 4.2 Objective 2: Prediction and Artefact

**Table 1.** GRU configuration and test metrics (train-only scaler).

| Item | METR-LA | PEMS-BAY |
|---|---|---|
| Sensors | 207 | 325 |
| Epochs (early stop) | 27 | 79 |
| Final train loss | 0.3847 | 0.0024 |
| Best validation loss | 0.4335 | 0.0027 |
| Test MAE | **3.48 mph** | **2.38 mph** |
| Test RMSE | 6.04 mph | 4.49 mph |

METR-LA MAE lies in the 3.1–4.2 mph band reported for comparable GRUs (Jeong et al., 2021) and is worse than DCRNN-class spatial models by design: those models were not selected for a 40 ms budget (Jiang & Luo, 2022; Li et al., 2018). PEMS-BAY error is lower because Bay Area freeway speeds are smoother, not because the Los Angeles model “failed.” The MAE gap of 1.10 mph is inside a 2.0 mph generalisation tolerance. Predicted METR-LA speeds on a held-out window ranged from about 32 to 70 mph with mean 63 mph, which is physically plausible.

The implemented pipeline (`run_simulation.py`, `simulation_core.py`) loaded `gru_improved_best.keras`, inverse-scaled to mph, and routed on the sensor graph with 100% edge coverage.

### 4.3 Objective 3: Threshold Policy

**Table 2.** Mean reduction versus Dijkstra and replans per journey by δ (*N* = 225 journeys per row: 75 OD × 3 scenarios).

| δ | Mean vs B1 (%) | Replans / journey | TD-A* latency (ms) |
|---|---|---|---|
| 0.05 | +5.726 | 0.45 | 0.370 |
| 0.10 | +5.748 | 0.44 | 0.367 |
| 0.15 | +5.726 | 0.43 | 0.368 |
| 0.20 | **+5.767** | **0.39** | 0.373 |

ANOVA: *F* = 0.001, *p* = 1.00. Unlike earlier drafts that reported **zero** replans, incident trips now replan about **once** (mean 1.03). Travel time does not move with δ because a 40% corridor drop exceeds every tested threshold. DSS theory then prefers the **highest** δ that still catches incidents: **0.20**, which also slightly reduces peak-hour fidgeting. The earlier recommendation δ = 0.10 was a planned default, not an empirical optimum from a working controller.

### 4.4 Objective 4: Travel Time and Latency

**Table 3.** Framework versus baselines (900 runs). Positive percentages mean the framework was faster.

| Comparison | Mean | SD | Median |
|---|---|---|---|
| vs B1 Dijkstra / current | **+5.74%** | 10.01% | 0.19% |
| vs B2 static A* | +7.39% | 12.08% | 0.70% |
| vs B3 reactive A* | +0.61% | 3.54% | 0.00% |
| vs B4 oracle | −1.69% | 5.64% | 0.00% |

**Table 4.** Reduction versus Dijkstra by scenario (pooled over δ; *N* = 300 per scenario).

| Scenario | Mean vs B1 | vs Oracle | Replans | *t* | *p* | Sig. at α = .05 |
|---|---|---|---|---|---|---|
| Incident | **+16.19%** | −3.80% | 1.03 | 26.43 | < .001 | Yes |
| Peak hour | +1.03% | −1.23% | 0.20 | 3.81 | .0002 | Yes |
| Off-peak | +0.01% | −0.05% | 0.04 | 0.12 | .90 | No |

Mean incident journey times were about 599 s for the framework versus 727 s for Dijkstra. Peak-hour means were about 506 s versus 513 s. Off-peak means were essentially tied near 403 s. TD-A* latency averaged **0.37 ms**; GRU inference **39.3 ms**; combined **~40 ms**, far below 1,000 ms.

### 4.5 Interpretation of Key Results

In one sentence: **when a road on the planned path is slowed, the system notices and offers another path, saving about one-sixth of Dijkstra time; when roads are already empty, prediction cannot invent a shortcut.**

Incident +16% sits in the same band as Abuaisha et al.’s 12–18% replanning gains, despite a different domain (unconstrained EV paths versus fixed transit). It does not match Sasikala et al.’s 35%, which came from signal priority, not TDSP. Peak +1% is small but statistically detectable: looking 15–30 minutes ahead is only slightly better than “now” when congestion is network-wide. Off-peak zero is a successful sanity check, not a failed model. The −1.69% oracle gap is required if B4 is honest. The +0.61% versus reactive A* is the residual value of the GRU horizon after a snapshot replan has already seen the incident.

Latency results exceed the DSS requirement by more than an order of magnitude. That, not a large travel-time claim in every scenario, is the computational contribution.

### 4.6 Integration with Literature and Implications

Werner et al. (2022) remain valuable and are **not** withdrawn: they show TD-A* can be fast; this artefact shows a **learned** five-minute predictor plus a **dispatcher threshold** can be fast **and** reduce incident time without continental preprocessing. Zhang et al. (2022) share adaptive planning; they do not report this GRU–δ sweep on METR-LA. Chowdhury et al. (2023) treated EV delay as an ITS problem and filled it with UAV-guided signal priority, not with GRU path choice. Jiang and Luo (2022) and Yin et al. (2022) explain why a reviewer might demand a GNN: the answer is the 40 ms combined budget and Jeong-style evidence that short-horizon GRU error is already usable as edge cost.

For Kenyan authorities the implication is infrastructural: a method of this type needs detector or probe speeds at a few-minute cadence. The numerical +16% is **not** a promise that Nairobi ambulances will shed 16% of 18–25 minutes until local data exist.

Figures to embed at submission (branch `cursor/improve-ev-routing-framework-c48b`): conceptual loop as Figure 1; `visualizations/improved_gru_training.png`; `results/simulation/figures/fig1_travel_time_comparison.png`; `fig2_reduction_by_scenario.png`; `fig3_delta_sensitivity.png`; `fig4_computational_performance.png`. Do not embed the old OSM coverage map or the 17-epoch training plots.

## 5. Conclusion, Limitations and Future Work

### 5.1 Summary of Main Findings

The study built a three-component emergency routing DSS. Separate GRUs on METR-LA and PEMS-BAY achieved 3.48 mph and 2.38 mph MAE. On 900 ground-truth METR-LA journeys the framework reduced Dijkstra time by 5.74% on average and **16.19% under corridor incidents**, with significant but small peak-hour gain, no off-peak gain, sub-second latency, and a working controller (about one replan per incident). δ in {5–20}% did not change travel time; **δ = 0.20** is the recommended default.

### 5.2 Limitations

METR-LA/PEMS-BAY are freeway, not matatu, streams. Routing tables use the Los Angeles detector graph, not a Nairobi street extract. PEMS-BAY was not given a parallel 900-journey routing campaign. Shapiro–Wilk tests often rejected normality; *t*-tests are reported as in the thesis protocol and should be read with medians. Infeasible (disconnected) graphs were excluded by OD sampling rather than stress-tested as a user-interface mode.

### 5.3 Future Research Directions

Immediate work is a PEMS-BAY routing graph with the same 900-protocol; sparse-sensor downsampling of the 100% detector graph to 10–30% to mimic Nairobi; field trials with dispatchers; and multi-vehicle coordination. High-volatility closures that fully disconnect the graph should return an explicit “no feasible path” message to the human operator.

## References

Abdullah, S. M., Periyasamy, M., Kamaludeen, N. A., Towfek, S. K., Marappan, R., Kidambi Raju, S., Alharbi, A. H., & Khafaga, D. S. (2023). Optimizing traffic flow in smart cities: Soft GRU-based recurrent neural networks for enhanced congestion prediction using deep learning. *Sustainability, 15*(7), 5949. https://doi.org/10.3390/su15075949

Abuaisha, A., Shen, B., Harabor, D., Stuckey, P., & Wallace, M. (2025). Dynamic replanning for improved public transport routing. *Proceedings of the International Joint Conference on Artificial Intelligence (IJCAI 2025)*. https://www.ijcai.org/proceedings/2025/937

African Development Bank. (2022). *African economic outlook 2022*. AfDB.

Benarmas, A., & Bey, M. (2024). A deep learning-based framework for road traffic prediction. *The Journal of Supercomputing, 80*, 7337–7357. https://doi.org/10.1007/s11227-023-05718-x

Binshaflout, A., & Ahmad, B. (2023). Graph neural networks for traffic pattern recognition: An overview. *IEEE Access, 11*, 14890–15005.

Boeing, G. (2025). Modeling and analyzing urban networks and amenities with OSMnx. *Geographical Analysis*. https://doi.org/10.1111/gean.70009

Chen, D., Li, L., Wang, Y., & Zhou, X. (2021). Online route planning over time-dependent road networks. *Proceedings of the 37th IEEE ICDE*, 1152–1163.

Cho, K., van Merriënboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., & Bengio, Y. (2014). Learning phrase representations using RNN encoder–decoder for statistical machine translation. *Proceedings of EMNLP*, 1724–1734.

Chowdhury, A., Kaisar, S., Khoda, M. E., Naha, R., Khoshkholghi, M. A., & Aiash, M. (2023). IoT-based emergency vehicle services in intelligent transportation system. *Sensors, 23*(11), 5324. https://doi.org/10.3390/s23115324

Creswell, J. W., & Creswell, J. D. (2018). *Research design* (5th ed.). SAGE.

Delling, D., & Wagner, D. (2009). Time-dependent route planning. In *Robust and online large-scale optimization* (pp. 207–230). Springer.

Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik, 1*, 269–271.

Dreyfus, S. E. (1969). An appraisal of some shortest-path algorithms. *Operations Research, 17*(3), 395–412.

Geisberger, R., Sanders, P., Schultes, D., & Delling, D. (2008). Contraction hierarchies: Faster and simpler hierarchical routing in road networks. In *Experimental algorithms* (pp. 319–333). Springer.

Goldberg, A. V., & Harrelson, C. (2005). Computing the shortest path: A* search meets graph theory. *Proceedings of SODA*, 156–165.

Golub, A., Stevens, M., Klopp, J. M., & Martin, E. (2021). Addressing public transit challenges in Sub-Saharan African cities. *Transport Policy, 105*, 62–72.

Gong, Z., et al. (2023). Querying shortest path on large time-dependent road networks with shortcuts. *IEEE ICDE*.

Gorry, G. A., & Scott Morton, M. S. (1971). A framework for management information systems. *Sloan Management Review, 13*(1), 55–70.

Hagberg, A. A., Schult, D. A., & Swart, P. J. (2024). *NetworkX* 3.5 documentation. https://networkx.org

Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. *IEEE Transactions on Systems Science and Cybernetics, 4*(2), 100–107.

Hugar, S. M., et al. (2025). Real-time adaptive traffic management system for emergency vehicle prioritisation. *IEEE CNC*.

Ikram, T., Sultana, T., Nawaz, M., & Hassan, M. F. (2025). Digital twin assisted real-time emergency vehicle navigation. *International Journal of Parallel, Emergent and Distributed Systems*.

INRIX. (2024). *INRIX 2024 global traffic scorecard*.

Jaballah, R., et al. (2021). The time-dependent shortest path and vehicle routing problem. *INFOR, 59*(3), 386–413.

Jeong, M.-H., Lee, T.-Y., Jeon, S.-B., & Youm, M. (2021). Highway speed prediction using gated recurrent unit neural networks. *Applied Sciences, 11*(7), 3059. https://doi.org/10.3390/app11073059

Jiang, W., & Luo, J. (2022). Graph neural network for traffic forecasting: A survey. *Expert Systems with Applications, 207*, 117921. https://doi.org/10.1016/j.eswa.2022.117921

Keen, P. G. W., & Scott Morton, M. S. (1978). *Decision support systems: An organizational perspective*. Addison-Wesley.

Lan, S., Ma, Y., Huang, W., Wang, W., Yang, H., & Li, P. (2022). DSTAGNN: Dynamic spatial-temporal aware graph neural network for traffic flow forecasting. *Proceedings of ICML*.

Li, Y., Yu, R., Shahabi, C., & Liu, Y. (2018). Diffusion convolutional recurrent neural network: Data-driven traffic forecasting. *Proceedings of ICLR*.

Ma, C., Dai, G., & Zhou, J. (2023). A novel STFSA-CNN-GRU hybrid model for short-term traffic speed prediction. *IEEE Transactions on Intelligent Transportation Systems, 24*(9), 9660–9673.

Mugeere, A., Munene, J., & Nsubuga, E. (2020). Emergency response systems in East African cities. *African Studies Quarterly, 19*(3–4), 35–52.

Ouyang, D., Yuan, L., Qin, L., Chang, L., Zhang, Y., & Lin, X. (2020). Efficient shortest path index maintenance on dynamic road networks with theoretical guarantees. *Proceedings of the VLDB Endowment, 13*(5), 602–615.

Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A design science research methodology for information systems research. *Journal of Management Information Systems, 24*(3), 45–77.

Qi, P., et al. (2025). A review of dynamic traffic flow prediction methods for global energy-efficient route planning. *Sensors*.

Reis, D., Odhiambo, L., Wachira, B., Kamau, N., & Temu, A. (2025). Leveraging innovative technology and health data to enhance access to emergency care in Kenya. *Oxford Open Digital Health, 3*(1).

Sahayaraj, K. K. A., Chodnekar, A., & Mishra, A. (2024). Optimizing urban traffic flow prediction. In *Smart data intelligence* (pp. 381–391). Springer.

Sasikala, N., et al. (2025). Emergency traffic prioritization system with priority-based dynamic route optimization. *IEEE CONIT*.

Shao, Z., Zhang, Z., Wang, F., & Xu, Y. (2022). Pre-training enhanced spatial-temporal graph neural network for multivariate time series forecasting. *Proceedings of KDD*.

Zhang, Q., Gao, X., Wang, H., Yiu, S. M., & Yin, H. (2025). Efficient traffic prediction through spatio-temporal distillation. *Proceedings of the AAAI Conference on Artificial Intelligence, 39*(1), 1093–1101. https://doi.org/10.1609/aaai.v39i1.32096

Werner, N., Buchhold, M., Storandt, S., & Wagner, D. (2022). Combining predicted and live traffic with time-dependent A* potentials. *Proceedings of SEA 2022*. https://doi.org/10.4230/LIPIcs.SEA.2022.18

World Health Organisation. (2015). *Health emergency and disaster risk management framework*. WHO Press.

Yildirim, U. M., & Catay, B. (2022). An enhanced network-consistent travel speed generation scheme. *IEEE Transactions on Intelligent Transportation Systems*.

Yin, X., Wu, G., Wei, J., Shen, Y., Qi, H., & Yin, B. (2022). Deep learning on traffic prediction: Methods, analysis, and future directions. *IEEE Transactions on Intelligent Transportation Systems, 23*(6), 4927–4943. https://doi.org/10.1109/TITS.2021.3054840

Zhang, L., Khalgui, M., & Li, Z. (2021). Predictive intelligent transportation: Alleviating traffic congestion in the Internet of Vehicles. *Sensors, 21*(21), 7330. https://doi.org/10.3390/s21217330

Zhang, Z., Sun, Y., & Liu, Q. (2022). An adaptive route planning method of connected vehicles for improving the transport efficiency. *ISPRS International Journal of Geo-Information, 11*(1), 39.

Zohir, H. M., et al. (2025). Advancements in accident-aware traffic management. *Scientific Reports, 15*, 2847.
