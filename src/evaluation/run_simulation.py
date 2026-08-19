"""
Objectives 3 and 4 — 900-experiment ground-truth simulation.

Usage (from project root, venv active):
    python -m src.evaluation.run_simulation
    python -m src.evaluation.run_simulation --quick
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
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
from src.evaluation.analyse_results import run_full_analysis

configure_utf8()

MODEL_DIR = os.path.join("models", "saved")
PROCESSED_DIR = os.path.join("data", "processed")
RESULTS_DIR = os.path.join("results", "simulation")
VIZ_DIR = os.path.join("visualizations")


def analyse(df: pd.DataFrame) -> None:
    safe_print("\n" + "=" * 65)
    safe_print("OBJECTIVE 4 -- FRAMEWORK vs BASELINES")
    safe_print("=" * 65)
    for col, label in [
        ("red_vs_b1", "vs Dijkstra/Current (B1)"),
        ("red_vs_b2", "vs Static A* (B2)       "),
        ("red_vs_b3", "vs Reactive A* (B3)     "),
        ("red_vs_b4", "vs Oracle A* (B4)       "),
    ]:
        m, s, med = df[col].mean(), df[col].std(), df[col].median()
        safe_print(f"  {label}  mean: {m:+.2f}%  SD: {s:.2f}%  median: {med:.2f}%")

    safe_print(f"\n  Avg TD-A* latency:       {df['fw_lat_ms'].mean():.3f} ms")
    safe_print(f"  Avg GRU inference:       {df['gru_ms'].mean():.1f} ms")
    safe_print(f"  Avg replannings/journey: {df['n_replannings'].mean():.2f}")

    safe_print("\n" + "=" * 65)
    safe_print("OBJECTIVE 3 -- THRESHOLD (delta) SENSITIVITY")
    safe_print("=" * 65)
    g = df.groupby("delta")[["red_vs_b1", "n_replannings", "fw_lat_ms"]].mean().round(3)
    g.columns = ["Mean Reduction vs B1 (%)", "Avg Replannings", "Avg Latency (ms)"]
    safe_print(g.to_string())

    try:
        from scipy import stats

        deltas = sorted(df["delta"].unique())
        groups = [df[df["delta"] == d]["red_vs_b1"].values for d in deltas]
        if all(len(g) > 1 and np.nanstd(g) > 1e-9 for g in groups):
            F, p = stats.f_oneway(*groups)
            safe_print(f"\n  ANOVA: F={F:.3f}  p={p:.4f}")
            best = df.groupby("delta")["red_vs_b1"].mean().idxmax()
            if p > 0.05:
                safe_print(
                    f"  No significant effect (p>0.05). Recommended delta = {best}"
                )
            else:
                safe_print(f"  Significant effect. Best delta = {best}")
        else:
            safe_print("  ANOVA skipped -- insufficient variance in groups.")
    except Exception as exc:
        safe_print(f"  ANOVA skipped: {exc}")

    safe_print("\n" + "=" * 65)
    safe_print("BREAKDOWN BY SCENARIO")
    safe_print("=" * 65)
    scn = df.groupby("scenario")[["red_vs_b1", "red_vs_b4", "n_replannings"]].mean().round(2)
    scn.columns = ["Reduction vs B1 (%)", "Reduction vs Oracle (%)", "Replannings"]
    safe_print(scn.to_string())

    safe_print("\n" + "=" * 65)
    safe_print("STATISTICAL SIGNIFICANCE (one-sample t-test vs 0, vs B1)")
    safe_print("=" * 65)
    try:
        from scipy import stats as st

        for scenario in ["peak_hour", "off_peak", "incident"]:
            sub = df[df["scenario"] == scenario]
            if len(sub) < 2:
                continue
            t_stat, p_val = st.ttest_1samp(sub["red_vs_b1"], 0)
            sig = "Yes" if p_val < 0.05 else "No"
            safe_print(
                f"  {scenario:<12}  mean={sub['red_vs_b1'].mean():.2f}%  "
                f"t={t_stat:.2f}  p={p_val:.4f}  sig={sig}"
            )
    except Exception as exc:
        safe_print(f"  t-test skipped: {exc}")


def visualise(df: pd.DataFrame) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(VIZ_DIR, exist_ok=True)
    NAVY, TEAL, GOLD, RED = "#1E2761", "#0D9488", "#E8A838", "#C0392B"
    scens = [s for s in ["peak_hour", "off_peak", "incident"] if s in set(df["scenario"])]

    fig, ax = plt.subplots(figsize=(11, 5))
    baselines = [
        ("red_vs_b1", "Dijkstra/Current", NAVY),
        ("red_vs_b2", "Static A*", TEAL),
        ("red_vs_b3", "Reactive A*", GOLD),
        ("red_vs_b4", "Oracle A*", RED),
    ]
    x = np.arange(len(scens))
    w = 0.18
    for i, (col, lbl, col_c) in enumerate(baselines):
        vals = [df[df["scenario"] == s][col].mean() for s in scens]
        ax.bar(x + i * w, vals, w, label=lbl, color=col_c, alpha=0.85)
    ax.set_xticks(x + w * 1.5)
    ax.set_xticklabels([s.replace("_", " ").title() for s in scens])
    ax.set_ylabel("Travel Time Reduction (%)")
    ax.legend()
    ax.set_title("Objective 4 -- Framework Travel Time Reduction vs Baselines", fontweight="bold")
    ax.axhline(0, color="black", lw=0.8)
    ax.grid(axis="y", alpha=0.3)
    ax.set_facecolor("#F4F7FF")
    plt.tight_layout()
    p = os.path.join(VIZ_DIR, "obj4_travel_time_reduction.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    safe_print(f"[OK] {p}")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Objective 3 -- Threshold (delta) Sensitivity Analysis", fontweight="bold")
    g = df.groupby("delta")
    deltas = sorted(df["delta"].unique())
    d_labels = [str(d) for d in deltas]
    axes[0].bar(d_labels, [g.get_group(d)["red_vs_b1"].mean() for d in deltas], color=NAVY, alpha=0.8)
    axes[0].set_xlabel("Threshold delta")
    axes[0].set_ylabel("Mean Reduction vs B1 (%)")
    axes[0].grid(axis="y", alpha=0.3)
    axes[1].bar(d_labels, [g.get_group(d)["n_replannings"].mean() for d in deltas], color=TEAL, alpha=0.8)
    axes[1].set_xlabel("Threshold delta")
    axes[1].set_ylabel("Avg Replannings per Journey")
    axes[1].grid(axis="y", alpha=0.3)
    plt.tight_layout()
    p = os.path.join(VIZ_DIR, "obj3_delta_sensitivity.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    safe_print(f"[OK] {p}")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(df["fw_lat_ms"], bins=30, color=NAVY, alpha=0.8, edgecolor="white")
    ml = df["fw_lat_ms"].mean()
    ax.axvline(ml, color=GOLD, lw=2, label=f"Mean: {ml:.3f} ms")
    ax.axvline(1000, color=RED, lw=1.5, ls="--", label="1,000 ms target")
    ax.set_xlabel("Routing Latency (ms)")
    ax.set_ylabel("Frequency")
    ax.set_title("Objective 4 -- TD-A* Routing Latency", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    p = os.path.join(VIZ_DIR, "obj4_latency_distribution.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    safe_print(f"[OK] {p}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="15 OD pairs for a smoke test")
    parser.add_argument("--n-od", type=int, default=75)
    parser.add_argument("--no-remap", action="store_true", help="Keep original random sensor mapping")
    args = parser.parse_args()

    n_od = 15 if args.quick else args.n_od
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(VIZ_DIR, exist_ok=True)

    safe_print("=" * 65)
    safe_print("OBJECTIVES 3 & 4 -- GROUND-TRUTH SIMULATION")
    safe_print("Sliding-window GRU + path-targeted incidents + interpolated speeds")
    safe_print("=" * 65)

    safe_print("\n[Phase 1] Loading GRU model...")
    model = load_keras_model(MODEL_DIR)
    scaler = load_scaler(MODEL_DIR, PROCESSED_DIR)

    safe_print("\n[Phase 2] Loading road network...")
    G, esm, weights, ff_mph, lengths, ff_tt = load_graph_and_costs(
        PROCESSED_DIR, remap=not args.no_remap
    )

    safe_print("\n[Phase 3] Loading test data (mph, inverse-scaled)...")
    X_test_seq, X_last, y_test_mph, hist_mph, _ = load_test_arrays(PROCESSED_DIR, scaler)

    safe_print("\n[Phase 4] Running experiments...")
    rows = run_experiments(
        model, scaler, G, weights, lengths, ff_mph, ff_tt,
        X_test_seq, X_last, y_test_mph, hist_mph,
        n_od=n_od,
    )
    df = pd.DataFrame(rows)
    raw = os.path.join(RESULTS_DIR, "simulation_results.csv")
    df.to_csv(raw, index=False)
    safe_print(f"\n[OK] Raw results -> {raw}  ({len(df)} records)")

    analyse(df)
    safe_print("\n[Phase 5] Saving visualisations...")
    visualise(df)

    fig_dir = os.path.join(RESULTS_DIR, "figures")
    try:
        run_full_analysis(raw, fig_dir)
    except Exception as exc:
        safe_print(f"  [WARN] analyse_results: {exc}")

    summ = df.groupby(["scenario", "delta"])[[
        "fw_tt_s", "b1_tt_s", "red_vs_b1", "red_vs_b2", "red_vs_b4",
        "fw_lat_ms", "n_replannings", "gru_ms",
    ]].agg(["mean", "std"]).round(3)
    sp = os.path.join(RESULTS_DIR, "summary_statistics.csv")
    summ.to_csv(sp)
    safe_print(f"[OK] Summary -> {sp}")
    safe_print("\nDONE")


if __name__ == "__main__":
    main()
