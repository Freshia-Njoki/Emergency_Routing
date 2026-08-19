# Speaker notes — 15-minute research seminar

Open `docs/Freshia_Njoki_Obj34_Findings_Presentation.pptx`. View → Notes.

Same navy/gold file as before; **slide 11 is now Limitations and further research**, not an internal correction list.

| Min | Slide | Say this |
|---|---|---|
| 0:00 | 1 Title | Thank the panel. This seminar reports a dispatcher-support loop: GRU speeds + time-dependent A* + a remaining-time trigger. 900 ground-truth journeys. |
| 0:30 | 2 Problem | Dispatch on the current map is optimal only at departure. A jam 15–30 minutes ahead is missed. Nairobi motivates the work; these percentages are Los Angeles detectors. |
| 1:45 | 3 Purpose / RQs | Read the purpose once. Four questions = four objectives. δ is a policy; *p* / α are statistics. This talk spends most time on Objectives 3 and 4. |
| 3:15 | 4 Framework | Observe 60 min → forecast 30 min → edge costs → TD-A* → δ → dispatcher authority. Remaining time is from where the vehicle is now. |
| 4:15 | 5 Design | Two GRUs, not one joint model. Routing = METR-LA 207 / 1,515 / 100%. 75×3×4 = 900. Four baselines including reactive A* and an oracle. |
| 5:30 | 6 Prediction | METR-LA MAE **3.48 mph** (27 epochs). PEMS-BAY **2.38 mph**, prediction only. Lightweight on purpose (sub-second loop). |
| 6:30 | 7 Objective 3 | Travel time flat across δ (ANOVA *F* ≈ 0, *p* = 1). Recommend **δ = 0.20**. 0.10 was the Chapter 3 guess. |
| 8:00 | 8 Journey time | Incident: **599 s vs 728 s**. Off-peak bars sit together. Framework must not beat the oracle. |
| 9:15 | 9 Reduction | **+16.19%** incidents (*p* < .001). Peak +1.03% (*p* = .0002). Off-peak ~0. Overall +5.74% is a mixture. |
| 10:45 | 10 Latency | Combined **~40 ms** (GRU 39.3 ms + TD-A* 0.37 ms) vs 1,000 ms cap. |
| 11:30 | 11 Limits | US freeways. 100% detector graph. No Nairobi 16%. Next: downsample **100% → 10–30%**; Bay *routing* 900-run; field trial. |
| 13:00 | 12 Close | Three lines: 16% in incidents; δ = 0.20; 40 ms. Then questions. |

**For you only — not on the slides.** If an examiner quotes an old draft: do not defend 78%, 123 s vs 588 s, +0.17%, 0 replans, 17 epochs, MAE 3.42, 0.315 ms as the system wait, 397 OSM nodes, or 18.6% as the 900-run graph. Defended file: `results/full_report.txt`.
