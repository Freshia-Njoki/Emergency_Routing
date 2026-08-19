# Speaker notes — 15 minutes (Objectives 3 & 4)

Open `docs/Freshia_Njoki_Obj34_Findings_Presentation.pptx`. View → Notes. Same text is under each slide.

| Min | Slide | Say this |
|---|---|---|
| 0:00 | 1 Title | This talk is Objectives 3 and 4 only, using the improved 900-run on branch `cursor/improve-ev-routing-framework-c48b`. |
| 0:30 | 2 Recap | Correct the last PPT: MAE **3.48** not 3.42; **34,272** frames; sensor graph **207 / 1,515**, not 397 OSM nodes. Two GRUs, not one. |
| 1:30 | 3 Design | 75 pairs × 3 scenarios × 4 δ = 900. Same clock, actual future speeds. Four baselines including reactive A* and an oracle. |
| 2:30 | 4 δ vs α | δ = remaining-time trigger. *p* / α = statistics. APA writes *p* = .0002 because *p* cannot exceed 1. |
| 3:30 | 5 Figure 3 | Incident reduction stays ~16% at every δ. ANOVA *F* ≈ 0, *p* = 1: travel time did not move. |
| 5:00 | 6 Table | Recommend **δ = 0.20** (least extra alerts, same time). 0.10 was the planned guess. |
| 6:00 | 7 Figure 1 | Incident: **599 s vs 728 s**. Off-peak bars sit together. Not 123 s vs 588 s. |
| 7:30 | 8 Figure 2 | **+16.19%** incidents (*p* < .001). Peak +1.03% (*p* = .0002). Off-peak ~0. Overall +5.74% is a mixture. |
| 9:00 | 9 Latency | Combined **~40 ms**, not 0.315 ms. 0.315 was routing-only on the old map. |
| 10:00 | 10 Meaning | Jam → offer another road. Empty roads should tie. Werner does not nullify this. |
| 11:30 | 11 Limits | US freeways. No Nairobi 16%. Next: downsample **100% → 10–30%**, not 18.6% → 5%. |
| 13:00 | 12 Close | Three lines: 16% in incidents; δ = 0.20; 40 ms. Then questions. |

If asked **which branch:** `cursor/improve-ev-routing-framework-c48b`, not `main`.
