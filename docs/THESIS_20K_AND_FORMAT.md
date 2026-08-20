# Thesis format check + 20,000-word expansion (paste into Word)

Use with the latest PDF (`__774a`). Do **not** paste this file into the thesis as a chapter. Paste only the **ADD** blocks at the headings named below.

KyU: tables on their own pages, title **above**; figures on their own pages, caption **below**; past tense for what was done; Chapter 5 has **no new citations**; APA hanging indent.

---

## ADD 1 — end of Section 2.4 (before 2.5)  (~1,050 words)

The forecasting literature after 2021 did not treat gated recurrent units as obsolete, but it did treat them as a temporal baseline against which spatial-temporal graph models were compared. Jiang and Luo (2022), in *Expert Systems with Applications*, surveyed graph neural networks for traffic forecasting and showed that message passing over a sensor graph usually reduces error on METR-LA and PEMS-BAY relative to a purely recurrent encoder, at additional memory and latency cost. Yin et al. (2022), in *IEEE Transactions on Intelligent Transportation Systems*, catalogued deep traffic-prediction methods and listed coupling those predictors to control and routing as an unfinished research direction rather than a solved engineering task. Those two surveys were used in this study as a design constraint, not as a claim that a two-layer GRU is the lowest-error model on either benchmark.

Spatial-temporal models published in 2022 illustrate how far the accuracy frontier moved. Lan et al. (2022) introduced DSTAGNN, a dynamic spatial-temporal aware graph network trained for traffic flow forecasting, and showed that allowing the spatial dependency structure to vary with time improved flow prediction over static-graph baselines. Shao et al. (2022) pre-trained a spatial-temporal graph network on multivariate series and then fine-tuned it, reporting gains attributable to the pre-training stage rather than to a larger decoder alone. Xu et al. (2022) proposed a multi-adaptive spatiotemporal flow graph network for speed forecasting and likewise located the gain in adaptive spatial mixing. None of those papers routed an emergency vehicle, none exposed a dispatcher threshold, and none reported a combined prediction-plus-search wait against a one-second budget. They were therefore cited as the performance ceiling this study declined: the artefact needed a predictor that could be called at every simulation step inside approximately 40 ms, not a leaderboard minimum mean absolute error.

Abdullah et al. (2023) retained a gated recurrent architecture, with a “soft” GRU, for urban congestion prediction in *Sustainability* (article 5949). Their objective was timely congestion estimates for smart-city operations, not ambulance path choice. That result was used here only to show that GRU-family models remained in active congestion-prediction use when the operational constraint was responsiveness. Zhang, Gao, Wang, Yiu, and Yin (2025) distilled a larger spatial-temporal teacher into a smaller student at AAAI 2025. This study did not distill. The paper was cited solely as evidence that compact models can approach heavier teachers; it does not describe the training procedure that produced `gru_improved_best.keras`.

Benarmas and Bey (2024) compared deep sequential models for road-traffic prediction and again placed GRU among computationally lighter options. Sahayaraj et al. (2024) reported large MAPE reductions from a hybrid GNN–GRU stack. Those MAPE figures were not claimed for the present METR-LA test set (MAE 3.48 mph, RMSE 6.04 mph). Hybrid spatial models were not re-implemented. The methodological choice was explicit: Jeong et al. (2021) had already shown that a stacked GRU is accurate enough on 15–30 minute highway speeds to serve as a cost model, at an inference cost compatible with repeated calls. That published trade-off, not a within-study LSTM bake-off, was why GRU was adopted.

Li et al. (2018) remained the dataset paper. METR-LA and PEMS-BAY exist as public five-minute speed archives because that work released them with a graph adjacency. Citing Li et al. (2018) does not mean DCRNN was implemented. The present predictor is a two-layer GRU on those archives. Ma et al. (2023) combined convolutional and gated recurrent blocks for short-term speed prediction; that hybrid was also not re-implemented, and their error figures were not transferred onto Table 4.3.

Taken together, the 2021–2025 prediction literature justified two statements that this study then tested. First, a GRU is still a legitimate congestion predictor when the product requirement is a short horizon and a tight latency budget. Second, the open problem named by Yin et al. (2022) and later by Qi et al. (2025) is not another increment of METR-LA MAE; it is whether a usable forecast can be consumed by a router that still answers inside a dispatch window. Section 2.5 turns to the papers that already joined prediction and search, and Section 2.6 to emergency-specific work that still, in the main, chose signals rather than paths.

---

## ADD 2 — end of Section 2.5 (after the paragraph that ends “not a state-of-the-art spatial-temporal predictor”)  (~850 words)

The integration papers that do exist must be read for what they measured, not for what their titles suggest. Werner et al. (2022), in *Proceedings of SEA 2022*, combined live and predicted travel times with time-dependent A* potentials and reported large query speed-ups on continental road graphs relative to Dijkstra. Predicted times in that work are an input to the potential; the paper does not train a GRU (or any other recurrent network) on METR-LA, does not sweep a remaining-time threshold for an emergency dispatcher, and relies on preprocessing that assumes edge weights are not rewritten every five minutes. At the 207-node detector graph used here, that preprocessor was unnecessary: time-dependent A* already returned in 0.37 ms, and the wait that mattered was GRU inference. Werner et al. (2022) therefore remain the closest routing ancestor and do not replace the present artefact.

Zhang, Khalgui, and Li (2021), in *Sensors* 21, 7330, coupled predictive signal control with vehicle route guidance in an Internet-of-Vehicles congestion model. The first author is Le Zhang. The paper is a prediction-plus-routing system, but it is not an emergency remaining-time controller, it is not a METR-LA 900-run, and it does not report a one-second dispatcher budget for a single priority vehicle. Zhang, Sun, and Liu (2022), in *ISPRS International Journal of Geo-Information*, described adaptive route planning for connected vehicles under incidents. That work is incident-aware routing for a connected fleet; it is not a GRU–δ sweep and it is not a source for cardiac-arrest mortality statistics.

Ikram et al. (2025) examined digital-twin-assisted emergency navigation with resource optimisation and reroute planning. A digital twin of a live city is a different artefact from a GRU trained on a public freeway archive. Their setting assumes an operational data loop that this study did not have. The paper was cited as a parallel emergency-navigation direction, not as a result that this simulation reproduced.

What remained after those distinctions was a narrow claim. Prediction and time-dependent search have been combined. Emergency services have been given signal priority and, in transit, corridor replanning. No reviewed paper trained a two-layer GRU on METR-LA, routed on that detector adjacency with time-dependent A*, exposed δ ∈ {0.05, 0.10, 0.15, 0.20} as a dispatcher control, and walked every method—including the proposed framework—on actual future speeds for 900 matched journeys. That is the integration this study designed and measured. It is not a claim that Werner et al. (2022) or Zhang, Khalgui, and Li (2021) failed; it is a claim that their published objects of study were different.

---

## ADD 3 — replace the Sasikala “useful performance comparison” sentence in 2.6  (~0 words net if you only replace)

**GET THIS**

```
Sasikala et al. (2025) applied modified static A* with IoT signal integration and reported 35 percent response time reductions, establishing a useful performance comparison for time-dependent predictive routing.
```

**REPLACE WITH**

```
Sasikala et al. (2025) applied modified static A* with IoT signal integration and reported a 35% response-time reduction in a simulated smart-city setting. That figure is a signal-priority result, not a path-choice result, and was not treated as a numerical target for Table 4.6.
```

---

## ADD 4 — end of Section 3.2 (after the pragmatism paragraph)  (~900 words)

Design Science Research Methodology was operationalised in six activities (Peffers et al., 2007). Problem identification was the ageing of a dispatch-time shortest path under five-minute traffic volatility, with life-safety consequences stated in Chapter 1. Objective definition was the four specific objectives in Section 1.4, including an empirical rather than assumed replanning threshold. Design and development produced three Python packages: prediction (`data_preprocessing.py`, `train_improved_gru.py`, `train_pems_bay.py`), routing (`td_astar.py`, `graph_builder.py`, `travel_times.py`), and control (`adaptive_controller.py` together with `simulation_core.py`). Demonstration used public METR-LA and PEMS-BAY archives rather than a private Nairobi feed, because the latter did not exist at the required five-minute detector resolution. Evaluation compared four baselines on identical origin–destination pairs, departure windows, and random seeds. Communication was the open repository and this thesis. No work plan or budget belongs in a thesis; those documents belonged to the proposal stage.

Internal validity rested on matching journeys: the same origin, destination, clock, and realised speeds, with five methods choosing the path. External validity was bounded on purpose. Chronological splits prevented the model from seeing later frames while training on earlier ones. A train-only scaler prevented the test partition from writing the marking scheme. Early stopping prevented selection of the last noisy epoch. Fixed seed 42 made the 75 pairs repeatable. Those controls do not convert Los Angeles freeways into Nairobi mixed traffic; they make the Los Angeles claim inspectable.

Hevner et al. (2004) required that a design-science evaluation state the claims the artefact is supposed to support. The claims here were three and only three. First, that a two-layer GRU trained on METR-LA would produce test error in a band already reported for comparable GRUs (Jeong et al., 2021). Second, that feeding those forecasts into time-dependent A* with a remaining-time controller would reduce ground-truth travel time relative to Dijkstra, historical A*, and reactive A*, without beating an oracle that used actual future speeds. Third, that the combined wait would remain under 1,000 ms. Claims that were not made—and were not tested—included a Nairobi field reduction, a lowest-MAE METR-LA predictor, and a 10–30% sensor-coverage experiment.

Pragmatism (Creswell & Creswell, 2018) justified simulation as the method of evaluation because the research questions asked for interval-scale travel time, latency, and replan counts under controlled regimes. A qualitative dispatcher study would have answered a different question. That study was listed as further research in Section 5.5 and was not presented as if it had been done.

---

## ADD 5 — end of Section 3.6  (~800 words)

The METR-LA predictor consumed 12 five-minute frames (60 minutes) and emitted six future frames (30 minutes) for each of 207 sensors. Two stacked GRU layers with 64 hidden units and dropout 0.2 after each recurrent layer supplied the temporal memory; a dense layer mapped the last hidden state to the six-step, 207-sensor target. Training used Adam, mean squared error on StandardScaler-transformed speeds, batch size 64, and early stopping with patience 10 on validation loss. The scaler was fitted on the training split only. Inverse transformation returned miles per hour so that routing costs remained physically interpretable. The same architecture, with a separate scaler fitted on the PEMS-BAY training split only, was trained for 325 sensors. A single tensor cannot hold 207 and 325 columns at once; joint training was therefore not performed.

Sequences were formed with a stride of one frame. After the chronological 70/15/15 split, the METR-LA training partition yielded 23,973 input sequences. Early stopping halted METR-LA training at 27 epochs (best validation loss 0.4335) and PEMS-BAY training at 79 epochs. Test MAE was 3.48 mph on METR-LA and 2.38 mph on PEMS-BAY. Those errors are inverse-transformed speeds, not losses on the scaled tensor. PEMS-BAY training and validation losses near 0.0024 and 0.0027 are scaled mean squared errors on that city’s scaler; they are not comparable in magnitude to the METR-LA scaled losses of 0.3847 and 0.4335, and they were not interpreted as evidence that the Bay model “overfit less” in physical units. The comparable quantities are the inverse-transformed MAE and RMSE in Table 4.4c.

GRU was selected from published evidence rather than from a within-study LSTM retraining. Jeong et al. (2021) reported that GRU matched or exceeded LSTM on highway speed prediction at lower parameter count. Jiang and Luo (2022) and Yin et al. (2022) documented that graph networks can beat that recurrent baseline on METR-LA MAE. The dispatch requirement was a combined wait near 40 ms. Spatial-temporal graph inference at every simulation step was therefore declined. Distillation (Zhang, Gao, et al., 2025) was also declined: the student in this study is the GRU itself, not a compressed teacher.

Zeros and non-positive loop readings were treated as missing and imputed with the sensor mean before scaling. That imputation is a limitation: a dropped detector is not a parked vehicle, and mean-fill attenuates genuine zeros. It is the procedure that produced the defended checkpoint, and it was applied identically on both archives.

---

## ADD 6 — new paragraphs on the text page AFTER Table 4.5 (not on the table page)  (~650 words)

Table 4.5 is read column-wise against Dijkstra (B1), not as a claim that the framework dominated every cell. Under incidents, mean framework time was 598.9 s against 727.5 s for Dijkstra, 723.2 s for historical A*, 603.7 s for reactive A*, and 580.5 s for the oracle. The large gap to Dijkstra and historical A* is the operational content of Objective 4: a 40% corridor slowdown that is invisible at dispatch, but visible to a 30-minute forecast and a remaining-time trigger, produced a detour. The small gap to reactive A* (598.9 s against 603.7 s) is expected once the incident is already in the current snapshot; the 30-minute horizon then adds little. The framework remained slower than the oracle, as required if B4 used actual future speeds.

Peak-hour means were 506.3 s (framework) against 513.1 s (Dijkstra and reactive A*), 552.5 s (historical A*), and 499.5 s (oracle). Widespread congestion leaves few quiet alternatives, so looking ahead helped only modestly. Off-peak means sat near 403 s for every method except a slightly slower historical A* (405.2 s). Empty roads are a negative control: a forecast and a current map should agree.

PEMS-BAY does not appear in Table 4.5 because PEMS-BAY was not a routing graph. The 325-sensor GRU was a second-city prediction check (Table 4.4c). Inserting Bay speeds into Los Angeles edges would have been a different, and invalid, experiment.

The four δ values were 0.05, 0.10, 0.15, and 0.20. Table 4.5 pools them (75 pairs × 4 thresholds = 300 journeys per scenario). Table 4.7 separates them. Pooling is why Table 4.6 reports N = 300 per row rather than N = 75.

---

## ADD 7 — on the text page AFTER Table 4.7 / after the δ = 0.20 paragraph (answers why 0.10 then 0.20)  (~500 words)

Chapter 3 specified δ = 0.10 as the mid-range candidate inside a 5–20% band drawn from decision-support practice: a threshold high enough to suppress noise, low enough to catch a material remaining-time jump. That value was a planned experimental centre, not a measured default. One-way ANOVA on reduction versus Dijkstra across the four policies returned F ≈ 0.001, p = 1.00. Mean reductions were 5.726%, 5.748%, 5.726%, and 5.767% at δ = 0.05, 0.10, 0.15, and 0.20. Replans per journey fell slightly from 0.45 to 0.39. A 40% corridor speed drop increases remaining time by more than 20%, so every tested policy still fired on incident journeys (about 1.03 replans). Decision-support theory then prefers the least frequent alert that still catches those incidents. After measurement, that policy was δ = 0.20. The Chapter 3 candidate of 0.10 was retained as the planned value and was not the recommended operational default.

F ≈ 0.001 is the ratio of between-policy variance to residual variance. It is near zero because the four group means are interchangeable. It is not evidence that the controller never replanned. Incident journeys replanned; the policies did not differ in travel time.

---

## ADD 8 — end of Section 3.11 (validity)  (~450 words)

Construct validity for travel time was ground-truth traversal: every method, including the framework, was walked on actual future speeds from the METR-LA test partition. Predicted costs selected the path; they did not mark the path. That separation is what made the oracle well-defined and what made the old predicted-as-journey-time tables indefensible. Latency construct validity was wall-clock time for time-dependent A* and for GRU inference on the hardware used for the reported run. Laptop re-measurement was expected to differ and was not substituted for the GitHub figures (0.37 ms, 39.3 ms, combined approximately 40 ms).

Statistical conclusion validity rested on matched pairs and on an explicit α = .05. Shapiro–Wilk tests rejected normality for most reduction distributions. Significance was therefore reported together with the directional means, and off-peak and many peak-hour cells have median 0%. The incident mean of 16.19% is not an artefact of a few outliers alone, but the distributions are skewed, and that limit was acknowledged. One-way ANOVA on δ assumed independence of the four policy groups; each group is a disjoint subset of the 900 journeys, so that assumption held. Multiple scenario tests were not Bonferroni-adjusted; the incident test (t = 26.43) and the peak-hour test (t = 3.81) would survive a conservative correction, and the off-peak test would not, which is the interpretation already given.

---

After these eight pastes, Word → Review → Word Count on Chapters 1–5. Target 20,200–21,000. If still short, add **one** extra paragraph per Chapter 2 theme (2.2, 2.3, 2.4) using only papers already in the reference list. Do not repeat the 16.19% paragraph.
