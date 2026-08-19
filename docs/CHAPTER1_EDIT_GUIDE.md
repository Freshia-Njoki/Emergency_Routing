# Chapter 1 edit sheet (section → sentence → replace)

Work in **Microsoft Word** on your thesis DOCX. Do **not** count balloons.

## How Word comment IDs work (read this once)

`C21` is **not** “comment number 21 from the top of Chapter 1.”

Word stores an internal ID on each balloon. IDs can skip numbers (`C0`, `C1`, then `C5`). **Do not start counting at C21.** Find a comment by clicking the highlighted sentence, or open **Review → Comments** and search the comment text (for example `Remove?`).

**Chapter 1 in your current DOCX has only four of your balloons:**

| Your comment text (search this) | Section | Highlighted words |
|---|---|---|
| Why is this intext-cited this way? | 1.1 Local Perspective | `Reis et al. (2025)` |
| Why is this intext-cited this way? | 1.1 Local Perspective | `Ikram et al. (2025)` |
| Meaning? There were gaos in dataset… | 1.7 Limitations | `Sensor-to-edge mapping covered only 18.6% of graph edges` |
| Include pems bay? | 1.8 Delimitations | `using METR-LA as the primary evaluation dataset` |

The balloons on `+0.17%` and `F = 0.000, P = 1.000` are in the **Abstract**, not Chapter 1. Fix the Abstract first so Chapter 1 does not fight the first page.

Each item below has three blocks:

- **GET THIS** / **REPLACE WITH** — paste into the thesis.
- **For you only — do not add to the paper** — answers the question you wrote in the balloon.

---

# Before Chapter 1 — Abstract

**Location:** page after Acknowledgements, one paragraph titled ABSTRACT.

## A1. Old incident result (`Interpret?`)

**After this clause (end of the simulation sentence):**  
`…on a real 397-node OpenStreetMap road network derived from Los Angeles County.`

**GET THIS**

```
The framework produced a statistically significant travel time reduction in incident conditions (+0.17%, p = 0.004). TD-A* routing latency averaged 0.315 milliseconds — approximately 3,175 times below the 1,000-millisecond sub-second dispatch target — confirming computational feasibility for real-time emergency dispatch. One-way ANOVA confirmed that route quality was consistent across all four threshold values (F = 0.000, P = 1.000), supporting δ = 0.10 as the recommended operational default.
```

**REPLACE WITH**

```
Nine hundred matched journeys used the METR-LA detector graph (207 nodes, 1,515 edges, every edge instrumented). Versus Dijkstra with current speeds, mean travel-time reduction was 5.74% overall and 16.19% under incident conditions (p < .001), with 1.03% in peak hour (p = .0002) and a non-significant 0.01% off-peak. Combined GRU and routing latency was about 40 ms against the 1,000 ms dispatch cap (TD-A* 0.37 ms; GRU 39.3 ms). One-way ANOVA showed that travel time did not differ among δ = 0.05, 0.10, 0.15 and 0.20 (F ≈ 0.001, p = 1.00); δ = 0.20 was therefore selected as the operational default because it triggered fewer extra recommendations without losing travel-time benefit.
```

Also in the same Abstract paragraph, fix the dataset/graph mix-up.

**GET THIS**

```
The GRU model was trained on the METR-LA and PEMS-BAY dataset comprising 207 sensors and 34,254 five-minute observations
```

**REPLACE WITH**

```
Two separate GRU models were trained: one on METR-LA (207 sensors) and one on PEMS-BAY (325 sensors). Routing experiments used only the METR-LA detector graph
```

**GET THIS**

```
Simulation experiments were conducted across 900 origin-destination experiments (75 pairs × 3 traffic scenarios × 4 threshold values) on a real 397-node OpenStreetMap road network derived from Los Angeles County.
```

**REPLACE WITH**

```
Simulation experiments comprised 900 origin–destination runs (75 pairs × 3 traffic scenarios × 4 threshold values) on the METR-LA detector graph.
```

**GET THIS** (baselines list in the Abstract)

```
against Dijkstra, Static A*, and Oracle A* baselines
```

**REPLACE WITH**

```
against Dijkstra with current speeds, historical static A*, reactive A*, and an oracle with perfect future speeds
```

**For you only — do not add to the paper**

- `+0.17%` and `0.315 ms` and `δ = 0.10` and the 397-node OSM graph are from the **broken** evaluator (incidents often missed the vehicle; remaining time was compared with the original full trip; many OSM edges were fake 30 mph). They are **wrong**. Do not interpret them. Delete them.
- `F` is the ANOVA statistic: between-group variance ÷ within-group variance. `F ≈ 0` and `p = 1` means the four δ values produced essentially the same travel time. That part is still true on the new run (`F ≈ 0.001`, `p = 1.00`), but the **recommendation changes** from 0.10 to **0.20** (least chatty policy that still fires in incidents).
- Write italic lowercase *p*, not `P`.
- Reis 160→13 minutes is **not** your result. Do not put it in the Abstract.
- After this replace, Abstract stays under 500 words.

---

# Chapter 1 — section by section

Fix the heading first. Your Heading 1 currently reads as one glued line.

## 1.0 Chapter title and 1.1 heading

**GET THIS** (the heading line)

```
Background of the StudyGlobal Perspective
```

**REPLACE WITH two headings**

```
1.1 Background of the Study
```

Next line, not Heading 1 — use the same style as “Regional Perspective”:

```
Global Perspective
```

---

## 1.1 Background — Global Perspective

**First paragraph:** starts `Intelligent transportation systems (ITS) emerged…`  
**Action:** keep. No balloon here.

**Second paragraph:** starts `Urban traffic congestion posed a direct threat…`  
**Action:** keep Zhang et al. (2022), ITF, Binshaflout & Ahmad (2023). Do **not** insert the eight new 2021–2026 papers here; they belong in Chapter 2.

**For you only — do not add to the paper**  
This paragraph is motivation, not your experiment. “10% mortality per minute” is from Zhang, Sun, and Liu (2022), not from your 900 runs.

---

## 1.1 Background — Regional Perspective

**Paragraph:** starts `In Sub-Saharan Africa…`  
**Action:** keep Golub et al. (2021), Mugeere et al. (2020), AfDB (2022).

**For you only — do not add to the paper**  
This is context. Your simulation never left Los Angeles County. Regional delay figures must not be converted into “my framework would save X minutes in Lagos.”

---

## 1.1 Background — Local Perspective

**Paragraph:** starts `The Nairobi context was particularly acute.`

### Your comment: “Why is this intext-cited this way?” on Reis et al. (2025) and Ikram et al. (2025)

**Action: KEEP both citations. Do not list every author.**

APA 7 (KyU): three or more authors → **et al. from the first mention**.

- Narrative (author in the sentence): `Reis et al. (2025) documented…`
- Parenthetical (author in brackets): `(Reis et al., 2025)`

That is why it looks “thin.” It is correct.

Optional polish only if you want the sentence to sound less like those papers are *your* deployment:

**GET THIS**

```
Recent evidence confirms that technology-driven routing improvements can be transformative in Kenyan contexts: Reis et al. (2025) documented a reduction in urban emergency response times from over 160 minutes to 13 minutes following deployment of real-time dispatch routing, while Ikram et al. (2025) demonstrated that dynamic routing algorithms outperformed static shortest-path approaches for emergency vehicle navigation in congested urban networks.
```

**REPLACE WITH**

```
Published Kenyan and related urban studies have shown that dispatch-side routing can cut delays when the organisational setting allows it: Reis et al. (2025) reported a fall in urban emergency response times from over 160 minutes to 13 minutes after real-time dispatch routing was deployed, and Ikram et al. (2025) reported that dynamic routing outperformed static shortest-path rules in congested networks. Those results motivate the present decision-support design; they are not measurements from this study’s simulation.
```

**For you only — do not add to the paper**

- Reis’s 160→13 min is another project’s operational figure. Your honest incident result is **16.19%** versus Dijkstra on METR-LA, about 727 s → 599 s in that cell — **not** 160 min → 13 min.
- Do **not** write “therefore Nairobi CBD would meet the WHO 8-minute target.” Your delimitations forbid that claim.
- If a supervisor asks for first-citation full names, that is APA 6. KyU asked for APA 7, so et al. stays.

**Figure 1.1** caption (`Illustrative — INRIX, 2024 & WHO, 2015`): keep, but the word **Illustrative** must stay. It is not an output of your GRU.

---

## 1.1 closing paragraph (after Figure 1.1)

**Paragraph:** starts `Research in ITS produced significant advances…` ends with Qi et al. (2025).

**Action:** keep Qi et al. (2025). After that sentence, add **one** gap sentence that later Chapter 2 will expand with the eight papers. Do not dump all eight citations into Chapter 1.

**After this sentence:**

```
A 2025 systematic review by Qi et al. (2025) explicitly identified the disconnection between traffic prediction and path planning as the primary open problem in intelligent transportation research, confirming the timeliness of this study.
```

**INSERT (one new sentence, then stop)**

```
Surveys of graph-based traffic forecasting likewise treat gated recurrent units as a strong temporal baseline rather than the lowest-error architecture, which is why this study used GRU inside a latency-bounded dispatch loop rather than as a claim of forecasting supremacy (Jiang & Luo, 2022; Yin et al., 2022).
```

**For you only — do not add to the paper**  
Jiang and Yin go in Chapter 2 in full. One sentence in 1.1 is enough so the examiner sees you already know GRU is not “best MAE.”

---

## 1.2 Statement of the Problem

**First paragraph:** static routes cost lives — **keep**.

**Second paragraph:** starts `While machine learning models accurately predicted…`

**GET THIS**

```
While machine learning models accurately predicted short-term traffic patterns and time-dependent pathfinding algorithms existed as separate research streams, no integrated decision-support framework simultaneously achieved prediction accuracy, computational efficiency, and adaptive route recommendation at a scale suitable for emergency dispatch centres (Abuaisha et al., 2025; Qi et al., 2025).
```

**REPLACE WITH**

```
While machine learning models predicted short-term traffic and time-dependent pathfinding algorithms existed as separate research streams, published emergency systems still emphasised detection or signal pre-emption rather than a remaining-time replanning controller, and prediction–routing integration for dispatch remained thin (Abuaisha et al., 2025; Chowdhury et al., 2023; Qi et al., 2025).
```

**For you only — do not add to the paper**  
Abuaisha does **not** nullify you: they replanned **fixed bus corridors** (12–18%). You replan **unconstrained EV paths** with GRU + TD-A* + δ. Keep the cite; the new clause stops the sentence from sounding as if “nobody ever combined prediction and routing.” Zhang, Khalgui and Li (2021) did, but not for emergency remaining-time control — that distinction belongs in Chapter 2, not a long Ch. 1 paragraph.

Leave the Nairobi WHO sentence in 1.2 as **motivation**. Do not attach `+16.19%` here.

---

## 1.3 Purpose of the Study

**GET THIS**

```
The purpose of this study was to design and evaluate through simulation a scalable Intelligent Route Optimisation Framework demonstrating potential for significantly reducing emergency vehicle travel time by anticipating traffic volatility through integrated predictive modelling and adaptive pathfinding.
```

**REPLACE WITH**

```
The purpose of this study was to design and evaluate, through simulation, an Intelligent Route Optimisation Framework that integrated short-term traffic prediction with time-dependent pathfinding and a remaining-time replanning threshold, and to measure whether that integration reduced emergency-vehicle travel time relative to non-predictive dispatch rules, especially when traffic was disrupted.
```

**For you only — do not add to the paper**  
“Significantly reducing” in the purpose sounds like you promised a large cut in every condition. Your results are **large in incidents (16.19%)**, **small in peak (1.03%)**, **zero off-peak**. The purpose should promise a **fair measurement**, not a 78% miracle.

---

## 1.4 Research Objectives

**General objective:** keep.

**Specific Objective 1:** keep (literature / gap analysis).

**Specific Objective 2** — missing asterisk.

**GET THIS**

```
a Time-Dependent A routing algorithm
```

**REPLACE WITH**

```
a Time-Dependent A* (TD-A*) routing algorithm
```

**Specific Objective 4** — your later tables use four baselines; the objective currently names two.

**GET THIS**

```
Specific Objective 4: To evaluate framework performance through simulation-based experiments against Dijkstra and static A* baselines using travel time reduction, computational latency, and recommendation update frequency as primary metrics.
```

**REPLACE WITH**

```
Specific Objective 4: To evaluate framework performance through simulation-based experiments against four baselines — Dijkstra with current speeds, historical static A*, reactive A* without a 30-minute forecast, and an oracle with perfect future speeds — using travel time reduction, computational latency, and recommendation update frequency as primary metrics.
```

**For you only — do not add to the paper**  
If you leave Objective 4 as “Dijkstra and static A* only,” Chapter 4’s B3/B4 tables look like extras you invented after the fact. You already ran four baselines. Align the objective with the experiment.

---

## 1.5 Research Questions

**RQ1:** keep (this is the question Table 3.1 must copy; the dash to fill is in Chapter 3, not here).

**RQ2:** keep. Optional: after `non-predictive systems` you may add `and against a reactive A* rule that replans only after a slowdown is already visible`.

**RQ3:** keep (`δ` across 5–20%).

**RQ4:** keep.

No balloon in this section.

---

## 1.6 Justification of the Study

**Paragraph:** starts `This research addressed a critical gap…`

**After this sentence:**

```
Theoretically, it advanced intelligent transportation systems by integrating predictive modelling with adaptive graph search optimised for time-dependent routing under computational constraints — an area that had received insufficient attention in the literature (Judijanto & Rismanto, 2021; Qi et al., 2025).
```

**INSERT**

```
The practical contribution was not a new shortest-path algorithm and not a lowest-error traffic predictor; it was the integration of a latency-feasible GRU, time-dependent A*, and an empirically tested remaining-time threshold, evaluated on 900 ground-truth journeys (Jiang & Luo, 2022; Abdullah et al., 2023).
```

**GET THIS** (last sentence of 1.6, overclaim)

```
The economic impact was substantial, with the potential to mitigate billions in annual congestion-related losses while meaningfully improving public safety outcomes.
```

**REPLACE WITH**

```
The intended beneficiaries were emergency dispatch centres operating under congestion, including services in rapidly growing cities such as Nairobi. Transfer of the method to Kenyan roads would still require local sensors; the present numbers are benchmark evidence, not a Nairobi field trial.
```

**For you only — do not add to the paper**  
You did not invent Dijkstra or A*. Humility is correct; erasing the integration is not. The “billions” sentence is not supported by your 900 runs.

---

## 1.7 Limitations

### Your comment: gaps in the dataset / 18.6% / did that break the model?

**GET THIS** (last sentence of the limitations paragraph)

```
Sensor-to-edge mapping covered only 18.6% of graph edges; the remaining edges used free-flow speed estimates rather than GRU-predicted travel times.
```

**REPLACE WITH**

```
The defended routing experiments used the METR-LA detector adjacency (207 nodes, 1,515 edges) so that every simulated edge carried a sensor speed. An earlier OpenStreetMap extract in which only 18.6% of edges were sensor-mapped was not the graph behind the reported 900-run tables. METR-LA and PEMS-BAY remain United States freeway traces; they do not reproduce Nairobi mixed traffic, and no claim is made that the measured percentages would hold in the CBD.
```

Keep the earlier sentences on Sub-Saharan mismatch and simulation limits.

**For you only — do not add to the paper**

- **18.6% was not “gaps in METR-LA.”** METR-LA missing loops were imputed in Chapter 3 (zeros / dropouts). 18.6% meant: on the **old OSM map**, only 190 of 1,024 streets sat near a detector; the other 81.4% were given a fake 30 mph. That made peak-hour detours look clever and flattened many comparisons. It is **not** why GRU MAE is 3.48 mph.
- **Did 18.6% make the model misbehave?** It made the **old router** misbehave. The improved 900-run turned that map off. Do not discuss 18.6% as a property of Table 4.5.
- **How to visualise missing detector values (for you, in code, not in Ch.1):** plot one sensor’s speed series; holes are zeros/NaNs before imputation. That belongs in Chapter 3/4 if you add a figure, not in 1.7.
- Do **not** paste “18.6% caused 0% routing” or “18.6% caused 78%.” Both old tables are invalid.

---

## 1.8 Delimitations

### Your comment: Include PEMS-BAY?

**Yes — as a second prediction city. No — as a second routing city.**

**GET THIS**

```
This study focused on emergency vehicle routing in urban road networks with significant temporal traffic variability, using METR-LA as the primary evaluation dataset. The research was delimited to short-term prediction (15 to 30 minutes), simulation-based evaluation, and single-vehicle route optimisation. Road network modelling used OpenStreetMap data for Los Angeles County.
```

**REPLACE WITH**

```
This study focused on emergency vehicle routing in urban road networks with significant temporal traffic variability. METR-LA was the routing evaluation dataset (detector graph, 207 nodes). PEMS-BAY was included only as a second-city check of the same GRU architecture (325 sensors), not as a second routing graph. The research was delimited to short-term prediction (15 to 30 minutes), simulation-based evaluation, and single-vehicle route optimisation.
```

**For you only — do not add to the paper**

- Including 325 Bay sensors **inside Table 4.5** would be a different city and a different graph. Do not mix the two speed matrices into one GRU.
- Script for the Bay **predictor** (already run): `python -m src.prediction.train_pems_bay` → MAE **2.38 mph**.
- Bay **routing** 900-run does not exist yet. Future work, not a Ch.1 promise you failed.

---

## 1.9 Assumptions

**GET THIS**

```
It was assumed that traffic sensors could be reliably mapped to OpenStreetMap road segments, that emergency vehicles experienced delays broadly correlating with general traffic conditions, and that FIFO properties held for road segments.
```

**REPLACE WITH**

```
It was assumed that detector-to-detector travel on the METR-LA adjacency was a sufficient routing surface for the simulation, that emergency vehicles experienced delays broadly correlating with general traffic conditions on those links, and that the FIFO property held after travel times were clipped to a one-second minimum.
```

**For you only — do not add to the paper**  
You no longer depend on “OSM mapping is reliable” for the headline result. FIFO clipping is in `travel_times` / the cost builder; it stops negative or reversed times so TD-A* stays valid.

---

## 1.10 Operational Definition of Terms

Keep all terms. One extra definition (helps later chapters; no balloon here).

**After the Replanning Threshold (δ) entry, INSERT**

```
Significance level (α). The Type I error rate used in t-tests and ANOVA, set at .05. This is not the same quantity as the replanning threshold δ; δ = 0.05 means a 5% remaining-time trigger, whereas α = .05 means a statistical decision rule.
```

**For you only — do not add to the paper**  
You asked this properly in Chapter 3 balloons. Defining both in 1.10 stops you mixing them later. Italic *p*, italic *F*, italic *α*, italic *δ*.

---

# What Chapter 1 must not do

- Do not paste 78%, 123 s, 588 s, +0.17%, 0 replans, 397 nodes, 18.6% as a headline result, 17 epochs, MAE 3.42, 0.315 ms, or “recommend δ = 0.10.”
- Do not put the full eight-paper review in Chapter 1 (that is Chapter 2, Sections 2.4–2.7).
- Do not discuss ANOVA, MAE tables, or 900-run interpretation in Chapter 1. Those sentences belong in Chapter 4 after the tables.
- Do not convert +16.19% into “Nairobi now meets eight minutes.”

---

# After you finish Chapter 1 (checklist)

1. Ctrl+F `0.17` `18.6` `397-node` `0.315` `δ = 0.10` `P = 1` — none should remain except a clearly labelled “earlier draft / unused OSM mode” phrase in 1.7, which you already replaced.
2. Ctrl+F `Time-Dependent A ` (space, no star) in Objective 2 — should now be `A*`.
3. Add Jiang and Luo (2022), Yin et al. (2022), Chowdhury et al. (2023), Abdullah et al. (2023) to the **reference list** when you first cite them (full APA is in the previous message). Chapter 2 will use the other four.
4. Word Count: Chapter 1 will grow by only a few hundred words. The 20,000-word gap is still Chapters 2–4.
