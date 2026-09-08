"""
evaluate_framework.py

Canonical 75 OD x 3 scenarios x 4 delta = 900 experiment harness
(thesis Section 3.9).  Uses the same ground-truth simulation as
run_simulation.py so Chapter 4 tables can no longer contradict each other.

Usage:
    python -m src.evaluation.evaluate_framework
    python -m src.evaluation.evaluate_framework --sliding-window
    python -m src.evaluation.evaluate_framework --quick
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.utils.console import configure_utf8, safe_print
from src.evaluation.simulation_core import (
    load_graph_and_costs,
    load_keras_model,
    load_scaler,
    load_test_arrays,
    run_experiments,
)

configure_utf8()


def _compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "framework_tt_s", "b1_dijkstra_tt_s", "b2_static_astar_tt_s",
        "framework_lat_ms", "framework_n_replannings",
        "reduction_vs_dijkstra_pct", "reduction_vs_static_astar_pct",
        "reduction_vs_oracle_pct", "gru_inference_ms",
    ]
    avail = [m for m in metrics if m in df.columns]
    if df.empty or "scenario" not in df.columns:
        return pd.DataFrame()
    return df.groupby(["scenario", "delta"])[avail].agg(["mean", "std", "median"]).round(3)


def run_evaluation(
    model_dir="models/saved",
    data_dir="data",
    results_dir="results",
    dataset="metr_la",
    use_synthetic=False,
    sliding=True,
    n_od=75,
    remap=True,
    graph_mode="sensor",
):
    os.makedirs(results_dir, exist_ok=True)
    processed = os.path.join(data_dir, "processed")

    safe_print("\n" + "=" * 60)
    safe_print(f"  Dataset: {dataset.upper().replace('_', '-')}  |  Sliding: YES")
    safe_print("  Ground-truth evaluation (actual future speeds)")
    safe_print("=" * 60 + "\n")

    if use_synthetic:
        safe_print("[WARN] --synthetic is ignored; OSM + METR-LA test set is required.")

    safe_print("[Phase 1] Loading GRU model...")
    model = load_keras_model(model_dir)
    scaler = load_scaler(model_dir, processed)

    safe_print("[Phase 2] Building road graph...")
    G, esm, weights, ff_mph, lengths, ff_tt = load_graph_and_costs(
        processed, remap=remap, graph_mode=graph_mode
    )

    safe_print("[Phase 3] Loading speed data (inverse-scaled mph)...")
    X_test_seq, X_last, y_test_mph, hist_mph, _ = load_test_arrays(processed, scaler)

    safe_print("[Phase 4] Historical averages from training split...")
    safe_print("[Phase 5-6] OD pairs, scenarios, deltas...")
    rows = run_experiments(
        model, scaler, G, weights, lengths, ff_mph, ff_tt,
        X_test_seq, X_last, y_test_mph, hist_mph,
        n_od=n_od,
    )
    df = pd.DataFrame(rows)
    df["dataset"] = dataset
    df["sliding"] = True

    raw = os.path.join(results_dir, "evaluation_results.csv")
    df.to_csv(raw, index=False)
    safe_print(f"\n[Phase 7] Results -> {raw}")

    summary = _compute_summary(df)
    summary.to_csv(os.path.join(results_dir, "summary_stats.csv"))
    safe_print(f"[Phase 8] Summary -> {results_dir}/summary_stats.csv")

    safe_print("\n[Phase 9] Generating figures...")
    try:
        from src.evaluation.analyse_results import run_full_analysis
        run_full_analysis(raw, os.path.join(results_dir, "figures"))
        safe_print(f"[Phase 9] Figures -> {results_dir}/figures/")
    except Exception as e:
        safe_print(f"[Phase 9] Error: {e}")
    return df


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir", default="models/saved")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--dataset", default="metr_la", choices=["metr_la", "pems_bay"])
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--sliding-window", action="store_true",
                   help="Always on in this version; kept for backwards compatibility.")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--n-od", type=int, default=75)
    p.add_argument("--no-remap", action="store_true")
    p.add_argument("--graph", choices=["sensor", "osm"], default="sensor")
    args = p.parse_args()
    run_evaluation(
        model_dir=args.model_dir,
        data_dir=args.data_dir,
        results_dir=args.results_dir,
        dataset=args.dataset,
        use_synthetic=args.synthetic,
        sliding=True,
        n_od=15 if args.quick else args.n_od,
        remap=not args.no_remap,
        graph_mode=args.graph,
    )
