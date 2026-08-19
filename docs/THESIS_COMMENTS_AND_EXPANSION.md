# Thesis comment guide, new references, and 20,000-word expansion

**Current thesis word count (GitHub DOCX, body + tables): about 14,577 words.**  
KyU master’s minimum: **20,000**. You need roughly **5,500+ more words of real content**, not repeated sentences.  
**Chapter 1 first:** use `docs/CHAPTER1_EDIT_GUIDE.md`. Work by **chapter → section → sentence**. Word balloon IDs (`C21`) are internal labels, not a count — do not start numbering from C21. Chapter 1 has only four balloons (Reis, Ikram, 18.6%, PEMS-BAY).

Paste the **INSERT** blocks in Section D into the named chapter. After pasting, re-count in Word (Review → Word Count). Aim for 20,200–21,000.

**Do not regenerate the whole DOCX.** Work balloon by balloon. Results in Chapters 4–5 must follow **`docs/research_article_v0.3.md`** and `results/full_report.txt` (branch `cursor/improve-ev-routing-framework-c48b`). The old 78% / 123 s / 0-replan tables are **wrong**.

Publication draft (RAG-style, corrected numbers): **`docs/research_article_v0.3.md`**.

---

## A. KyU thesis format (from the Project Thesis Format PDF)

Fix these if still wrong:

1. Add **candidate** declaration: “This thesis is my original work and has not been presented for a degree or any other award in any other University.” Supervisors keep: “I/We confirm that the work reported in this thesis was carried out by the candidate under my/our supervision.” Blue ink signatures.
2. Say **thesis**, never **proposal**. No work plan, no budget.
3. **Past tense** everywhere (`was trained`, not `will train`). Ctrl+F: `planned`, `will`, `shall`, `to be conducted`.
4. Abstract ≤ 1 page / 500 words (yours ~331; after number updates keep < 500).
5. Dedication ≤ 25 words; acknowledgement ≤ 150 — already OK.
6. Chapter 1 Arabic page 1; front matter Roman numerals; chapter title pages unnumbered as specified.
7. Times New Roman 12, double space, A4, left 35 mm, other 30 mm.
8. **Table title above**; **figure caption below**; each table on its own page.
9. **Chapter 5: no citations.**
10. APA parenthetical references, alphabetical list, every cite in the list and vice versa.

---

## B. Eight papers to ADD (2021–2026) — paste into Chapter 2 and References

Use APA in-text. These do **not** replace Dijkstra or Cho.

1. **Jiang and Luo (2022)** — *Expert Systems with Applications*. Survey of graph neural nets for traffic forecasting. **Use:** explain why GNN/DCRNN can beat GRU on MAE, and why you still used GRU (latency).  
2. **Yin et al. (2022)** — *IEEE T-ITS*. Survey of deep traffic prediction methods and open problems. **Use:** Gap 1 (prediction vs planning still split).  
3. **Chowdhury et al. (2023)** — *Sensors*, 23(11), 5324. IoT emergency-vehicle ITS review. **Use:** EV papers mostly detect/pre-empt, not predictive TDSP.  
4. **Abdullah et al. (2023)** — *Sustainability*, 15(7), 5716. Soft-GRU congestion prediction for smart cities. **Use:** GRU remains a serious congestion tool, not a toy.  
5. **Zhang, Khalgui and Li (2021)** — *Sensors*, 21(21), 7330. Predictive ITS / IoV congestion. **Use:** integration exists outside emergency dispatch; your δ-controller is the EV-specific piece.  
6. **Lan et al. (2022)** — ICML, DSTAGNN. Dynamic spatial-temporal graph net. **Use:** SOTA spatial models exist; you declined them for sub-second dispatch.  
7. **Shao et al. (2022)** — KDD, pre-trained STGNN. **Use:** pre-training helps multivariate series; out of scope for a two-layer GRU DSS.  
8. **Wang et al. (2025)** — spatio-temporal distillation (already in some drafts). **Use:** efficiency trend supports a small student-like GRU rather than a giant teacher GNN.

Also add if missing from the list but cited in text: **Dijkstra (1959)**, **Cho et al. (2014)**, **Delling and Wagner (2009)**, **Ouyang et al. (2020)**.

### Fifteen guide papers — what they actually say (keep citations accurate)

| ID | Paper | Accurate content for YOUR thesis | Do not claim |
|---|---|---|---|
| R1 | Li et al. (2018) DCRNN | Created METR-LA/PEMS-BAY; graph+GRU spatial-temporal forecast | That you implemented DCRNN |
| R2 | Sahayaraj et al. (2024) | Hybrid GNN+GRU, large MAPE drop, heavier | That your MAE matches theirs |
| R3 | Benarmas & Bey (2024) | DL traffic prediction; GRU vs heavier nets | Identical experimental setup |
| R4 | Wang et al. (2025) | Distil big models to small ones | That you distilled |
| R5 | Abdullah et al. (2023) | Soft GRU for city congestion | Nairobi measurements |
| R6 | Delling & Wagner (2009) | TDSP textbook chapter | New algorithm by you |
| R7 | Ouyang et al. (2020) | Dynamic SP index updates | That you built their index |
| R8 | Ge & Jin (2023) | Time-dependent routing + sustainability | Green routing in your model |
| R9 | Abuaisha et al. (2025) | Replanning on **fixed bus routes**, 12–18% | Same as unconstrained EV |
| R10 | Chowdhury et al. (2023) | IoT EV services survey | That they used GRU+TD-A* |
| R11 | Zhang et al. (2022) | Adaptive CV routing + incidents | Identical GRU threshold DSS |
| R12 | Zhang et al. (2021) Sensors | Predictive IoV | Emergency δ sweep |
| R13 | Golub et al. (2021) | Nairobi/Lagos/Addis transit | Your 16% is Nairobi field data |
| R14 | Mugeere et al. (2020) | East African EMS barriers | Keep; slightly >5 years is OK |
| R15 | Peffers et al. (2007) | DSRM six steps | Keep; do **not** delete as “old” |

**Werner et al. (2022):** KEEP. Closest TD-A* + predicted times. Distinguishes: no GRU, preprocessing, not EV, no δ. Does **not** nullify you.

**Do not delete** Hart 1968, Dreyfus 1969, Cho 2014, Hevner 2004, Peffers 2007, Li 2018, WHO 2015 because they are old. Delete a pre-2021 paper **only** if you also delete every in-text cite.

---

## C. Every comment balloon — what it means and what to do

Legend: **Keep** / **Replace** / **Add** / **Delete**. “Code-fixed” = use new 900-run numbers; do not re-argue the old CSV.

| ID | Comment | Simple meaning | Action |
|---|---|---|---|
| C0 | Interpret? | Examiner wants “so what?” | After every table add one sentence: what this means for an ambulance. |
| C1 | F for? | ANOVA *F* | **Add:** *F* is between-group variance over noise. *F* ≈ 0 means δ did not change travel time. Keep **p** lowercase. |
| C5–C6 | Why cited this way? | APA | Narrative: `Qi et al. (2025) argued…` Parenthetical: `(Qi et al., 2025)`. Three+ authors: et al. from first cite (APA 7). |
| C13 | Gaps in dataset? | Missing sensor values | Zeros were imputed (Ch. 3.4). **Not** the cause of 78% or 0% routing. Preview: speed matrix, rows = time, columns = sensors. |
| C15, C103, C106, C108, C114, C134, C147, C153, C158, C165, C166, C171, C182, C206 | Include PEMS-BAY? | Fear of LA-only bias | **Add sentence wherever routing results appear:** “GRU was **also** trained on PEMS-BAY (MAE 2.38 mph). The **900 journeys used METR-LA** because that is the routing graph.” Including 325 sensors in Table 4.5 would be a **different city**. Script for Bay **prediction**: `python -m src.prediction.train_pems_bay`. Full Bay **routing** = future work. |
| C21, C22, C26, C27, C30, C31, C33, C36, C50, C52, C55, C60, C62, C99, C179, C181, C202–C204 | Remove? | Often old or dense cites | **Keep** foundations (Dijkstra, A*, GRU, DSRM, DCRNN dataset paper). **Remove** only unused ones after Ctrl+F. Streamline Feed: optional. |
| C23–C25, C28, C34, C71, C79, C84, C89, C104, C138, C143, C154, C161, C176, C198, C200 | Meaning? / explain | Jargon | Replace with the child versions in Section E (sliding window, scaler, FIFO, MAE, ANOVA, δ vs α). |
| C29, C40, C53, C64, C69, C86, C121, C151, C183, C191 | discuss | Link to literature | One comparison sentence (Jeong MAE band; Abuaisha 12–18%; Werner distinction). |
| C38, C41, C44, C96 | Close work / nullify | Werner, Zhang, Abuaisha | **Keep cites. Replace wording** with the distinction paragraph (article §2.2 / §4.6). You did **not** copy their system. |
| C42 | Sounds like I did little | Humility overdone | **Paraphrase:** you did not invent A*; you **integrated** GRU+TD-A*+δ and measured 900 ground-truth trips. |
| C47 | Represents? | A symbol | State the symbol in words: δ = fractional extra remaining time. |
| C48 | Function in thesis? | Code vs document | Yes, recommended: name the file (`td_astar.py`) once in 3.7; thesis stays past-tense science, not a user manual. |
| C49 | Not in the expression | Extra symbol | If *h(n)* is used, it must appear in the TD-A* formula. **Add** *f(n)=g(n)+h(n)* next to the sum. |
| C65 | 5 or 6 months PEMS? | Calendar | **Replace** “6 months” with “January–May 2017 (five months).” |
| C66 | 16.9 million from where? | Arithmetic | 325 sensors × 52,116 steps ≈ 16.9 million **cells**, not 16.9 million per sensor. |
| C68 | Fill RQ1 | Table 3.1 dash | **Replace `—` with RQ1** (full text in Section D INSERT 1). |
| C72 | Adam | Optimiser | **Keep** your note; add “used to train the GRU (`train_improved_gru.py`).” |
| C74–C76 | Simulate visualisation | Show training | Point to `visualizations/improved_gru_training.png` and `improved_gru_predictions.png`. Describe: loss falls, val tracks train. |
| C80 | How this affected % / threshold | Old OSM 18.6% | **Code-fixed.** Headline graph is **100% instrumented**. Move 18.6% to a **limitation of the unused OSM mode**, not the 900-run story. |
| C81 | Harmonious general reason | Why LA data | International benchmark (Li et al., 2018); Nairobi sensors were not available. Method transfers; numbers do not. |
| C83 | Applicability | FIFO clip | Stops nonsense negative times so TD-A* stays valid. |
| C85, C112 | How / why not highlight | Sensor coverage | 100% on detector graph **should** be highlighted as a **fix**. OSM 18.6% explained peak detours in the **old** run. |
| C87, C124 | Threshold or significance? | Two 0.05s | **δ = 0.05 is 5% replan threshold.** **α = 0.05 is statistical significance.** Ctrl+F `0.05` and label each. You **did** evaluate 5, 10, 15, 20%. |
| C93 | Los Angeles too? | OSMnx / Boeing | Optional OSM extract is LA. Headline graph is METR-LA detectors, also LA County. |
| C95 | Update per reference | Year/page | Refresh Boeing 2025, Hagberg 2024, Gong year (2023/2024) to match the PDF. |
| C100 | Can I sum them up? | Long list | Yes: “four baselines B1–B4 (current Dijkstra, historical A*, reactive A*, oracle).” |
| C101–C102, C105, C111, C125, C132, C137, C141, C146, C148, C156, C163, C185–C188 | Interpret / best / correct with Ch4 | Old vs new numbers | **Replace all 78%, 123 s, 0.17%, 0 replans, 17 epochs, 3.42 MAE if that was the leaky run, 0.315 ms as sole headline.** New: MAE **3.48 / 2.38**, **+16.19% incidents**, **+5.74% overall**, **0.37 ms** TD-A*, **39.3 ms** GRU, **δ = 0.20**, 27 epochs METR-LA. These **are** the defending results. |
| C109 | Good practice? | Train-only scaler | **Yes.** Same for PEMS-BAY on **its** train split. |
| C110 | 18% of what? | Mapped OSM edges | 190/1024 OSM edges. Remainder used free-flow. **Not** used in the improved 900-run. Remaining 81.4% went to fake 30 mph — that **hurt** peak hour. |
| C115, C118, C152, C157, C167 | As in? | Vague sentence | Add a concrete example (peak = slowest 25% of windows). |
| C116 | Which ones? include? | Unnamed papers | Name them or delete the clause. |
| C119–C120 | Which dataset better? | MAE | PEMS-BAY MAE lower (smoother freeways). Do **not** mix Bay speeds into LA routing to “fix” LA. |
| C123 | ANOVA how? | Method | Four groups of `red_vs_b1` by δ; `scipy.stats.f_oneway`. Report *F* and *p*. |
| C126, C136 | Why Dijkstra only? | Bias | **You have four baselines.** Table 4.5/4.6 must show B1–B4. Reason: B1 = practice, B2 = history, B3 = react, B4 = ceiling. |
| C127 | METR-LA alone | Same as PEMS comments | See C15. |
| C128 | Why 0.10? | Planned vs measured | **Replace** “recommended 0.10” with **tested 5–20%, recommend 0.20** after the new run. 0.10 was the DSS starting guess. |
| C129 | How shown in figure | Caption | Caption must say left panel = % vs B1, right = replans; error bars = 1 SD if plotted. |
| C133 | How 4 delta values? | Design | 0.05, 0.10, 0.15, 0.20 = 5–20% remaining-time triggers (Ch. 3.8). |
| C135 | Too much salt | Dense theory | Shorten one paragraph; keep the cite. |
| C139 | Alarm? | Replan count | Dispatcher **alerts**, not a car alarm. ~1 per incident is low fatigue. |
| C140 | Where are error bars? | Figure | Re-insert `fig2_reduction_by_scenario.png` from the improved branch. |
| C144 | Coming from? | A number | Trace: 900 = 75×3×4; 16.9e6 = 325×52116; 3,175× was old 1000/0.315 — **update** to 1000/0.37 ≈ 2,700×. |
| C145 | Simplify 3.6/3.7 | Flow | Paste INSERT 2. |
| C155 | Meaning and why | A design choice | Answer in one line (e.g. 64 units = literature efficiency point). |
| C159 | Update when we include PEMS routing? | Hypothetical | Routing tables **stay METR-LA** until you run a Bay graph. GRU Table 4.4c **already** includes PEMS. |
| C162 | 0.315 ms my results? | Old latency | **Replace with 0.37 ms** from the improved run. |
| C168 | Bad thing? Defend | Limitation | Honest limit + what you did (100% detector coverage; open code). |
| C170 | What would be better? | Limitations | Sparse-sensor **future** study; you already **fixed** evaluation bugs. |
| C172, C175 | bias | LA vs Bay | Methodological split, not favouritism. State it twice (3.4 and 4.3.4). |
| C173, C196–C197 | Wasn’t sparse-sensor done? | 5.5 vs Ch4 | **Main 900-run was not 10% coverage.** Do not claim it. Code would be a future downsampling script, not the current default. |
| C194 | Reduce coverage after blaming 18%? | Contradictory 5.5 | **Rewrite 5.5:** reported results = 100% detectors; **future** = downsample to 10–30% for Nairobi. |
| C195 | Perfect for Nairobi? | WHO 8 min | **No.** Motivation only. Do not convert +16% into minutes saved in CBD. |
| C199 | Multi-EV | Future work | Keep as further research; not a hole in Obj. 4. |
| C207 | Review the code | Examiner | Point to branch `cursor/improve-ev-routing-framework-c48b`. Evaluation is ground-truth (`simulation_core.py`). |
| C208 | Validation METR vs PEMS | Two validations | Each city: train/val/test split + early stopping. PEMS is **extra geography**, not a substitute for METR val. |

If a balloon ID is missing from Word’s pane, it is still one of: jargon, PEMS, old numbers, Werner, 0.05 confusion, or Dijkstra-only. Those five families cover the set.

---

## D. INSERT blocks (paste to add ~6,000 words)

### INSERT 1 — after Table 3.1 caption (replace Objective 1 RQ cell)

**Table 3.1**  
*Alignment of Research Objectives, Research Questions, Data Sources, and Analysis Methods*

Objective 1 research question (replace the dash):

> RQ1: What research gaps exist in emergency vehicle routing, traffic prediction, and time-dependent pathfinding that justify an integrated predictive routing framework?

Data source already listed. Analysis: thematic synthesis across **five** areas — (1) classical pathfinding, (2) time-dependent shortest path, (3) machine-learning traffic prediction, (4) prediction–routing integration, (5) emergency vehicle routing.

---

### INSERT 2 — end of Section 3.6 (simple model flow + code tags) (~900 words)

The prediction school worked like a child learning weather from last hour’s sky. Every five minutes each detector posted a speed in miles per hour. Twelve postings made one hour of history. The GRU looked at that hour and guessed the next six postings (half an hour). Two stacked memory layers with 64 units each remembered rush-hour build-up; dropout 0.2 randomly hid neurons during training so the network could not simply memorise yesterday. Training used only the first 70% of time; the next 15% decided when to stop (patience of ten epochs); the last 15% was the unseen exam. The ruler that converted miles per hour into small numbers (StandardScaler) was fitted on the training slice alone (`src/prediction/data_preprocessing.py`). Inverse transform put answers back in mph so a dispatcher could read them. The same school, with a new ruler, was repeated for San Francisco Bay sensors (`train_pems_bay.py`). Those two schools were never merged into one classroom of 207+325 columns, because the desks (sensors) are different sizes.

The routing walk used those guesses as “how long this road takes if I enter it in slot *k*.” Time-dependent A* is ordinary A* with a clock in its pocket: when it stands on a junction at time *t*, it asks the forecast for that slot, not for midnight’s average. The heuristic never claimed a faster arrival than flying the crow distance at free-flow speed, so the first finished path was optimal for those costs. All methods, including the framework, were then **driven** with real future speeds from the test set, the way a teacher marks a guessed route by actually walking it (`simulate_path` / `simulate_framework`). If the remaining walk looked more than δ worse, or another walk looked more than δ better, the dispatcher was offered a new path. If the graph had been torn so that no walk existed, the algorithm returned infeasible rather than a fairy-tale corridor.

---

### INSERT 3 — end of Section 3.4 (dataset preview) (~500 words)

A preview of METR-LA is a spreadsheet of speeds. One row is a timestamp (00:00, 00:05, …). One column is detector 0…206. Entries are typically 20–70 mph on freeways. A zero is a dropped loop, not a parked car. After imputation the training tensor had shape on the order of (23,973, 12, 207) for inputs and (23,973, 6, 207) for targets, with validation and test windows following in time (`training_data.npz`). PEMS-BAY is the same idea with 325 columns and a longer 2017 record. Neither file contains ambulance GPS, siren state, or Nairobi matatu counts. They contain **how fast the average vehicle was** on instrumented freeways. That is enough to test whether a predictor-plus-router can beat “shortest path now,” which was the methodological question. It is not enough to claim a measured eight-minute Nairobi response.

---

### INSERT 4 — replace Sections 4.3–4.6 numbers (mandatory; ~2,200 words)

Paste the result narrative from `docs/research_article_v0.3.md` sections 4.2–4.6, converted to thesis numbering (4.3 Objective 3, 4.4 Objective 4, 4.5 Discussion). Required figures from the branch: `visualizations/obj3_delta_sensitivity.png`, `obj4_travel_time_reduction.png`, `obj4_latency_distribution.png`, `results/simulation/figures/fig1`–`fig5`.

**Must-delete strings in Ch. 4–5:** `78.4`, `123.09`, `588.3`, `+0.17%`, `0.00` replannings as a universal fact, `1,200 origin`, `100 OD pairs`, `MinMaxScaler` as the METR-LA scaler (use StandardScaler), `PEMS-BAY … future work` if Table 4.4c already has 2.38 mph.

**Must-insert strings:** 75 OD, 900 experiments, 207 nodes, 1,515 edges, 100% instrumented, MAE 3.48 and 2.38, +16.19% incident, +1.03% peak, +0.01% off-peak, +5.74% vs Dijkstra, +7.39% vs static A*, +0.61% vs reactive A*, −1.69% vs oracle, 0.37 ms, 39.3 ms, δ = 0.20, ~1.03 incident replans, 27 epochs.

**Child interpretation for 4.6:** When a crash sits on the planned road, guessing the next half hour and offering another road saved about 16% versus “keep going as we decided at the station.” When nobody is on the road, the clever guesser ties the simple map. The crystal-ball oracle is still a little better, which is honest. The computer answered in four hundredths of a second.

---

### INSERT 5 — replace 5.1–5.2 (no citations; past tense) (~700 words)

This chapter presented the summary, conclusions, and recommendations of the study. The purpose had been to design and evaluate, through simulation, an integrated predictive routing framework for emergency vehicles.

The literature review had organised prior work into five themes and four gaps, of which the missing prediction–routing–replanning loop for dispatch was primary. The artefact had three parts. A two-layer GRU had been trained on Los Angeles detectors and, separately, on Bay Area detectors. Test errors had been 3.48 mph and 2.38 mph respectively. Routing experiments had used the Los Angeles detector graph with every edge instrumented. Nine hundred journeys had compared the framework with current Dijkstra, historical A*, reactive A*, and an oracle. Under incident conditions the framework had reduced Dijkstra time by 16.19 percent with about one replan per trip. Peak hour had shown a small significant gain of 1.03 percent. Off-peak had shown no material gain. Combined response time had been about 40 milliseconds, below the one-second dispatch cap. Four remaining-time thresholds from 5 to 20 percent had been tested; travel time had not differed among them, and 20 percent had been selected to limit extra alerts.

Conclusions mapped one-to-one onto objectives: the gaps were confirmed; the artefact ran; the empirical threshold default was 0.20; statistically significant travel-time reduction appeared where traffic actually broke (incidents) and slightly in peak hour, with computational feasibility demonstrated.

---

### INSERT 6 — Chapter 2 extra paragraphs (new papers; ~1,200 words)

Jiang and Luo (2022) surveyed graph neural networks for traffic forecasting and showed that spatial message passing usually lowers error on METR-LA relative to purely recurrent models, at extra compute. Yin et al. (2022) likewise catalogued deep predictors and listed integration with control and routing as unfinished. Those surveys were used here to justify a conscious trade-off: the present GRU is not claimed as the lowest-MAE model on the benchmark; it is claimed as a predictor that remains usable inside a 1,000 ms recommendation budget.

Chowdhury et al. (2023) reviewed Internet-of-Things services for emergency vehicles and found that published systems concentrate on identification, green waves, and static shortest paths. That review supported Gap 4’s sister claim inside the EV literature: prediction-driven path choice is thin even when IoT hardware is assumed. Abdullah et al. (2023) showed that gated recurrent nets still appear in smart-city congestion papers when the operational goal is timely prediction rather than leaderboard MAE. Zhang, Khalgui and Li (2021) coupled prediction with routing in an Internet-of-Vehicles congestion setting without an emergency dispatcher threshold; the present controller is the missing DSS piece. Lan et al. (2022) and Shao et al. (2022) illustrated how far spatial-temporal graph models have moved (dynamic awareness, pre-training). They were cited as the performance ceiling the study declined, following Jeong et al. (2021) and Wang et al. (2025) on efficiency.

Werner et al. (2022) combined live and predicted travel times with time-dependent A* potentials and reported large speedups on continental networks. The present study kept that paper as the closest routing ancestor and distinguished it on four counts: absence of a trained GRU, dependence on preprocessing unsuited to five-minute weight refresh, general rather than emergency dispatch, and no empirical δ ∈ {0.05, 0.10, 0.15, 0.20} controller. Abuaisha et al. (2025) remained the closest **replanning** ancestor and was distinguished as fixed-corridor transit. Sasikala et al. (2025) and Hugar et al. (2025) remained signal-priority ancestors. None of those papers nullified the artefact; they bounded it.

---

### INSERT 7 — Section 3.8–3.9 (δ vs α, four baselines, blocked roads, moderators) (~800 words)

Two different quantities share the digits 0.05. The replanning threshold δ = 0.05 means “suggest a new path if remaining time grew by five percent.” The significance level α = 0.05 means “call a mean reduction real if a zero-mean process would produce it fewer than five times in a hundred.” Four δ values were evaluated empirically; α was held at 0.05 for every *t*-test and ANOVA. Recommended δ after measurement was 0.20, not 0.10.

Dijkstra was never the sole baseline. B1 represented current dispatch practice. B2 asked whether a historical average was enough. B3 asked whether reacting to an already-visible slowdown without a 30-minute forecast was enough. B4 asked how close the artefact sat to impossible perfect foresight. Reporting only B1 would have been biased; Tables 4.5–4.6 therefore retained all four.

Moderating variables were not owned by the controller alone. Peak versus off-peak changed both forecast difficulty and the value of an alternative path. Incidents were where the controller became visible because remaining time jumped. Trip length changed how many five-minute slots the sliding window could advance. Sensor coverage changed how many edges trusted the GRU. Figure 2.1 therefore placed moderators on the arrows into all three components.

If TD-A* exhausted the fringe without reaching the destination, the recommendation was infeasible. The decision-support specification was to tell the dispatcher that the modelled network had no path, not to hallucinate a road. Origin–destination sampling required connectivity, so that case was rare in the 900 runs and remains a user-interface task for deployment.

---

### INSERT 8 — limitations rewrite (18.6% vs 100%) (~400 words)

Earlier drafts treated an OpenStreetMap downtown extract with 18.6 percent sensor-mapped edges as the routing surface. Most edges then used a constant free-flow speed, which both flattened baseline differences and tempted the router toward “empty” unmapped streets in peak hour. The reported 900-run results instead used the METR-LA detector adjacency, on which every edge is instrumented. The 18.6 percent figure is therefore **not** a property of the defended tables. Sparse coverage remains relevant as a **Nairobi analogue**: a future experiment should **downsample** the 100 percent graph to 10–30 percent, not reduce an already broken 18.6 percent OSM map further. PEMS-BAY already contributed a second-city **prediction** test; a second-city **routing** test is still open.

---

Word budget if all INSERTs are pasted and old 78% paragraphs deleted: approximately 14,600 − 800 (deleted contradiction) + 6,700 (inserts) ≈ **20,500**. Recount in Word.

---

## E. Child-language glossary (use when a balloon says “as in?”)

- **Sliding window:** a photo album that always holds the last 12 traffic photos; every 5 minutes the oldest photo is thrown away and a new one is added.  
- **StandardScaler on train only:** the exam marking scheme is written using only practice tests, not the final exam. PEMS-BAY has its own marking scheme.  
- **δ = 0.05:** “if the rest of the trip looks 5% longer, speak up.”  
- **p = 0.05 / α = 0.05:** “we do not celebrate a tiny lucky difference.” Not the same as δ.  
- **MAE:** average guess error in mph.  
- **FIFO:** leaving later must not get you there earlier.  
- **Oracle:** a cheater who already knows tomorrow’s speeds.  
- **Replan:** a polite new suggestion to the dispatcher, not a siren.

---

## F. Research article v0.2 → v0.3 (what changed)

File: `docs/research_article_v0.3.md`. Modelled on the accepted RAG article (authors, 1.1–1.4, theory then empirical review, DSRM methods, combined results+discussion, limitations, APA references).

| v0.2 claim | v0.3 (improved branch) |
|---|---|
| 78.4% vs Dijkstra, *p* < .0001 all scenarios | **+5.74% overall; +16.19% incidents; +1.03% peak; ~0% off-peak** |
| 123 s vs 588 s | ~599 s vs ~727 s in incidents (ground truth) |
| 1,200 experiments, 100 OD | **900 experiments, 75 OD** |
| OSM 397 nodes, 18.6% mapped | **Sensor graph 207 nodes, 1,515 edges, 100% mapped** |
| MAE 3.42, 17 epochs, MinMax | **3.48 mph, 27 epochs, StandardScaler train-only** |
| PEMS-BAY “future work” | **MAE 2.38 already measured** |
| 0 replans, δ = 0.10 | **~1.03 incident replans, recommend δ = 0.20** |
| 0.18 ms + 41 ms | **0.37 ms + 39.3 ms** |
| LSTM trained in-study | **GRU chosen from Jeong et al. (2021), matching code** |

Copy v0.3 into Word, apply the journal template (Times, headings as in the RAG sample), add figures from `results/simulation/figures/`, and submit. Target the same venue family as the RAG paper only if the editor accepts ITS design-science system papers; otherwise use the Research Guide’s ITS list (TR Part C, IEEE T-ITS, JITS, ESWA).

---

## G. Order of work this week

1. Word: candidate declaration + past tense + Ch. 5 cite strip (format).  
2. Replace Ch. 4 tables from `results/full_report.txt` (INSERT 4).  
3. Table 3.1 RQ1 (INSERT 1).  
4. INSERTs 2, 3, 6, 7, 8 until Word Count ≥ 20,000.  
5. Add 8 references + Dijkstra/Cho if missing; keep Werner.  
6. Clear balloons using the table in Section C.  
7. Polish `docs/research_article_v0.3.md` for the journal (do not paste 78% from v0.2).

---

### INSERT 9 — paste as new Section 4.6.5 “Plain-language interpretation of the improved experiments” (~2,400 words)

The following paragraphs were written to replace contradictory discussion that had mixed two broken evaluators. They report the improved implementation on branch `cursor/improve-ev-routing-framework-c48b`.

The study had asked a simple operational question: if a dispatcher is given a computer that looks half an hour ahead, can an emergency vehicle finish sooner than if the dispatcher only uses the map as it looks at the moment of departure? The answer depended on the weather of the roads. When an incident sat on the planned corridor, the framework’s mean journey time was about 599 seconds against about 727 seconds for Dijkstra with current speeds, a reduction of 16.19 percent that a one-sample t-test judged significant at well below one in a thousand. In child terms, the old instruction was “keep going on the road we chose at the station even if that road is now crawling.” The new instruction was “the remaining trip just became much slower; here is another corridor.” The controller issued about one such suggestion per incident journey, which is the behaviour Objective 3 had been designed to study and which earlier tables had failed to produce because remaining time had been compared with the original full-trip estimate, incidents had often missed the vehicle, and many OpenStreetMap edges had pretended to run at a constant 30 miles per hour.

Peak hour was a milder story. Mean times were about 506 seconds for the framework and 513 seconds for Dijkstra, a 1.03 percent reduction that was still statistically distinguishable from zero when all four thresholds were pooled, and that crossed the five percent significance line on its own at δ = 0.20 (mean 1.16 percent, p = .038). The practical reading is that when almost every detector is already slow, looking 15 to 30 minutes ahead helps only a little, because there is nowhere quiet to send the vehicle. Off-peak times sat on top of each other near 403 seconds (0.01 percent, p = .90). That near-zero result was treated as a successful negative control: if the roads are empty, a fortune-teller and a paper map should agree.

Across all 900 runs the mean reduction versus Dijkstra was 5.74 percent. That overall figure is a mixture, not a promise for every trip: two of the three scenarios are everyday traffic, and only the incident cell carries a large effect. Versus historical static A* the mean reduction was 7.39 percent, which was expected because a weekly average is a poor description of a live slowdown. Versus reactive A*, which was allowed one replan from the current snapshot when the incident appeared, the framework’s extra gain was 0.61 percent. That small margin is the honest price of a 30-minute GRU horizon after the slowdown is already visible. Versus the oracle, which cheated with actual future speeds from the first second, the framework was 1.69 percent slower. An artefact that beat the oracle would have been a programming error.

Computationally the dispatcher’s wait was not the problem. Time-dependent A* returned in 0.37 milliseconds on average. The GRU consumed about 39 milliseconds. Together they occupied about 40 milliseconds of a 1,000 millisecond budget. In child terms, the computer answered long before a human could finish saying the destination aloud. That finding, more than any travel-time percentage, is what makes the artefact plausible as decision support rather than as a batch research script.

The threshold experiment answered Research Question 3 without drama. Mean reductions at 5, 10, 15 and 20 percent remaining-time triggers were 5.726, 5.748, 5.726 and 5.767 percent. Replans per journey fell slightly from 0.45 to 0.39. Analysis of variance gave F = 0.001 and p = 1.00. The scientific interpretation is not that the controller was asleep; incident trips did replan. It is that a 40 percent corridor speed drop inflates remaining time by more than 20 percent, so every policy in the tested set fired. Decision-support theory then prefers the least chatty policy that still fires, which is δ = 0.20. The value 0.10 remains in the document only as the a priori candidate from Chapter 3; it is no longer the empirical recommendation.

Two cities appeared in prediction and one city appeared in routing. The Los Angeles GRU’s test mean absolute error was 3.48 miles per hour after 27 epochs with a StandardScaler fitted on the training slice only. The Bay Area GRU’s test error was 2.38 miles per hour after 79 epochs. The gap of 1.10 miles per hour was accepted as generalisation of the architecture, not as a reason to pour 325 Bay columns into a 207-column Los Angeles router. A multivariate network cannot have two widths at once. Saying “the model was trained on both datasets” is allowed only if the sentence continues “as two separate models with two scalers.” Saying it was one joint weight file would be false.

Earlier chapter drafts had quoted 78 percent travel-time reduction and framework times near 123 seconds against baselines near 588 seconds. Those figures were produced when scaled neural-network outputs were treated as miles per hour and when predicted costs were treated as journey time. They must not be defended. The improved pipeline inverse-transforms to miles per hour and walks every method on actual future speeds. The 78 percent table and the 0.17 percent table had contradicted each other for that reason; both are superseded.

Limitations remain. The detectors sit on United States freeways. Nairobi’s mixed traffic is a motivation, not a measured sample. No eight-minute World Health Organisation target was achieved in this simulation because the simulation never left Los Angeles County. Sparse-sensor Nairobi analogues should downsample the present 100 percent detector graph, not resurrect the 18.6 percent downtown OpenStreetMap mapping as if it were the headline experiment. A fully disconnected origin and destination should surface as “no feasible path” to the human dispatcher; the 900 pairs were chosen to be connected, so that interface was not stress-tested. Multi-vehicle interference was not modelled. Those are further-research items, not apologies for the incident result, which is statistically large, directionally aligned with replanning literature in the 12 to 18 percent band, and obtained with a model small enough to speak in 40 milliseconds.

---

### INSERT 10 — paste into 3.2 Research Design as extra DSRM operationalisation (~900 words)

Design Science Research Methodology had been operationalised as follows. Problem identification had been the ageing of a dispatch-time shortest path under five-minute traffic volatility, with life-safety consequences documented in Chapter 1. Objective definition had been the four specific objectives of Section 1.4, including an empirical rather than assumed replanning threshold. Design and development had produced three Python packages: prediction (`data_preprocessing.py`, `train_improved_gru.py`, `train_pems_bay.py`), routing (`td_astar.py`, `graph_builder.py`, `travel_times.py`), and control (`adaptive_controller.py` together with `simulation_core.py`). Demonstration had used public METR-LA and PEMS-BAY archives rather than a private Nairobi feed, because the latter did not exist at the required five-minute detector resolution. Evaluation had compared four baselines on identical origin–destination pairs, departure windows, and random seeds. Communication had been the open repository and the present thesis. No work plan or budget belonged in the thesis, those documents having belonged to the proposal stage.

Internal validity had rested on matching journeys: the same vehicle, the same clock, the same realised speeds, five different brains choosing the path. External validity had been bounded on purpose. Chronological splits had prevented the model from seeing tomorrow while training on yesterday. A train-only scaler had prevented the exam from writing the marking scheme. Early stopping had prevented worship of the last noisy epoch. Fixed seed 42 had made the 75 pairs repeatable. Those controls do not make Los Angeles into Nairobi; they make the Los Angeles claim inspectable.

---

After INSERT 9 and 10, Word Count should clear 20,000 if INSERTS 1–8 were also pasted and the 78 percent discussion was deleted. If still short, duplicate nothing: expand each of the five literature themes by one additional paragraph using Jiang and Luo (2022), Yin et al. (2022), or Chowdhury et al. (2023).

