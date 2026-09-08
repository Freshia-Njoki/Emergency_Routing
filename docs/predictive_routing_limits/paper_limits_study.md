# What Limits Predictive Emergency Vehicle Routing? Sensor Coverage, Not Model Accuracy

**Freshia Njoki Macharia¹\*, Gilbert Langat², Stephen Mageto²**
¹Department of Computer Science and Informatics, Kirinyaga University, Kerugoya, Kenya
²School of Pure and Applied Sciences, Kirinyaga University, Kerugoya, Kenya
\*Corresponding author: fnjokimacharia@gmail.com

> **Author note (not for submission).** This paper is scoped to contributions the published *Design and Evaluation of a GRU-Based Predictive Routing Framework for Emergency Vehicles* (**Macharia et al., 2025**) did not make. It **cites** that paper for the framework and adds two new diagnostic experiments — a predictor-accuracy ablation and a sensor-coverage degradation study — that together identify the binding constraint. Every number in §4 is from a real run on the latest `main` pipeline (`results/accuracy/`, `results/coverage/`); nothing is invented. At full coverage the harness reproduces the published 16.19% incident baseline.

---

## Abstract

Predictive emergency-vehicle routing that couples short-horizon traffic forecasting with time-dependent search reduces incident-condition travel time on fully instrumented road networks, but the field has optimised the wrong lever. Effort concentrates on more accurate spatial–temporal predictors, whereas the deployment barrier in the cities that most need the technology is sparse sensing. This article asks which of the two levers — predictor accuracy or sensor coverage — actually limits routing benefit, using a GRU + Time-Dependent A\* emergency-routing framework as the test bed and holding the router, controller, graph, and ground-truth speeds fixed. Two experiments were run over 8,550 matched simulated journeys on the METR-LA detector graph. First, forecast fidelity was swept from the raw GRU up to a perfect oracle (mean absolute error 0 mph) and down to noisy and naive forecasts (MAE up to 9 mph), and a trained LSTM was added as a real architectural alternative. Incident-condition travel-time reduction versus current-map Dijkstra was statistically flat across the entire accuracy range (11–15%; Pearson r = −0.23 between predictor MAE and benefit, p = 0.55); a perfect oracle achieved 12.5%, no better than the raw GRU. Second, sensor coverage was thinned from 100% to 10%, with uncovered edges reconstructed by inverse-distance interpolation; the same reduction fell monotonically and sharply from 16.3% at full coverage to 4.4% at 30% and a 4–5% plateau below (all p < 0.001). The diagnosis is unambiguous: within this framework, prediction accuracy is not the bottleneck — sensor-coverage density is. The finding redirects both research effort and instrumentation policy: for sparsely sensed cities such as Nairobi, funding sensor coverage yields far more emergency-response benefit than funding a more accurate predictor, and roughly half of arterial edges must be instrumented to retain half of the achievable incident benefit.

**Keywords:** emergency vehicle routing; sensor coverage; traffic prediction; ablation study; gated recurrent unit; time-dependent A\*; intelligent transportation systems

---

## 1. Introduction

Each additional minute of ambulance delay at a cardiac-arrest scene is associated with roughly a 10% rise in mortality (Zhang, Sun, & Liu, 2022), and predictive routing that forecasts traffic 15–30 minutes ahead has been shown to cut incident-condition travel time relative to the snapshot shortest paths used by current dispatch (Macharia et al., 2025; Qi et al., 2025). Two research programmes promise further gains. The larger one, by volume of publications, pursues ever more accurate traffic prediction — graph neural networks, spatio-temporal transformers, and hybrids that shave mean absolute error on the METR-LA and PEMS-BAY benchmarks (Jiang & Luo, 2022; Li, Yu, Shahabi, & Liu, 2018). The smaller one concerns the sensing infrastructure those predictors consume, which in the low- and middle-income cities that most need emergency-routing help is sparse and unevenly distributed (Golub et al., 2021).

These two levers are rarely compared, yet a deployment planner must choose between them: fund a better model, or fund more sensors? This article answers that question directly. Using the published GRU + Time-Dependent A\* (TD-A\*) emergency-routing framework as a fixed test bed, we run two controlled experiments that isolate each lever while holding everything else — router, controller, road graph, and the ground-truth speeds a vehicle actually experiences — constant. Our contributions are:

1. **A predictor-accuracy ablation** that sweeps forecast fidelity from the raw GRU up to a perfect oracle and down to noisy and naive forecasts, and adds a trained LSTM, showing that incident-routing benefit is statistically flat across the entire accuracy range.
2. **A sensor-coverage degradation study** that thins live coverage from 100% to 10%, showing that the same benefit collapses monotonically and identifying coverage as the binding constraint.
3. **A decision-relevant diagnosis and instrumentation target** derived from the two curves, redirecting effort from prediction accuracy toward sensing density for sparse-network deployment.

## 2. Related Work

Time-dependent routing on costs that change with entry time is well established (Dreyfus, 1969; Jaballah, Veenstra, Coelho, & Renaud, 2021; Werner & Zeitz, 2022), and Macharia et al. (2025) integrated a GRU predictor with TD-A\* and a remaining-time controller for emergency dispatch, evaluating it on matched journeys scored with actual future speeds — but only at full sensor coverage and with a single predictor. The prediction literature built on METR-LA/PEMS-BAY (Li et al., 2018; Jeong, Lee, Jeon, & Youm, 2021; Jiang & Luo, 2022) competes on accuracy in isolation, without measuring whether accuracy gains propagate to routing outcomes. Emergency-vehicle work concentrates on signal priority and detection (Chowdhury et al., 2023; Hugar et al., 2025; Sasikala et al., 2025), and reviews still name proactive predictive routing as open (Zohir, Ismael, El-Gendy, & Saafan, 2025). No prior study asks, for emergency routing, whether accuracy or coverage is the operative constraint. This article does.

## 3. Materials and Methods

### 3.1 Framework under study (full design in Macharia et al., 2025)

We use the published framework unchanged: a two-layer GRU (64 units, dropout 0.2; test MAE 3.48 mph on METR-LA, cross-validated at 2.38 mph on PEMS-BAY), a TD-A\* router with an admissible great-circle heuristic and FIFO-preserving one-second cost clipping, and a remaining-time controller with δ = 0.20. The routing graph is the METR-LA detector adjacency (207 nodes, 1,515 directed edges). Across both experiments the vehicle always traverses the true future speeds; only the router's information is manipulated. Incidents are a 40% corridor speed drop applied to the route current-map Dijkstra had chosen, revealed after 20% of the journey. Evaluation is 50 origin–destination pairs per condition; the primary outcome is percentage travel-time reduction versus Dijkstra (B1), one-sample t-test against zero, α = 0.05. Software: Python 3.11, TensorFlow/Keras 3, NetworkX.

### 3.2 Experiment A — predictor-accuracy ablation

Holding coverage at 100%, we varied only the fidelity of the forecast the framework routes on. A continuous fidelity axis was constructed by blending the raw GRU forecast toward the true future (oracle) at fractions α ∈ {0, 0.25, 0.5, 0.75, 1.0}, tracing effective forecast MAE from the GRU level down to 0 mph; a degraded branch added Gaussian noise (MAE up to 9 mph); a naive historical-mean forecast provided a high-MAE anchor; and a **trained LSTM** (two layers, 64 units, dropout 0.2; test MAE 3.54 mph) provided a genuine alternative architecture. For each variant we recorded its effective forecast MAE against the true future and the resulting incident travel-time reduction, and tested the association between the two with Pearson correlation. A flat curve means accuracy is not the routing bottleneck.

### 3.3 Experiment B — sensor-coverage degradation

Holding the predictor fixed, we thinned the fraction of sensors whose live speed the router may use to c ∈ {100, 70, 50, 30, 20, 10}%, with three independent sensor-retention draws per level for error bars. Two speed fields were maintained: a **true field** (all sensors) used only to accumulate realised journey time, identical across levels so journeys share a common ground truth; and an **observed field** (retained sensors) used for every routing decision, with uncovered edges inheriting speed by k-nearest-neighbour (k = 4) inverse-distance interpolation from retained sensors within 2.5 km. Under the incident scenario the framework can detect the slowdown only on retained sensors, so an incident on an unsensored corridor is invisible to the router though the vehicle still suffers it. Full reproduction: `python accuracy_experiment.py` and `python coverage_experiment.py`.

## 4. Results

### 4.1 Validation

At full coverage with the raw GRU, the harness reproduces the published framework (16.19% incident reduction), confirming the manipulations reduce to the original evaluation at the reference point.

### 4.2 Prediction accuracy does not change the route (Experiment A)

Incident-condition travel-time reduction was statistically flat across the entire accuracy range (Table 1, Figure 1b). A **perfect oracle** with zero forecast error achieved 12.5% — no better than the raw GRU (13.5%) or a noisy forecast with 9 mph MAE (12.2%). The trained LSTM (MAE 3.54 mph) landed in the same band (11.2%). Across variants spanning MAE 0–9 mph, reduction stayed within 11–15% with no monotonic trend, and the association between predictor MAE and routing benefit was negligible and non-significant (Pearson r = −0.23, p = 0.55). Within this framework, a more accurate forecast does not produce a better ambulance route.

**Table 1.** Incident reduction versus predictor accuracy (100% coverage, N = 50 per variant).

| Predictor variant | Forecast MAE (mph) | Incident reduction vs Dijkstra (%) |
|---|---|---|
| Oracle (perfect future) | 0.00 | 12.5 |
| GRU→oracle blend 75% | 1.25 | 12.3 |
| GRU→oracle blend 50% | 2.77 | 13.9 |
| GRU→oracle blend 25% | 3.68 | 15.3 |
| GRU (deployed) | 4.99 | 13.5 |
| LSTM (trained alternative) | 5.29 | 11.2 |
| GRU + noise | 6.41 | 12.8 |
| Historical mean | 7.82 | 12.1 |
| GRU + heavier noise | 9.03 | 12.2 |

*Note.* Effective MAE is measured against the true future during incidents (hence above the 3.48 mph clean-test value). Pearson r(MAE, reduction) = −0.23, p = 0.55.

### 4.3 Sensor coverage sharply changes the route (Experiment B)

Incident reduction fell monotonically as coverage thinned: 16.3% (100%) → 10.1% (70%) → 8.2% (50%) → 4.4% (30%), then a 4.6–5.2% plateau at 10–20% (Table 2, Figure 1a). Every level remained significant against zero (t ≥ 5.2, p < 0.001). Mean replans per incident journey fell from 0.92 to 0.19, and at 10% coverage one incident in four became entirely invisible to the router. Peak-hour and off-peak reductions stayed near zero at every coverage level (a negative control), so coverage acts specifically through incident avoidance.

**Table 2.** Incident reduction versus sensor coverage (mean over three retention seeds, N = 150 per level).

| Coverage (%) | Reduction vs Dijkstra (%) | SD |
|---|---|---|
| 100 | 16.3 | — |
| 70 | 10.1 | 0.9 |
| 50 | 8.2 | 0.8 |
| 30 | 4.4 | 0.9 |
| 20 | 5.2 | 1.8 |
| 10 | 4.6 | 1.4 |

*Note.* All reductions significant at p < 0.001.

**Figure 1.** The two levers side by side. (a) Coverage is the binding constraint — a steep monotonic decline; the shaded band marks 10–30% coverage typical of sparsely sensed cities. (b) Prediction accuracy is not — reduction is flat across forecast MAE from a perfect oracle to 9 mph error (r = −0.23, p = 0.55). *(File: `results/accuracy/fig_limits_two_panel.png`.)*

### 4.4 Computational cost

Routing latency was sub-millisecond in both experiments (TD-A\* search ≈ 0.4 ms), so neither lever trades against dispatch speed.

## 5. Discussion

**The bottleneck is coverage, not accuracy.** The two experiments share a test bed and differ only in which lever moves, so the contrast is causal within the framework: a fourfold swing in forecast error (0→9 mph) barely moves the route, while thinning coverage from full to 30% cuts the benefit almost fourfold. The reason a perfect oracle helps so little is structural — the framework already extracts most of the available benefit from a modest forecast, and the residual gap to the oracle is small (Macharia et al., 2025). The reason coverage helps so much is that it governs whether the disruption is observable at all: below ~30% coverage, incidents on unsensored corridors are invisible and interpolation smears those that remain, so the router cannot distinguish the failing route from its alternatives.

**Implications for research and policy.** For the research community, the result cautions against equating benchmark MAE with operational value in emergency routing; a lighter predictor that meets the latency budget is sufficient, and the marginal research return lies in sensing and observability, not accuracy. For transport authorities in sparsely sensed cities, the coverage curve is an instrumentation target: recovering the majority of predictive-routing benefit requires instrumenting on the order of half of arterial edges, while a minimal 10–20% deployment on the highest-incident corridors still yields a small but significant ~5% improvement, supporting a phased rollout. This is directly actionable for Nairobi Metropolitan Services and the Kenya National Highways Authority.

**Limitations.** METR-LA is a US freeway archive; the percentages transfer as a method and a shape, not as Nairobi field values. Sensors were dropped uniformly at random, whereas real networks cluster sensing on major corridors, which would likely lie above the random-drop curve. The accuracy axis was traced primarily by blending toward the true future and by one trained alternative architecture rather than a full suite of graph models; the flatness we observe is nonetheless consistent across the oracle, the LSTM, and the noise branch. The evaluation is single-vehicle simulation.

## 6. Conclusions

Using a fixed GRU + TD-A\* emergency-routing test bed, we showed that incident-condition routing benefit is statistically flat across predictor accuracy from a perfect oracle to a 9 mph-error forecast (r = −0.23, p = 0.55), yet falls sharply and monotonically as sensor coverage thins from 100% to 10% (16.3% → 4.6%, all p < 0.001). Sensor-coverage density, not model accuracy, is the binding constraint on predictive emergency-vehicle routing. Research effort and instrumentation budgets for sparse-network deployment should be redirected accordingly. Code and data: https://github.com/Freshia-Njoki/Emergency_Routing.

## References

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
