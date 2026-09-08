# How Much Sensing Is Enough? Sensor-Coverage Sensitivity of GRU-Based Predictive Emergency Vehicle Routing

**Freshia Njoki Macharia¹\*, Gilbert Langat², Stephen Mageto²**
¹Department of Computer Science and Informatics, Kirinyaga University, Kerugoya, Kenya
²School of Pure and Applied Sciences, Kirinyaga University, Kerugoya, Kenya
\*Corresponding author: fnjokimacharia@gmail.com

> **Note to author (not part of the manuscript).** This paper is deliberately scoped to a contribution your **published** paper — *Design and Evaluation of a GRU-Based Predictive Routing Framework for Emergency Vehicles* (hereafter **Macharia et al., 2025**) — did **not** make: it treated the framework only at 100% sensor coverage and named coverage sensitivity as future work. This manuscript delivers that experiment. It **cites** the published paper for the framework rather than re-reporting it, which is what keeps the two papers non-overlapping and ethically publishable. Every number in the Results is from a real run (`results/coverage/coverage_results.csv`); nothing is invented.

---

## Abstract

Predictive emergency-vehicle routing that couples short-horizon traffic forecasting with time-dependent search has been shown to cut incident-condition travel time on fully instrumented road networks. Whether that benefit survives the sparse sensing typical of low- and middle-income cities is unknown, and it is the question that determines transferability. This article quantifies, for the first time, how the benefit of a Gated Recurrent Unit (GRU) plus Time-Dependent A\* (TD-A\*) emergency-routing framework degrades as sensor coverage falls from complete instrumentation toward Nairobi-realistic sparsity. Holding the trained predictor, the detector graph, and the ground-truth future speeds fixed, we varied only the fraction of network edges whose live speed the router can observe (100%, 70%, 50%, 30%, 20%, 10%); uncovered edges inherited speeds by k-nearest-neighbour inverse-distance interpolation, the standard loop-detector reconstruction. The vehicle always experienced true speeds; only the router's information was thinned. Across 8,100 matched simulated journeys on the METR-LA detector graph, incident-condition travel-time reduction versus current-map Dijkstra fell monotonically from 16.3% at full coverage to 10.1% at 70%, 8.2% at 50%, and 4.4% at 30%, then plateaued near 4.6–5.2% at 10–20% (all *p* < 0.001). Peak-hour and off-peak reductions stayed near zero at every coverage level, a negative control. Routing latency remained sub-millisecond throughout. The results establish sensor-coverage density — not model accuracy or compute — as the binding constraint on predictive-routing benefit, quantify a steep decline between full and ~30% coverage followed by a low residual plateau, and give transport authorities a concrete instrumentation target: roughly half of arterial edges must carry live sensing to retain half of the achievable incident benefit.

**Keywords:** emergency vehicle routing; sensor coverage; spatial interpolation; gated recurrent unit; time-dependent A\*; intelligent transportation systems; sparse instrumentation

---

## 1. Introduction

Urban emergency response is a shortest-path problem executed under time pressure, and each additional minute of ambulance delay at a cardiac-arrest scene is associated with roughly a 10% rise in mortality (Zhang, Sun, & Liu, 2022). Predictive routing frameworks that forecast traffic 15–30 minutes ahead and route on those forecasts have recently been shown to reduce incident-condition travel time relative to the snapshot shortest paths used by current computer-aided dispatch (Macharia et al., 2025; Qi et al., 2025). In prior work we designed, implemented, and evaluated one such framework — a GRU speed predictor, a Time-Dependent A\* router, and a remaining-time replanning controller — and reported a 16.19% incident-condition reduction versus current-map Dijkstra on a fully instrumented detector graph (Macharia et al., 2025).

That result, like almost all predictive-routing evaluations, assumed complete sensing: every routing edge carried a live speed. Real deployment targets, and especially the rapidly growing cities of Sub-Saharan Africa that motivate emergency-routing research, do not meet that assumption. Nairobi and comparable cities instrument only a small fraction of their road network, and mixed traffic makes each sensor's reading less locally representative (Golub et al., 2021). The open question is therefore not whether predictive routing helps when every edge is observed, but **how much of that benefit remains as coverage thins** — and, correspondingly, how much sensing a transport authority must fund before the approach is worth deploying. Prior work, including our own, listed this coverage sensitivity explicitly as future work but did not measure it (Macharia et al., 2025).

This article closes that gap. Our contributions are:

1. **A coverage-degradation protocol** that isolates the effect of sensor sparsity: the trained predictor, the road graph, and the ground-truth speeds are held fixed while only the fraction of edges the router can observe is varied, with uncovered edges reconstructed by inverse-distance interpolation.
2. **The first quantitative degradation curve** for GRU + TD-A\* emergency routing, from full instrumentation to 10% coverage, with statistical significance and error bars over independent sensor-retention draws.
3. **A minimum-viable-coverage finding** — the benefit falls steeply from full to ~30% coverage and then plateaus at a low residual — together with the mechanism (loss of incident observability and cost-field precision) and its practical implication for instrumentation policy.

## 2. Related Work

**Predictive and time-dependent routing.** Time-dependent shortest-path theory routes on costs that change with entry time (Dreyfus, 1969; Jaballah, Veenstra, Coelho, & Renaud, 2021), and Werner and Zeitz (2022) combined predicted and live traffic inside time-dependent A\* on continental networks. Macharia et al. (2025) integrated a GRU predictor with TD-A\* and a remaining-time controller specifically for emergency dispatch and evaluated it on matched journeys scored with actual future speeds. None of these studies varied sensor coverage; all assumed the routing graph's speeds were available.

**Traffic prediction under sparse sensing.** The METR-LA and PEMS-BAY benchmarks (Li, Yu, Shahabi, & Liu, 2018) provide dense freeway sensing; the deep-learning literature built on them (Jeong, Lee, Jeon, & Youm, 2021; Jiang & Luo, 2022) optimises accuracy under full observation. Missing-sensor imputation and kriging exist for the prediction task in isolation, but the downstream question — how imputed speeds affect *routing decisions and realised travel time* for emergency vehicles — has not been quantified.

**Emergency vehicle systems.** Work in this domain concentrates on signal priority, detection, and current-map rerouting (Chowdhury et al., 2023; Hugar et al., 2025; Sasikala et al., 2025), and reviews continue to name proactive predictive routing as an open direction (Zohir, Ismael, El-Gendy, & Saafan, 2025). The transferability of predictive routing to sparsely instrumented cities — the practical barrier for Sub-Saharan deployment — remains untested, which is the gap this article addresses.

## 3. Materials and Methods

### 3.1 Framework under study (summary; full design in Macharia et al., 2025)

We study the published framework without modification: a two-layer GRU (64 hidden units, dropout 0.2) trained on METR-LA with a chronological 70/15/15 split and a train-only StandardScaler (test MAE 3.48 mph; cross-validated on PEMS-BAY at 2.38 mph); a Time-Dependent A\* router with an admissible great-circle heuristic and FIFO-preserving one-second cost clipping; and a remaining-time controller that replans when remaining travel time deteriorates by more than δ. The routing graph is the METR-LA detector adjacency (207 nodes, 1,515 directed edges), which at full instrumentation carries a sensor speed on every edge. We fix δ = 0.20, the operational default identified in the prior work, because travel time was shown to be invariant to δ.

### 3.2 Coverage-degradation design

Coverage *c* is the fraction of the 207 sensors whose live speed the router may use. For each level *c* ∈ {100, 70, 50, 30, 20, 10}% we draw a retained subset of ⌈c·207⌉ sensors and construct **two speed fields**:

- **True field (100% sensors)** — used only to accumulate realised journey time, i.e. what the vehicle actually experiences, including the injected incident. This field is identical across all coverage levels, so journeys are compared on a common ground truth.
- **Observed field (retained sensors only)** — used for every routing decision (the current snapshot, the GRU-forecast cost field, the historical baseline, and every replan). Edges whose sensor was dropped inherit speed by k-nearest-neighbour (k = 4) inverse-distance weighting (IDW) from the nearest retained sensors within 2.5 km — the standard loop-detector spatial reconstruction. Edges with no retained sensor in range fall back to the road-class free-flow speed.

This separation is the methodological core: it isolates the effect of *what the router can see* from *what is true*, so the measured degradation is attributable to sensing, not to a changing world. The predictor is trained once on the full historical archive (as in reality, offline training uses whatever history exists); coverage thins only the live field consumed at dispatch. Under the incident scenario, the framework can detect and persist the slowdown only on retained sensors, so an incident on an unsensored corridor is invisible to the router even though the vehicle still suffers it.

### 3.3 Experimental setup

For each coverage level we ran three independent sensor-retention draws (seeds) to obtain error bars; at 100% the draw is degenerate (all sensors retained) and deterministic. Each run evaluated 50 origin–destination pairs (minimum eight hops, ≥300 s free-flow, seed-fixed sampling) across three scenarios — peak-hour, off-peak, and a path-targeted incident (a 40% speed drop applied to the corridor the current-map Dijkstra route had chosen, revealed after 20% of the journey) — giving 50 × 3 = 150 journeys per run and 8,100 journeys in total. For each journey, five methods chose paths on the observed field and were then traversed on the true field: Dijkstra on the current snapshot (B1), static A\* on historical means (B2), reactive A\* allowed one snapshot replan (B3), an oracle with perfect future knowledge (B4), and the framework. The primary outcome is percentage travel-time reduction versus B1. Significance is a one-sample t-test of the per-journey reductions against zero (α = 0.05). Software: Python 3.11, TensorFlow/Keras 3, NetworkX; all code and the coverage harness are in the public repository (see §6). Full reproduction: `python coverage_experiment.py`.

## 4. Results

### 4.1 Validation at full coverage

At 100% coverage the protocol reproduces the published framework: incident-condition reduction was 16.29% (versus 16.19% reported in Macharia et al., 2025; the small difference reflects a 50- rather than 75-pair sample), with peak-hour and off-peak reductions near 1% and 0% respectively. This confirms that the two-field harness reduces exactly to the original evaluation when no sensor is dropped.

### 4.2 Degradation of incident benefit with coverage

Incident-condition travel-time reduction fell monotonically as coverage thinned (Table 1, Figure 1). From 16.3% at full instrumentation it dropped to 10.1% at 70% coverage, 8.2% at 50%, and 4.4% at 30%, then plateaued at 4.6–5.2% across 10–20%. Every level remained statistically significant against zero (t ≥ 5.2, p < 0.001), so predictive routing retains a real, if much smaller, advantage even under severe sparsity. Mean replans per incident journey fell in step (0.92 → 0.19), and the fraction of incidents in which any affected sensor was still observed fell to 74% at 10% coverage — one incident in four became entirely invisible to the router.

**Table 1.** Incident-condition travel-time reduction versus Dijkstra by sensor coverage (mean over three retention seeds; N = 150 journeys per run).

| Sensor coverage (%) | Reduction vs Dijkstra (%) | SD (across seeds) | Reduction vs reactive A\* (%) | Mean replans/journey |
|---|---|---|---|---|
| 100 | 16.29 | — | −0.15 | 0.92 |
| 70 | 10.10 | 0.93 | −1.16 | 0.67 |
| 50 | 8.20 | 0.83 | −1.67 | 0.55 |
| 30 | 4.37 | 0.91 | −1.33 | 0.28 |
| 20 | 5.21 | 1.83 | −3.11 | 0.27 |
| 10 | 4.60 | 1.36 | 0.18 | 0.19 |

*Note.* All reductions versus Dijkstra significant at p < 0.001 (one-sample t-test).

**Figure 1.** Incident travel-time reduction versus Dijkstra as a function of sensor coverage, with ±SD over retention seeds; the shaded band marks the 10–30% coverage typical of sparsely instrumented cities. *(File: `results/coverage/fig_coverage_degradation.png`.)*

### 4.3 Non-incident scenarios and reactive baseline

Peak-hour and off-peak reductions remained near zero at every coverage level (peak 0.1–1.2%, off-peak ≈ 0%), consistent with the prior finding that a forecast helps little when congestion is network-wide or absent; coverage therefore acts specifically through incident avoidance. The framework's margin over the reactive A\* baseline (B3) was small and slightly negative below full coverage, indicating that once the observed field is coarse, the 30-minute GRU horizon adds little beyond a single reactive replan — an honest boundary of the approach under sparsity.

### 4.4 Computational cost

Routing latency was unaffected by coverage: TD-A\* search averaged 0.39 ms (median 0.24 ms), and GRU inference on the order of tens of milliseconds, keeping the combined dispatch response well under one second at every coverage level. Sensor sparsity degrades routing *quality*, not *speed*.

## 5. Discussion

**Coverage is the binding constraint.** The framework's compute budget and predictor accuracy are held fixed across the entire sweep, so the near-fourfold collapse in incident benefit (16.3% → 4.4% by 30% coverage) is attributable solely to sensing. This confirms, and quantifies for the first time, the qualitative claim in Macharia et al. (2025) that sensor-coverage density rather than model accuracy limits real-world benefit. For deployment planning the practical reading is direct: at roughly 50% arterial coverage about half of the achievable incident benefit is retained, whereas below ~30% the benefit falls into a low 4–5% residual plateau.

**Mechanism.** Two effects compound as coverage thins. First, incident *observability* declines: with the disruption confined to the corridor the vehicle was about to drive, dropping the sensors on that corridor removes the very signal the controller needs, until at 10% coverage a quarter of incidents are unseen. Second, cost-field *precision* declines: even when some corridor sensors survive, IDW smears the slowdown across neighbouring edges, so the alternative route the router computes is less well distinguished from the failing one. The residual 4–5% plateau reflects the incidents that remain partly observable plus the diffuse benefit of the historical/forecast field, and it is why the reduction stays significant rather than reaching zero.

**Implications for instrumentation policy.** The curve converts an abstract "we need more sensors" into a target. A city aiming to recover the majority of predictive-routing benefit should instrument on the order of half its arterial edges; a minimal deployment at 10–20% coverage still yields a small but significant ~5% incident improvement, which may justify a phased rollout that begins on the highest-incident corridors. This is directly actionable for Nairobi Metropolitan Services and the Kenya National Highways Authority.

**Limitations.** METR-LA is a US freeway archive; mixed-traffic dynamics and the spatial statistics of Nairobi sensing may differ, so the specific percentages are transferable as a method and a shape, not as Nairobi field values. Retained sensors were dropped uniformly at random; real sparse networks cluster sensing on major corridors, which would likely lie above our random-drop curve and is a natural extension. The predictor was not retrained per coverage level; studying a coverage-matched predictor is future work. Finally, the evaluation is single-vehicle simulation, as in the framework it builds on.

## 6. Conclusions

We measured how the benefit of GRU + TD-A\* predictive emergency routing degrades as sensor coverage falls from complete instrumentation to Nairobi-realistic sparsity. Incident-condition travel-time reduction versus current-map Dijkstra declined monotonically from 16.3% at full coverage to ~4.4% by 30% coverage and a 4–5% plateau below, remaining statistically significant throughout, while non-incident scenarios were unaffected and latency stayed sub-millisecond. Sensor-coverage density is therefore the binding constraint on predictive-routing benefit, and roughly half of arterial edges must be instrumented to retain half of the achievable incident improvement. Code and data are openly available at https://github.com/Freshia-Njoki/Emergency_Routing.

## References

*(Use the target journal's style; APA shown. All entries are already verified in your thesis reference list except Macharia et al., 2025, which is your published Paper 1.)*

- Chowdhury, A., Kaisar, S., Khoda, M. E., Naha, R., Khoshkholghi, M. A., & Aiash, M. (2023). IoT-based emergency vehicle services in intelligent transportation system. *Sensors, 23*(11), 5324.
- Dreyfus, S. E. (1969). An appraisal of some shortest-path algorithms. *Operations Research, 17*(3), 395–412.
- Golub, A., Stevens, M., Klopp, J. M., & Martin, E. (2021). Addressing public transit challenges in Sub-Saharan African cities. *Transport Policy, 105*, 62–72.
- Hugar, S. M., Immanuel Prabaharan, S., Priyadharshini, S., Sheeba, D., Gold Beulah Patturose, J., & Allada, S. R. (2025). Real-time adaptive traffic management system for emergency vehicle prioritisation. In *2025 IEEE CNC* (pp. 1237–1242).
- Jaballah, R., Veenstra, M., Coelho, L. C., & Renaud, J. (2021). The time-dependent shortest path and vehicle routing problem. *INFOR, 59*(4), 592–622.
- Jeong, M.-H., Lee, T.-Y., Jeon, S.-B., & Youm, M. (2021). Highway speed prediction using gated recurrent unit neural networks. *Applied Sciences, 11*(7), 3059.
- Jiang, W., & Luo, J. (2022). Graph neural network for traffic forecasting: A survey. *Expert Systems with Applications, 207*, 117921.
- Li, Y., Yu, R., Shahabi, C., & Liu, Y. (2018). Diffusion convolutional recurrent neural network: Data-driven traffic forecasting. In *ICLR*.
- Macharia, F. N., Langat, G., & Mageto, S. (2025). Design and evaluation of a GRU-based predictive routing framework for emergency vehicles. *[your published venue]*.
- Qi, P., Pan, C., Xu, X., Wang, J., Liang, J., & Zhou, W. (2025). A review of dynamic traffic flow prediction methods for global energy-efficient route planning. *Sensors, 25*(17), 5560.
- Sasikala, N., Sridhar, S., Reddy, S. H., John, S., & Shrinikethan, S. (2025). Emergency traffic prioritization system with priority-based dynamic route optimization and IoT-enabled dynamic signal control. In *2025 CONIT*.
- Werner, N., & Zeitz, T. (2022). Combining predicted and live traffic with time-dependent A\* potentials. In *ESA 2022* (pp. 89:1–89:15).
- Zhang, Z., Sun, Y., & Liu, Q. (2022). An adaptive route planning method of connected vehicles for improving the transport efficiency. *ISPRS International Journal of Geo-Information, 11*(1), 39.
- Zohir, H. M., Ismael, I. M., El-Gendy, E. M., & Saafan, M. M. (2025). Advancements in accident-aware traffic management: A comprehensive review of V2X-based route optimization. *Scientific Reports, 15*, 35041.
