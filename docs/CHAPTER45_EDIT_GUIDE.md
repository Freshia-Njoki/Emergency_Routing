# Pin-the-inserts (your questions) + Chapters 4–5

**Do not count balloon IDs.** Work by heading and the quoted sentence.

---

## 1.7, 1.8, 1.9 — are they okay as they are?

### 1.7 Limitations — **almost. Change only the last sentence.**

The Nairobi / freeway / simulation sentences can stay. They already cover “this is not a Nairobi field trial,” so you did **not** need that extra sentence in 1.6.

**GET THIS** (last sentence only)

```
Sensor-to-edge mapping covered only 18.6% of graph edges; the remaining edges used free-flow speed estimates rather than GRU-predicted travel times.
```

**REPLACE WITH**

```
An earlier OpenStreetMap extract mapped sensors to only 18.6% of edges; that map was not used for the reported 900 journeys. Those journeys used the METR-LA detector graph, on which every edge had a sensor speed.
```

**For you only.** If you leave 18.6% as a fact about the *study*, Chapter 4 will contradict you. If that last sentence is already gone in your Word file, 1.7 is fine.

### 1.8 Delimitations — **okay with one short add** if you still only name METR-LA.

Keep: urban networks, 15–30 min, simulation, one vehicle, no multi-vehicle, no live Nairobi sensors.

**GET THIS**

```
using METR-LA as the primary evaluation dataset. The research was delimited to short-term prediction (15 to 30 minutes), simulation-based evaluation, and single-vehicle route optimisation. Road network modelling used OpenStreetMap data for Los Angeles County.
```

**REPLACE WITH**

```
using METR-LA as the routing dataset and PEMS-BAY only as a second-city check of the same GRU. The research was delimited to short-term prediction (15 to 30 minutes), simulation-based evaluation, and single-vehicle route optimisation.
```

If you already pasted this in Word, **stop.** 1.8 is done.

### 1.9 Assumptions — **yes, they can stay as they are.**

FIFO, typical traffic for training, EVs delayed like other traffic: all still true. The OSM-mapping clause is slightly old; do not spend time on it. Fix the graph in **3.9 and 4.3.2**, not here.

---

## Journal article — is it fine to submit?

**The numbers in `docs/research_article_v0.3.md` are the defending numbers.** You may submit *that* draft to a journal after you:

1. Paste it into the journal’s Word/LaTeX template.
2. Insert figures from `results/simulation/figures/` and `visualizations/improved_gru_training.png`.
3. Use the corrected Abdullah article **5949** (not 5716) and cite the distillation paper as **Zhang, Gao, Wang, Yiu, and Yin (2025)** (AAAI), not Wang et al. on arXiv.

It is **not** a camera-ready PDF yet (template, figures, cover letter, venue rules). It **is** scientifically aligned with the improved 900-run. Do **not** submit the current thesis Chapter 4 tables (123 s / +0.17% / 0 replans) as a paper.

Thesis and article can differ in tone. Keep your simpler thesis purpose.

---

## RQ1 for Table 3.1 — brief, like the others

Other cells: `RQ2: Travel time reduction vs baselines` / `RQ3: Optimal threshold policy`.

**GET THIS** `—`  
**REPLACE WITH**

```
RQ1: Gaps in EV routing, prediction, and time-dependent pathfinding
```

---

## Citations — years okay?

**Yes for the papers you were told to add**, if the reference list matches the in-text year:

| In-text | Year | Note |
|---|---|---|
| Jiang & Luo | 2022 | OK |
| Yin et al. | 2022 | OK |
| Chowdhury et al. | 2023 | OK |
| Abdullah et al. | 2023 | Article **5949**, DOI `10.3390/su15075949` |
| Zhang, Khalgui, & Li | 2021 | OK |
| Lan et al. | 2022 | ICML / PMLR 162 |
| Shao et al. | 2022 | KDD |
| Zhang, Gao, Wang, Yiu, & Yin | 2025 | AAAI 39(1), 1093–1101 |
| Dijkstra | 1959 | Keep |
| Hart et al. | 1968 | Keep |
| Dreyfus | 1969 | Keep |
| Cho et al. | 2014 | Keep |
| Li et al. | 2018 | DCRNN / METR-LA |
| Jeong et al. | 2021 | Keep |
| Werner et al. | 2022 | Keep |
| Abuaisha et al. | 2025 | Keep |
| Qi et al. | 2025 | Keep |
| Boeing | 2025 | Match the PDF year you downloaded |
| PEMS-BAY duration | 2017 | Five months (Jan–May), not six |

**For you only.** Two Zhangs: 2021 = IoV prediction+routing; 2025 = distillation. First mention of 2025: `Zhang, Gao, et al. (2025)`.

---

## Are all corrections already in the thesis?

**No.**

| Place | Status |
|---|---|
| Code and 900-run (`full_report.txt`, branch `cursor/improve-ev-routing-framework-c48b`) | Done |
| Journal draft v0.3 numbers | Done |
| Your Word thesis Chapters 4–5 | **Not done** — still 123 s, +0.17%, 0 replans, 397 nodes, δ = 0.10, 17 epochs, MAE 3.42, 0.315 ms |
| Word Chapters 1–3 | Only what you pasted yourself |

Until you replace Chapter 4 tables, the thesis is **not** “as expected.”

---

## Gap 1 was too long — use this short one

**Section 2.7, Gap 1, second sentence.**

**GET THIS**

```
Existing studies addressed prediction and routing independently, leaving the integration challenge unresolved (Qi et al., 2025).
```

**REPLACE WITH** (short)

```
Prediction and routing are often studied apart. A few systems combine them, but not as an emergency GRU, time-dependent A*, and remaining-time threshold under a one-second dispatch budget (Qi et al., 2025; Werner et al., 2022).
```

That is two sentences. Do not paste the long version.

---

## The three sentences you could not find (Chapter 3)

All three are **real sentences already in your DOCX**. Search the first five words.

### A. Unmapped edges / free-flow (Section 3.7, second paragraph)

**Find this exact sentence:**

```
Edges without sensor mapping used a constant free-flow travel time throughout, consistent with the fallback applied during sensor mapping (Section 3.5).
```

**REPLACE WITH**

```
On the detector graph used for the 900 experiments, every edge had a sensor speed. Constant free-flow fallback applied only to the unused downtown OpenStreetMap mode.
```

**For you only.** “Unmapped” meant: on the old OSM map, most streets had no detector, so the computer pretended they ran at 30 mph. That is **not** how the defended 900-run worked.

### B. After the six-element array sentence (same paragraph, the sentence *before* the unmapped one)

**Find this exact sentence:**

```
Time-dependent edge costs were implemented as six-element arrays indexed by elapsed five-minute slots since departure, advancing as the simulated vehicle moved through the network.
```

**Leave that sentence.** Put the new sentence **immediately after it:**

```
Those six numbers are the predicted time to cross that road now, in five minutes, in ten minutes, and so on up to 25–30 minutes. As the vehicle moved, the clock index advanced so the router read the matching slot.
```

**For you only.** This *is* the visualisation: six sticky notes on each road. No figure required.

### C. 10–30% coverage (Section 3.11, second sentence)

**Find this exact sentence:**

```
External validity was addressed through sensitivity analysis reducing sensor coverage to 10 to 30 percent to simulate conditions analogous to Nairobi's sparser infrastructure.
```

**REPLACE WITH**

```
External validity was bounded on purpose: methods were demonstrated on United States freeway detectors. A 10 to 30 percent coverage run, as a Nairobi analogue, remains further research and was not the reported 900-run.
```

**For you only.** You did **not** already run that downsample. There is no script result to cite. Saying you did it in 3.11 and then listing it as future work in 5.5 is a contradiction.

---

## 3.8 — where the correction goes

**Heading:** `3.8 Route Recommendation Mechanism`

**The whole paragraph starts:** `The framework employed threshold-based triggering…`

**Step 1 — GET THIS** (the formula sentence)

```
A new recommendation was issued when: [T_new(current, dest) minus T_old(current, dest)] divided by T_old(current, dest) exceeded threshold δ.
```

**REPLACE WITH**

```
A new recommendation was issued when remaining time on the current path, from the vehicle’s present position, grew by more than δ, or when a newly computed path was better by more than δ.
```

**Step 2 — after the next sentence** (`Four threshold values δ ∈ {5%, 10%, 15%, 20%} were evaluated.`) **INSERT**

```
Here δ is the remaining-time trigger. It is not the statistical significance level α = .05 used in Section 3.10.
```

Leave the sliding-window sentence as it is.

**For you only.** If T_old is the *original full trip from the station*, the controller almost never fires (your old 0-replan tables). Remaining time must be from *where the vehicle is now*.

---

## 3.10 — where to insert “paired” and “δ vs α”

**Heading:** `3.10 Data Analysis Methods`

### Paired t-tests

**Find:**

```
Paired t-tests were used for RQ2 because the experimental design generated matched pairs — each origin-destination route was tested under the framework and each baseline under identical conditions.
```

Your sentence is already almost enough. **INSERT only this clause at the end of that sentence** (after `identical conditions`):

```
: the same origin, destination, departure time, and realised speeds.
```

Do not add a new paragraph.

### δ vs α

**Find the last two sentences of 3.10:**

```
All statistical tests used α = 0.05 significance level. t-statistics were computed as t = (mean/SD) × √N.
```

**INSERT between those two sentences:**

```
The four δ values (5%, 10%, 15%, 20%) are replanning policies. α = .05 is only the statistical rule. They are not the same 0.05.
```

---

# Chapter 4 — replace old numbers (mandatory)

Ctrl+F and delete these from Chapters 4–5 if they describe *your* results: `123.09`, `588.3`, `+0.17%`, `0.00` replannings as a universal fact, `17 epochs`, `3.42` MAE, `0.315 ms`, `δ = 0.10` as the recommended default, `397-node` as the 900-run graph, `MinMaxScaler` as the METR-LA scaler, `78`.

Use **`results/full_report.txt`**. Figures: `visualizations/improved_gru_training.png`, `improved_gru_predictions.png`, `results/simulation/figures/fig1`–`fig5`.

---

## 4.1 Introduction

**GET THIS**

```
All experiments were conducted on the METR-LA dataset (207 sensors, 34,254 time steps) using a real 397-node, 1,024-edge OpenStreetMap road network for Los Angeles County.
```

**REPLACE WITH**

```
Routing experiments used the METR-LA detector graph (207 sensors, 34,272 time steps, 207 nodes, 1,515 edges). A second GRU was trained on PEMS-BAY for prediction checks only.
```

**Your comment (OSM / LA data):** LA detectors *are* the data. Useful because they are the public benchmark with five-minute speeds. They are not Nairobi measurements.

**37 papers 2018–2026:** keep the count if that is what you reviewed. After adding the eight papers, Ctrl+F the reference list and update “37” if the total changed (e.g. 45). Foundations before 2018 stay in Chapter 2 and do not have to sit in this “2018–2026” tally.

---

## 4.2 Objective 1

**Werner nullifies?** No. Keep the cite.

**GET THIS**

```
Werner et al. (2022) represented the closest precedent but relied on preprocessing-based speedup techniques incompatible with five-minute weight update cycles and incorporated no machine learning model.
```

**REPLACE WITH**

```
Werner et al. (2022) remained the closest routing precedent. That work used predicted and live times inside time-dependent A*, but not a trained GRU, not an emergency remaining-time threshold, and not this 900-journey ground-truth test.
```

**For you only.** Closest ≠ copy. You are allowed to stand next to Werner.

In Table 4.1, EV Routing gap row: you may add Chowdhury et al. (2023) next to Hugar/Sasikala/Abuaisha.

---

## 4.3.1 GRU module

**GET THIS** `trained on the METR-LA and PEMS BAY datasets` / `gru_improved_best.h5`  
**REPLACE WITH** `Two GRUs were trained separately (`gru_improved_best.keras` on METR-LA; `gru_bay_best.h5` or the Bay checkpoint on PEMS-BAY).`  
File name in the thesis: **`gru_improved_best.keras`** is what the improved pipeline saves. If your folder still has `.h5`, write whichever file you actually used. Do not imply one file held both cities.

**Table 4.2 row “207, 325”:** keep both numbers; add a note under the table: `Two models, not one joint network.`

**Figure 4.1 interpret:** training loss should fall; validation should follow it. If they stay close, the model is not merely memorising. Use `improved_gru_training.png` (27 epochs), not the old 17-epoch plot.

**Replace Table 4.3 values:**

| Metric | METR-LA (defended) |
|---|---|
| Epochs | 27 |
| Final train loss | 0.3847 |
| Best val loss | 0.4335 |
| Test MAE | **3.48 mph** |
| Test RMSE | **6.04 mph** |
| GRU inference | **39.3 ms** (not 69.1 ms) |

**GET THIS** `converged in 17 epochs` and `MAE of 3.42` and `MinMaxScaler`  
**REPLACE WITH** `converged in 27 epochs` / `MAE of 3.48 mph` / `StandardScaler fitted on the training split only`.

**After the MAE sentence, INSERT (plain, one line)**

```
That error sits in the published GRU band on METR-LA (Jeong et al., 2021). It is not the lowest MAE in the graph-neural-network literature, and it was not claimed to be.
```

**PEMS in Table 4.3?** No. PEMS stays in Table 4.4c. Including 325 sensors in the METR-LA MAE cell would be a different model.

**For you only.** 3.48 vs 3.42 is the train-only scaler run. Defend 3.48. 17 epochs / 3.42 was the older checkpoint.

---

## 4.3.2 Road network — replace the whole subsection story

**GET THIS** the paragraph that starts `The road network for the Los Angeles study area was extracted from OpenStreetMap`

**REPLACE WITH**

```
The reported routing graph was the METR-LA detector adjacency: 207 nodes, 1,515 directed edges, every edge instrumented. Downtown OpenStreetMap (397 nodes, 1,024 edges, 190 mapped) was not used for the 900-run tables.
```

**Replace Table 4.4:**

| Property | Value |
|---|---|
| Source | METR-LA detector adjacency (Li et al., 2018) |
| Nodes | 207 |
| Directed edges | 1,515 |
| Sensor-mapped edges | 1,515 (100%) |
| Fallback 30 mph | Not used in the reported run |

**Figure 4.3:** do not keep “190 edges highlighted” as the headline figure. Use the sensor-graph figure from the branch, or caption the old OSM map as *unused optional mode*.

**For you only.** 18.6% = 190/1024. The other 81.4% was fake 30 mph. That flattened methods and tempted peak-hour detours. It is **not** “gaps in METR-LA.” Good practice is 100% coverage on the detector graph, which you now have.

`3-tuples to 2-tuples`: OSM edges are (from, to, key). NetworkX needed (from, to). Only relevant if you describe OSM mode. Skip it on the sensor graph.

---

## 4.3.3 Implementation table

You may keep file names. Updates:

- Loader: `gru_improved_best.keras` and train-only `scaler.pkl`; 207 sensors for routing.
- Graph: `graph_builder.py` builds the **sensor** graph by default, not `la_road_network.pkl`.
- Evaluation: `src/evaluation/run_simulation.py` and `simulation_core.py` (900 runs). `evaluate_framework.py` is the older name if still present — do not list a file you no longer run.
- Five figures: `fig1` travel time, `fig2` reduction by scenario, `fig3` delta, `fig4` latency, `fig5` poster — from `results/simulation/figures/`.

---

## 4.3.4 PEMS-BAY

**Independently** = a **second** training run, new scaler, 325 columns. Not 207+325 in one net.

**Table 4.4c — replace METR-LA column** with 27 epochs, train loss 0.3847, val 0.4335, MAE **3.48**, RMSE **6.04**. Keep PEMS MAE **2.38**, RMSE 4.49, 79 epochs.

Training window counts: METR-LA **23,973** (not 23,977).

**Which city was “better”?** PEMS MAE is lower because Bay freeways are smoother, not because Los Angeles “failed.” **Do not** mix Bay speeds into the LA router to “fix” LA.

**Kenyan deployment sentence:** keep only as *feasibility of the architecture*, not “ready for Nairobi CBD.”

**Figure 4.8 caption:** METR-LA **27** epochs, not 17.

---

## 4.4 Objective 3 — replace Table 4.7 entirely

From `full_report.txt` (mean vs Dijkstra, all scenarios mixed):

| δ | Mean vs B1 | Replans / journey | TD-A* latency |
|---|---|---|---|
| 0.05 | +5.726% | 0.45 | 0.370 ms |
| 0.10 | +5.748% | 0.44 | 0.367 ms |
| 0.15 | +5.726% | 0.43 | 0.368 ms |
| 0.20 | **+5.767%** | **0.39** | 0.373 ms |

ANOVA: *F* = 0.001, *p* = 1.00.

**GET THIS** `Zero replannings` / `δ = 0.10 was recommended`

**REPLACE WITH**

```
Incident journeys replanned about once (mean 1.03). Travel time did not differ among the four δ values, so δ = 0.20 was recommended as the operational default because it issued fewer extra alerts without losing travel-time benefit.
```

**F for?** *F* is between-group variance over noise. *F* ≈ 0 means the four thresholds produced the same travel time. *p* = 1.00 agrees. That is **not** a failed experiment.

**α = 0.05 here** is significance, not δ.

**Why Dijkstra in the ANOVA table?** ANOVA was on reduction *versus B1*. Tables 4.5–4.6 still show B2–B4. You are not Dijkstra-only.

**Figure 4.4:** left = % vs B1 by δ; right = replans. Use `obj3_delta_sensitivity.png` / `fig3`. Error bars = 1 SD if the figure has them.

**For you only.** Old Table 4.7 (+0.17% incidents, 0 replans, −1.50% peak) is the **broken** run. Do not interpret it. Throw it away.

---

## 4.5.1 Travel time — replace Tables 4.5 and 4.6

**Table 4.5 mean journey times (seconds), 300 runs per scenario (75 OD × 4 δ):**

| Scenario | B1 Dijkstra | B2 static A* | B3 reactive A* | B4 oracle | Framework |
|---|---|---|---|---|---|
| Peak hour | 513.1 | 552.5 | 513.1 | 499.5 | **506.3** |
| Off-peak | 403.5 | 405.2 | 403.5 | 403.1 | **403.4** |
| Incident | 727.5 | 723.2 | 603.7 | 580.5 | **598.9** |

**GET THIS** `The framework consistently produced lower travel times than baselines B1 through B4 in all scenarios.`  
**REPLACE WITH** `The framework was faster than Dijkstra, historical A*, and reactive A* on average, and slower than the oracle, as required if the oracle is honest.`

**Table 4.6 vs Dijkstra (pooled over δ, N = 300 per scenario):**

| Scenario | N | Mean % | t | *p* | Significant at α = .05? |
|---|---|---|---|---|---|
| Peak hour | 300 | **+1.03%** | 3.81 | .0002 | Yes |
| Off-peak | 300 | **+0.01%** | 0.12 | .90 | No |
| Incident | 300 | **+16.19%** | 26.43 | < .001 | Yes |

Also report overall vs B1 **+5.74%**, vs B2 **+7.39%**, vs B3 **+0.61%**, vs B4 **−1.69%**.

**GET THIS** any note that says reductions were significant in *all three* scenarios.  
**REPLACE WITH** significant in **incident and peak**; off-peak not significant.

**Four delta values in the table note:** 900 = 75 × 3 × 4. Each row in 4.5 pools the four δ values (hence N = 300, not 75).

**PEMS in Table 4.5?** No. Different city, no Bay routing graph in this study.

**Ground-truth evaluation:** keep the idea in one short clause: everyone was *driven* on actual future speeds. You can drop the long jargon.

**Error bars:** re-insert `fig2_reduction_by_scenario.png` from the improved branch. Caption: whiskers = 1 SD if that is what the script plotted.

**Alarm?** Replans are **dispatcher suggestions**, not a siren. ~1 per incident is low fatigue.

**For you only.** Framework 123 s vs baseline 588 s was scaled GRU output treated as mph / predicted cost treated as journey time. **Wrong.** 598.9 vs 727.5 in incidents is the real cell.

---

## 4.5.2 Latency

**GET THIS** `0.315 ms` / `69.1 ms` / `3,175 times`

**REPLACE WITH** TD-A* **0.37 ms**, GRU **39.3 ms**, combined **~40 ms**, about **25 times** below 1,000 ms (1000/40). Do not use 3,175×; that used 0.315 ms as if it were the whole system.

**Why 207 sensors in the latency note?** Routing used the LA GRU. Bay inference is a separate model; do not mix 325 into Table 4.8.

**For you only.** 0.315 ms *was* a measured TD-A* time on the old OSM graph. Your defending TD-A* time is **0.37 ms** on the sensor graph. Combined wait is **GRU + router**, ~40 ms.

---

## 4.6 Discussion — replace 4.6.1–4.6.3 (do not interpret +0.17%)

**GET THIS** the paragraph that starts `The statistically significant travel time reduction in incident conditions (+0.17%`

**REPLACE WITH**

```
Under incident conditions the framework cut Dijkstra time by 16.19% (about 599 s against 728 s, p < .001) with about one replan per journey. In plain terms, when the planned road was jammed, the system offered another road. Peak hour showed a small significant gain (1.03%, p = .0002): when almost every road is already slow, looking ahead helps only a little. Off-peak times were tied (0.01%, p = .90), which is the expected result on empty roads.
```

**GET THIS** the 18.6% / −1.50% peak explanation and the **zero replannings** paragraphs.

**REPLACE WITH**

```
Those older peak-hour losses and zero-replan results came from the unused OpenStreetMap map and from comparing remaining time with the original full trip. They are not the defending findings. On the detector graph, incidents sat on the planned corridor and remaining time was measured from the vehicle’s current position, so the controller did fire.
```

**vs literature (one short paragraph):**

```
The 16% incident gain sits in the same band as Abuaisha et al. (2025) (12–18% on fixed transit corridors), in a different setting. It is not Sasikala et al.’s 35% signal-priority figure. Werner et al. (2022) remain the closest router and do not replace this GRU-and-threshold loop.
```

**4.6.2:** `0.37 ms` routing, `~40 ms` combined, still far under 1,000 ms. Preprocessing not needed at this urban size.

**4.6.3:** ANOVA unchanged in meaning (*p* = 1); **recommend δ = 0.20**, not 0.10.

**4.6.4 Limitations — GET THIS** 18.6% as a property of the reported tables / “sparse-sensor analysis was applied”

**REPLACE WITH**

```
Reported routing used 100% detector coverage on Los Angeles freeways, not Nairobi mixed traffic. PEMS-BAY confirmed the GRU in a second city (MAE 2.38 mph) but was not given a 900-journey routing test. A 10–30% coverage run remains further work.
```

**For you only.** You *solved* the 18.6% problem by changing the graph, not by pretending Nairobi was measured. Off-peak ~0% is a **good** negative control, not something to hide.

---

## 4.7 Summary

Rewrite the last paragraph with: 3.48 / 2.38 mph; 207-node sensor graph; δ = 0.20; +16.19% incidents; +1.03% peak; ~0% off-peak; ~40 ms; ~1 incident replan. No +0.17%, no 397 nodes as the result graph.

---

# Chapter 5 — no new citations (KyU)

Fix the stray `introduced.r` at the end of 5.1.

**Keep** “no new citations” (your balloon: keep that rule).

**5.2 Objective 2:** METR-LA 34,272 steps; **also** a PEMS-BAY GRU; routing on **207-node detector graph**, not 397-node OSM.

**5.2 Objective 3:** *F* ≈ 0.001, *p* = 1.00; recommend **δ = 0.20**. Write italic *p*, not `P`.

**5.2 Objective 4:** **+16.19%** incidents (*p* < .001), not +0.17%; latency **~40 ms**, not 0.315 ms as the system wait; **do not** blame 18.6% for the defending tables.

**Table 5.1:** same number replacements as 5.2.

**5.3 overall conclusion:** feasible in simulation; large gain when the corridor is disrupted; not a claim that Nairobi now meets eight minutes.

**5.4.1**

- Latency bullet: **~40 ms** combined, not 0.315 ms as if that were the user wait.
- Default δ: **0.20**, not 0.10.
- **GET THIS** “increase coverage toward 80%” as if 18.6% were the reported graph. **REPLACE WITH** keep 100% detector coverage in simulation; for Nairobi, a future downsample study (10–30%) is needed — do not tell Kenya to copy METR-LA hardware as a requirement of *these* percentages.
- Sensor investment in Kenya: keep as policy, not as “these 16% will appear in the CBD.”

**5.5 Further research — this is the balloon you found confusing**

You cannot **blame 18.6%** and then **recommend reducing coverage further** as if that were the next honest test of the *same* broken map.

**GET THIS** the bullet that reduces coverage from 18.6% to 10% and 5%.

**REPLACE WITH**

```
Sparse-sensor Nairobi analogue: downsample the present 100% detector graph to 10–30% coverage and repeat the 900-run. That was not done in this study.
```

**GET THIS** the duplicate 100%→10–30% bullet if both remain — keep **one** copy only.

**GET THIS** “increase coverage from 18.6% to 100%” as future work.

**REPLACE WITH** `That 100% detector run is already the reported experiment.`

**High-volatility 60% drop:** optional future work. You already used 40% on the corridor and the controller fired. You do not have to run 60% to graduate.

**Multi-EV:** keep as further research. Two ambulances on the same detour is a fleet problem you did not model. Not a hole in Objective 4.

**Matatu GPS aggregators:** live Kenyan probe data, not your METR-LA file. Future work. You do not need to explain the product; one line is enough.

**WHO 8 minutes / “perfect for Nairobi?”** **No.** Do not convert +16% of 727 s into CBD minutes against the eight-minute target.

---

# After Chapters 4–5 (checklist)

1. Ctrl+F `0.17` `123.` `588.3` `0.315` `69.1` `3,175` `δ = 0.10` `delta = 0.10` `17 epochs` `3.42` `MinMax` — none should describe the defending run.
2. Ctrl+F `397` `18.6` — only as unused OSM mode or as a mistake you retired.
3. Chapter 5: no new citations.
4. Word Count after these replacements and Chapter 2 inserts; add INSERT 9 from `docs/THESIS_COMMENTS_AND_EXPANSION.md` only if you still sit under 20,000 words.
5. Strip comment balloons before printing.
