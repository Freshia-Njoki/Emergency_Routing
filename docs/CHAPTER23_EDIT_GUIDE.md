# Chapters 2–3 edit sheet (section → sentence → replace)

Same rules as Chapter 1. **Do not count balloon IDs.** Search **Review → Comments** for the words you typed (`Remove?`, `Fill RQ1`, `meaning`).

**Your questions from this turn (answers first):**

| You asked | Short answer |
|---|---|
| Keep my **purpose** (not the jargon replace)? | **Yes. Keep yours.** |
| Change article v0.3? | **Not for the thesis.** Only if you submit the journal draft. |
| RQ1 for Table 3.1 | Paste the sentence in §3.5 below. |
| Skip Nairobi-sensors sentence in 1.6? | **Yes, if 1.7/1.8 already say US data ≠ Nairobi.** |
| Delimitations okay? | **Yes**, if METR-LA = routing and PEMS-BAY = second GRU only. |
| Assumptions unchanged? | **Yes, they can stay.** |

Each item: **GET THIS / REPLACE WITH** goes in the thesis. **For you only** does not.

---

# Your Chapter 1 decisions (locked)

## Purpose — KEEP yours

This is fine:

> The purpose of this study was to design and evaluate through simulation a scalable Intelligent Route Optimisation Framework demonstrating potential for significantly reducing emergency vehicle travel time by anticipating traffic volatility through integrated predictive modelling and adaptive pathfinding.

**For you only.** “Significantly” is justified by the **incident** cell (16.19%), not by off-peak (~0%). You do not need my longer purpose. Optional extra clause, still plain: after `travel time` add `particularly when incidents disrupt the planned road`. Skip it if you are happy.

## Justification — skipping the sensors sentence is OK

You replaced the billions sentence and did **not** add the Nairobi-sensors line. That is allowed **if** Section 1.7 or 1.8 already says the numbers are Los Angeles benchmarks. Do not put that caveat in 1.6 and again in 1.7.

## Delimitations — OK if this is what you now have

- METR-LA = routing graph (207 nodes).
- PEMS-BAY = second-city GRU check, not a second 900-run.
- 15–30 min forecast, simulation, one vehicle.

If that is in 1.8, stop. Do not put 325 Bay sensors into Table 4.5.

## Assumptions — they can stay

FIFO, emergency vehicles delayed like general traffic, and historical METR-LA/PEMS-BAY patterns being “typical enough to train” are still true.

The OSM-mapping clause is slightly old (the 900-run used detector-to-detector links, not downtown OSM). **Leave it.** Chapter 3.9 is where the graph must be corrected, not Chapter 1.9.

## Article v0.3 — do you need to change it?

**No, not in order to finish the thesis.** `docs/research_article_v0.3.md` is the journal draft. It already has the defended numbers (3.48 / 2.38 mph, +16.19% incidents, 207-node sensor graph, δ = 0.20).

- Thesis purpose can stay in your simpler wording.
- Article 1.3 can stay in journal wording.
- When you later copy the article into a journal template, keep v0.3 numbers. Do **not** paste old `+0.17%` or `34,254` into the article.
- You do **not** need to rewrite v0.3 this week while editing Word Chapters 2–3.

---

# Table 3.1 — RQ1 (fill the dash)

**Location:** Chapter 3, Section 3.5, Table 3.1, row “Specific Objective 1: Literature review”, column “Research Question”.

**GET THIS** (the dash)

```
—
```

**REPLACE WITH** (same wording as Section 1.5 RQ1)

```
RQ1: What research gaps exist in the literature on emergency vehicle routing, traffic prediction, and time-dependent pathfinding that justify the development of an integrated predictive routing framework?
```

**For you only.** You are not inventing a new question. Copy 1.5 into the table so Objective 1 is not blank.

---

# Chapter 2

Do **not** delete Dijkstra (1959), A* (1968), Dreyfus (1969), Cho et al. (2014), Gorry (1971), or Peffers. KyU’s “recent literature” rule does not apply to the **foundations** of the algorithm you used.

## 2.1 Introduction

Keep. No balloon.

---

## 2.2 Classical pathfinding

### Balloons: Remove? on 1959 and 1968

**Action: KEEP** `Dijkstra's algorithm (1959)` and `The A* algorithm (Hart, Nilsson, & Raphael, 1968)`.

**For you only.** You used both as baselines. Removing the origin papers looks like you claimed the algorithms.

### Balloons: meaning / explain — haversine

**After:** `The haversine distance to the destination served as an admissible heuristic for urban routing.`

**INSERT (plain)**

```
Haversine distance is the great-circle distance between two points on the Earth, computed from latitude and longitude. In this study it was used only as a lower bound on remaining travel time: straight-line distance divided by free-flow speed. Because a vehicle cannot arrive sooner than that bound, A* remains optimal.
```

**For you only.** You do not need a map figure here. Think of it as “as the crow flies,” then divide by the fastest legal speed so the computer never cheats.

### Balloons: explain Bidirectional Dijkstra / ALT; Remove? Pohl, Geisberger, Goldberg; discuss NP-completeness

**KEEP** the citations. Add one short explanation after `the ALT algorithm (Goldberg & Harrelson, 2005).`

**INSERT**

```
Bidirectional Dijkstra searches from both the origin and the destination at once. Contraction Hierarchies add shortcut links during a slow setup phase so later queries are fast. ALT uses a few landmark places and the triangle inequality to guess remaining distance. None of these methods were used as the live router here, because their setup assumes edge times that do not change every five minutes.
```

**GET THIS** (NP-completeness clause — too sharp, unexplained)

```
and Chen et al. (2021) established the NP-completeness of online route planning over time-dependent networks.
```

**REPLACE WITH**

```
and Chen et al. (2021) showed that planning a route while travel times keep changing is computationally hard in the general case, which is why this study used a deterministic FIFO approximation rather than a fully stochastic online planner.
```

**For you only.** NP-complete means “no fast exact method is known for the fully general problem.” You did **not** solve Chen’s hard problem. You used a simpler, valid special case (FIFO, discrete five-minute slots). That does not weaken you.

---

## 2.3 Time-dependent shortest path

### Balloon: Remove? Dreyfus 1969

**KEEP.** This is the FIFO/TDSP foundation.

### Balloon: Meaning? non-decreasing travel time

**After:** `Equivalently, travel time functions must be non-decreasing in departure time.`

**INSERT**

```
In plain terms, leaving later must not get the vehicle there earlier. If a predicted travel time went negative or reversed that order, Time-Dependent A* could pick a nonsense path. Clipping every predicted time to at least one second stopped that.
```

**For you only.** That clip is in the cost builder. It is why FIFO is not just a slogan.

---

## 2.4 Traffic prediction

### Balloon: Remove? Box and Jenkins 1976

**KEEP one mention** as history (`ARIMA models (Box & Jenkins, 1976)`). It is in the reference list if cited. Do not build a whole ARIMA section.

**After Jeong et al. (2021)** (the sentence on GRU vs LSTM), **INSERT the new papers** (this is where the eight go, in plain language):

```
Jiang and Luo (2022) and Yin et al. (2022) surveyed graph neural networks and deep traffic predictors and showed that spatial-temporal models now occupy the lowest-error band on METR-LA, while gated recurrent units remain a strong temporal baseline. That literature was used here to justify GRU as a latency-bounded dispatch predictor, not as the lowest-MAE model on the leaderboard. Abdullah et al. (2023) likewise treated GRU-style recurrent nets as a practical congestion tool in smart-city settings. Lan et al. (2022) and Shao et al. (2022) illustrated how far dynamic and pre-trained spatial-temporal graphs have moved; those models were cited as the accuracy ceiling this study declined because of dispatch latency. Zhang, Gao, Wang, Yiu, and Yin (2025) showed that compact models can approach heavier teachers through distillation; this study did not distill, but that efficiency trend supports keeping a small GRU in the loop.
```

**GET THIS** (false claim in 2.8.2 — fix when you reach 2.8.2; listed here so you do not also claim LSTM in 2.4)

Do not write that you trained LSTM in this study. Jeong already covers GRU vs LSTM.

**For you only.** Sahayaraj’s 56% MAPE drop is **their** hybrid GNN, not your MAE. Do not write “this study reduced MAPE by 56%.”

---

## 2.5 Integration of prediction and routing

### Balloon: Werner close / does it nullify me?

**KEEP** your Werner paragraph. It already distinguishes you. Optional extra sentence at the end of that paragraph:

**INSERT after** `rather than emergency dispatch.`

```
Zhang, Khalgui, and Li (2021) also coupled prediction with routing in an Internet-of-Vehicles congestion setting, but without an emergency remaining-time threshold or a dispatcher-facing replanning policy. Werner et al. (2022) therefore remains the closest routing ancestor and does not replace the present artefact.
```

**For you only.** Werner is faster on huge maps because of preprocessing. You refresh weights every five minutes, train a GRU, target emergency dispatch, and sweep δ. That is the distinction. **Do not delete Werner.**

---

## 2.6 Emergency vehicle routing

### Balloon: discuss YOLOv8

**After** `Hugar et al. (2025) combined YOLOv8 detection with reinforcement learning for adaptive signal control but did not provide route-level optimisation.`

**INSERT**

```
YOLOv8 is a camera object detector. In that paper it spotted vehicles at junctions so signals could turn green. It does not choose the next road. This study does not use cameras or YOLOv8.
```

### Balloon: Abuaisha close to my work

**KEEP** the fixed-corridor distinction you already wrote. Optional after `limiting its direct applicability.`

**INSERT**

```
Chowdhury et al. (2023) proposed a UAV-assisted emergency-vehicle priority scheme and reported about 8% lower simulated response time. The literature they surveyed still concentrated on identification and green waves rather than a learned 15–30 minute path. That paper is related ITS work; it is not this GRU plus Time-Dependent A* loop.
```

### Balloon: “Sounds like I didn’t do much” — paraphrase

**GET THIS**

```
The collective body of evidence confirmed that each component — signal control, predictive rerouting, and time-dependent routing — had been addressed individually, but no study combined all three within a single framework explicitly designed for emergency dispatch.
```

**REPLACE WITH**

```
Prior work had already solved pieces of the problem: intersection priority, transit replanning on fixed corridors, and time-dependent search on predicted or live times. What this study added was the combination of a trained GRU, Time-Dependent A* on five-minute costs, and a remaining-time threshold, built as dispatcher decision support and measured on 900 ground-truth journeys. That combination, not a new shortest-path formula, is the contribution.
```

**For you only.** You did not invent A*. You integrated three parts and measured them. That is a master’s contribution.

---

## 2.7 Research gaps

### Balloon: Gap 1 “nullifies my work”

**GET THIS**

```
Existing studies addressed prediction and routing independently, leaving the integration challenge unresolved (Qi et al., 2025).
```

**REPLACE WITH**

```
Prediction and routing have each been studied in depth, and a few systems combine live or predicted times with time-dependent search (Werner et al., 2022; Zhang, Khalgui, & Li, 2021). What remained thin was an emergency dispatch loop that learns speeds with a GRU, routes on those costs, and exposes an empirically tested remaining-time threshold under a one-second recommendation budget (Qi et al., 2025; Chowdhury et al., 2023).
```

**For you only.** “Nobody ever integrated anything” is false and makes Werner look like it kills you. “This emergency GRU + TD-A* + δ loop was missing” is true.

---

## 2.8 Theory

### Balloons: Represents? / is the formula recommended?

**KEEP the formula.** After the equation, **INSERT**

```
The formula says: the journey time of path P leaving at time t₀ is the sum of the time to drive each successive road, where each road’s time depends on the clock when the vehicle enters it.
```

**For you only.** Yes, the thesis should show this. It is the thing TD-A* minimises. You do not need to paste Python (`td_astar.py`) here; one file name in 3.7 is enough.

### Balloon: τ is not in the expression

**KEEP** `τ(u,v)(t)`. **INSERT before the “where G = …” sentence:**

```
The symbol τ(u,v)(t) is the travel time of road (u,v) if entered at time t. It is the same τ that appears inside the sum above.
```

### Balloon: Remove? Dreyfus 1969, Cho 2014, Gorry 1971

**KEEP all three.** They are theory, not “old papers to delete.”

### Balloon: discuss spatial dependencies

**After** `does not explicitly capture spatial dependencies between road network sensors—a limitation compared to graph-based architectures such as DCRNN.`

**INSERT**

```
Neighbouring detectors often slow down together. A graph model passes messages along the map; a plain GRU sees each detector mainly as a time series. That is why DCRNN-style models can beat GRU on MAE (Jiang & Luo, 2022). This study accepted that gap in exchange for faster inference.
```

**GET THIS** (you did not train LSTM in this study)

```
LSTM is retained as an experimental comparison model to empirically quantify this trade-off.
```

**REPLACE WITH**

```
LSTM was not retrained in this study; the GRU versus LSTM trade-off was taken from Jeong et al. (2021).
```

---

## 2.9 Conceptual framework

**GET THIS** (implies one model on both cities)

```
this component uses a GRU neural network trained on METR-LA and PEMS-BAY datasets to analyze historical traffic patterns
```

**REPLACE WITH**

```
this component uses a GRU neural network trained on METR-LA to analyse historical traffic patterns
```

Then add, still in Component 1:

```
A second GRU with the same architecture was trained on PEMS-BAY to check prediction quality in another city; it did not supply costs to the router.
```

**GET THIS** if still present under moderators

```
Sensor data availability (full density vs. reduced 10–30% for Nairobi simulation)
```

**REPLACE WITH**

```
Sensor data availability (full detector coverage in the reported experiments; reduced coverage reserved as further research)
```

**For you only.** The 900-run was **not** a 10–30% Nairobi downsample. Do not let Figure 2.1 promise a test you did not run.

---

# Chapter 3

## 3.1 Introduction

Keep. Optional: `METR-LA and PEMS-BAY` is fine here because both were **used** (prediction). Routing still METR-LA only — you will say that in 3.4 and 3.9.

## 3.2 Philosophy

### Balloon: Remove Creswell 2018?

**KEEP.** Pragmatism/DSRM needs a methods cite. 2018 is the edition, not “outdated science.”

## 3.3 Research design

### Balloon: Remove Morgan 2014?

**KEEP.** Same reason.

Typo in the DSRM sentence: **GET THIS** `METR-LA  ans PEMS BAY` **REPLACE WITH** `METR-LA and PEMS-BAY`.

**After** the six DSRM activities, **INSERT** (plain)

```
Demonstration used public METR-LA and PEMS-BAY archives because Nairobi did not have a matching five-minute detector feed for this study. Evaluation compared four baselines on the same origin–destination pairs, departure windows, and random seed.
```

---

## 3.4 Data collection

### Balloon: discuss linear interpolation / did gaps break the model?

**GET THIS**

```
Data quality: sensor dropout rates of approximately 8% were addressed through linear interpolation for gaps shorter than 30 minutes; longer gaps resulted in segment exclusion
```

**REPLACE WITH**

```
Data quality: readings at or below zero were treated as missing and filled with that sensor’s mean speed before training. Those holes are dropped loops, not parked cars, and they are not the reason routing percentages changed between drafts. The improved 900-run used a fully instrumented detector graph, not the old map in which most roads had no sensor.
```

**For you only.** Your code fills zeros with the column mean (`data_preprocessing.py`). It does **not** do 30-minute linear interpolation. Do not describe a method you did not run. Gaps did **not** cause the old 78% or 0.17% tables; those were evaluation bugs.

### Balloon: 5 or 6 months PEMS-BAY?

**GET THIS** `Duration: 6 months (January to May 2017), yielding 52,128 observations per sensor`  
**REPLACE WITH** `Duration: January to May 2017 (five months), yielding 52,116 observations per sensor`

**For you only.** January–May is five calendar months. Use 52,116 (standard PEMS-BAY) unless your file prints another length.

### Balloon: where does 23,977 / 16.9 million come from?

**GET THIS**

```
Data were split chronologically to prevent temporal data leakage: 70 percent training (23,977 samples), 15 percent validation (5,138 samples), and 15 percent test (5,139 samples), ordered by time.
```

**REPLACE WITH**

```
METR-LA contained 34,272 five-minute frames and 207 sensors. After a chronological 70/15/15 split, sliding windows were cut inside each split, giving 23,973 training, 5,123 validation, and 5,125 test windows. PEMS-BAY’s 16.9 million figure is 325 sensors × about 52,116 frames (cells in the table), not 16.9 million readings per sensor.
```

**For you only.** 23,973 is `X_train` in `training_data.npz`. 6.5 million ≈ 207 × 34,272. Do not mix window counts with raw frames.

---

## 3.5 Instruments / Table 3.1

Fill RQ1 (above).

### Balloon: Discuss ANOVA across delta values

**After the ANOVA cell, or in a sentence under the table, INSERT**

```
ANOVA asked whether the four δ values produced different travel-time reductions. Chapter 4 reports the test; Chapter 3 only names the method.
```

**For you only.** In the 900-run, *F* ≈ 0.001, *p* = 1.00: the four thresholds **tied** on travel time. That is not a failed study. Incidents were large enough that 5% and 20% both fired. You pick δ = 0.20 later because it talks less, not because it was faster.

---

## 3.6 GRU module

### Balloon: meaning of 12 time steps

**After** `An input layer accepted 12-time steps (60 minutes of 5-minute resolution data).`

**INSERT**

```
The model always looked at the last hour: twelve speed readings, five minutes apart. At the next clock tick the oldest reading was dropped and the newest added (a sliding window). It then wrote six future readings (the next half hour).
```

### Balloon: Adam

**KEEP** `Adam optimiser`. Optional: after it, `which adapts a separate step size for each network weight.` Do not paste a textbook of RMSprop.

**For you only.** Adam is the usual Keras trainer. You used it; that is enough.

---

## 3.7 Time-dependent routing

### Balloons: simulate visualisation (six-element costs / unmapped edges / FIFO clip)

Do **not** add a cartoon unless you want a simple Figure 3.2. Add these three plain sentences after the haversine paragraph:

**GET THIS** (B3 name — must match Chapter 4)

```
Four baseline algorithms were implemented: Dijkstra with current conditions (B1), Static A* with historical averages (B2), Static A* with current conditions (B3), and Oracle A* with actual future travel times (B4).
```

**REPLACE WITH**

```
Four baseline algorithms were implemented: Dijkstra with current conditions (B1), static A* with historical averages (B2), reactive A* that could replan from the current snapshot when a slowdown was already visible (B3), and oracle A* with actual future travel times (B4).
```

**GET THIS**

```
Edges without sensor mapping used a constant free-flow travel time throughout, consistent with the fallback applied during sensor mapping (Section 3.5).
```

**REPLACE WITH**

```
On the detector graph used for the 900 experiments, every edge had a sensor speed. Constant free-flow fallback applied only to the unused downtown OpenStreetMap mode, not to the reported tables.
```

**INSERT after the six-element array sentence** (this is the “visualisation” in words)

```
Those six numbers are the predicted time to cross that road if the vehicle arrives in slot 0, 1, 2, 3, 4, or 5 (now, five minutes later, …, 25–30 minutes later). As the simulated vehicle moved, the clock index advanced so the router read the matching slot.
```

**For you only.** Picture six sticky notes on each road. FIFO clip: if the GRU spat out 0 or a negative time, it was raised to 1 second so “leave later, arrive earlier” could not happen.

---

## 3.8 Replanning

Keep the four δ values. **After** the formula sentence, **INSERT**

```
Here δ is the remaining-time trigger (5% means “speak if the rest of the trip looks 5% worse”). It is not the statistical significance level α = .05 used in Chapter 3.10.
```

**GET THIS** if you still say remaining time was compared with the original full trip — you should not. The improved controller uses remaining time from the **current** position.

If 3.8 still defines T_old as the original dispatch estimate, **REPLACE the formula line with**

```
A new recommendation was issued when remaining time on the current path, from the vehicle’s present position, grew by more than δ, or when a newly computed path was better by more than δ.
```

**For you only.** The old T_old = full original trip produced **zero replans**. Do not describe that bug as the method.

---

## 3.9 Evaluation setup — this section must change

### Balloon: meaning of lowest 25th percentile

**After** `peak-hour (departure slots where mean sensor speed fell in the lowest 25th percentile)`

**INSERT**

```
Peak hour meant the slowest quarter of departure times (mean speed across sensors in the bottom 25%). Off-peak meant the fastest quarter. Incident meant a 40% speed drop on roads that lay on the planned corridor, held so the vehicle actually met the jam.
```

### Balloon: 397 nodes / 1,024 edges — how it affected % and threshold

**GET THIS**

```
The road network was extracted from OpenStreetMap using OSMnx (Boeing, 2025), producing a directed graph of 397 nodes and 1,024 edges for the Los Angeles study area. Sensor-to-edge mapping covered 190 edges.
```

**REPLACE WITH**

```
The reported 900 journeys used the METR-LA detector adjacency: 207 nodes, 1,515 directed edges, every edge instrumented. Downtown OpenStreetMap (397 nodes, 1,024 edges, 190 sensor-mapped) was not the graph behind the result tables. On that older map most roads had a fake free-flow speed, which flattened baseline differences and was dropped for the defended experiments.
```

**For you only.** 18.6% mapping **did** hurt the old run (peak detours onto “empty” unmapped streets; weak incident targeting). It did **not** set δ. After the sensor-graph rerun, travel time was the same at 5–20% δ; you recommend 0.20 for fewer alerts. Do not discuss 397 nodes in Chapter 4 as if they were the 900-run.

### Balloon: harmonious reason for four baselines

Your 3.9 baseline paragraph is already good. Keep it once B3 is named **reactive A*** (see 3.7). No extra jargon.

**For you only.** B1 = what dispatchers do now. B2 = weekly average. B3 = replan only after the jam is visible, no 30-minute GRU. B4 = crystal ball. You need all four so “we beat Dijkstra” cannot be the whole story.

---

## 3.10 Data analysis

### Balloon: paired t-tests — applicability?

**KEEP.** **INSERT after** `Paired t-tests were used for RQ2…`

```
Each origin–destination pair was driven once by the framework and once by each baseline on the same clock and the same realised speeds, so the observations were paired.
```

### Balloon: Shapiro-Wilk — remove? simplify?

**KEEP one clause**, simplify:

**GET THIS**

```
Wilcoxon signed-rank tests served as the non-parametric alternative for paired data where the Shapiro-Wilk test indicated non-normality.
```

**REPLACE WITH**

```
Where a Shapiro-Wilk test on a scenario slice suggested the differences were not normal, a Wilcoxon signed-rank test was used as the paired alternative. Both families were interpreted at α = .05.
```

### Balloon: How ANOVA for RQ3?

**INSERT**

```
ANOVA placed the 900 reductions versus Dijkstra into four groups by δ (0.05, 0.10, 0.15, 0.20) and tested whether the group means differed.
```

### Balloon: discuss Pearson and Spearman

**GET THIS** if you did not actually compute them in the 900-run report

```
Pearson and Spearman correlation were applied for RQ4 to quantify the relationship between GRU prediction accuracy and route optimality.
```

**REPLACE WITH**

```
RQ4 was answered with paired travel-time tests against the four baselines, plus latency and replan counts. A correlation between MAE and journey time was not required for that claim.
```

**For you only.** Do not promise Pearson in Chapter 3 if Chapter 4 never shows it. The improved `full_report.txt` uses t-tests and ANOVA, not a MAE–travel-time scatter.

### Balloon: δ 5–20 vs α = 0.05

**INSERT at the end of 3.10**

```
The four δ values (5%, 10%, 15%, 20%) are replanning policies. The significance level α = .05 is the statistical rule for those tests. They share the digits 0.05 only in the first policy; they are not the same quantity.
```

---

## 3.11 Validity

### Balloon: meaning of seed=42

**INSERT after** `fixed random seeds (seed=42)`

```
Seed 42 fixed the random draw of the 75 origin–destination pairs so the same journeys could be repeated. It does not make Los Angeles into Nairobi.
```

**GET THIS** if 3.11 still claims you already ran 10–30% coverage

```
External validity was addressed through sensitivity analysis reducing sensor coverage to 10 to 30 percent to simulate conditions analogous to Nairobi's sparser infrastructure.
```

**REPLACE WITH**

```
External validity was bounded on purpose: methods were demonstrated on United States freeway detectors. A 10 to 30 percent coverage run, as a Nairobi analogue, remains further research and was not the reported 900-run.
```

---

## 3.12 Ethics

Keep. No balloon that requires a replace.

---

# After Chapters 2–3 (checklist)

1. Ctrl+F `397 nodes` `1,024 edges` `18.6%` — should appear only as the **unused OSM mode**, not as the 900-run design.
2. Ctrl+F `LSTM is retained` — gone.
3. Ctrl+F `6 months (January` — gone.
4. Add to References: Jiang and Luo (2022); Yin et al. (2022); Chowdhury et al. (2023); Abdullah et al. (2023); Zhang, Khalgui and Li (2021); Lan et al. (2022); Shao et al. (2022); Zhang, Gao, Wang, Yiu and Yin (2025). APA list already supplied.
5. Do not paste Chapter 4 numbers into Chapter 2. Chapter 2 may cite 12–18% as **Abuaisha’s** transit result, not yours.

Chapter 4 next, same format, after you say Chapter 2–3 are in.
