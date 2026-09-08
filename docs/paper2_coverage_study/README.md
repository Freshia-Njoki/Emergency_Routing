# Paper 2 — Sensor-Coverage Sensitivity Study

Second research article built on the published framework (*Design and Evaluation of a
GRU-Based Predictive Routing Framework for Emergency Vehicles*). It quantifies how the
framework's incident-condition travel-time benefit degrades as sensor coverage falls from
full instrumentation toward Nairobi-realistic sparsity.

## Contents
- `paper2_coverage_study.md` — the manuscript (IMRaD).
- `coverage_experiment.py` — the coverage-degradation harness.
- `coverage_results.csv` — raw per-journey results (8,100 journeys).
- `coverage_summary.csv` — incident reduction vs coverage (mean over retention seeds).
- `fig_coverage_degradation.png` — Figure 1.

## Method (summary)
Two speed fields per run: the vehicle always traverses the **true** 100%-sensor field
(common ground truth), while the router only sees a **k%** field; uncovered edges inherit
speed by k-NN inverse-distance interpolation from retained sensors. The trained GRU, the
detector graph, δ = 0.20, and the ground-truth speeds are held fixed; only coverage varies.
At 100% coverage the harness reproduces the published 16.19% incident reduction, validating
the two-field fork.

## Reproduce
```bash
# from the repository root, with the main pipeline environment:
python -m src.prediction.data_preprocessing        # regenerate data/processed/training_data.npz
python docs/paper2_coverage_study/coverage_experiment.py
```
Coverage levels {100, 70, 50, 30, 20, 10}% × 3 sensor-retention seeds × 3 scenarios × 50 OD pairs.

## Headline result
Incident reduction vs Dijkstra: 16.3% (100%) → 10.1% (70%) → 8.2% (50%) → 4.4% (30%) →
~4.6–5.2% (10–20%), all p < 0.001. Peak/off-peak ≈ 0% (negative control). Latency sub-ms.
Sensor coverage — not compute or model accuracy — is the binding constraint.
