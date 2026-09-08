# What Limits Predictive Emergency Routing? Sensor Coverage, Not Model Accuracy

Second research article (builds on and cites the published *Design and Evaluation…* paper).
It runs two controlled experiments on the fixed GRU + TD-A\* framework to identify the
binding constraint on incident-routing benefit.

## Contents
- `paper_limits_study.md` — the manuscript (IMRaD).
- `accuracy_experiment.py` — Experiment A: forecast-fidelity sweep (GRU→oracle blend, noise, historical, trained LSTM).
- `coverage_experiment.py` — Experiment B: sensor-coverage degradation (two-speed-field design, k-NN IDW).
- `train_lstm.py` — trains the LSTM alternative predictor used in Experiment A.
- `results/accuracy_results.csv`, `results/coverage_results.csv`, `results/coverage_summary.csv`.
- `results/fig_limits_two_panel.png` — main figure (coverage steep vs accuracy flat).
- `results/fig_coverage_degradation.png` — coverage curve.

## Key findings (real runs on `main` @ dd0b6d4)
- **Accuracy is flat:** incident reduction 11–15% across forecast MAE 0→9 mph; a perfect oracle (MAE 0) = 12.5%, no better than the GRU; LSTM (MAE 3.54) in the same band. Pearson r(MAE, reduction) = −0.23, p = 0.55.
- **Coverage is steep:** incident reduction 16.3% (100%) → 4.4% (30%) → ~4.6% (10%), all p < 0.001.
- **Diagnosis:** sensor-coverage density, not model accuracy, is the binding constraint.
- Validation: at 100% coverage with the raw GRU the harness reproduces the published 16.19% baseline.

## Reproduce
```bash
python -m src.prediction.data_preprocessing     # regenerate data/processed/training_data.npz
python train_lstm.py                            # optional: trains lstm_best.keras for Experiment A
python accuracy_experiment.py                    # Experiment A
python coverage_experiment.py                    # Experiment B
```
Requires the main pipeline environment (TensorFlow/Keras 3, NetworkX, scikit-learn) and the METR-LA detector graph + model already in the repo.
