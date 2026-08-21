# Design and Evaluation of a GRU-Based Predictive Routing Framework for Emergency Vehicles

Freshia Njoki Macharia¹*, Gilbert Langat², Stephen Mageto²

¹Department of Computer Science and Informatics, Kirinyaga University, Kerugoya, Kenya
²School of Pure and Applied Sciences, Kirinyaga University, Kerugoya, Kenya

*Corresponding author: fnjokimacharia@gmail.com | Co-authors: glangat@kyu.ac.ke; snyakiba@kyu.ac.ke

## Abstract

Emergency dispatch still computes a shortest path from speeds observed at departure. That path is optimal only for the snapshot; a corridor that slows fifteen to thirty minutes later is missed. This article reports a design-science artefact that closes that gap: a dispatcher decision-support framework joining a Gated Recurrent Unit (GRU) speed predictor, Time-Dependent A* (TD-A*) routing, and a remaining-time threshold controller. Two identical two-layer GRUs (64 hidden units, dropout 0.2) were trained separately on METR-LA (207 sensors) and PEMS-BAY (325 sensors) with chronological 70/15/15 splits and a train-only StandardScaler. METR-LA test mean absolute error was 3.48 mph (RMSE 6.04 mph); PEMS-BAY test MAE was 2.38 mph (RMSE 4.49 mph). Routing used the METR-LA detector graph (207 nodes, 1,515 fully instrumented edges). Nine hundred matched journeys (75 origin–destination pairs × three traffic scenarios × four δ values) were traversed on actual future speeds. Versus Dijkstra with current speeds, mean travel-time reduction was 5.74% overall and 16.19% under incident conditions (p < .001), with 1.03% in peak hour (p = .0002) and a non-significant 0.01% off-peak. The framework sat 1.69% below an oracle with perfect future knowledge and 0.61% above a reactive A* baseline. Combined GRU plus routing latency was about 40 ms against a 1,000 ms dispatch cap. Travel time did not differ among δ ∈ {0.05, 0.10, 0.15, 0.20} (ANOVA F ≈ 0.001, p = 1.00); δ = 0.20 is the operational default. The contribution is an integrated, latency-feasible emergency routing loop, not a new state-of-the-art spatial-temporal predictor.

**Keywords:** emergency vehicle routing; gated recurrent unit; time-dependent A*; traffic prediction; adaptive replanning; design science

## 1. Introduction

### 1.1 Background of the Study

Intelligent transportation systems sit at the junction of computer science, urban operations, and public safety. Within that field, routing an ambulance, fire appliance, or police unit is among the highest-stakes uses of a shortest-path algorithm: each extra minute at a cardiac-arrest scene is associated with about a 10% rise in mortality (World Health Organisation [WHO], 2015). Congestion still adds 30–50% to ambulance times in peak hours in many metropolitan areas, and commercial tools such as Google Maps and Waze remain largely snapshot-based, computing a path from speeds visible at the click rather than from speeds expected fifteen to thirty minutes later (Binshaflout & Ahmad, 2023; International Transport Forum, 2023; Qi et al., 2025).

The regional picture is more severe. African Development Bank assessments have placed emergency response in several East African capitals well beyond recommended thresholds (African Development Bank, 2022). Mixed traffic, including paratransit vehicles and motorcycles, is poorly captured by freeway-trained models, and most cities still lack an integrated predictive dispatch stack (Golub et al., 2021). Evidence for what works in this setting remains thin relative to the scale of the delay.

In Kenya, and in Nairobi specifically, peak-hour ambulance times of 18–25 minutes sit far above the World Health Organisation eight-minute target for life-threatening calls (WHO, 2015; INRIX, 2024). Recent Kenyan deployments show that better dispatch routing can cut delays dramatically when the organisational setting allows it (Reis et al., 2025). That evidence makes a computationally light, predictive decision-support design a practical research target rather than a purely theoretical one. The binding constraint is not the existence of a shortest-path library; it is whether a recommendation that looks ahead 15–30 minutes can be issued inside a dispatcher’s click and updated only when remaining travel time has truly deteriorated.

Research has advanced along two parallel streams. Deep learning traffic prediction, from the METR-LA and PEMS-BAY benchmarks of Li et al. (2018) through stacked GRUs (Jeong et al., 2021) and graph networks (Jiang & Luo, 2022; Yin et al., 2022), can forecast short-horizon speeds with usable accuracy. Time-dependent shortest-path theory (Dreyfus, 1969; Jaballah et al., 2021) can route on costs that change with entry time. A 2025 systematic review names the disconnection between prediction and path planning as a primary open problem in intelligent transportation research (Qi et al., 2025). Emergency vehicle work has concentrated on signal priority, detection, and current-map rerouting rather than a learned 15–30 minute path with a tested dispatcher threshold (Chowdhury et al., 2023; Hugar et al., 2025; Sasikala et al., 2025; Zohir et al., 2025).

### 1.2 Statement of the Problem

The ideal dispatch condition is a route that remains near-optimal as traffic evolves over the next 15–30 minutes, with a new recommendation issued only when remaining travel time has truly deteriorated, and with an answer returned well under one second. The present condition is a static or current-only path that ages as soon as a queue forms downstream. Machine-learning traffic prediction and time-dependent shortest paths exist as separate literatures (Li et al., 2018; Jaballah et al., 2021; Werner et al., 2022). What has been missing is a single emergency-oriented artefact that (a) learns short-horizon speeds, (b) routes on time-varying costs, (c) exposes a human-calibrated remaining-time threshold, and (d) reports travel time, latency, and update frequency together on matched journeys scored with actual future speeds (Qi et al., 2025; Zohir et al., 2025).

Cloud-scale spatial-temporal models could in principle close the prediction half of that gap, but they substitute a second problem for the first: inference cost that sits uneasily inside a one-second dispatch click, and a research culture that reports mean absolute error in one paper and route time in another. Published emergency-vehicle systems that do replan typically do so from the current map or by holding a green wave, not from a 30-minute learned horizon with a remaining-time policy. If the gap remains unaddressed, dispatch centres face a false choice between keeping a snapshot shortest path that is already obsolete when the vehicle is mid-corridor, and adopting heavy spatial-temporal models whose wait time the dispatcher cannot afford. This study addresses the gap by designing, implementing, and evaluating an integrated GRU, time-dependent A*, and remaining-time controller under that budget.

### 1.3 Objective of the Study

The general objective was to design, develop, and evaluate an Intelligent Route Optimisation Framework for emergency vehicle navigation by integrating GRU forecasting with time-dependent A* and a threshold-based controller.

The corresponding research questions were: (RQ1) what gaps remain among emergency vehicle routing, traffic prediction, and time-dependent pathfinding; (RQ2) how accurately a lightweight GRU can forecast 15–30 minute speeds on loop-detector traces; (RQ3) which remaining-time threshold δ ∈ {5%, 10%, 15%, 20%} balances route quality against extra dispatcher alerts; and (RQ4) whether the integrated loop reduces realised travel time versus baselines while remaining under one second.

### 1.4 Justification and Scope

A design-science stance is appropriate because the object of inquiry is an artefact that must be built before its utility can be measured (Peffers et al., 2007). The knowledge sought is prescriptive: which configuration of predictor, router, and controller is accurate enough, fast enough, and stable enough for a dispatcher who retains final authority. Pragmatism justified simulation measurement rather than a claim of universal optimality (Creswell & Creswell, 2018). Primary measurement on public freeway archives, rather than a claim of Nairobi field reduction, is likewise necessary because five-minute detector traces at the required spatial density were not available for the Kenyan capital at the time of the study.

The study is delimited to 15–30 minute speed forecasts, simulation on METR-LA (routing) and PEMS-BAY (cross-dataset GRU checks), a single vehicle, and travel-time minimisation only. Live Nairobi sensors, multi-vehicle coordination, and signal pre-emption were out of scope. METR-LA and PEMS-BAY are United States freeway benchmarks; they do not reproduce matatu dynamics, and that limit is stated rather than hidden. An OpenStreetMap extract of downtown Los Angeles was built during development and was not the graph behind the reported 900 journeys. Conceptually, the article reports design, implementation, and evaluation together rather than splitting those activities across companion papers. The literature reviewed spans 1959 to 2026, with emphasis on the 2018–2026 period in which METR-LA/PEMS-BAY benchmarks and prediction–planning integration matured.

## 2. Literature Review and Conceptual Framework

### 2.1 Theoretical Framework

The study is anchored in three complementary theories that bound the artefact, together with a process methodology that prescribed how the artefact was produced.

Time-dependent shortest path (TDSP) theory (Dreyfus, 1969) treats edge cost as a function of entry time. With the first-in-first-out (FIFO) property, later departure cannot produce earlier arrival, and label-setting search remains correct. The search state is a pair (vertex, arrival time). The priority key is f(n) = g(n) + h(n), with h(n) equal to haversine distance divided by free-flow speed, which is admissible. Predicted times were clipped to at least one second so that FIFO was preserved even when a forecast was briefly erratic. Chen et al. (2021) established that online route planning over fully stochastic time-dependent networks is computationally hard in the general case, which is why this study used a deterministic FIFO approximation with discrete five-minute slots rather than a fully online stochastic planner. TDSP therefore supplies both the correctness condition and the reason a special case was required.

GRU sequence modelling (Cho et al., 2014) captures daily and weekly speed cycles with fewer parameters than long short-term memory. Jeong et al. (2021) reported that stacked GRU matched or exceeded LSTM on highway speeds at lower inference cost — the relevant trade-off when inference must share a one-second dispatch window (Benarmas & Bey, 2024). Graph networks can beat that recurrent baseline on METR-LA mean absolute error (Jiang & Luo, 2022; Li et al., 2018; Yin et al., 2022). Distillation and “soft GRU” variants shrink compute further (Abdullah et al., 2023; Zhang, Gao, Wang, Yiu, & Yin, 2025). For a dispatch loop, the present study declined a heavier spatial encoder because the binding constraint was combined wait, not leaderboard MAE. GRU theory therefore enters as a latency–accuracy compromise, not as a claim that two-layer GRU is the globally best predictor.

Decision support systems (DSS) theory (Gorry & Scott Morton, 1971; Keen & Scott Morton, 1978) requires that recommendations be timely, sparse enough to avoid alert fatigue, and subordinate to the human dispatcher. The remaining-time threshold δ operationalises that requirement: a new path is offered only when remaining time from the vehicle’s current position has grown by more than δ, or when a newly computed path is better by δ.

The Design Science Research Methodology of Peffers et al. (2007) supplies the process: problem identification, definition of objectives, design and development, demonstration on public benchmarks, evaluation against four baselines, and communication through an open repository. The four anchors are complementary rather than redundant. TDSP, GRU theory, and DSS explain why the three components take the form they do; DSRM explains how they were produced and tested. Their integration yields a research logic in which the ageing snapshot path constitutes problem identification, the four research questions constitute the definition of solution objectives, and the three-component loop constitutes the design output that Sections 4 and 5 then evaluate.

### 2.2 Review of Related Empirical Studies

**Classical pathfinding.** Dijkstra (1959) and A* (Hart et al., 1968) remain the operational standard in many computer-aided dispatch stacks (Hagberg et al., 2024). Bidirectional search, contraction hierarchies, and landmark heuristics accelerate static queries but assume weights that do not jump every five minutes (Gong et al., 2023). Those accelerators are not withdrawn; they solve a different problem. The present artefact needs a searcher that remains correct when every edge weight is rewritten from a 30-minute forecast at detector resolution.

**Traffic prediction.** Li et al. (2018) released METR-LA and PEMS-BAY and the diffusion convolutional recurrent network. Citing that paper does not mean DCRNN was implemented; the present predictor is a two-layer GRU on those archives. Subsequent surveys document a race among graph neural networks and transformers (Jiang & Luo, 2022; Yin et al., 2022). Hybrid convolutional–GRU models can cut error at higher inference cost (Ma et al., 2023). Compact students can approach heavier teachers by distillation (Zhang, Gao, et al., 2025); this study did not distill. For a dispatch loop, Jeong et al. (2021) remains the relevant published trade-off: stacked GRU is accurate enough on 15–30 minute highway speeds and cheap enough to call repeatedly. Abdullah et al. (2023) likewise retained a gated recurrent architecture when the operational constraint was timely congestion estimates rather than leaderboard MAE.

**Time-dependent routing and integration.** Jaballah et al. (2021) and Yildirim and Catay (2022) operationalise time-varying speeds on real networks. Werner et al. (2022) combine live and predicted times inside TD-A* and obtain large speedups on continental graphs. That paper is the closest routing precedent. Predicted times in that work are an input to a preprocessed potential; the paper does not train a GRU on METR-LA, does not sweep a dispatcher remaining-time threshold, and relies on preprocessing that sits uneasily with five-minute weight refresh. At 207 nodes that preprocessor was unnecessary. Zhang, Khalgui and Li (2021) integrate prediction and routing in an Internet-of-Vehicles setting without an emergency remaining-time policy. Zhang, Sun and Liu (2022) describe adaptive route planning for connected vehicles under incidents; that work is fleet incident routing and is not a source for cardiac-arrest mortality statistics.

**Emergency vehicle services.** Chowdhury et al. (2023) proposed a UAV-assisted priority scheme and reported about 8% lower response time and 12% better incident-area clearance in simulation; the literature they surveyed still concentrated on detection, green waves, and static routes rather than a learned 15–30 minute path. Hugar et al. (2025) and Sasikala et al. (2025) improve intersection priority; those gains are not interchangeable with predictive path choice. Abuaisha et al. (2025) report 12–18% reliability gains from replanning on fixed public-transport corridors. Ikram et al. (2025) explore digital-twin emergency navigation, which assumes an operational city-data loop this study did not have. Zohir et al. (2025) still list proactive predictive routing as an open emergency-vehicle direction. None of these papers evaluate GRU + TD-A* + δ on METR-LA with ground-truth traversal.

### 2.3 Identification of Research Gaps

Four gaps follow. First, prediction and time-dependent routing are often studied apart; a few systems combine live or predicted times with search, but not as an emergency GRU, time-dependent A*, and remaining-time threshold under a one-second dispatch budget (Qi et al., 2025; Werner et al., 2022; Chowdhury et al., 2023). Second, threshold policies for mid-journey recommendations are not systematically swept over {5, 10, 15, 20}%. Third, MAE and route time are usually reported in different papers, so prediction error never appears as travel-time regret against an oracle that used actual future speeds. Fourth, Sub-Saharan mixed-traffic deployment remains untested on local sensors; this study can only offer a transferable method, not Nairobi measurements. The present article addresses the first three gaps by construction and measurement, and states the fourth as a boundary rather than as a result already obtained.

### 2.4 Conceptual Framework

The conceptual framework, presented in Figure 1, positions the design parameters of the three components as independent variables, the integrated loop as the mediating artefact, and journey outcomes as dependent variables. Independent variables are GRU depth and width, the TD-A* heuristic, the remaining-time threshold δ, and dataset. The mediating artefact is the dispatcher-support loop: Component 1 maps a 60-minute window to a 30-minute speed forecast; Component 2 computes a time-dependent path; Component 3 issues a new path when remaining time on the current path rises by more than δ, or when a newly computed path is better by δ. Dependent variables are journey time, gap to oracle, latency, and replans per trip.

Moderators — congestion regime, time of day, path length, and sensor coverage — affect all three components, not only the controller. Congestion changes the gap between predicted and actual edge times; time of day governs which historical patterns the GRU draws upon; path length determines how many five-minute slots a journey occupies; sensor coverage decides which edges receive predicted costs versus free-flow fallback. On the detector graph used for the 900 journeys every edge was instrumented, so coverage was held at 100%. The framework thus serves at once as a design blueprint and as an evaluation structure: the same variables that shaped the artefact are the variables against which Tables 1–6 are read.

**Figure 1.** Conceptual framework of the study: independent variables, three-component mediating artefact, dependent outcomes, and moderators acting on all three components.

## 3. Methodology

### 3.1 Research Design

The study adopted a quantitative experimental design embedded within the Design Science Research Methodology of Peffers et al. (2007), under a pragmatist orientation that evaluates knowledge claims by their fitness for purpose rather than by adherence to a single epistemological tradition (Creswell & Creswell, 2018). Pragmatism suits design science because the research product is an artefact intended to solve an operational problem and its warrant lies in demonstrable utility. The six DSRM activities were all executed in this article: problem identification was the ageing of a dispatch-time shortest path under five-minute traffic volatility; objective definition produced the four research questions; design and development produced three Python packages (prediction, routing, and control); demonstration used public METR-LA and PEMS-BAY archives; evaluation compared four baselines on identical origin–destination pairs, departure windows, and random seed 42; communication is the open repository (https://github.com/Freshia-Njoki/Emergency_Routing) and this article.

Internal validity rested on matching journeys: the same origin, destination, clock, and realised speeds, with five methods choosing the path. External validity was bounded on purpose. Chronological splits prevented the model from seeing later frames while training on earlier ones. A train-only scaler prevented the test partition from writing the marking scheme. Early stopping prevented selection of the last noisy epoch. Those controls do not convert Los Angeles freeways into Nairobi mixed traffic; they make the Los Angeles claim inspectable.

### 3.2 Dataset Description and Preprocessing

METR-LA contains 207 loop detectors and 34,272 five-minute speed frames (March–June 2012). PEMS-BAY contains 325 detectors and 52,116 frames (January–May 2017, about five months). Cells at or below zero were treated as missing and imputed with the sensor mean. Splits were chronological: 70% train, 15% validation, 15% test, applied to raw time before windowing so that validation and test windows never mixed training observations. A StandardScaler was fitted on the METR-LA training partition only and applied to METR-LA validation and test windows. PEMS-BAY used its own scaler on its own training split. Sequences were 12 steps in (60 minutes) and six steps out (30 minutes).

A multivariate GRU cannot take 207 and 325 sensors in one tensor. The study therefore trained two models, not one joint city model. Routing used METR-LA because that is the graph on which vehicles were simulated. PEMS-BAY answered whether the same architecture still predicted speeds in another region.

### 3.3 Variables and Operationalisation

Travel time was the primary dependent variable: realised seconds from origin to destination after every method was driven on actual future speeds. Predicted costs selected the path; they did not mark the path. That separation made the oracle well-defined. Secondary outcomes were percentage reduction versus each baseline, wall-clock latency of TD-A* and of GRU inference, and replans per journey. The policy variable δ ∈ {0.05, 0.10, 0.15, 0.20} is the remaining-time trigger. It is not the significance level α = .05 used for t-tests and ANOVA.

Four baselines were required. B1 (Dijkstra on the current snapshot) represents dispatch practice. B2 (static A* on historical mean speeds) tests whether an average day is sufficient. B3 (reactive A*) is allowed one replan from the latest snapshot when the incident becomes visible, without a 30-minute GRU horizon. B4 (oracle A*) uses actual future speeds and is an unreachable ceiling. Reporting only B1 would have been biased.

### 3.4 Experimental Procedure

**GRU.** Two stacked GRU layers of 64 units, dropout 0.2 after each, a dense projection, and a reshape to (6, N sensors) were trained with Adam (learning rate 0.001), mean squared error, batch size 64, early stopping patience 10, and learning-rate reduction on plateau. Inverse scaling recovered miles per hour. GRU was adopted from published LSTM comparisons (Jeong et al., 2021) rather than a fresh LSTM bake-off, because the dispatch constraint is latency. The defended METR-LA checkpoint is `models/saved/gru_improved_best.keras`.

**Graph.** The reported routing graph was the METR-LA detector adjacency (Li et al., 2018): 207 nodes and 1,515 directed edges, with a sensor speed on every edge. Haversine distance to the destination divided by free-flow speed served as the admissible heuristic. If search exhausted the fringe without reaching the destination, the result was treated as infeasible and a dispatcher would be told that the modelled graph had no route. Origin–destination pairs were sampled to be reachable (minimum eight hops and at least 300 s free-flow time).

**Controller.** A new recommendation was issued when remaining time on the current path, from the vehicle’s present position, grew by more than δ, or when a newly computed path was better by more than δ. The sliding-window configuration advanced the 12-frame GRU input with vehicle progress at each five-minute slot. When an incident became visible, slowed speeds were written into the recent frames and fused with the forecast. A single forecast frozen at departure was not the configuration behind the tables.

**Scenarios.** Peak hour used the slowest quartile of test-window mean speed; off-peak the fastest quartile; incident applied a 40% speed drop on the planned Dijkstra corridor after 20% of planned B1 time, so the vehicle actually met the disruption. Design: 75 pairs × 3 scenarios × 4 δ = 900 journeys. Random seed 42 was fixed. The evaluation harness is `src/evaluation/run_simulation.py` with `simulation_core.py`.

### 3.5 Data Analysis

Descriptive means, standard deviations and medians, one-sample t-tests of percentage reduction versus Dijkstra against zero, and one-way ANOVA on δ used α = .05. Shapiro–Wilk statistics were reported; many reduction distributions were non-normal, so significance was interpreted alongside medians. Software was Python 3 with TensorFlow/Keras and NetworkX. The account is in the past tense: the experiments were run.

### 3.6 Ethical Considerations

The study used publicly available datasets and involved no human participants. No live ambulance was routed by the artefact, and no operational dispatch decision was taken on the basis of these tables. Simulation journeys were synthetic origin–destination pairs on the detector graph and were not traces of named emergency calls. Institutional approval was sought from Kirinyaga University’s Research and Ethics Committee prior to implementation. The METR-LA and PEMS-BAY datasets contained no vehicle tracking data attributable to individuals; they consisted solely of aggregated speed measurements from fixed sensors. Source code, processed datasets, and experimental configurations were made publicly available via the GitHub repository to support reproducibility.

## 4. Results

### 4.1 Prediction Performance

Table 1 reports the defended GRU metrics. METR-LA training stopped at 27 epochs. Final training loss was 0.3847 and best validation loss 0.4335 on StandardScaler-transformed speeds. Test MAE was 3.48 mph and RMSE 6.04 mph after inverse transform. Predicted speeds on a held-out window ranged from about 32 to 70 mph with mean 63 mph, which is physically plausible. PEMS-BAY, with its own scaler, stopped at 79 epochs (scaled train/validation losses 0.0024 and 0.0027). Those scaled losses are not comparable in magnitude to the METR-LA scaled losses; the comparable quantities are inverse-transformed MAE and RMSE. PEMS-BAY test MAE was 2.38 mph (RMSE 4.49 mph), a gap of 1.10 mph relative to Los Angeles, inside a 2.0 mph generalisation tolerance. Lower Bay error reflects smoother freeway speeds, not a failed Los Angeles model.

METR-LA MAE lies in the 3.1–4.2 mph band reported for comparable GRUs (Jeong et al., 2021). Graph networks can beat it (Li et al., 2018). They were not selected for a 40 ms combined loop.

**Table 1.** GRU configuration and test metrics (train-only StandardScaler).

| Item | METR-LA | PEMS-BAY |
|---|---|---|
| Sensors | 207 | 325 |
| Frames (5 min) | 34,272 | 52,116 |
| Epochs (early stop) | 27 | 79 |
| Final train loss (scaled MSE) | 0.3847 | 0.0024 |
| Best validation loss (scaled MSE) | 0.4335 | 0.0027 |
| Test MAE | 3.48 mph | 2.38 mph |
| Test RMSE | 6.04 mph | 4.49 mph |
| Role | Routing GRU | Prediction check only |

### 4.2 Artefact and Graph

Table 2 summarises the routing graph. Every directed edge carried a detector speed. An unused downtown OpenStreetMap extract (397 nodes, 1,024 edges, 18.6% sensor-mapped) was not the 900-run network. Free-flow fallback was therefore unused on the reported journeys.

**Table 2.** Road network used for the 900 journeys.

| Property | Value |
|---|---|
| Source | METR-LA detector adjacency (Li et al., 2018) |
| Nodes | 207 |
| Directed edges | 1,515 |
| Sensor-mapped edges | 1,515 (100%) |
| Free-flow fallback on reported journeys | Not used |

**Figure 2.** METR-LA detector adjacency used for the 900 journeys (207 nodes, 1,515 edges, 100% instrumented).

### 4.3 Threshold Sensitivity (Objective 3)

Table 3 reports mean reduction versus Dijkstra and replans per journey by δ. N = 225 journeys per row (75 origin–destination pairs × 3 scenarios). Travel time did not move (ANOVA F ≈ 0.001, p = 1.00). Incident journeys averaged about 1.03 replans at every tested value because a 40% corridor drop increases remaining time by more than 20%. Decision-support practice then prefers the least frequent alert that still catches those incidents: δ = 0.20. The Chapter 3 candidate of 0.10 is retained as the planned mid-range value, not as the measured default. δ is a policy; α = .05 is a Type I error rate. They share digits; they are not the same quantity.

Figure 3 shows the same pattern graphically: incident reduction stays near 16% across the four thresholds, while update frequency falls as δ rises. Peak-hour reduction remains near 1%; off-peak reduction remains near zero.

**Table 3.** Mean reduction versus Dijkstra and replans by remaining-time threshold (N = 225 per row).

| δ | Mean vs B1 (%) | Replans / journey | TD-A* latency (ms) |
|---|---|---|---|
| 0.05 | +5.726 | 0.45 | 0.370 |
| 0.10 | +5.748 | 0.44 | 0.367 |
| 0.15 | +5.726 | 0.43 | 0.368 |
| 0.20 | +5.767 | 0.39 | 0.373 |

*Note.* ANOVA on reduction versus Dijkstra: F ≈ 0.001, p = 1.00. Recommended operational default: δ = 0.20.

**Figure 3.** Threshold sensitivity: travel-time reduction versus Dijkstra (left) and mean replans per journey (right) by δ. Reduction is invariant; update frequency falls as δ rises.

### 4.4 Journey Time versus Baselines (Objective 4)

Table 4 reports mean travel times in seconds. Table 4 pools the four δ values (75 pairs × 4 thresholds = 300 journeys per scenario) because Table 3 showed δ does not change time. Table 5 reports t-tests of percentage reduction versus Dijkstra.

Under incidents, mean framework time was 598.9 s against 727.5 s for Dijkstra, 723.2 s for historical A*, 603.7 s for reactive A*, and 580.5 s for the oracle. Peak-hour means were 506.3 s (framework) against 513.1 s (Dijkstra and reactive A*), 552.5 s (historical A*), and 499.5 s (oracle). Off-peak means sat near 403 s for every method except a slightly slower historical A* (405.2 s). Figure 4 displays those means; Figure 5 displays the corresponding percentage reductions.

**Table 4.** Mean travel time in seconds by scenario (N = 300 per row: 75 pairs × 4 δ).

| Scenario | B1 Dijkstra | B2 static A* | B3 reactive A* | B4 oracle | Framework |
|---|---|---|---|---|---|
| Peak | 513.1 | 552.5 | 513.1 | 499.5 | 506.3 |
| Off-peak | 403.5 | 405.2 | 403.5 | 403.1 | 403.4 |
| Incident | 727.5 | 723.2 | 603.7 | 580.5 | 598.9 |

*Note.* Paths were selected with each method’s own information; journey time was accumulated from actual future speeds.

**Table 5.** Percentage reduction versus Dijkstra (one-sample t-test against zero; α = .05).

| Scenario | N | Mean % | t | p |
|---|---|---|---|---|
| Peak hour | 300 | +1.03 | 3.81 | .0002 |
| Off-peak | 300 | +0.01 | 0.12 | .90 |
| Incident | 300 | +16.19 | 26.43 | < .001 |

Overall reduction versus Dijkstra was +5.74%; versus static A* +7.39%; versus reactive A* +0.61%; versus the oracle −1.69%. Combined GRU and routing latency was approximately 40 ms (TD-A* 0.37 ms; GRU 39.3 ms) against a 1,000 ms cap (Table 6; Figure 6). Search at 0.37 ms is negligible beside GRU inference; the predictor, not the router, was the computational bottleneck, and the loop still fitted the budget. A later wall-clock re-measurement under different CPU load is expected to differ and is not substituted for the reported 40 ms combined wait.

**Table 6.** Computational latency (milliseconds).

| Scenario | TD-A* | GRU inference | Combined | Target |
|---|---|---|---|---|
| Peak | 0.37 | 39.3 | ~40 | < 1,000 |
| Off-peak | 0.37 | 39.3 | ~40 | < 1,000 |
| Incident | 0.37 | 39.3 | ~40 | < 1,000 |

*Note.* Combined wait is GRU inference plus time-dependent A*, not routing alone.

**Figure 4.** Mean travel times (seconds) versus four baselines on matched journeys scored with actual future speeds.

**Figure 5.** Framework travel-time reduction (%) versus Dijkstra, static A*, and reactive A*.

**Figure 6.** Computational performance: TD-A* ≈ 0.37 ms; GRU ≈ 39.3 ms; combined ≈ 40 ms, against a 1,000 ms dispatch cap.

## 5. Discussion

### 5.1 Interpretation of Key Results

The incident cell is the operational content of the artefact. When the planned corridor was slowed by 40%, remaining time from the vehicle’s current position increased by more than δ, and an alternative path was offered. Mean time fell from 727.5 s to 598.9 s versus Dijkstra (t = 26.43, p < .001), with about one replan per journey. That is what a 30-minute forecast and a remaining-time trigger are for: diversion before the vehicle remains on a road that has already failed.

Peak hour showed a smaller but statistically significant reduction of 1.03% (t = 3.81, p = .0002). When congestion is network-wide, alternative corridors are also slow, so looking 15–30 minutes ahead helps only modestly. Off-peak times were tied (0.01%, t = 0.12, p = .90; both means about 403 s). That near-zero result was treated as a successful negative control, not as model failure: on empty roads a forecast and a current map should agree.

The 0.61% margin over reactive A* is the residual value of the 30-minute horizon once the incident is already visible in the current snapshot. Reporting that small gap is required if B3 is an honest comparator. The 1.69% gap behind the oracle is likewise required if B4 used actual future speeds. Overall +5.74% versus Dijkstra is a mixture of three regimes and is not a promise for every trip. If one number is quoted, it should be 16.19% under incident conditions.

ANOVA F ≈ 0.001, p = 1.00 does not mean the controller never replanned. Incident journeys replanned; the four policies did not differ in travel time. DSS theory then selects δ = 0.20.

N must not be confused. Nine hundred is the whole study. Two hundred and twenty-five is one δ across three regimes (Table 3). Three hundred is one regime across four δ (Tables 4–5). Pooling δ in Tables 4–5 is valid only because Table 3 showed travel time to be insensitive to δ.

### 5.2 Integration with Existing Literature

The architecture both aligns with and departs from the reviewed literature. It follows Jeong et al. (2021) in retaining stacked GRU for a latency-bounded highway-speed task, and Dreyfus (1969) and Werner et al. (2022) in routing on time-varying costs with an admissible heuristic. Werner et al. remain the closest routing precedent and are not withdrawn: they show that time-dependent A* can be fast on continental graphs when preprocessing is available. At 207 nodes that preprocessor was unnecessary, so edge weights could be rewritten every five minutes. Werner et al. do not train a METR-LA GRU, do not sweep a dispatcher remaining-time threshold, and do not report matched ground-truth emergency journeys. The present artefact therefore extends rather than replaces that line.

Qi et al. (2025) independently named the prediction–planning disconnect. The 16.19% incident reduction lies in a similar numerical band to the 12–18% replanning gains of Abuaisha et al. (2025) on fixed transit corridors; the problems differ and the comparison is indicative only. It is not comparable to signal-priority percentages (Chowdhury et al., 2023; Hugar et al., 2025). Jeong et al. (2021) supplies the MAE band against which 3.48 mph is read. Jiang and Luo (2022) and Yin et al. (2022) explain why a reviewer might demand a graph network: the answer is the 40 ms combined budget.

Zhang, Sun and Liu (2022) share incident-aware adaptive planning for connected vehicles; they are not the source of the 10% cardiac-arrest statistic (WHO, 2015). Zhang, Khalgui and Li (2021) couple prediction and routing in an Internet-of-Vehicles model without this GRU–δ sweep on METR-LA. The claim is therefore narrow: no reviewed paper trained a two-layer GRU on METR-LA, routed on that detector adjacency with time-dependent A*, exposed δ ∈ {0.05, 0.10, 0.15, 0.20} as a dispatcher control, and walked every method — including the proposed framework — on actual future speeds for 900 matched journeys.

### 5.3 Theoretical Implications

Two theoretical contributions follow. First, TDSP theory remains sufficient for emergency dispatch when FIFO is enforced by clipping and when the horizon is discretised into five-minute slots. The study did not solve Chen et al.’s (2021) general stochastic online problem; it used a valid special case. That special case is itself a theoretical result of a kind: it shows where the hardness result does not bind for a single priority vehicle on a FIFO detector graph. Second, DSS theory is not a slogan attached after the algorithm. The remaining-time test, the choice of δ = 0.20 after a flat ANOVA, and the retention of dispatcher authority are the same theory operating at design time, at evaluation time, and at the recommended default. GRU theory enters as a latency–accuracy compromise rather than as a claim that two-layer GRU is the globally best predictor. In that respect the study treats sequence-model choice as a design instrument bounded by an operational envelope, analogous to treating deployment topology as a generative constraint rather than as implementation detail.

### 5.4 Practical and Policy Implications

For dispatch centres, a recommendation of this type can be issued inside a dispatch click: combined wait was about 40 ms. The default remaining-time trigger should be 20%, not the 10% mid-range guess used to plan the experiment. For transport authorities, including Nairobi Metropolitan Services and the Kenya National Highways Authority, the binding constraint for transfer is local sensor coverage, not compute. The reported percentages describe a 100% instrumented detector graph. A Nairobi-density analogue should downsample that graph to 10–30% coverage and repeat the 900-run, rather than treat 16.19% as already a mixed-traffic field result. Kenyan deployments that have already cut delay through better routing (Reis et al., 2025) show organisational appetite; they do not substitute for local detectors.

## 6. Conclusion, Limitations and Future Work

### 6.1 Summary of Main Findings

This article set out to design, develop, and evaluate a three-component dispatcher-support loop for emergency vehicle navigation. A two-layer GRU forecast 30-minute speeds at 3.48 mph MAE on METR-LA and 2.38 mph on a separate PEMS-BAY model. Time-dependent A* routed on a 207-node, 1,515-edge detector graph. Across 900 ground-truth journeys, incident travel time fell 16.19% versus current-map Dijkstra (p < .001), peak hour 1.03% (p = .0002), and off-peak not at all. Combined latency was about 40 ms. Travel time did not differ among δ = 0.05–0.20; the operational default is 0.20. The contribution is the integrated loop under a one-second budget, not a new leaderboard predictor. The design, development, and evaluation objectives were therefore achieved.

### 6.2 Study Limitations

Four limits apply. First, METR-LA and PEMS-BAY are United States freeway traces; they do not reproduce Nairobi mixed traffic. Second, the 900 journeys used 100% detector coverage; a 10–30% coverage run was not executed. Third, PEMS-BAY confirmed prediction in a second city but was not given a routing 900-run. Fourth, the evaluation is single-vehicle simulation; multi-ambulance interference and live incident feeds were out of scope. If search returned no path, the modelled graph would be declared infeasible; sampled origin–destination pairs were reachable, so that fallback was not triggered in the tables. The reported percentages therefore describe reachable journeys on a fully instrumented freeway detector graph.

### 6.3 Future Research Directions

Four directions follow. First, the present 100% detector graph should be downsampled to 10–30% coverage and the 900-run repeated as a sparse-sensor analogue of Nairobi-density instrumentation. Second, a PEMS-BAY routing graph should be built and Objectives 3 and 4 repeated, testing whether the incident cell survives a second freeway topology. Third, when local sensors exist, a field trial should be conducted in which the dispatcher remains in authority. Fourth, multi-vehicle coordination and live incident feeds lie beyond this proof of method and should be specified as a subsequent design-science cycle rather than retrofitted onto these tables.

## References

Abdullah, S. M., Periyasamy, M., Kamaludeen, N. A., Towfek, S. K., Marappan, R., Kidambi Raju, S., Alharbi, A. H., & Khafaga, D. S. (2023). Optimizing traffic flow in smart cities: Soft GRU-based recurrent neural networks for enhanced congestion prediction using deep learning. *Sustainability, 15*(7), 5949. https://doi.org/10.3390/su15075949

Abuaisha, A., Shen, B., Harabor, D., Stuckey, P., & Wallace, M. (2025). Dynamic replanning for improved public transport routing. In *Proceedings of the International Joint Conference on Artificial Intelligence*. https://www.ijcai.org/proceedings/2025/937

African Development Bank. (2022). *African economic outlook 2022*. AfDB.

Benarmas, R., & Bey, M. (2024). A deep learning-based framework for road traffic prediction. *The Journal of Supercomputing, 80*, 7337–7357. https://doi.org/10.1007/s11227-023-05718-x

Binshaflout, A., & Ahmad, B. (2023). Graph neural networks for traffic pattern recognition: An overview. *IEEE Access, 11*, 14890–15005.

Chen, D., Li, L., Wang, Y., & Zhou, X. (2021). Online route planning over time-dependent road networks. In *Proceedings of the 37th IEEE International Conference on Data Engineering* (pp. 1152–1163).

Cho, K., van Merriënboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., & Bengio, Y. (2014). Learning phrase representations using RNN encoder–decoder for statistical machine translation. In *Proceedings of EMNLP* (pp. 1724–1734).

Chowdhury, A., Kaisar, S., Khoda, M. E., Naha, R., Khoshkholghi, M. A., & Aiash, M. (2023). IoT-based emergency vehicle services in intelligent transportation system. *Sensors, 23*(11), 5324. https://doi.org/10.3390/s23115324

Creswell, J. W., & Creswell, J. D. (2018). *Research design: Qualitative, quantitative, and mixed methods approaches* (5th ed.). SAGE.

Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik, 1*, 269–271.

Dreyfus, S. E. (1969). An appraisal of some shortest-path algorithms. *Operations Research, 17*(3), 395–412. https://doi.org/10.1287/opre.17.3.395

Golub, A., Stevens, M., Klopp, J. M., & Martin, E. (2021). Addressing public transit challenges in Sub-Saharan African cities. *Transport Policy, 105*, 62–72.

Gong, Z., et al. (2023). Querying shortest path on large time-dependent road networks with shortcuts. In *Proceedings of IEEE ICDE*.

Gorry, G. A., & Scott Morton, M. S. (1971). A framework for management information systems. *Sloan Management Review, 13*(1), 55–70.

Hagberg, A. A., Schult, D. A., & Swart, P. J. (2024). *NetworkX 3.5 documentation*. https://networkx.org

Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. *IEEE Transactions on Systems Science and Cybernetics, 4*(2), 100–107.

Hugar, S. M., et al. (2025). Real-time adaptive traffic management system for emergency vehicle prioritisation. In *Proceedings of IEEE CNC*.

Ikram, T., Sultana, T., Nawaz, M., & Hassan, M. F. (2025). Digital twin assisted real-time emergency vehicle navigation for resource optimization and reroute planning. *International Journal of Parallel, Emergent and Distributed Systems, 40*(2), 112–128.

INRIX. (2024). *INRIX 2024 global traffic scorecard*.

International Transport Forum. (2023). *ITF transport outlook 2023*. OECD Publishing. https://doi.org/10.1787/b6cc9ad5-en

Jaballah, R., et al. (2021). The time-dependent shortest path and vehicle routing problem. *INFOR, 59*(3), 386–413.

Jeong, M.-H., Lee, T.-Y., Jeon, S.-B., & Youm, M. (2021). Highway speed prediction using gated recurrent unit neural networks. *Applied Sciences, 11*(7), 3059. https://doi.org/10.3390/app11073059

Jiang, W., & Luo, J. (2022). Graph neural network for traffic forecasting: A survey. *Expert Systems with Applications, 207*, 117921. https://doi.org/10.1016/j.eswa.2022.117921

Keen, P. G. W., & Scott Morton, M. S. (1978). *Decision support systems: An organizational perspective*. Addison-Wesley.

Li, Y., Yu, R., Shahabi, C., & Liu, Y. (2018). Diffusion convolutional recurrent neural network: Data-driven traffic forecasting. In *Proceedings of ICLR*.

Ma, C., Dai, G., & Zhou, J. (2023). A novel STFSA-CNN-GRU hybrid model for short-term traffic speed prediction. *IEEE Transactions on Intelligent Transportation Systems, 24*(9), 9660–9673.

Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A design science research methodology for information systems research. *Journal of Management Information Systems, 24*(3), 45–77. https://doi.org/10.2753/MIS0742-1222240302

Qi, P., Pan, C., Xu, X., Wang, J., Liang, J., & Zhou, W. (2025). A review of dynamic traffic flow prediction methods for global energy-efficient route planning. *Sensors, 25*(17), 5560. https://doi.org/10.3390/s25175560

Reis, D., Odhiambo, L., Wachira, B., Kamau, N., & Temu, A. (2025). Leveraging innovative technology and health data to enhance access to emergency care and referral services in Kenya. *Oxford Open Digital Health, 3*(1). https://doi.org/10.1093/oodh/oqaf004

Sasikala, N., et al. (2025). Emergency traffic prioritization system with priority-based dynamic route optimization. In *Proceedings of IEEE CONIT*.

Werner, N., Buchhold, M., Storandt, S., & Wagner, D. (2022). Combining predicted and live traffic with time-dependent A* potentials. In *Proceedings of SEA 2022*. https://doi.org/10.4230/LIPIcs.SEA.2022.18

World Health Organisation. (2015). *Health emergency and disaster risk management framework*. WHO Press.

Yildirim, U. M., & Catay, B. (2022). An enhanced network-consistent travel speed generation scheme. *IEEE Transactions on Intelligent Transportation Systems, 23*(8), 13204–13217.

Yin, X., Wu, G., Wei, J., Shen, Y., Qi, H., & Yin, B. (2022). Deep learning on traffic prediction: Methods, analysis, and future directions. *IEEE Transactions on Intelligent Transportation Systems, 23*(6), 4927–4943. https://doi.org/10.1109/TITS.2021.3054840

Zhang, L., Khalgui, M., & Li, Z. (2021). Predictive intelligent transportation: Alleviating traffic congestion in the Internet of Vehicles. *Sensors, 21*(21), 7330. https://doi.org/10.3390/s21217330

Zhang, Q., Gao, X., Wang, H., Yiu, S. M., & Yin, H. (2025). Efficient traffic prediction through spatio-temporal distillation. *Proceedings of the AAAI Conference on Artificial Intelligence, 39*(1), 1093–1101. https://doi.org/10.1609/aaai.v39i1.32096

Zhang, Z., Sun, Y., & Liu, Q. (2022). An adaptive route planning method of connected vehicles for improving the transport efficiency. *ISPRS International Journal of Geo-Information, 11*(1), 39.

Zohir, H. M., et al. (2025). Advancements in accident-aware traffic management: A comprehensive review of V2X-based route optimization. *Scientific Reports, 15*, 2847.
