"""Figures 1 to 7 for revision 1, in the RISE colour scheme.

Usage: python make_figures.py <results_dir> <fig_dir>

Colours are the RISE theme colours and custom profile colours only. No automatic
tints are used. The only blended colours are the continuous colour scale in
Figure 7 and the small overlap of the two histograms in Figure 6a.
Outputs: vector PDF and 600 dpi PNG for each figure. Widths follow Elsevier
column sizes (90, 140 and 190 mm).
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib import font_manager

R = Path(sys.argv[1]); F = Path(sys.argv[2]); F.mkdir(parents=True, exist_ok=True)

# ---------------- RISE palette (theme colours and custom profile colours)
BLACK, DARK, LIGHTGRAY, WHITE = "#000000", "#222322", "#f0f0f0", "#ffffff"
TEAL, PINK, YELLOW = "#009ba5", "#e83c63", "#fee402"
MINT, PEACH, CREAM = "#ebf5ef", "#fde8df", "#fff6dd"
LTEAL, LPINK, LYELLOW, PETROL, PURPLE = "#8bc7c6", "#f4a8aa", "#ffee8e", "#0d4d64", "#472d55"
INK, INK2, GRID = DARK, "#222322", LIGHTGRAY

MM = 1 / 25.4
W1, W15, W2 = 90 * MM, 140 * MM, 190 * MM

font = "Inter" if any("Inter" in f.name for f in font_manager.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams.update({
    "font.family": font, "font.size": 7.5, "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "axes.titlesize": 8, "axes.titleweight": "semibold", "axes.titlelocation": "left",
    "axes.titlepad": 6, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK,
    "axes.linewidth": 0.6, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "legend.frameon": False, "lines.linewidth": 1.6, "figure.dpi": 150, "savefig.dpi": 600,
    "savefig.facecolor": WHITE, "pdf.fonttype": 42, "ps.fonttype": 42, "hatch.linewidth": 0.6,
})

def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(F / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)

def xgrid(ax):
    ax.grid(axis="x", color=GRID, lw=0.7); ax.set_axisbelow(True)

def panel(ax, letter, text):
    ax.set_title(f"{letter}   {text}", fontweight="semibold")

DOMAIN_ORDER = ["Food and drink", "Housing", "Local transport", "Flights", "Other consumption",
                "Leisure, sport and culture", "Clothing and shoes"]
DCOL = dict(zip(DOMAIN_ORDER, [TEAL, PETROL, PINK, PURPLE, LTEAL, LPINK, YELLOW]))
EDGE = {d: (INK if c in (YELLOW, LTEAL, LPINK) else c) for d, c in DCOL.items()}

# ---------------- Figure 1: concept (schematic)
yrs = np.linspace(2025, 2050, 300); t = (yrs - 2025) / 25
ref = 6.0 - 2.0 * t
targ = 6.0 - 5.0 * (1 - (1 - t) ** 1.4)
best = targ + 1.2 * t ** 1.3
fig, ax = plt.subplots(figsize=(W15, 72 * MM))
ax.fill_between(yrs, best, ref, color=MINT, lw=0)
ax.fill_between(yrs, targ, best, color=LPINK, lw=0)
ax.plot(yrs, ref, color=DARK, lw=1.4, ls=(0, (1.2, 1.4)))
ax.plot(yrs, best, color=TEAL, lw=2)
ax.plot(yrs, targ, color=BLACK, lw=1.3, ls=(0, (5, 2)))
ax.text(2050.5, ref[-1], "Reference trajectory\n(current trends)", va="center", fontsize=7, color=DARK)
ax.text(2050.5, best[-1] + 0.12, "Lowest-emission\nfeasible pathway", va="bottom", fontsize=7, color=TEAL, fontweight="semibold")
ax.text(2050.5, targ[-1] - 0.05, "Target pathway", va="top", fontsize=7, color=BLACK)
ax.annotate("", xy=(2025.6, targ[-1]), xytext=(2025.6, 6.0), arrowprops=dict(arrowstyle="<->", color=DARK, lw=0.8))
ax.text(2026.1, 3.0, "Required\nreduction", fontsize=7, color=DARK, va="center")
ax.text(2039.5, (best[170] + ref[170]) / 2, "Feasible transition space\ncoverage, depth, adoption limits",
        fontsize=7, ha="center", va="center", color=PETROL)
ax.annotate("Urban consumption gap\nresidual after feasible action", xy=(2046.5, (best[260] + targ[260]) / 2),
            xytext=(2037.5, 0.55), fontsize=7, ha="center", va="center", color=PINK, fontweight="semibold",
            arrowprops=dict(arrowstyle="-", color=PINK, lw=0.8, shrinkB=0))
ax.set_xlim(2025, 2050); ax.set_ylim(0, 6.3); ax.set_yticks([]); ax.set_xticks([2025, 2030, 2040, 2050])
ax.set_ylabel("Consumption-based emissions per capita"); ax.set_xlabel("Year")
ax.spines["left"].set_visible(True)
save(fig, "fig1_urban_consumption_gap_framework")

# ---------------- Figure 2: baseline and hotspot ceiling
cumdf = pd.read_csv(R / "cumulative_coverage.csv"); ceil = json.load(open(R / "hotspot_ceiling.json"))
fig, (a, b) = plt.subplots(1, 2, figsize=(W2, 98 * MM), gridspec_kw=dict(width_ratios=[1.3, 1], wspace=0.42))
top = cumdf.head(20).iloc[::-1]
a.barh(np.arange(len(top)), top.E0, color=[DCOL[d] for d in top.domain],
       edgecolor=[EDGE[d] if DCOL[d] == YELLOW else DCOL[d] for d in top.domain], lw=0.5, height=0.74)
a.set_yticks(np.arange(len(top)))
a.set_yticklabels([c.split(" - ", 1)[1] for c in top.category], fontsize=6.5)
for i, (v, h) in enumerate(zip(top.E0, top.hot)):
    a.text(v + 10, i, f"{v:.0f}", va="center", fontsize=6.3, color=INK)
    if h:
        a.plot(v + 75 + 9 * len(f"{v:.0f}"), i, marker="o", ms=3.2, color=PINK, mec=PINK)
a.set_xlabel("kg CO$_2$e per capita per year"); xgrid(a); a.set_xlim(0, top.E0.max() * 1.18)
a.tick_params(axis="y", length=0)
panel(a, "a", "Twenty largest of 110 categories")
hs = [Patch(facecolor=DCOL[d], edgecolor=EDGE[d] if DCOL[d] == YELLOW else DCOL[d], lw=0.5, label=d) for d in DOMAIN_ORDER]
hs.append(Line2D([], [], marker="o", ls="", color=PINK, ms=3.5, label="Hotspot set"))
a.legend(handles=hs, loc="lower right", fontsize=6.3, handlelength=1.1, handleheight=0.9)
n = np.arange(1, len(cumdf) + 1); cs_ = 100 * cumdf.cum_share.values
b.fill_between(n, 0, cs_, color=MINT, lw=0)
b.plot(n, cs_, color=TEAL, lw=1.8)
req = 100 * ceil["required_coverage"]
b.axhline(req, color=BLACK, ls=(0, (5, 2)), lw=1)
b.text(len(cumdf), req + 2.5, f"Required cut to 1.0 t: {req:.0f}%", ha="right", fontsize=6.8, color=BLACK)
hot = 100 * ceil["hot_share"]
b.axhline(hot, color=PINK, lw=1, ls=(0, (1.2, 1.4)))
b.text(len(cumdf), hot - 6, f"Hotspot ceiling: {hot:.0f}%", ha="right", fontsize=6.8, color=PINK, fontweight="semibold")
b.annotate("", xy=(104, req), xytext=(104, hot), arrowprops=dict(arrowstyle="<->", color=DARK, lw=0.7))
b.text(102, (req + hot) / 2, "Shortfall of\nhotspot strategy", ha="right", va="center", fontsize=6.5, color=DARK)
nf = ceil["n_categories_full_removal"]; ynf = cs_[nf - 1]
b.plot(nf, ynf, "o", ms=4.5, color=PETROL, mec=WHITE, mew=0.8, zorder=5)
b.annotate(f"{nf} categories needed\neven at 100% elimination", xy=(nf, ynf), xytext=(nf + 6, 22),
           fontsize=6.8, color=PETROL, arrowprops=dict(arrowstyle="-", color=PETROL, lw=0.7))
b.set_xlabel("Number of categories addressed, largest first"); b.set_ylabel("Cumulative share of baseline (%)")
b.set_xlim(0, len(cumdf) + 1); b.set_ylim(0, 102); b.grid(color=GRID, lw=0.7); b.set_axisbelow(True)
panel(b, "b", "Cumulative coverage of the footprint")
save(fig, "fig2_baseline_and_hotspot_ceiling")

# ---------------- Figure 3: named pathways
pw = pd.read_csv(R / "named_pathways.csv")
lab = {"N0": "Reference", "N1": "Hotspot, full depth", "N2": "Lifestyle only", "N3": "Lifestyle + infrastructure",
       "N4": "Technology only", "N5": "Coordinated"}
colr = {"N0": DARK, "N1": PURPLE, "N2": LPINK, "N3": PINK, "N4": TEAL, "N5": PETROL}
lsty = {"N0": (0, (1.2, 1.4)), "N1": (0, (4, 1.5, 1, 1.5)), "N2": (0, (3, 1.5)), "N3": "-", "N4": "-", "N5": "-"}
lw = {"N0": 1.4, "N1": 1.4, "N2": 1.6, "N3": 1.4, "N4": 1.6, "N5": 2.4}
fig, ax = plt.subplots(figsize=(W15, 88 * MM))
yy_ = pw.year.values
tm = pw.year >= 2030
ax.plot(pw.year[tm], pw.target[tm], color=BLACK, lw=1.2, ls=(0, (5, 2)), zorder=4)
ax.plot(2025, 5.735, "o", ms=4, color=DARK, zorder=6)
ends = {}
for kk in ["N0", "N1", "N2", "N3", "N4", "N5"]:
    ax.plot(yy_, pw[kk].values, color=colr[kk], ls=lsty[kk], lw=lw[kk], zorder=5 if kk == "N5" else 3)
    ends[kk] = pw[kk].iloc[-1]
ax.plot([2030, 2050], [3.1, 1.0], "D", ms=4, color=BLACK, zorder=6)
ax.text(2029.6, 3.1, "3.1 t", fontsize=6.5, ha="right", va="center")
ax.text(2025.4, 5.9, "2022 baseline 5.7 t", fontsize=6.5, color=DARK)
order = sorted(ends, key=lambda x: ends[x]); last = -9; ypos = {}
for kk in order:
    ypos[kk] = max(ends[kk], last + 0.27); last = ypos[kk]
for kk in order:
    ax.plot([2050.6, 2052.2], [ypos[kk]] * 2, color=colr[kk], ls=lsty[kk], lw=lw[kk], clip_on=False)
    ax.text(2052.6, ypos[kk], f"{lab[kk]}  {ends[kk]:.1f} t", va="center", fontsize=6.8, color=INK,
            fontweight="semibold" if kk == "N5" else "normal")
ax.plot([2050.6, 2052.2], [0.6] * 2, color=BLACK, lw=1.2, ls=(0, (5, 2)), clip_on=False)
ax.text(2052.6, 0.6, "Target  1.0 t", va="center", fontsize=6.8, color=BLACK)
ax.set_xlim(2025, 2050); ax.set_ylim(0, 6.2); ax.set_xticks([2025, 2030, 2035, 2040, 2045, 2050])
ax.set_xlabel("Year"); ax.set_ylabel("t CO$_2$e per capita per year")
ax.grid(axis="y", color=GRID, lw=0.7); ax.set_axisbelow(True)
save(fig, "fig3_scenario_pathways")

# ---------------- Figure 4: Shapley decomposition, coloured by municipal reach
sh = pd.read_csv(R / "shapley.csv", index_col=0)
lev = ["Technology", "Coverage", "Behaviour", "CCS", "Infrastructure"]
lcol = {"Coverage": TEAL, "Behaviour": PETROL, "Infrastructure": LTEAL, "CCS": PURPLE, "Technology": PINK}
fig, axs = plt.subplots(1, 2, figsize=(W2, 62 * MM), sharey=True, gridspec_kw=dict(wspace=0.08))
for ax, y, letter in zip(axs, ["2030", "2050"], "ab"):
    vals = sh.loc[lev, y].values; tot = sh.loc["Total", y]
    ax.barh(np.arange(len(lev))[::-1], vals, color=[lcol[l] for l in lev], height=0.64)
    for i, v in enumerate(vals):
        ax.text(v + 0.02, len(lev) - 1 - i, f"{v:.2f} t  ({100*v/tot:.0f}%)", va="center", fontsize=6.8)
    ax.set_yticks(np.arange(len(lev))[::-1]); ax.set_yticklabels(lev); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 1.6); xgrid(ax)
    ax.set_xlabel("Reduction below reference (t CO$_2$e per capita)")
    city = sh.loc[["Coverage", "Behaviour", "Infrastructure"], y].sum()
    panel(ax, letter, f"{y}: total {tot:.2f} t; city portfolio levers {city:.2f} t ({100*city/tot:.0f}%)")
from matplotlib.legend_handler import HandlerTuple
fig.legend(handles=[(Patch(color=TEAL), Patch(color=PETROL), Patch(color=LTEAL)), Patch(color=PURPLE), Patch(color=PINK)],
           labels=["Within the city's portfolio", "Local energy system", "Mostly outside municipal control"],
           handler_map={tuple: HandlerTuple(ndivide=None, pad=0)}, loc="lower center", bbox_to_anchor=(0.5, -0.2),
           ncol=3, fontsize=6.8, handlelength=3.0)
save(fig, "fig4_shapley_decomposition")

# ---------------- Figure 5: domain contributions
dom = pd.read_csv(R / "domain_contributions_v2.csv", index_col=0).loc[DOMAIN_ORDER[::-1]]
fig, ax = plt.subplots(figsize=(W15, 74 * MM))
yy = np.arange(len(dom)); h = 0.36
for i, d in enumerate(dom.index):
    c = DCOL[d]; e = INK if c == YELLOW else c
    ax.barh(i + h / 2, dom.loc[d, "reduction_vs_baseline"], height=h, color=c, edgecolor=e, lw=0.5)
    ax.barh(i - h / 2, dom.loc[d, "reduction_vs_reference"], height=h, color=WHITE, edgecolor=e, hatch="//////", lw=0.8)
    ax.text(dom.loc[d, "reduction_vs_baseline"] + 0.015, i + h / 2, f"{dom.loc[d, 'reduction_vs_baseline']:.2f}", va="center", fontsize=6.5)
    ax.text(dom.loc[d, "reduction_vs_reference"] + 0.015, i - h / 2, f"{dom.loc[d, 'reduction_vs_reference']:.2f}", va="center",
            fontsize=6.5, color=DARK)
ax.set_yticks(yy); ax.set_yticklabels(dom.index); ax.tick_params(axis="y", length=0)
ax.set_xlim(0, 1.25); xgrid(ax)
ax.set_xlabel("2050 reduction in the coordinated scenario (t CO$_2$e per capita)")
ax.legend(handles=[Patch(facecolor=DARK, edgecolor=DARK, label="Compared with 2022 baseline"),
                   Patch(facecolor=WHITE, edgecolor=DARK, hatch="//////", label="Beyond the reference trend")],
          loc="lower right", fontsize=6.8)
save(fig, "fig5_domain_contributions")

# ---------------- Figure 6: uncertainty
mc = pd.read_csv(R / "mc_samples.csv"); sob = pd.read_csv(R / "sobol.csv"); ms = json.load(open(R / "mc_summary.json"))
fig, (a, b) = plt.subplots(1, 2, figsize=(W2, 72 * MM), gridspec_kw=dict(width_ratios=[1.1, 0.9], wspace=0.5))
bins = np.linspace(0, 6, 61)
a.hist(mc.e2030, bins=bins, color=LPINK, lw=0)
a.hist(mc.e2030, bins=bins, histtype="step", color=PINK, lw=0.9)
a.hist(mc.e2050, bins=bins, color=LTEAL, lw=0, alpha=0.85)
a.hist(mc.e2050, bins=bins, histtype="step", color=PETROL, lw=0.9)
ymax = a.get_ylim()[1]
a.axvline(1.0, color=PETROL, ls=(0, (5, 2)), lw=1); a.axvline(3.1, color=PINK, ls=(0, (5, 2)), lw=1)
a.set_xlim(0, 6); a.set_ylim(0, ymax * 1.62)
a.legend(handles=[Patch(facecolor=LTEAL, edgecolor=PETROL, label=f"2050: median {ms['median_2050']:.1f} t; {100*ms['share_2050_le_target']:.0f}% of runs ≤ 1.0 t"),
                  Patch(facecolor=LPINK, edgecolor=PINK, label=f"2030: median {ms['median_2030']:.1f} t; {100*ms['share_2030_le_target']:.0f}% of runs ≤ 3.1 t"),
                  Line2D([], [], color=PETROL, ls=(0, (5, 2)), lw=1, label="2050 target, 1.0 t"),
                  Line2D([], [], color=PINK, ls=(0, (5, 2)), lw=1, label="2030 target, 3.1 t")],
          loc="upper left", fontsize=6.3, handlelength=1.6, frameon=True, facecolor=WHITE, edgecolor="none", framealpha=1)
a.set_xlabel("t CO$_2$e per capita"); a.set_ylabel("Number of runs")
panel(a, "a", f"Coordinated scenario, {ms['n']:,} runs")
# Rank by the larger of the 2030 and 2050 indices, so that adoption timing (dominant in 2030) is shown.
s = sob.assign(ST_max=sob[["ST_2030", "ST_2050"]].max(axis=1)).sort_values("ST_max").tail(8); yy = np.arange(len(s))
b.barh(yy + 0.19, s.ST_2050, height=0.36, color=PETROL, label="2050")
b.barh(yy - 0.19, s.ST_2030, height=0.36, color=PINK, label="2030")
b.set_yticks(yy); SHORT = {"tau": "Generic supply-side cut", "v": "Consumption volume growth", "k": "Adoption speed",
         "kappa": "CCS capture rate", "g": "Autonomous intensity decline", "beta": "Behavioural potentials",
         "lam_h": "Hard-to-change ceilings", "rho": "Re-spending of savings", "t0_shift": "Adoption timing",
         "hh_scale": "Household technology", "omega": "Adoption overlap", "lam_o": "Other adoption ceilings"}
b.set_yticklabels([SHORT[p_] for p_ in s.param], fontsize=6.8)
b.tick_params(axis="y", length=0); b.set_xlim(0, 1); xgrid(b)
b.set_xlabel("Total-order Sobol index"); b.legend(loc="lower right", fontsize=6.8)
panel(b, "b", "Contribution to output variance")
save(fig, "fig6_uncertainty")

# ---------------- Figure 7: target-consistency frontier
fz = np.load(R / "frontier.npz")
cmap = LinearSegmentedColormap.from_list("rise_div", [PETROL, TEAL, LTEAL, WHITE, LPINK, PINK, PURPLE])
norm = TwoSlopeNorm(vmin=0.2, vcenter=1.0, vmax=3.0)
fig, ax = plt.subplots(figsize=(W15, 92 * MM))
X, Y = 100 * fz["taus"], 100 * fz["lams"]
cs = ax.contourf(X, Y, fz["ccs_on"], levels=np.r_[np.arange(0.2, 1.0, 0.1), np.arange(1.0, 3.01, 0.2)], cmap=cmap, norm=norm)
c1 = ax.contour(X, Y, fz["ccs_on"], levels=[1.0], colors=BLACK, linewidths=1.6)
c2 = ax.contour(X, Y, fz["ccs_off"], levels=[1.0], colors=BLACK, linewidths=1.2, linestyles=[(0, (5, 2))])
ax.clabel(c1, fmt={1.0: "1.0 t with CCS"}, fontsize=6.5, inline_spacing=3)
ax.clabel(c2, fmt={1.0: "1.0 t without CCS"}, fontsize=6.5, inline_spacing=3)
ax.plot(70, 100, marker="*", ms=10, color=YELLOW, mec=BLACK, mew=0.7, zorder=5, clip_on=False)
ax.text(68.5, 97.3, "Central values", fontsize=6.8, ha="right", va="top")
ax.text(38, 46, "Target missed", fontsize=7, color=WHITE, fontweight="semibold")
ax.text(92, 46, "Target\nmet", fontsize=7, color=WHITE, fontweight="semibold", ha="right")
for sp in ax.spines.values(): sp.set_visible(False)
cb = fig.colorbar(cs, ax=ax, pad=0.03, fraction=0.05, ticks=[0.2, 0.6, 1.0, 1.5, 2.0, 2.5, 3.0])
cb.set_label("2050 emissions with CCS (t CO$_2$e per capita)"); cb.outline.set_visible(False); cb.ax.tick_params(length=0)
ax.set_xlabel("Generic supply-side intensity cut by 2050 (%)")
ax.set_ylabel("Hard-to-change adoption ceilings (% of central)")
save(fig, "fig7_target_frontier")
print("figures written with font", font)
