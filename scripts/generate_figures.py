#!/usr/bin/env python3
"""
generate_figures.py
───────────────────
Generates all manuscript and supplementary figures from the cleaned CSV data.
Run from the repo root:  python scripts/generate_figures.py

Requires: numpy, pandas, matplotlib
Outputs:  figures/fig[1-5]_*.{png,pdf} and figures/supp_*.{png,pdf}

Figures:
  1. Urban consumption gap framework (conceptual schematic)
  2. Malmö baseline consumption footprint: top categories
  3. Scenario pathways compared with target pathway
  4. Domain contributions to reductions in Scenario 4
  5. Sensitivity tornado for the coordinated transition pathway
  S1. Scenario coverage vs residual emissions (supplementary)
  S2. Baseline emissions as activity x intensity (supplementary; requires
      data/coicop_activity_intensity_crosswalk.csv, produced by
      scripts/build_activity_intensity_crosswalk.py)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / 'data'
FIG_DIR = REPO_ROOT / 'figures'
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Global style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.dpi':          120,
    'savefig.dpi':         300,
    'font.family':         'sans-serif',
    'font.sans-serif':     ['DejaVu Sans', 'Helvetica', 'Arial'],
    'font.size':           10,
    'axes.spines.top':     False,
    'axes.spines.right':   False,
    'axes.labelsize':      11,
    'axes.titlesize':      12,
    'xtick.labelsize':     9,
    'ytick.labelsize':     9,
    'legend.fontsize':     9,
    'legend.framealpha':   0.92,
    'lines.linewidth':     2.2,
    'figure.facecolor':    'white',
    'axes.facecolor':      'white',
    'savefig.facecolor':   'white',
    'grid.alpha':          0.25,
})

# ── Colour palettes ───────────────────────────────────────────────────────────
DOMAIN_ORDER = [
    'Food and drink', 'Housing', 'Local transport', 'Flights',
    'Other consumption', 'Leisure, sport and culture', 'Clothing and shoes',
]

DOMAIN_COLORS = {
    'Food and drink':            '#6C9A73',
    'Housing':                   '#4C78A8',
    'Local transport':           '#F58518',
    'Flights':                   '#B279A2',
    'Other consumption':         '#8E6C4A',
    'Leisure, sport and culture':'#72B7B2',
    'Clothing and shoes':        '#E45756',
    'Carbon capture placeholder':'#9A9A9A',
}

SCENARIO_COLORS = {'S1': '#9A9A9A', 'S2': '#4C78A8', 'S3': '#F58518', 'S4': '#54A24B'}
SCENARIO_LABELS = {
    'S1': 'S1: Limited change',
    'S2': 'S2: Hotspot focus',
    'S3': 'S3: Lifestyle-centred',
    'S4': 'S4: Coordinated transition',
}

TARGET_2030 = 3.1
TARGET_2050 = 1.0


def savefig(name):
    """Save current figure as both 300-DPI PNG and vector PDF."""
    plt.tight_layout()
    plt.savefig(FIG_DIR / f'{name}.png', bbox_inches='tight', pad_inches=0.12)
    plt.savefig(FIG_DIR / f'{name}.pdf', bbox_inches='tight', pad_inches=0.12)
    plt.close()
    print(f'  {name}.png + .pdf')


# ── Load data ─────────────────────────────────────────────────────────────────
baseline   = pd.read_csv(DATA_DIR / 'baseline_categories.csv')
results    = pd.read_csv(DATA_DIR / 'scenario_results.csv')
cat_res    = pd.read_csv(DATA_DIR / 'category_results.csv')
summary    = pd.read_csv(DATA_DIR / 'scenario_summary.csv')
sensitivity= pd.read_csv(DATA_DIR / 'sensitivity_results.csv')
domain_c   = pd.read_csv(DATA_DIR / 'domain_reduction_contributions_s4.csv')
activity_crosswalk_path = DATA_DIR / 'coicop_activity_intensity_crosswalk.csv'


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 1.  Urban consumption gap framework (conceptual schematic)
# ═════════════════════════════════════════════════════════════════════════════
def fig1_conceptual():
    years = np.linspace(2025, 2050, 300)
    t = (years - 2025) / 25
    y0 = 8.0

    current     = y0 - 1.5 * t
    target      = y0 - (y0 - 1.5) * (1 - (1 - t)**1.3)
    coordinated = y0 - (y0 - 2.5) * (1 - (1 - t)**2.2)
    coordinated = np.clip(coordinated, target + 0.45, current - 0.12)

    fig, ax = plt.subplots(figsize=(7.5, 4.5))

    # Shaded zones
    ax.fill_between(years, coordinated, current,
                    alpha=0.12, color='#2ca02c', label='Modelled transition potential', zorder=1)
    ax.fill_between(years, target, coordinated,
                    alpha=0.20, color='#d62728', label='Urban consumption gap (residual)', zorder=2)

    # Lines
    ax.plot(years, current,     color='#777777', linewidth=2.2, solid_capstyle='round',
            label='Current trajectory (limited change)', zorder=3)
    ax.plot(years, target,      color='black',   linewidth=1.8, linestyle='--',
            dash_capstyle='round', label='Target-compatible pathway', zorder=4)
    ax.plot(years, coordinated, color='#2ca02c', linewidth=2.2, solid_capstyle='round',
            label='Coordinated transition pathway', zorder=5)

    # Right-side labels
    rx = 2051
    ax.text(rx, coordinated[-1], 'Best feasible\ntransition pathway',
            va='center', ha='left', fontsize=7, color='#2ca02c', linespacing=1.3)
    ax.text(rx, target[-1], 'Climate\ntarget',
            va='center', ha='left', fontsize=7, color='black', linespacing=1.3)

    # Gap annotation
    gap_yr = 2045
    idx = np.argmin(np.abs(years - gap_yr))
    gap_mid = (coordinated[idx] + target[idx]) / 2
    ax.annotate('Residual gap after\nfeasible transitions',
                xy=(gap_yr, gap_mid), xytext=(2031, 0.9),
                fontsize=8.5, color='#b22222', ha='left', linespacing=1.3,
                arrowprops=dict(arrowstyle='->', color='#b22222', lw=0.9,
                                connectionstyle='arc3,rad=-0.2'), zorder=6)

    # Transition potential annotation
    tp_yr = 2043
    idx2 = np.argmin(np.abs(years - tp_yr))
    tp_mid = (current[idx2] + coordinated[idx2]) / 2
    ax.annotate('Modelled feasible reductions through\ncoordinated lifestyle, infrastructure\nand technology transitions',
                xy=(tp_yr, tp_mid), xytext=(2027, 8.6),
                fontsize=7.5, color='#1a7a1a', ha='left', linespacing=1.3,
                arrowprops=dict(arrowstyle='->', color='#1a7a1a', lw=0.9,
                                connectionstyle='arc3,rad=-0.1'), zorder=6)

    ax.set_xlim(2025, 2055)
    ax.set_ylim(0, 9.8)
    ax.set_xlabel('Year')
    ax.set_ylabel('Consumption-based emissions\n(t CO\u2082e per capita per year)')
    ax.set_yticks([])
    ax.set_xticks([2025, 2030, 2035, 2040, 2045, 2050])
    ax.axhline(1.5, color='#dddddd', linewidth=0.5, linestyle=':', zorder=0)
    ax.text(2025.2, 0.55, 'Target level (2050)', fontsize=6.5, color='#aaaaaa')
    ax.legend(loc='upper right', frameon=True, edgecolor='#cccccc', fancybox=False, borderpad=0.6)
    ax.grid(axis='x', alpha=0.25)

    savefig('fig1_urban_consumption_gap_framework')


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 2.  Baseline footprint: top 25 categories
# ═════════════════════════════════════════════════════════════════════════════
def fig2_baseline():
    df = baseline[~baseline['is_placeholder']].nlargest(25, 'baseline_kgco2e_per_capita')
    df = df.iloc[::-1]  # smallest at top for horizontal bars

    fig, ax = plt.subplots(figsize=(10, 7.5))
    y = np.arange(len(df))
    colors = [DOMAIN_COLORS.get(d, '#999999') for d in df['domain']]
    bars = ax.barh(y, df['baseline_kgco2e_per_capita'], color=colors, edgecolor='white', linewidth=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels(df['category'], fontsize=8)
    ax.set_xlabel('Baseline emissions (kg CO\u2082e per capita per year)')
    ax.set_title("Malm\u00f6 baseline consumption footprint: top contributing categories")
    ax.grid(axis='x', alpha=0.25)
    for i, v in enumerate(df['baseline_kgco2e_per_capita']):
        ax.text(v + 8, i, f'{v:.0f}', va='center', fontsize=7)

    # Domain legend
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=DOMAIN_COLORS[d], label=d) for d in DOMAIN_ORDER]
    ax.legend(handles=handles, loc='lower right', fontsize=7.5, framealpha=0.92, edgecolor='#cccccc')

    savefig('fig2_baseline_footprint_top_categories')


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 3.  Scenario pathways vs target pathway
# ═════════════════════════════════════════════════════════════════════════════
def fig3_pathways():
    fig, ax = plt.subplots(figsize=(9, 5.4))

    for sid in ['S1', 'S2', 'S3', 'S4']:
        df = results[results['scenario_id'] == sid]
        ax.plot(df['year'], df['emissions_tco2e_per_capita'],
                label=SCENARIO_LABELS[sid], color=SCENARIO_COLORS[sid], linewidth=2.5)

    # Target pathway
    years = np.arange(2026, 2051)
    target = np.where(years <= 2030, TARGET_2030,
             TARGET_2030 + (TARGET_2050 - TARGET_2030) * (years - 2030) / 20)
    ax.plot(years, target, linestyle='--', color='black', linewidth=2, label='Target pathway')

    # 2030 and 2050 milestone markers
    ax.scatter([2030], [TARGET_2030], color='black', s=50, zorder=5, marker='D')
    ax.scatter([2050], [TARGET_2050], color='black', s=50, zorder=5, marker='D')
    ax.annotate(f'{TARGET_2030} t', xy=(2030, TARGET_2030), xytext=(2031.2, TARGET_2030 + 0.25),
                fontsize=8, color='black', arrowprops=dict(arrowstyle='->', lw=0.7, color='black'))
    ax.annotate(f'{TARGET_2050} t', xy=(2050, TARGET_2050), xytext=(2047, TARGET_2050 - 0.45),
                fontsize=8, color='black', arrowprops=dict(arrowstyle='->', lw=0.7, color='black'))

    # Right-edge endpoint labels for each scenario
    for sid in ['S1', 'S2', 'S3', 'S4']:
        df = results[results['scenario_id'] == sid]
        y_end = df[df['year'] == 2050]['emissions_tco2e_per_capita'].values[0]
        ax.text(2050.5, y_end, f'{y_end:.2f}', va='center', fontsize=7.5,
                color=SCENARIO_COLORS[sid], fontweight='bold')

    ax.set_ylim(0, 6.2)
    ax.set_xlim(2026, 2053)
    ax.set_xlabel('Year')
    ax.set_ylabel('Consumption-based emissions\n(t CO\u2082e per capita per year)')
    ax.set_title("Scenario pathways compared with Malm\u00f6's target pathway")
    ax.grid(axis='y', alpha=0.25)
    ax.legend(frameon=True, edgecolor='#cccccc', fancybox=False, loc='upper right')

    savefig('fig3_scenario_pathways_targets')


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 4.  Domain contributions to reductions in S4, 2050
# ═════════════════════════════════════════════════════════════════════════════
def fig4_domain_reductions():
    df = domain_c[(domain_c['year'] == 2050) & (domain_c['domain'] != 'Carbon capture placeholder')]
    df = df.sort_values('reduction_tco2e_per_capita')

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    y = np.arange(len(df))
    colors = [DOMAIN_COLORS.get(d, '#999999') for d in df['domain']]
    ax.barh(y, df['reduction_tco2e_per_capita'], color=colors)
    ax.set_yticks(y)
    ax.set_yticklabels(df['domain'])
    ax.set_xlabel('Reduction in 2050 (t CO\u2082e per capita per year)')
    ax.set_title('Domain contributions to reductions in the coordinated transition (Scenario 4)')
    ax.grid(axis='x', alpha=0.25)
    for i, (_, r) in enumerate(df.iterrows()):
        ax.text(r['reduction_tco2e_per_capita'] + 0.02, i,
                f"{r['reduction_tco2e_per_capita']:.2f}", va='center', fontsize=8)

    # Annotate total
    total = df['reduction_tco2e_per_capita'].sum()
    ax.text(0.97, 0.05, f'Total reduction: {total:.2f} t CO\u2082e/cap',
            transform=ax.transAxes, ha='right', fontsize=9, fontstyle='italic', color='#444444')

    savefig('fig4_domain_reduction_contributions_s4')


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 5.  Sensitivity tornado for Scenario 4
# ═════════════════════════════════════════════════════════════════════════════
def fig5_sensitivity():
    df = sensitivity[sensitivity['variant_id'] != 'base'].copy()
    df = df.reindex(df['delta_2050_vs_base_tco2e_per_capita'].abs().sort_values(ascending=False).index)
    df = df.head(12).iloc[::-1]  # top 12, smallest at top

    fig, ax = plt.subplots(figsize=(9, 6.2))
    y = np.arange(len(df))
    deltas = df['delta_2050_vs_base_tco2e_per_capita'].values
    colors = ['#E45756' if d > 0 else '#54A24B' for d in deltas]
    ax.barh(y, deltas, color=colors)
    ax.axvline(0, color='black', linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(df['variant'], fontsize=8)
    ax.set_xlabel('Change in 2050 emissions relative to Scenario 4\n(t CO\u2082e per capita per year)')
    ax.set_title('Sensitivity of the coordinated transition pathway')
    ax.grid(axis='x', alpha=0.25)
    for i, d in enumerate(deltas):
        ha = 'left' if d >= 0 else 'right'
        offset = 0.015 if d >= 0 else -0.015
        ax.text(d + offset, i, f'{d:+.2f}', va='center', ha=ha, fontsize=8)

    # Annotate base S4 value
    base_row = sensitivity[sensitivity['variant_id'] == 'base']
    if len(base_row):
        base_val = base_row['emissions_2050_tco2e_per_capita'].values[0]
        ax.text(0.97, 0.97, f'Scenario 4 base: {base_val:.3f} t CO\u2082e/cap',
                transform=ax.transAxes, ha='right', va='top', fontsize=8.5,
                fontstyle='italic', color='#444444')

    savefig('fig5_sensitivity_tornado_2050')


# ═════════════════════════════════════════════════════════════════════════════
# SUPPLEMENTARY: Coverage vs residual emissions
# ═════════════════════════════════════════════════════════════════════════════
def supp_coverage():
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    for _, r in summary.iterrows():
        sid = r['scenario_id']
        ax.scatter(r['active_baseline_coverage_pct'], r['emissions_2050_tco2e_per_capita'],
                   s=130, color=SCENARIO_COLORS[sid], edgecolor='white', linewidth=1.2, zorder=3)
        ax.text(r['active_baseline_coverage_pct'] + 1.5, r['emissions_2050_tco2e_per_capita'],
                SCENARIO_LABELS[sid], va='center', fontsize=8.5)

    ax.axhline(TARGET_2050, color='black', linestyle='--', linewidth=1.3, label='2050 target (1.0 t)', zorder=2)
    ax.set_xlim(-3, 108)
    ax.set_ylim(0, 6.2)
    ax.set_xlabel('Share of baseline footprint actively addressed (%)')
    ax.set_ylabel('2050 residual emissions\n(t CO\u2082e per capita per year)')
    ax.set_title('Scenario coverage and residual emissions')
    ax.grid(alpha=0.25)
    ax.legend(frameon=True, edgecolor='#cccccc', fancybox=False)

    savefig('supp_coverage_vs_residual_emissions')


# ═════════════════════════════════════════════════════════════════════════════
# SUPPLEMENTARY: Baseline emissions as activity x intensity
# ═════════════════════════════════════════════════════════════════════════════
def supp_activity_intensity():
    """Requires data/coicop_activity_intensity_crosswalk.csv (see
    scripts/build_activity_intensity_crosswalk.py). Skips with a warning if
    the file is not present, rather than failing the whole run."""
    if not activity_crosswalk_path.exists():
        print('  [skipped] supp_activity_intensity_baseline: '
              f'{activity_crosswalk_path.name} not found in data/. '
              'Run scripts/build_activity_intensity_crosswalk.py first.')
        return

    cw = pd.read_csv(activity_crosswalk_path)
    df = cw[cw['flag'].isin(['OK', 'LOW-CONF', 'SHARED'])].copy()
    df['sek_per_capita_2021'] = pd.to_numeric(df['sek_per_capita_2021'], errors='coerce')
    df['implied_intensity_kgco2e_per_sek'] = pd.to_numeric(
        df['implied_intensity_kgco2e_per_sek'], errors='coerce')
    df['baseline_kgco2e_cap'] = pd.to_numeric(df['baseline_kgco2e_cap'], errors='coerce')
    df = df[(df['sek_per_capita_2021'] > 0) & (df['implied_intensity_kgco2e_per_sek'] > 0)]

    fig, ax = plt.subplots(figsize=(8.2, 6.4))

    x_lo, x_hi = 6, 30000
    y_lo, y_hi = 8e-5, 2

    # Iso-emission reference lines: M x I = E, for a few round E values (kg/cap)
    x_ref = np.logspace(np.log10(x_lo), np.log10(x_hi), 300)
    for E in [5, 30, 150, 600]:
        y_ref = E / x_ref
        mask = (y_ref >= y_lo) & (y_ref <= y_hi)
        ax.plot(x_ref[mask], y_ref[mask], color='#bbbbbb', linewidth=0.9,
                linestyle=(0, (4, 3)), zorder=1, clip_on=True)
        y_at_right = E / x_hi
        ax.text(x_hi * 1.12, y_at_right, f'{E} kg/cap', fontsize=6.8, color='#999999',
                ha='left', va='center')

    for domain in DOMAIN_ORDER:
        if domain == 'Flights':
            continue  # flights uses km, not SEK; not comparable on this axis
        sub = df[df['domain'] == domain]
        if sub.empty:
            continue
        ax.scatter(sub['sek_per_capita_2021'], sub['implied_intensity_kgco2e_per_sek'],
                   s=np.clip(sub['baseline_kgco2e_cap'] * 2.2, 18, 900),
                   color=DOMAIN_COLORS[domain], alpha=0.75, edgecolor='white',
                   linewidth=0.6, zorder=3, label=domain)

    # Callouts for the three categories discussed in Section 3.6 / 4.1
    callouts = {
        'Food and drink - Meat': 'Meat',
        'Clothing and shoes - Clothing': 'Clothing',
        'Housing - Electricity': 'Electricity',
    }
    for cat, label in callouts.items():
        row = df[df['category'] == cat]
        if row.empty:
            continue
        x, y = row['sek_per_capita_2021'].iloc[0], row['implied_intensity_kgco2e_per_sek'].iloc[0]
        ax.annotate(label, xy=(x, y), xytext=(10, 10), textcoords='offset points',
                    fontsize=8.5, fontweight='bold', color='#333333',
                    arrowprops=dict(arrowstyle='-', color='#333333', lw=0.7))

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(y_lo, y_hi)
    ax.set_xlabel('Baseline activity, $M_{0,c}$ (SEK per capita per year, 2021)')
    ax.set_ylabel('Baseline intensity, $I_{0,c}$ (kg CO\u2082e per SEK)')
    ax.set_title('Baseline emissions as activity \u00d7 intensity, by category')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v):,}'))
    ax.grid(alpha=0.2, which='both')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper right', fontsize=7.8, framealpha=0.92,
              edgecolor='#cccccc', title='Domain', title_fontsize=8, markerscale=0.7)

    ax.text(0.015, 0.02,
            'Point size \u221d baseline emissions. Dashed lines are constant-emission contours (M\u00d7I).\n'
            'Flights excluded: activity measured in km, not SEK (see Section 3.8).',
            transform=ax.transAxes, fontsize=7, color='#777777', va='bottom', ha='left')

    savefig('supp_activity_intensity_baseline')


# ═════════════════════════════════════════════════════════════════════════════
# SUPPLEMENTARY: Baseline emissions as activity x intensity (interactive)
# ═════════════════════════════════════════════════════════════════════════════
def supp_activity_intensity_baseline_interactive():
    """Interactive HTML companion to supp_activity_intensity_baseline. Same
    data and layout, but built with Plotly so a reader can hover over any
    bubble to see the category name, domain, baseline emissions, and the
    activity/intensity values behind it, rather than only reading position
    off the axes. Requires plotly (pip install plotly); skips gracefully if
    it is not installed, so it never blocks the rest of the figure run."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        print('  [skipped] supp_activity_intensity_baseline_interactive.html: '
              "plotly not installed. Run 'pip install plotly' and re-run this script.")
        return

    if not activity_crosswalk_path.exists():
        print('  [skipped] supp_activity_intensity_baseline_interactive.html: '
              f'{activity_crosswalk_path.name} not found in data/. '
              'Run scripts/build_activity_intensity_crosswalk.py first.')
        return

    cw = pd.read_csv(activity_crosswalk_path)
    df = cw[cw['flag'].isin(['OK', 'LOW-CONF', 'SHARED'])].copy()
    df['sek_per_capita_2021'] = pd.to_numeric(df['sek_per_capita_2021'], errors='coerce')
    df['implied_intensity_kgco2e_per_sek'] = pd.to_numeric(
        df['implied_intensity_kgco2e_per_sek'], errors='coerce')
    df['baseline_kgco2e_cap'] = pd.to_numeric(df['baseline_kgco2e_cap'], errors='coerce')
    df = df[(df['sek_per_capita_2021'] > 0) & (df['implied_intensity_kgco2e_per_sek'] > 0)]
    df = df[df['domain'] != 'Flights']  # activity measured in km, not SEK; not comparable here

    x_lo, x_hi = 6, 30000
    y_lo, y_hi = 8e-5, 2

    fig = go.Figure()

    # Iso-emission reference lines: M x I = E, matching the static figure
    x_ref = np.logspace(np.log10(x_lo), np.log10(x_hi), 200)
    for E in [5, 30, 150, 600]:
        y_ref = E / x_ref
        mask = (y_ref >= y_lo) & (y_ref <= y_hi)
        fig.add_trace(go.Scatter(
            x=x_ref[mask], y=y_ref[mask], mode='lines',
            line=dict(color='#bbbbbb', width=1, dash='dash'),
            hoverinfo='skip', showlegend=False,
        ))
        fig.add_annotation(
            x=np.log10(x_hi), y=np.log10(E / x_hi), xref='x', yref='y',
            text=f'{E} kg/cap', showarrow=False, xanchor='left',
            font=dict(size=10, color='#999999'),
        )

    max_emissions = df['baseline_kgco2e_cap'].max()
    sizeref = 2.0 * max_emissions / (42.0 ** 2)

    for domain in DOMAIN_ORDER:
        if domain == 'Flights':
            continue
        sub = df[df['domain'] == domain]
        if sub.empty:
            continue
        hover = [
            f"<b>{cat}</b><br>"
            f"Domain: {domain}<br>"
            f"Baseline emissions: {e:.2f} kg CO\u2082e/cap<br>"
            f"Activity (M\u2080): {m:,.0f} SEK/cap<br>"
            f"Intensity (I\u2080): {i:.4f} kg CO\u2082e/SEK<br>"
            f"COICOP code(s): {coic}<br>"
            f"Match quality: {flag}"
            for cat, e, m, i, coic, flag in zip(
                sub['category'], sub['baseline_kgco2e_cap'], sub['sek_per_capita_2021'],
                sub['implied_intensity_kgco2e_per_sek'], sub['coicop_codes'], sub['flag'])
        ]
        fig.add_trace(go.Scatter(
            x=sub['sek_per_capita_2021'], y=sub['implied_intensity_kgco2e_per_sek'],
            mode='markers', name=domain,
            marker=dict(
                size=sub['baseline_kgco2e_cap'], sizemode='area', sizeref=sizeref, sizemin=3,
                color=DOMAIN_COLORS[domain], line=dict(width=0.6, color='white'), opacity=0.78,
            ),
            hovertext=hover, hoverinfo='text',
        ))

    # Callouts for the three categories discussed in Section 3.6 / 4.1
    callouts = {
        'Food and drink - Meat': 'Meat',
        'Clothing and shoes - Clothing': 'Clothing',
        'Housing - Electricity': 'Electricity',
    }
    for cat, label in callouts.items():
        row = df[df['category'] == cat]
        if row.empty:
            continue
        fig.add_annotation(
            x=row['sek_per_capita_2021'].iloc[0], y=row['implied_intensity_kgco2e_per_sek'].iloc[0],
            text=f'<b>{label}</b>', showarrow=True, arrowhead=0, arrowcolor='#333333',
            ax=28, ay=-24, font=dict(size=12, color='#333333'),
        )

    fig.update_xaxes(
        title_text='Baseline activity, M\u2080,c (SEK per capita per year, 2021)',
        type='log', range=[np.log10(x_lo), np.log10(x_hi)], showgrid=True, gridcolor='#eeeeee',
    )
    fig.update_yaxes(
        title_text='Baseline intensity, I\u2080,c (kg CO\u2082e per SEK)',
        type='log', range=[np.log10(y_lo), np.log10(y_hi)], showgrid=True, gridcolor='#eeeeee',
    )
    fig.update_layout(
        title='Baseline emissions as activity \u00d7 intensity, by category (hover to explore)',
        template='plotly_white', width=980, height=700,
        legend=dict(title='Domain'),
        hoverlabel=dict(bgcolor='white', font_size=12, font_family='Arial'),
        margin=dict(t=70, r=140),
        annotations=list(fig.layout.annotations) + [dict(
            x=0.01, y=-0.13, xref='paper', yref='paper', showarrow=False,
            text='Bubble size \u221d baseline emissions. Dashed lines are constant-emission contours '
                 '(M\u00d7I). Flights excluded: activity measured in km, not SEK (see Section 3.8).',
            font=dict(size=10, color='#777777'), xanchor='left',
        )],
    )

    out_path = FIG_DIR / 'supp_activity_intensity_baseline_interactive.html'
    fig.write_html(out_path, include_plotlyjs=True, full_html=True)
    print(f'  {out_path.name}')


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Generating figures...')
    fig1_conceptual()
    fig2_baseline()
    fig3_pathways()
    fig4_domain_reductions()
    fig5_sensitivity()
    supp_coverage()
    supp_activity_intensity()
    supp_activity_intensity_baseline_interactive()
    print(f'All figures saved to {FIG_DIR}/')
