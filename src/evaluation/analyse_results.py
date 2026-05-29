"""
analyse_results.py  — auto-called by evaluate_framework.py after every run.
Generates 5 publication-quality PNG figures to results/figures/, overwriting
previous outputs.  Also prints a statistical summary table.

Figures produced
----------------
Fig 1  — Travel time: framework vs all baselines (grouped bar)
Fig 2  — Travel time reduction % per scenario (bar + error bars)
Fig 3  — δ threshold sensitivity (line: reduction + update frequency)
Fig 4  — Computational performance (routing latency + GRU inference)
Fig 5  — Combined summary poster (2x2 grid, publication-ready)
"""

import os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from scipy import stats

warnings.filterwarnings('ignore')

# ── style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':      'DejaVu Sans',
    'font.size':        11,
    'axes.titlesize':   13,
    'axes.titleweight': 'bold',
    'axes.labelsize':   11,
    'axes.spines.top':  False,
    'axes.spines.right':False,
    'axes.grid':        True,
    'grid.alpha':       0.3,
    'grid.linewidth':   0.6,
    'legend.frameon':   False,
    'figure.dpi':       150,
    'savefig.dpi':      300,
    'savefig.bbox':     'tight',
})

PALETTE = {
    'framework':  '#2563EB',
    'dijkstra':   '#DC2626',
    'static_a':   '#6B7280',
    'reactive':   '#D97706',
    'oracle':     '#16A34A',
    'peak_hour':  '#EF4444',
    'off_peak':   '#22C55E',
    'incident':   '#F97316',
}
SCENARIOS    = ['peak_hour', 'off_peak', 'incident']
SCENARIO_LABELS = {'peak_hour': 'Peak hour', 'off_peak': 'Off-peak', 'incident': 'Incident'}
DELTAS       = [0.05, 0.10, 0.15, 0.20]
FIG_DIR      = 'results/figures'
RESULTS_PATH = 'results/evaluation_results.csv'
ALPHA        = 0.05


def load(path: str = RESULTS_PATH) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Run evaluate_framework.py first.\nExpected: {path}")
    df = pd.read_csv(path)
    print(f"[Figures] Loaded {len(df):,} records from {path}")
    return df


# ── Fig 1: Framework vs baselines — mean travel time grouped bar ──────────────
def fig1_travel_time_comparison(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))

    x     = np.arange(len(SCENARIOS))
    w     = 0.16
    cols  = [
        ('framework_tt_s',      'TD-A* + GRU\n(framework)', PALETTE['framework']),
        ('b1_dijkstra_tt_s',    'Dijkstra',                  PALETTE['dijkstra']),
        ('b2_static_astar_tt_s','Static A*',                 PALETTE['static_a']),
        ('b3_reactive_astar_tt_s','Reactive A*',             PALETTE['reactive']),
        ('b4_oracle_tt_s',      'Oracle A*\n(upper bound)',  PALETTE['oracle']),
    ]

    for i, (col, label, color) in enumerate(cols):
        if col not in df.columns:
            continue
        means = [df[df['scenario'] == s][col].mean() for s in SCENARIOS]
        sds   = [df[df['scenario'] == s][col].std()  for s in SCENARIOS]
        offset = (i - 2) * w
        bars = ax.bar(x + offset, means, w, label=label, color=color,
                      alpha=0.88, edgecolor='white', linewidth=0.5)
        ax.errorbar(x + offset, means, yerr=sds, fmt='none',
                    color='#111', capsize=3, linewidth=1.2)

    ax.set_xticks(x)
    ax.set_xticklabels([SCENARIO_LABELS[s] for s in SCENARIOS], fontsize=11)
    ax.set_ylabel('Mean travel time (seconds)')
    ax.set_title('Fig 1 — Framework vs baseline travel times')
    ax.legend(loc='upper right', fontsize=9, ncol=2)
    ax.set_ylim(bottom=0)

    # annotate framework bars with value
    for i, s in enumerate(SCENARIOS):
        val = df[df['scenario'] == s]['framework_tt_s'].mean()
        ax.text(i - 2*w, val + 8, f'{val:.0f}s', ha='center',
                fontsize=8.5, color=PALETTE['framework'], fontweight='bold')

    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig1_travel_time_comparison.png')
    plt.savefig(path)
    plt.close()
    print(f"[Figures] Saved → {path}")


# ── Fig 2: Travel time reduction % per scenario — bar + error bars ────────────
def fig2_reduction_by_scenario(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=True)

    comparisons = [
        ('reduction_vs_dijkstra_pct',      'vs Dijkstra',      PALETTE['dijkstra']),
        ('reduction_vs_static_astar_pct',  'vs Static A*',     PALETTE['static_a']),
        ('reduction_vs_reactive_astar_pct','vs Reactive A*',   PALETTE['reactive']),
    ]
    comparisons = [(c, l, col) for c, l, col in comparisons if c in df.columns]

    x   = np.arange(len(comparisons))
    w   = 0.22

    for ax, scenario in zip(axes, SCENARIOS):
        sub = df[df['scenario'] == scenario]
        for i, (col, label, color) in enumerate(comparisons):
            vals   = sub[col].dropna()
            mean_v = vals.mean()
            sd_v   = vals.std()
            bar = ax.bar(i, mean_v, w*2.5, color=color, alpha=0.85,
                         edgecolor='white', linewidth=0.5)
            ax.errorbar(i, mean_v, yerr=sd_v, fmt='none',
                        color='#111', capsize=4, linewidth=1.4)
            ax.text(i, mean_v + sd_v + 0.5, f'{mean_v:.1f}%',
                    ha='center', fontsize=9, fontweight='bold')

        ax.set_title(f'{SCENARIO_LABELS[scenario]}',
                     color=PALETTE[scenario], fontweight='bold')
        ax.set_xticks(range(len(comparisons)))
        ax.set_xticklabels([l for _, l, _ in comparisons], fontsize=8.5,
                           rotation=10)
        ax.axhline(15, color='green', linestyle=':', linewidth=1.2,
                   label='15% min target' if scenario == 'peak_hour' else '')
        ax.set_ylim(bottom=0)

    axes[0].set_ylabel('Travel time reduction (%)')
    axes[0].legend(fontsize=8)
    fig.suptitle('Fig 2 — Framework travel time reduction vs each baseline',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig2_reduction_by_scenario.png')
    plt.savefig(path)
    plt.close()
    print(f"[Figures] Saved → {path}")


# ── Fig 3: δ threshold sensitivity ───────────────────────────────────────────
def fig3_delta_sensitivity(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for scenario in SCENARIOS:
        sub   = df[df['scenario'] == scenario]
        color = PALETTE[scenario]
        label = SCENARIO_LABELS[scenario]

        means_tt  = []
        means_upd = []
        sds_tt    = []

        for d in DELTAS:
            sub_d = sub[sub['delta'] == d]
            if 'reduction_vs_dijkstra_pct' in sub_d.columns:
                means_tt.append(sub_d['reduction_vs_dijkstra_pct'].mean())
                sds_tt.append(sub_d['reduction_vs_dijkstra_pct'].std())
            means_upd.append(sub_d['framework_n_replannings'].mean())

        axes[0].plot(DELTAS, means_tt, marker='o', color=color,
                     linewidth=2.2, label=label, markersize=7)
        axes[0].fill_between(DELTAS,
            np.array(means_tt) - np.array(sds_tt),
            np.array(means_tt) + np.array(sds_tt),
            color=color, alpha=0.10)

        axes[1].plot(DELTAS, means_upd, marker='s', color=color,
                     linewidth=2.2, label=label, markersize=7,
                     linestyle='--')

    for ax in axes:
        ax.set_xticks(DELTAS)
        ax.set_xticklabels([f'δ={d}' for d in DELTAS])
        ax.legend(fontsize=9)

    axes[0].set_ylabel('Travel time reduction vs Dijkstra (%)')
    axes[0].set_title('Reduction % vs threshold δ')
    axes[0].set_ylim(bottom=0)

    axes[1].set_ylabel('Mean replannings per journey')
    axes[1].set_title('Update frequency vs threshold δ\n(lower δ = more updates)')
    axes[1].set_ylim(bottom=-0.05)

    fig.suptitle('Fig 3 — Threshold policy (δ) sensitivity analysis',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig3_delta_sensitivity.png')
    plt.savefig(path)
    plt.close()
    print(f"[Figures] Saved → {path}")


# ── Fig 4: Computational performance ─────────────────────────────────────────
def fig4_computational_performance(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # left: routing latency box per scenario
    lat_data  = [df[df['scenario'] == s]['framework_lat_ms'].dropna().values
                 for s in SCENARIOS]
    bp = axes[0].boxplot(lat_data, patch_artist=True, notch=False,
                         widths=0.45, medianprops=dict(color='white', linewidth=2))
    for patch, scenario in zip(bp['boxes'], SCENARIOS):
        patch.set_facecolor(PALETTE[scenario])
        patch.set_alpha(0.85)
    axes[0].axhline(1000, color='red', linestyle='--', linewidth=1.5,
                    label='1,000 ms sub-second target')
    axes[0].set_xticks(range(1, len(SCENARIOS)+1))
    axes[0].set_xticklabels([SCENARIO_LABELS[s] for s in SCENARIOS])
    axes[0].set_ylabel('Latency (ms) — log scale')
    axes[0].set_yscale('log')
    axes[0].set_title('TD-A* routing latency\n(sub-second target = 1,000 ms)')
    axes[0].legend(fontsize=9)

    # right: GRU inference time per scenario
    inf_data  = [df[df['scenario'] == s]['gru_inference_ms'].dropna().values
                 for s in SCENARIOS]
    bp2 = axes[1].boxplot(inf_data, patch_artist=True, notch=False,
                          widths=0.45, medianprops=dict(color='white', linewidth=2))
    for patch, scenario in zip(bp2['boxes'], SCENARIOS):
        patch.set_facecolor(PALETTE[scenario])
        patch.set_alpha(0.85)

    means = [df[df['scenario'] == s]['gru_inference_ms'].mean() for s in SCENARIOS]
    for i, (m, s) in enumerate(zip(means, SCENARIOS), 1):
        axes[1].text(i, m + 1, f'{m:.0f}ms', ha='center',
                     fontsize=9, fontweight='bold')

    axes[1].set_xticks(range(1, len(SCENARIOS)+1))
    axes[1].set_xticklabels([SCENARIO_LABELS[s] for s in SCENARIOS])
    axes[1].set_ylabel('Inference time (ms)')
    axes[1].set_title('GRU prediction inference time\n(15–30 min horizon per call)')

    # legend patches
    patches = [mpatches.Patch(color=PALETTE[s], label=SCENARIO_LABELS[s])
               for s in SCENARIOS]
    axes[1].legend(handles=patches, fontsize=9)

    fig.suptitle('Fig 4 — Computational performance (latency)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'fig4_computational_performance.png')
    plt.savefig(path)
    plt.close()
    print(f"[Figures] Saved → {path}")


# ── Fig 5: Publication summary poster (2×2) ───────────────────────────────────
def fig5_summary_poster(df: pd.DataFrame):
    fig = plt.figure(figsize=(14, 10))
    gs  = GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.32)

    # ── top-left: framework vs dijkstra travel time (bar) ────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    means_fw = [df[df['scenario'] == s]['framework_tt_s'].mean()     for s in SCENARIOS]
    means_d  = [df[df['scenario'] == s]['b1_dijkstra_tt_s'].mean()   for s in SCENARIOS]
    x = np.arange(len(SCENARIOS))
    ax1.bar(x - 0.2, means_fw, 0.35, label='TD-A* + GRU',
            color=PALETTE['framework'], alpha=0.88)
    ax1.bar(x + 0.2, means_d,  0.35, label='Dijkstra',
            color=PALETTE['dijkstra'],  alpha=0.88)
    ax1.set_xticks(x)
    ax1.set_xticklabels([SCENARIO_LABELS[s] for s in SCENARIOS], fontsize=9)
    ax1.set_ylabel('Travel time (s)')
    ax1.set_title('(a) Travel time — framework vs Dijkstra')
    ax1.legend(fontsize=8)

    # ── top-right: reduction % bar ────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    col = 'reduction_vs_dijkstra_pct'
    if col in df.columns:
        means_r = [df[df['scenario'] == s][col].mean() for s in SCENARIOS]
        sds_r   = [df[df['scenario'] == s][col].std()  for s in SCENARIOS]
        colors  = [PALETTE[s] for s in SCENARIOS]
        bars = ax2.bar(range(len(SCENARIOS)), means_r, 0.5,
                       color=colors, alpha=0.88, edgecolor='white')
        ax2.errorbar(range(len(SCENARIOS)), means_r, yerr=sds_r,
                     fmt='none', color='#111', capsize=5, linewidth=1.5)
        for i, (v, sd) in enumerate(zip(means_r, sds_r)):
            ax2.text(i, v + sd + 0.5, f'{v:.1f}%',
                     ha='center', fontsize=10, fontweight='bold')
        ax2.axhline(15, color='green', linestyle=':', linewidth=1.2,
                    label='15% minimum target')
        ax2.set_xticks(range(len(SCENARIOS)))
        ax2.set_xticklabels([SCENARIO_LABELS[s] for s in SCENARIOS], fontsize=9)
        ax2.set_ylabel('Reduction vs Dijkstra (%)')
        ax2.set_title('(b) Travel time reduction by scenario')
        ax2.legend(fontsize=8)
        ax2.set_ylim(bottom=0)

    # ── bottom-left: δ sensitivity ────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    for scenario in SCENARIOS:
        sub  = df[df['scenario'] == scenario]
        if col in sub.columns:
            means = [sub[sub['delta'] == d][col].mean() for d in DELTAS]
            ax3.plot(DELTAS, means, marker='o', label=SCENARIO_LABELS[scenario],
                     color=PALETTE[scenario], linewidth=2, markersize=6)
    ax3.set_xticks(DELTAS)
    ax3.set_xticklabels([str(d) for d in DELTAS], fontsize=9)
    ax3.set_xlabel('Replanning threshold δ')
    ax3.set_ylabel('Reduction vs Dijkstra (%)')
    ax3.set_title('(c) Threshold δ sensitivity analysis')
    ax3.legend(fontsize=8)
    ax3.set_ylim(bottom=0)

    # ── bottom-right: latency ─────────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    lat_means = [df[df['scenario'] == s]['framework_lat_ms'].mean()
                 for s in SCENARIOS]
    inf_means = [df[df['scenario'] == s]['gru_inference_ms'].mean()
                 for s in SCENARIOS]
    x = np.arange(len(SCENARIOS))
    ax4.bar(x - 0.2, lat_means, 0.35, label='Routing latency (ms)',
            color=PALETTE['framework'], alpha=0.88)
    ax4.bar(x + 0.2, inf_means, 0.35, label='GRU inference (ms)',
            color='#F59E0B', alpha=0.88)
    ax4.axhline(1000, color='red', linestyle='--', linewidth=1.2,
                label='1,000 ms target')
    ax4.set_xticks(x)
    ax4.set_xticklabels([SCENARIO_LABELS[s] for s in SCENARIOS], fontsize=9)
    ax4.set_ylabel('Time (ms) — log scale')
    ax4.set_yscale('log')
    ax4.set_title('(d) Computational performance')
    ax4.legend(fontsize=8)

    fig.suptitle(
        'GRU-Based Predictive Route Optimisation Framework for Emergency Vehicle Navigation\n'
        'Simulation Results — METR-LA Dataset, 75 OD pairs × 3 scenarios × 4 δ values',
        fontsize=12, fontweight='bold', y=1.01
    )
    path = os.path.join(FIG_DIR, 'fig5_summary_poster.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"[Figures] Saved → {path}")


# ── Statistical summary table ─────────────────────────────────────────────────
def print_stats_table(df: pd.DataFrame):
    print("\n" + "="*72)
    print("  STATISTICAL SUMMARY — Travel Time Reduction vs Dijkstra")
    print("="*72)
    col = 'reduction_vs_dijkstra_pct'
    if col not in df.columns:
        print("  Column not found.")
        return

    rows = []
    for scenario in SCENARIOS:
        for delta in DELTAS:
            sub = df[(df['scenario'] == scenario) & (df['delta'] == delta)][col].dropna()
            if len(sub) < 3:
                continue
            t_stat, p_val = stats.ttest_1samp(sub, popmean=0)
            _, sw_p       = stats.shapiro(sub[:50])
            rows.append({
                'Scenario': scenario, 'δ': delta, 'N': len(sub),
                'Mean %': round(sub.mean(), 2),
                'SD':     round(sub.std(),  2),
                'Median': round(sub.median(),2),
                't-stat': round(t_stat, 3),
                'p-value':round(p_val,  4),
                'Sig α=0.05': 'YES' if p_val < ALPHA else 'NO',
                'SW p (normality)': round(sw_p, 4)
            })

    stats_df = pd.DataFrame(rows)
    print(stats_df.to_string(index=False))

    # save
    stats_path = 'results/statistical_tests.csv'
    stats_df.to_csv(stats_path, index=False)
    print(f"\n[Stats] Saved → {stats_path}")
    print("="*72)

    # ANOVA across delta values
    print("\n  ONE-WAY ANOVA — Effect of δ on travel time reduction")
    groups = [df[df['delta'] == d][col].dropna() for d in DELTAS]
    groups = [g for g in groups if len(g) > 2]
    if len(groups) >= 2:
        f, p = stats.f_oneway(*groups)
        print(f"  F={f:.3f}, p={p:.4f} → "
              f"{'SIGNIFICANT' if p < ALPHA else 'NOT significant'} at α={ALPHA}")
    print("="*72 + "\n")

    return stats_df


# ── Master entry point ────────────────────────────────────────────────────────
def run_full_analysis(results_path: str = RESULTS_PATH,
                      figures_dir:  str = FIG_DIR):
    global FIG_DIR
    FIG_DIR = figures_dir
    os.makedirs(FIG_DIR, exist_ok=True)

    df = load(results_path)

    print("\n[Figures] Generating 5 publication figures...")
    fig1_travel_time_comparison(df)
    fig2_reduction_by_scenario(df)
    fig3_delta_sensitivity(df)
    fig4_computational_performance(df)
    fig5_summary_poster(df)

    stats_df = print_stats_table(df)

    print(f"\n[Figures] ✓ All figures saved to: {FIG_DIR}/")
    print("  fig1_travel_time_comparison.png")
    print("  fig2_reduction_by_scenario.png")
    print("  fig3_delta_sensitivity.png")
    print("  fig4_computational_performance.png")
    print("  fig5_summary_poster.png  ← publication-ready poster")
    return df, stats_df


if __name__ == '__main__':
    run_full_analysis()