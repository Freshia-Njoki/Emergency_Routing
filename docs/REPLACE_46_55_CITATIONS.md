# Exact GET / REPLACE — 17 epochs, δ default, §4.6, §5.5, two citations

Ctrl+F the **GET THIS** string. Paste **REPLACE WITH**.  
**For you only** is not for the thesis or the article.

---

## 17 epochs → 27 epochs

**Yes.**

**GET THIS** `17 epochs`  
**REPLACE WITH** `27 epochs`

Do this everywhere it describes **your** METR-LA GRU (Table 4.3, the paragraph under it, Figure 4.8 caption, Chapter 5 if present).

Same paragraph usually also has the old error. Fix those too:

**GET THIS** `3.42` (when it is *your* test MAE)  
**REPLACE WITH** `3.48`

**GET THIS** `6.14` (when it is *your* test RMSE)  
**REPLACE WITH** `6.04`

**For you only.** Early stopping stopped the improved training at epoch 27 (`results/full_report.txt`: `Epochs trained : 27`). 17 was the older checkpoint (MAE 3.42). Do not write both.

PEMS-BAY **stays 79 epochs**. Do not change that 17.

---

## δ = 0.10 as default → δ = 0.20

**GET THIS** (any of these)

```
δ = 0.10 was recommended as the operational default
```

```
delta = 0.10 was recommended as the operational default
```

```
The threshold policy delta = 0.10 should be adopted as the default
```

```
recommended operational default of delta = 0.10
```

**REPLACE WITH** the matching sentence using **0.20**:

```
δ = 0.20 was recommended as the operational default
```

```
delta = 0.20 was recommended as the operational default
```

```
The threshold policy delta = 0.20 should be adopted as the default
```

```
recommended operational default of delta = 0.20
```

### Why 0.20 now (for you only — do not paste this paragraph into Chapter 3 as if it were the plan)

Chapter 3 **guessed** 0.10 (middle of 5–20%, not too many alerts).

The 900-run then showed:

| δ | Travel time vs Dijkstra | Replans per journey |
|---|---|---|
| 0.05 | +5.726% | 0.45 |
| 0.10 | +5.748% | 0.44 |
| 0.15 | +5.726% | 0.43 |
| 0.20 | +5.767% | 0.39 |

ANOVA: *F* ≈ 0.001, *p* = 1.00 → the four policies **tied on travel time**.  
A 40% corridor slowdown makes remaining time jump by **more than 20%**, so even δ = 0.20 still fires in incidents (~1 replan).  
DSS theory: if quality is the same, pick the policy that talks **less** → **0.20**.

Keep `{5%, 10%, 15%, 20%}` as the **tested set**. Only the **recommended default** changes from 0.10 to 0.20.

---

## Section 4.6.1 — replace all three paragraphs

**Heading:** `4.6.1 Travel Time Reduction`

**GET THIS** (paragraph 1)

```
The statistically significant travel time reduction in incident conditions (+0.17%, p = 0.004) confirmed that TD-A* routing guided by GRU predictions identified marginally faster alternatives when sudden speed drops affected sensor-mapped road segments. When the METR-LA test set injected incident conditions — reducing speeds to 40 percent of normal on 15 percent of sensors — the GRU module detected likely congestion ahead and computed alternative routing decisions before the vehicle arrived at affected segments. This constituted the primary operational advantage of the predictive framework over reactive baselines, which could not anticipate conditions beyond the current snapshot.
```

**REPLACE WITH**

```
Under incident conditions the framework reduced Dijkstra travel time by 16.19% (about 599 s against 728 s, p < .001), with about one replan per journey. When the planned road was slowed by 40%, the controller offered another path. That was the main operational gain over keeping the dispatch-time route.
```

**GET THIS** (paragraph 2)

```
Peak-hour and off-peak reductions were not statistically significant. This outcome reflected a structural constraint rather than a model failure: only 190 of 1,024 directed graph edges (18.6 percent) carried GRU-predicted travel times. The remaining 81.4 percent of edges used free-flow speed estimates regardless of routing method. During peak hour, the GRU correctly predicted lower speeds on sensor-mapped primary roads, causing the framework to reroute towards unmapped alternative roads. Those alternatives, however, also experienced peak-hour congestion not captured by sensor data, resulting in actual journey times slightly exceeding Dijkstra's path (mean −1.50 percent, p = 0.062). This finding was directionally consistent with the established observation in predictive routing literature that incorrect or incomplete predictions can introduce detour costs exceeding prediction benefits (Qi et al., 2025; Werner et al., 2022). It also established sensor coverage density — rather than prediction accuracy — as the binding constraint on travel time improvement in this experimental configuration.
```

**REPLACE WITH**

```
Peak hour showed a small significant gain of 1.03% (p = .0002): when most roads were already slow, looking 15 to 30 minutes ahead helped only a little. Off-peak times were tied (0.01%, p = .90). That near-zero result was expected on empty roads and was treated as a successful check, not a failed model. These figures used the METR-LA detector graph with every edge instrumented. They do not come from the unused OpenStreetMap extract in which only 18.6% of edges had sensors.
```

**GET THIS** (paragraph 3)

```
The framework produced zero replannings across all 900 experiments. This reflected the high temporal consistency of successive GRU prediction windows on METR-LA historical data: the deviation between initial and updated predictions never exceeded any tested threshold during the short journeys characteristic of a 397-node proof-of-concept network. This finding was consistent with the ANOVA result for Objective 3 and confirmed that the adaptive controller was correctly implemented; the proof-of-concept dataset and network simply did not produce the high-volatility conditions under which mid-journey replanning is expected to activate. Field deployment with live sensor feeds in Nairobi — where matatu operations and mixed-traffic incidents produce abrupt, unpredictable speed changes — is expected to generate the replanning trigger conditions absent from historical freeway data.
```

**REPLACE WITH**

```
Incident journeys triggered about one replan (mean 1.03). That replaced the earlier zero-replan tables, which had compared remaining time with the original full trip and had often missed the vehicle with the incident. Nairobi live sensors were not used in this simulation; the 16.19% figure is a Los Angeles detector result, not a measured CBD saving.
```

**For you only.** Do not interpret +0.17%, −1.50%, or 0 replans. Those were the broken run.

---

## Section 4.6.2

**GET THIS**

```
Routing latency of 0.315 ms on a 397-node urban graph confirmed that unpreprocessed TD-A* was computationally trivial for dispatch hardware. Werner et al. (2022) achieved interactive query times on continental networks through preprocessing-based techniques; this study demonstrated that preprocessing was unnecessary at urban dispatch scale, eliminating the incompatibility with five-minute weight update cycles identified as a limitation of that approach. The practical system bottleneck was GRU inference at approximately 69.1 ms, which remained well within operational limits. Combined system response time averaged 69.4 ms per route recommendation — approximately 3,175 times below the 1,000 ms dispatch requirement, and approximately 14 times faster than the reported human decision window in emergency dispatch contexts, confirming computational feasibility for real-time deployment.
```

**REPLACE WITH**

```
TD-A* routing latency averaged 0.37 ms on the 207-node detector graph. GRU inference averaged 39.3 ms. Combined response time was about 40 ms, well below the 1,000 ms dispatch cap. Werner et al. (2022) showed that time-dependent A* can be fast on very large maps using preprocessing; at this urban scale, preprocessing was not required, so edge weights could be refreshed every five minutes.
```

---

## Section 4.6.3

**GET THIS**

```
The insensitivity of travel time reduction to threshold value (ANOVA p = 1.000) carried a specific operational implication: within the range tested, a dispatcher received fewer or more updates without any measurable change in the underlying route quality. This supported delta = 0.10 as the recommended default, consistent with DSS theory, which emphasised calibrating information delivery to the decision-maker's cognitive constraints rather than maximising information volume. The zero-replanning result across all 900 experiments reflected the high temporal consistency of successive GRU prediction windows on METR-LA historical data. Higher-volatility conditions, such as live Nairobi dispatch environments where matatu incidents produce abrupt speed drops across multiple sensors simultaneously — are expected to activate the controller in field deployment.
```

**REPLACE WITH**

```
Travel time did not differ among δ = 0.05, 0.10, 0.15 and 0.20 (ANOVA F ≈ 0.001, p = 1.00). Incident trips still replanned at every tested value. The operational default was therefore δ = 0.20: the same travel time, slightly fewer extra alerts. The value 0.10 remains in Chapter 3 only as the planned starting guess, not as the measured recommendation.
```

**GET THIS** (next paragraph in 4.6.3, if still there)

```
The zero-replanning outcome across all 900 experiments reflected two compounding factors. First, the METR-LA historical test set exhibited high temporal autocorrelation: consecutive 5-minute speed readings on the same sensor were highly correlated, producing successive GRU prediction windows with very similar forecast values. Second, journeys on the 397-node proof-of-concept network completed in fewer time steps than the 6-step prediction horizon, meaning the sliding prediction window had not advanced far enough during any single journey to generate substantially different forecasts between the initial route and the replanning check. These conditions described the stability of the historical simulation rather than a deficiency in the controller implementation, which remained correctly designed and ready to activate under higher-volatility real-world inputs.
```

**REPLACE WITH**

```
The controller was not silent. Remaining time was measured from the vehicle’s current position, and incidents sat on the planned corridor, so remaining time jumped enough to exceed δ. That is why incident replans averaged about one per journey rather than zero.
```

---

## Section 4.6.4

**GET THIS**

```
Three limitations of the presented results should be acknowledged. First, sensor-to-edge mapping covered 190 of 1,024 graph edges (18.6 percent); the remaining edges used free-flow speed estimates rather than GRU-predicted travel times. Greater mapping coverage would increase prediction influence on routing outcomes. Second, METR-LA data reflected US freeway conditions that differed from the mixed-traffic, lower-sensor-density environment of Nairobi. Sparse-sensor sensitivity analysis (10 to 30 percent sensor coverage) was applied to address this gap. Third, GRU cross-dataset validation on PEMS-BAY was completed and confirmed generalisation (MAE 2.38 mph, Section 4.3.4). Full routing simulation on the PEMS-BAY road network — constructing an equivalent OpenStreetMap graph for San Francisco Bay Area and running the 900-experiment harness — remains as immediate next work to test the framework under a second geographical network topology.
```

**REPLACE WITH**

```
Three limits should be stated. First, the reported 900 journeys used 100% detector coverage on Los Angeles freeways, not Nairobi mixed traffic. Second, a 10 to 30 percent coverage run, as a Nairobi analogue, was not carried out and remains further research. Third, PEMS-BAY confirmed the GRU in a second city (MAE 2.38 mph) but was not given a 900-journey routing test.
```

---

## Section 5.5 — replace the coverage bullets

**Heading:** `5.5 Suggestions for Further Research`  
KyU: **no new citations** in Chapter 5.

**GET THIS**

```
Nairobi sparse-sensor deployment study: This study demonstrated that 18.6 percent sensor coverage constrained route differentiation in peak-hour conditions. A systematic study progressively reducing sensor coverage from 18.6 percent to 10 and 5 percent of road edges should be conducted to simulate the infrastructure density of Nairobi's road network, identifying the minimum viable sensor density at which the framework maintains statistically significant routing improvements over reactive baselines.
```

**REPLACE WITH**

```
Sparse-sensor Nairobi analogue: A future experiment should downsample the present 100% detector graph to 10 to 30% coverage and repeat the 900-run. That experiment was not part of this study.
```

**GET THIS** (duplicate bullet, if both exist)

```
Sparse-sensor sensitivity analysis: A systematic study reducing sensor coverage from 100 percent to 10 to 30 percent should be conducted to model Nairobi's infrastructure density and quantify the degradation in framework performance under sparse conditions.
```

**REPLACE WITH**  
Delete this bullet if you already pasted the one above. Keep **one** sparse-sensor bullet only.

**GET THIS**

```
Sensor coverage density study: This study demonstrated that 18.6 percent sensor coverage constrained the framework's ability to differentiate routing paths in peak-hour conditions. A systematic study increasing sensor coverage from 18.6 percent to 50, 75, and 100 percent through simulated imputation or network densification should be conducted to identify the coverage threshold at which travel time reductions become statistically significant across all scenarios.
```

**REPLACE WITH**

```
The 100% detector-coverage experiment is already the reported 900-run. No further increase from 18.6% is required for this thesis.
```

Leave the multi-vehicle, field-trial, and live-data bullets. They are genuine further work.

**GET THIS** (5.4.1, if present)

```
Dispatch system developers should prioritise sensor-to-edge mapping coverage as a primary quality metric. Increasing coverage toward 80 percent or higher would allow the framework to deploy GRU-predicted travel times on a substantially larger portion of the routing graph.
```

**REPLACE WITH**

```
Future Nairobi-oriented work should test the same controller on a downsampled detector graph (10 to 30% coverage), not on the unused downtown OpenStreetMap extract.
```

---

## The two article citations (this is only a bibliography fix)

These are **not** new experiments. They are the **correct published record** of papers you already meant to cite.

### 1. Abdullah et al. (2023) — wrong article number

MDPI *Sustainability* uses an **article number**, not pages. An earlier draft wrote **5716**. The GRU congestion paper is article **5949**.

**GET THIS** (reference list)

```
Abdullah, S. M., Periyasamy, M., Kamaludeen, N. A., Towfek, S. K., Marappan, R., Kidambi Raju, S., Alhussan, A. A., & Khafaga, D. S. (2023). Optimizing traffic flow in smart cities: Soft GRU-based recurrent neural networks for enhanced congestion prediction using deep learning. Sustainability, 15(7), 5716. https://doi.org/10.3390/su15075716
```

**REPLACE WITH**

```
Abdullah, S. M., Periyasamy, M., Kamaludeen, N. A., Towfek, S. K., Marappan, R., Kidambi Raju, S., Alharbi, A. H., & Khafaga, D. S. (2023). Optimizing traffic flow in smart cities: Soft GRU-based recurrent neural networks for enhanced congestion prediction using deep learning. Sustainability, 15(7), 5949. https://doi.org/10.3390/su15075949
```

**In-text stays:** `(Abdullah et al., 2023)`  
You do **not** write 5949 in the chapter sentence. 5949 belongs only in the reference list.

**For you only.** 5716 is a different article ID / a typo. Open https://doi.org/10.3390/su15075949 to check it is the soft-GRU paper.

### 2. Distillation paper — wrong first author

Same research, two listings. arXiv listed Wang first. The **published AAAI 2025** paper lists **Zhang, Q.** first. APA cites the published version.

**GET THIS** (in-text)

```
Wang et al. (2025)
```

**REPLACE WITH**

```
Zhang, Gao, et al. (2025)
```

(`Gao` is needed so it is not confused with Zhang, Khalgui, and Li, 2021.)

**GET THIS** (reference list, arXiv line)

```
Wang, H., Shen, Z., Zhang, Y., et al. (2025). Efficient traffic prediction through spatio-temporal distillation. arXiv:2501.10459.
```

**REPLACE WITH**

```
Zhang, Q., Gao, X., Wang, H., Yiu, S. M., & Yin, H. (2025). Efficient traffic prediction through spatio-temporal distillation. Proceedings of the AAAI Conference on Artificial Intelligence, 39(1), 1093–1101. https://doi.org/10.1609/aaai.v39i1.32096
```

**For you only.** You did **not** run distillation. You only cite that paper to say: the field is shrinking big models; that supports keeping a small GRU. The article file `docs/research_article_v0.3.md` already has both of these reference lines. Copy them into your journal Word/LaTeX list if they are still 5716 / Wang et al. there.

---

## Quick Ctrl+F after you finish

| Find | Should remain as *your* result? |
|---|---|
| `17 epochs` | No → 27 (METR-LA only) |
| `3.42` | No → 3.48 (your MAE) |
| `0.315` | No → 0.37 ms routing, ~40 ms combined |
| `+0.17%` | No → +16.19% |
| `zero replan` | No → ~1.03 in incidents |
| `δ = 0.10` as **default** | No → 0.20 (keep 0.10 as a **tested** value) |
| `18.6%` as the 900-run graph | No |
| `5716` | No → 5949 in the Abdullah reference only |
| `Wang et al. (2025)` distillation | No → Zhang, Gao, et al. (2025) |
