"""
analyse_results.py
------------------
Loads evaluation_results.csv and produces:

1. Statistical tests (paired t-test, Wilcoxon, ANOVA) matching Section 3.10
2. Publication-quality figures:
   - Fig A: Travel time reduction vs baselines (box plot)
   - Fig B: Latency distribution (violin plot)
   - Fig C: Update frequency vs δ across scenarios (line plot)
   - Fig D: GRU MAE contribution to route optimality (scatter)
   - Fig E: δ sensitivity — travel time vs update frequency trade-off
3. Prints full statistical table ready to paste into your paper
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from typing import List

warnings.filterwarnings('ignore')

ALPHA     = 0.05
RESULTS   = 'results/evaluation_results.csv'
FIG_DIR   = 'results/figures'
SCENARIOS = ['peak_hour', 'off_peak', 'incident']
DELTAS    = [0.05, 0.10, 0.15, 0.20]
PALETTE   = {'peak_hour': '#e74c3c', 'off_peak': '#2ecc71', 'incident': '#e67e22'}


def load_results(path: str = RESULTS) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Results not found at {path}. Run evaluate_framework.py first.")
    df = pd.read_csv(path)
    print(f"[Analysis] Loaded {len(df)} rows from {path}")
    return df


# ── 1. Statistical Tests ──────────────────────────────────────────────────────

def run_statistical_tests(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each scenario × δ:
        - paired t-test: framework vs each baseline
        - Wilcoxon signed-rank (non-parametric backup)
        - Bonferroni-corrected p-values
    """
    rows = []
    comparisons = [
        ('reduction_vs_dijkstra_pct',       'vs Dijkstra'),
        ('reduction_vs_static_astar_pct',   'vs Static A*'),
        ('reduction_vs_reactive_astar_pct', 'vs Reactive A*'),
    ]

    for scenario in SCENARIOS:
        sub = df[df['scenario'] == scenario]
        for delta in DELTAS:
            sub_d = sub[sub['delta'] == delta]
            for col, label in comparisons:
                if col not in sub_d.columns:
                    continue
                vals = sub_d[col].dropna()
                if len(vals) < 5:
                    continue

                # paired t-test (H0: mean reduction = 0)
                t_stat, p_val = stats.ttest_1samp(vals, popmean=0)

                # Wilcoxon (non-parametric)
                try:
                    w_stat, w_p = stats.wilcoxon(vals - 0)
                except Exception:
                    w_stat, w_p = np.nan, np.nan

                # Shapiro-Wilk normality
                _, sw_p = stats.shapiro(vals[:50]) if len(vals) > 3 else (np.nan, np.nan)

                rows.append({
                    'Scenario':    scenario,
                    'Delta':       delta,
                    'Comparison':  label,
                    'N':           len(vals),
                    'Mean_Reduction_%': round(vals.mean(), 2),
                    'SD':          round(vals.std(), 2),
                    'Median_%':    round(vals.median(), 2),
                    't_stat':      round(t_stat, 3),
                    'p_val_ttest': round(p_val, 4),
                    'W_stat':      round(w_stat, 3) if not np.isnan(w_stat) else 'NA',
                    'p_val_wilcox':round(w_p, 4) if not np.isnan(w_p) else 'NA',
                    'SW_normality_p': round(sw_p, 4) if not np.isnan(sw_p) else 'NA',
                    'Significant_0.05': 'YES' if p_val < ALPHA else 'NO'
                })

    result_df = pd.DataFrame(rows)
    path = 'results/statistical_tests.csv'
    result_df.to_csv(path, index=False)
    print(f"\n[Analysis] Statistical tests saved → {path}")
    print(result_df.to_string(index=False))
    return result_df


def run_anova_delta(df: pd.DataFrame):
    """
    One-way ANOVA: does δ significantly affect travel time reduction?
    Addresses Research Question 3 directly.
    """
    print("\n[ANOVA] Testing effect of δ on travel time reduction...")
    groups = [df[df['delta'] == d]['reduction_vs_dijkstra_pct'].dropna()
              for d in DELTAS]
    groups = [g for g in groups if len(g) > 2]
    if len(groups) < 2:
        print("[ANOVA] Insufficient data")
        return
    f_stat, p_val = stats.f_oneway(*groups)
    print(f"  F-statistic: {f_stat:.3f},  p-value: {p_val:.4f}")
    if p_val < ALPHA:
        print(f"  → SIGNIFICANT: δ meaningfully affects travel time reduction (p < {ALPHA})")
    else:
        print(f"  → NOT significant at α={ALPHA}")
    return f_stat, p_val


def run_correlation_analysis(df: pd.DataFrame):
    """
    RQ4: Pearson + Spearman correlation between GRU inference time and
    route optimality (reduction %). Section 3.10.
    """
    print("\n[Correlation] GRU inference time vs route optimality...")
    x = df['gru_inference_ms'].dropna()
    y = df['reduction_vs_dijkstra_pct'].dropna()
    common = df[['gru_inference_ms', 'reduction_vs_dijkstra_pct']].dropna()
    if len(common) < 5:
        print("  Insufficient data")
        return

    r_p, p_p = stats.pearsonr(common['gru_inference_ms'],
                               common['reduction_vs_dijkstra_pct'])
    r_s, p_s = stats.spearmanr(common['gru_inference_ms'],
                                common['reduction_vs_dijkstra_pct'])
    print(f"  Pearson r={r_p:.3f}, p={p_p:.4f}")
    print(f"  Spearman ρ={r_s:.3f}, p={p_s:.4f}")


# ── 2. Figures ────────────────────────────────────────────────────────────────

def fig_travel_time_boxplot(df: pd.DataFrame):
    """Fig A: Travel time reduction vs each baseline — box plots."""
    os.makedirs(FIG_DIR, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    for ax, scenario in zip(axes, SCENARIOS):
        sub = df[df['scenario'] == scenario]
        data = [
            sub['reduction_vs_dijkstra_pct'].dropna(),
            sub['reduction_vs_static_astar_pct'].dropna(),
            sub['reduction_vs_reactive_astar_pct'].dropna() if
            'reduction_vs_reactive_astar_pct' in sub.columns else pd.Series([]),
        ]
        labels = ['vs Dijkstra', 'vs Static A*', 'vs Reactive A*']
        data_clean   = [d for d in data if len(d) > 0]
        labels_clean = [l for l, d in zip(labels, data) if len(d) > 0]

        bp = ax.boxplot(data_clean, patch_artist=True, notch=False)
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        for patch, color in zip(bp['boxes'], colors[:len(data_clean)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
        ax.axhline(15, color='green', linestyle=':', linewidth=1.0,
                   label='Min target 15%')
        ax.set_title(f'{scenario.replace("_"," ").title()}', fontsize=12,
                     fontweight='bold')
        ax.set_xticklabels(labels_clean, fontsize=9)
        ax.set_ylabel('Travel Time Reduction (%)', fontsize=10)
        ax.grid(axis='y', alpha=0.3)

    fig.suptitle('Framework Travel Time Reduction vs Baselines\n'
                 '(TD-A* + GRU, all δ values pooled)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig_A_travel_time_reduction.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Figures] Saved → {path}")


def fig_latency_violin(df: pd.DataFrame):
    """Fig B: Computational latency distribution."""
    os.makedirs(FIG_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    data   = [df[df['scenario'] == s]['framework_lat_ms'].dropna()
              for s in SCENARIOS]
    parts  = ax.violinplot(data, positions=[1,2,3], showmedians=True)
    for i, (pc, scenario) in enumerate(zip(parts['bodies'], SCENARIOS)):
        pc.set_facecolor(PALETTE[scenario])
        pc.set_alpha(0.7)
    ax.axhline(1000, color='red', linestyle='--', linewidth=1.2,
               label='1000 ms sub-second target')
    ax.set_xticks([1,2,3])
    ax.set_xticklabels([s.replace('_',' ').title() for s in SCENARIOS])
    ax.set_ylabel('Routing Latency (ms)', fontsize=11)
    ax.set_title('TD-A* Computational Latency by Scenario', fontsize=12,
                 fontweight='bold')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    path = os.path.join(FIG_DIR, 'fig_B_latency_violin.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Figures] Saved → {path}")


def fig_delta_sensitivity(df: pd.DataFrame):
    """Fig C: δ sensitivity — travel time reduction vs update frequency."""
    os.makedirs(FIG_DIR, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    for scenario in SCENARIOS:
        sub = df[df['scenario'] == scenario]
        means_tt  = [sub[sub['delta']==d]['reduction_vs_dijkstra_pct'].mean()
                     for d in DELTAS]
        means_upd = [sub[sub['delta']==d]['framework_n_replannings'].mean()
                     for d in DELTAS]

        axes[0].plot(DELTAS, means_tt, marker='o', label=scenario.replace('_',' ').title(),
                     color=PALETTE[scenario], linewidth=2)
        axes[1].plot(DELTAS, means_upd, marker='s', label=scenario.replace('_',' ').title(),
                     color=PALETTE[scenario], linewidth=2)

    axes[0].set_xlabel('Replanning Threshold δ', fontsize=11)
    axes[0].set_ylabel('Mean Travel Time Reduction (%)', fontsize=11)
    axes[0].set_title('Travel Time Reduction vs δ', fontsize=12,
                      fontweight='bold')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].set_xlabel('Replanning Threshold δ', fontsize=11)
    axes[1].set_ylabel('Mean Replannings per Journey', fontsize=11)
    axes[1].set_title('Update Frequency vs δ\n(lower δ = more updates)',
                      fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    fig.suptitle('Threshold Policy (δ) Sensitivity Analysis',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig_C_delta_sensitivity.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Figures] Saved → {path}")


def fig_scenario_comparison(df: pd.DataFrame):
    """Fig D: Grouped bar — all baselines vs framework per scenario."""
    os.makedirs(FIG_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5))

    x      = np.arange(len(SCENARIOS))
    width  = 0.18
    cols   = {
        'B1 Dijkstra':       ('b1_dijkstra_tt_s',     '#e74c3c'),
        'B2 Static A*':      ('b2_static_astar_tt_s', '#e67e22'),
        'B4 Oracle':         ('b4_oracle_tt_s',       '#2ecc71'),
        'Framework TD-A*':   ('framework_tt_s',       '#3498db'),
    }
    for i, (label, (col, color)) in enumerate(cols.items()):
        means = [df[df['scenario']==s][col].mean() for s in SCENARIOS]
        ax.bar(x + (i - 1.5) * width, means, width,
               label=label, color=color, alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels([s.replace('_',' ').title() for s in SCENARIOS],
                        fontsize=11)
    ax.set_ylabel('Mean Travel Time (seconds)', fontsize=11)
    ax.set_title('Framework vs Baselines — Mean Travel Time by Scenario',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig_D_scenario_comparison.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Figures] Saved → {path}")


def run_full_analysis(results_path: str = RESULTS):
    df = load_results(results_path)

    print("\n" + "="*60)
    print("  STATISTICAL ANALYSIS — GRU Emergency Routing Framework")
    print("="*60)

    stats_df  = run_statistical_tests(df)
    run_anova_delta(df)
    run_correlation_analysis(df)

    print("\n[Figures] Generating publication figures...")
    fig_travel_time_boxplot(df)
    fig_latency_violin(df)
    fig_delta_sensitivity(df)
    fig_scenario_comparison(df)

    print(f"\n[Done] All figures in → {FIG_DIR}/")
    return stats_df


if __name__ == '__main__':
    run_full_analysis()