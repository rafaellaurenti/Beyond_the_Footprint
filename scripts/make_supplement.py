"""Build Supplementary Material A (markdown) and Table A2 (Excel) from results.
Usage: python make_supplement.py <repo_dir> [output_dir]   (default output: <repo_dir>/supplementary)"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
W = Path(sys.argv[1]); R = W / "results"; D = W / "data"
O = Path(sys.argv[2]) if len(sys.argv) > 2 else W / "supplementary"; O.mkdir(parents=True, exist_ok=True)
cat = pd.read_csv(R / "category_inputs_v2.csv")
par = pd.read_csv(D / "scenario_parameters.csv"); s4 = par[par.scenario_id == "S4"].set_index("category_id")
xw = pd.read_csv(D / "coicop_activity_intensity_crosswalk.csv").set_index("category_id")
oat = pd.read_csv(R / "oat_v2.csv"); v1oat = pd.read_csv(D / "sensitivity_results.csv")  # one-at-a-time tests of the submitted version
sob = pd.read_csv(R / "sobol.csv"); fac = pd.read_csv(R / "factorial_32.csv")
v1 = pd.read_csv(R / "v1_validation.csv", index_col=0); named = pd.read_csv(R / "named_scenarios.csv")
thr = json.load(open(R / "technology_thresholds.json"))
mcs = json.load(open(R / "mc_summary.json")); ceil = json.load(open(R / "hotspot_ceiling.json"))

def tech_src(r):
    if r.dh: return "A: CCS in district heating; sectoral expectation, no confirmed local plan (tested 0-95%)"
    if r.hh_tech: return "A: household technology switch (electric vehicles, fossil-free heating)"
    if np.isclose(r.Rt, 0.7): return "A: generic supply-side cut; anchored in energy and agriculture projections (project report); benchmarked against Cap et al. (2024); tested 40-90%"
    if r.Rt > 0: return "A: category-specific supply-side assumption"
    return "-"
def note(r):
    parts = []
    if r.Rb > 0: parts.append(f"activity -{100*r.Rb:.0f}%")
    if r.Rt > 0: parts.append(f"intensity -{100*r.Rt:.0f}%")
    parts.append(f"ceiling {100*r.L:.0f}%")
    return "; ".join(parts)

rows = []; xl = []
def tcode(r):
    if r.dh: return "A-CCS"
    if r.hh_tech: return "A-HH"
    if np.isclose(r.Rt, 0.7): return "A-GEN"
    if r.Rt > 0: return "A-CAT"
    return "-"
for _, r in cat.sort_values("E0", ascending=False).iterrows():
    ev = "C / " + ("J" if r.Rb > 0 else "-") + " / " + tcode(r) + " / J"
    rows.append("| " + " | ".join([r.category.replace("|", "/"), f"{r.E0:.1f}", f"{r.Rb:.2f}", f"{r.Rt:.2f}",
        f"{r.L:.2f}", f"{r.k:.1f}", f"{int(r.t0)}", "x" if r.hot else "", "x" if r.hard else "", ev]) + " |")
    xl.append(dict(category=r.category, domain=r.domain, baseline_kg=r.E0, R_beh=r.Rb, R_tech=r.Rt,
        combined=1-(1-r.Rb)*(1-r.Rt), L=r.L, k=r.k, t0=int(r.t0), hotspot=bool(r.hot), hard_to_change=bool(r.hard),
        household_technology=bool(r.hh_tech), parameter_derived_note=note(r), evidence_coverage="C",
        evidence_behaviour="J" if r.Rb > 0 else "-", evidence_technology=tcode(r), technology_source=tech_src(r),
        evidence_adoption="J"))
pd.DataFrame(xl).to_excel(O / "Table_A2_parameters_and_evidence.xlsx", index=False)
tA2 = ("| Category | Baseline (kg) | R^b^ | R^t^ | L | k | t~0~ | Hot | Hard | Evidence (cov./beh./tech./adopt.) |\n"
       "|--------------------|--------|-------|-------|-------|-----|--------|-----|-----|----------------|\n" + "\n".join(rows))

act = []
for cid, r in cat.set_index("category_id").sort_values("E0", ascending=False).iterrows():
    x = xw.loc[cid] if cid in xw.index else None
    if x is None: continue
    act.append(f"| {r.category} | {x.coicop_codes if isinstance(x.coicop_codes, str) else '-'} | "
               f"{'' if pd.isna(x.sek_per_capita_2021) else f'{x.sek_per_capita_2021:.1f}'} | "
               f"{'' if pd.isna(x.implied_intensity_kgco2e_per_sek) else f'{x.implied_intensity_kgco2e_per_sek:.5f}'} | {x.flag} |")
tA2b = "| Category | COICOP code(s) or metric | Activity M~0~ (SEK/cap; flights km/cap) | Intensity I~0~ (kg CO~2~e/unit) | Flag |\n|--------------------------|----------|-----------|-----------|----------------------|\n" + "\n".join(act)

# baseline by domain (Note S1)
dom = cat.groupby("domain").E0.sum().sort_values(ascending=False)
tdom = "| Domain | kg CO~2~e per capita | Share of baseline |\n|---|---|---|\n" + "\n".join(
    f"| {d} | {v:,.0f} | {100*v/dom.sum():.0f}% |" for d, v in dom.items()) + f"\n| Total | {dom.sum():,.0f} | 100% |"

tA1 = "| Test | 2030 | 2050 | Change 2030 | Change 2050 | Gap 2030 | Gap 2050 |\n|----------------------------------------|---|---|---|---|---|---|\n" + "\n".join(
    f"| {r.test} | {r.e2030:.2f} | {r.e2050:.2f} | {r.d2030:+.2f} | {r.d2050:+.2f} | {r.gap2030:+.2f} | {r.gap2050:+.2f} |" for _, r in oat.iterrows())
tA1b = "| Variant (original model) | 2030 | 2050 | Change 2050 |\n|---|---|---|---|\n" + "\n".join(
    f"| {r.variant} | {r.emissions_2030_tco2e_per_capita:.2f} | {r.emissions_2050_tco2e_per_capita:.2f} | {r.delta_2050_vs_base_tco2e_per_capita:+.2f} |" for _, r in v1oat.iterrows())
tA3 = "| Parameter | Range | First-order 2030 | Total-order 2030 | First-order 2050 | Total-order 2050 |\n|---|---|---|---|---|---|\n" + "\n".join(
    f"| {r.description} | {r.low:g} to {r.high:g} | {r.S1_2030:.3f} | {r.ST_2030:.3f} | {r.S1_2050:.3f} | {r.ST_2050:.3f} |" for _, r in sob.iterrows())
tA4a = "| Original scenario | Original label | 2030 (original model) | 2050 (original model) | Closest revised cell | Main difference |\n|---|---|---|---|---|---|\n" + "\n".join([
    f"| S1 | Limited change | {v1.loc['S1','2030']:.2f} | {v1.loc['S1','2050']:.2f} | Reference (g = 0) | Revised reference includes autonomous decarbonisation |",
    f"| S2 | Hotspot-focused | {v1.loc['S2','2030']:.2f} | {v1.loc['S2','2050']:.2f} | Hotspot, full depth | Original used shallower measures on the hotspot set |",
    f"| S3 | Lifestyle-centred | {v1.loc['S3','2030']:.2f} | {v1.loc['S3','2050']:.2f} | Lifestyle + infrastructure | Original included CCS and electrification; 1.46 t of its 2.73 t 2050 cut came from technology |",
    f"| S4 | Coordinated | {v1.loc['S4','2030']:.2f} | {v1.loc['S4','2050']:.2f} | Coordinated | Revised model separates household and supply-side adoption (see Note S4) |"])
tA4b = "| Coverage | Behaviour | Technology | Infrastructure | CCS | 2030 | 2050 |\n|---|---|---|---|---|---|---|\n" + "\n".join(
    f"| {'broad' if r.Coverage else 'hotspot'} | {'on' if r.Behaviour else 'off'} | {'deep' if r.Technology else 'reference'} | {'enabling' if r.Infrastructure else 'current'} | {'on' if r.CCS else 'off'} | {r.e2030:.2f} | {r.e2050:.2f} |"
    for _, r in fac.iterrows())
tA4c = "| Scenario | g (per year) | 2030 | 2050 | Gap 2030 | Gap 2050 |\n|---|---|---|---|---|---|\n" + "\n".join(
    f"| {r.scenario} | {r.g:.3f} | {r.e2030:.2f} | {r.e2050:.2f} | {r.gap2030:+.2f} | {r.gap2050:+.2f} |" for _, r in named.iterrows())

# worked example, meat
m = cat.set_index("category_id").loc["food_and_drink_meat"]
def ex(y):
    A = m.L / (1 + np.exp(-m.k * (y - m.t0))); f = 0.985 ** (y - 2025)
    I = min(f, 1 - A * m.Rt); B = 1 - A * m.Rb; ov = (A - A * A) * m.Rb * m.Rt
    return A, f, I, B, ov, m.E0 * (B * I + ov)
e30, e50 = ex(2030), ex(2050)

md = f"""---
title: "Supplementary Material A"
subtitle: "Beyond the footprint: the urban consumption gap and the limits of hotspot strategies in city climate governance (revision 1)"
---

This document contains six supplementary notes and four supplementary tables. All values can be regenerated with `revision_model.py` and `make_supplement.py` in the repository (https://github.com/rafaellaurenti/Beyond_the_Footprint).

# Note S1. Baseline, activity data and crosswalk

**Baseline.** The baseline is the 2022 personal consumption-based footprint of Malmö residents from the Consumption Compass 2.0 (Dawkins et al., 2024): 5,735 kg CO~2~e per capita over 110 categories with positive emissions. It covers household final consumption, including residents' consumption outside Malmö, and excludes public consumption, capital formation and visitors' consumption. Statistics Sweden calculates the national footprint with an environmentally extended input-output model (PRINCE; Fauré et al., 2019; Palm et al., 2019). The Consumption Compass downscales it to statistical areas with a hybrid approach: local data for categories such as direct vehicle emissions, building energy, diets and flight frequency, and expenditure or income proxies for the rest.

**Baseline by domain.** The table below gives the baseline by consumption domain.

{tdom}

**Activity decomposition.** For interpretation only, we recovered activity levels from Statistics Sweden's national household expenditure by COICOP for 2021 (Statistics Sweden, 2022), matched at 4-digit level. Ten categories share a COICOP code with others; we split the shared total in proportion to baseline emissions. Four categories (4.3 kg, 0.08% of the baseline) have no counterpart. Direct emissions from vehicle use and heating are measured physically in the source data. Flights are anchored to national air-travel distance (5,800 km per capita, data from 2010 to 2013; Larsson et al., 2018), giving an implied intensity of 0.146 kg CO~2~e per passenger-km. Kamb and Larsson (2019) report 0.17 kg CO~2~e per passenger-km in 2017 including non-CO~2~ effects (0.09 kg CO~2~ only), with a decline of about 1.9% per year; projected to 2022 this gives about 0.155 kg. The flight emissions themselves come from the Consumption Compass, which uses Kamb and Larsson (2019) scaled with passenger-kilometre statistics for 2019 to 2023. The decomposition does not enter baseline emissions or scenario results except through the re-spending test (Note S4). Table A2b lists the activity data and confidence flags.

**Coverage of the activity data by type.** Direct COICOP match 3,449 kg (60%); low-confidence proxy 837 kg (15%); physical flight distance 850 kg (15%); direct physical emissions 468 kg (8%); shared codes 128 kg (2%); no match 4 kg (0.1%).

# Note S2. Evidence status of parameters and corrections

**Evidence codes (Table A2).** **C**: co-produced choice, made in workshops and working meetings with municipal staff and documented in the project report (Vejbrink et al., 2026). This applies to category coverage and scenario logic. **J**: project-team judgement, documented in the report without a specific source. This applies to behavioural potentials and to adoption ceilings, speeds and inflection years. **A**: author assumption, anchored where possible in literature or projections. This applies to technological potentials. No parameter was empirically calibrated or individually validated by municipal staff. The project report states that the team set reductions partly from what the targets required and partly from what seemed possible; the coordinated scenario is therefore a backcast.

**Corrections to assumption notes.** In the original Table A2, six notes did not match the parameters used in the model. We corrected the notes; no model value changed. (1) Meat: the note said 90% of residents cut meat by 80%, but the ceiling was 1.0. (2) Dairy: the note said 75% of residents cut by 75%, but the behavioural potential was 0.5 and the ceiling 1.0. (3) Clothing: the note said new purchases fall by 50%, but the behavioural potential was 0.75. (4) Cars: the note said each car keeps today's footprint, but a 70% technological potential applied. (5) Actual rent: the note said 75% of the population, but the ceiling was 1.0. (6) Fuels and lubricants: the note described electrification, which the parameters represented as a 90% behavioural and 90% technological potential. The original manuscript also stated that ceilings for hard-to-change categories sat below 1.0; in the coordinated scenario most were 1.0. The revised Table A2 replaces all notes with parameter-derived descriptions.

# Note S3. Combination of behavioural and technological reductions

Let a share $a_b$ of a category's population or stock adopt behavioural change (potential $R^b$) and a share $a_t$ adopt technological change (potential $R^t$). Let $o$ be the share that adopts both, with $\\max(0, a_b + a_t - 1) \\le o \\le \\min(a_b, a_t)$. Relative emissions are

$$e(o) = o(1-R^b)(1-R^t) + (a_b - o)(1-R^b) + (a_t - o)(1-R^t) + (1 - a_b - a_t + o) = 1 - a_b R^b - a_t R^t + o R^b R^t .$$

Because $\\partial e/\\partial o = R^b R^t \\ge 0$, emissions increase with overlap. Nested adoption, $o = \\min(a_b, a_t)$, gives the highest emissions and the smallest combined reduction. Independent adoption, $o = a_b a_t$, gives $e = (1 - a_b R^b)(1 - a_t R^t)$. With equal adoption shares $a$, nested adoption gives $e = 1 - a[1 - (1-R^b)(1-R^t)]$, the rule of the original project tool. That rule is therefore the conservative bound with respect to adoption correlation. At full adoption both cases converge to $(1-R^b)(1-R^t)$, which follows from emissions being activity times intensity. Correlation in magnitude, as opposed to adoption, can act in either direction; for example, consumers who cut meat may also buy lower-intensity products. The re-spending and volume tests (Table A1) cover the main anti-conservative channel, rebound.

# Note S4. Revised model specification

**Equations.** Adoption follows main text Eq. (3). The full emissions equation for category $c$ in year $y$ is

$$E_{{c,y}} = E_{{0,c}}\\, v_y \\left[ (1 - A^b_{{c,y}} R^b_c)\\, I_{{c,y}} + \\omega \\left(\\min(A^b_{{c,y}}, A^t_{{c,y}}) - A^b_{{c,y}} A^t_{{c,y}}\\right) R^b_c R^t_c \\right] \\qquad \\text{{(S1)}}$$

$$I_{{c,y}} = \\min\\left\\{{ f_y,\\; 1 - A^t_{{c,y}} R^t_c \\right\\}}, \\qquad f_y = (1 - g)^{{y - 2025}}, \\qquad v_y = (1 + v)^{{y - 2025}} \\qquad \\text{{(S2)}}$$

$A^b_{{c,y}}$ and $A^t_{{c,y}}$ are the behavioural and technological adoption shares from Eq. (3). The intensity factor $I_{{c,y}}$ cannot be worse than the reference trend $f_y$; categories without deep technological change follow $f_y$ alone. The term $v_y$ allows for growth or decline in consumption volume ($v$ = 0 in the central case). The overlap parameter $\\omega$ sets how the two adoptions combine during diffusion: $\\omega$ = 0 is independent adoption, and $\\omega$ = 1 is nested adoption (Note S3). The central case uses $\\omega$ = 1. Main text Eq. (4) is the special case $\\omega$ = 0 and $v$ = 0. Years run from 2026 to 2050; the reference trend and volume factor start after 2025. Scenario emissions are the sum over categories.

**Behavioural adoption** uses the category's ceiling $L_c$, speed $k_c$ and inflection year $t_{{0,c}}$ from the coordinated scenario. Under current conditions, ceilings are capped at 0.75.

**Technological adoption.** Generic supply-side intensity cuts (70% in the coordinated scenario) do not depend on household adoption, so their ceiling is 1.0 with the category's speed and timing. Household technologies (direct vehicle emissions, vehicle fuels, direct heating emissions) use the category ceiling, capped at 0.75 under current conditions. District-heating CCS uses its own parameters (ceiling 0.95, k = 1.0, t~0~ = 2030). The original model applied each category's single ceiling to both behavioural and technological change. This made household ceilings limit supply-side decarbonisation, for example of flights and food production. It explains why a 25% cut in hard-to-change ceilings raised 2050 emissions by 0.64 t in the original model and by 0.11 t in the revised model.

**Hotspot set** (nine categories, {100*ceil['hot_share']:.0f}% of the baseline): passenger flights; district heating; direct emissions from vehicle use; meat; dairy and eggs; vehicle fuels and lubricants; cars; direct emissions from heating; company-car benefit.

**Hard-to-change set:** passenger flights; package holidays; meat; dairy and eggs; cars; imputed rent for owned dwellings; actual rent; clothing; footwear.

**Reference trend:** $f_y = (1-g)^{{y-2025}}$, $g$ = 1.5% per year (0% and 3% tested). In cells with deep technology, the intensity factor is the lower of the reference trend and the deep-technology factor.

**Re-spending:** money saved through behavioural change equals $\\sum_c M_{{0,c}} v_y A^b_{{c,y}} R^b_c$ (flights at 1 SEK per passenger-km). A share $\\rho$ is re-spent at the residual average intensity of the basket in that year.

**Two-group test:** a high-footprint group (share 0.4, footprint multiplier m = 1.25, 1.5 or 2) and a lower-footprint group (multiplier (1 - 0.4m)/0.6). Category composition is proportional. A 25% shortfall reduces behavioural adoption and household-technology adoption in one group.

**Shapley values:** computed exactly over the 32 cells (Table A4b), with the low level of each lever as the starting point. The all-low cell equals the reference.

**Global sensitivity analysis:** 16,384 base samples, Saltelli design, Jansen estimators for first-order and total-order indices (Saltelli et al., 2010). Ranges in Table A3. Summary: median 2050 emissions {mcs['median_2050']:.2f} t (5th to 95th percentile {mcs['p05_2050']:.2f} to {mcs['p95_2050']:.2f}); {100*mcs['share_2050_le_target']:.1f}% of runs at or below 1.0 t; {100*mcs['share_2050_le_strict']:.1f}% at or below 0.7 t. Median 2030 emissions {mcs['median_2030']:.2f} t; {100*mcs['share_2030_le_target']:.1f}% at or below 3.1 t. The sum of first-order indices for 2050 is {mcs['sum_S1_2050']:.2f}; values slightly above 1 reflect sampling error.

**Technology thresholds:** the smallest generic supply-side cut that meets 1.0 t in 2050 is {100*thr['coordinated_ccs']:.0f}% in the coordinated scenario with CCS and {100*thr['coordinated_no_ccs']:.0f}% without CCS. Without behavioural change it is {100*thr['no_behaviour_ccs']:.0f}% with CCS and {100*thr['no_behaviour_no_ccs']:.0f}% without CCS (`technology_thresholds.json`).

**Validation:** with the original specification, the code reproduces the original scenario results exactly (Table A4a).

# Note S5. Worked example: meat in the coordinated scenario

Baseline 289.9 kg CO~2~e per capita; $R^b$ = 0.80, $R^t$ = 0.70, $L$ = 1.0, $k$ = 0.2, $t_0$ = 2029; nested adoption ($\\omega$ = 1); $g$ = 1.5% per year.

| Year | Adoption A | Reference factor f | Intensity factor I | Behaviour factor | Overlap term | Emissions (kg) |
|---|---|---|---|---|---|---|
| 2030 | {e30[0]:.3f} | {e30[1]:.3f} | {e30[2]:.3f} | {e30[3]:.3f} | {e30[4]:.3f} | {e30[5]:.1f} |
| 2050 | {e50[0]:.3f} | {e50[1]:.3f} | {e50[2]:.3f} | {e50[3]:.3f} | {e50[4]:.3f} | {e50[5]:.1f} |

These values equal those of the original model (140 kg and 21 kg), because nested adoption with equal adoption shares reproduces the original rule.

# Note S6. Hotspot ceiling

If the hotspot set holds a share $h$ of the baseline $E_0$, a hotspot strategy cannot reduce emissions below $(1-h)E_0$ on a static baseline, or $(1-h)E_0 f_y$ with the reference trend. For Malmö, $h$ = {ceil['hot_share']:.3f}, so the floor is {ceil['hot_floor_t']:.2f} t (static) and {ceil['hot_floor_with_reference_trend_t']:.2f} t in 2050 with the reference trend. The 2050 target requires a {100*ceil['required_coverage']:.1f}% cut. Addressing categories from largest to smallest, {ceil['n_categories_full_removal']} categories are needed to cover this share at complete elimination, and {ceil['n_categories_at_s4_depth']} at coordinated-scenario depth with full adoption.

# Table A1. One-at-a-time tests of the coordinated scenario (revised model)

t CO~2~e per capita. Gaps against 3.1 t (2030) and 1.0 t (2050).

{tA1}

**Table A1b.** Original one-at-a-time tests (original model, as submitted), retained for comparison.

{tA1b}

# Table A2. Category-level parameters of the coordinated scenario with evidence status

R^b^ behavioural potential; R^t^ technological potential (district heating: CCS); L adoption ceiling; k speed; t~0~ inflection year. Evidence codes: C co-produced; J project-team judgement; A author assumption (Note S2). Technology codes: A-GEN generic supply-side cut of 70%, anchored in energy and agriculture projections cited in the project report, benchmarked against Cap et al. (2024) and tested from 40% to 90%; A-HH household technology switch (electric vehicles, fossil-free heating); A-CCS carbon capture in district heating, a sectoral expectation without a confirmed local plan, tested from 0% to 95%; A-CAT category-specific assumption. The file Table_A2_parameters_and_evidence.xlsx gives the same table with parameter-derived notes.

{tA2}

**Table A2b.** Activity and implied intensity by category (Note S1).

{tA2b}

# Table A3. Global sensitivity analysis: parameter ranges and Sobol indices

Coordinated scenario; uniform distributions; 16,384 base samples. Most ranges extend from the central value toward less favourable values, because central values were set to reach the target.

{tA3}

# Table A4. Reconciliation with the original scenarios and full factorial results

**Table A4a.** Original scenarios reproduced with the original specification.

{tA4a}

**Table A4b.** All 32 factorial cells (revised model; g = 1.5% per year).

{tA4b}

**Table A4c.** Named scenarios at three reference rates.

{tA4c}

# References

Cap, S., de Koning, A., Tukker, A., Scherer, L., 2024. (In)Sufficiency of industrial decarbonization to reduce household carbon footprints to 1.5°C-compatible levels. Sustainable Production and Consumption 45, 216–227. https://doi.org/10.1016/j.spc.2023.12.031

Dawkins, E., Rahmati-Abkenar, M., Axelsson, K., Grah, R., Broekhoff, D., 2024. The carbon footprints of consumption of goods and services in Sweden at municipal and postcode level and policy interventions. Sustainable Production and Consumption 52, 63–79. https://doi.org/10.1016/j.spc.2024.10.013

Fauré, E., Dawkins, E., Wood, R., Finnveden, G., Palm, V., Persson, L., Schmidt, S., 2019. Environmental pressure from Swedish consumption: The largest contributing producer countries, products and services. Journal of Cleaner Production 231, 698–713. https://doi.org/10.1016/j.jclepro.2019.05.148

Kamb, A., Larsson, J., 2019. Climate footprint from Swedish residents' air travel. Chalmers University of Technology, Gothenburg.

Larsson, J., Kamb, A., Nässén, J., Åkerman, J., 2018. Measuring greenhouse gas emissions from international air travel of a country's residents: methodological development and application for Sweden. Environmental Impact Assessment Review 72, 137–144. https://doi.org/10.1016/j.eiar.2018.05.013

Palm, V., Wood, R., Berglund, M., Dawkins, E., Finnveden, G., Schmidt, S., Steinbach, N., 2019. Environmental pressures from Swedish consumption: A hybrid multi-regional input-output approach. Journal of Cleaner Production 228, 634–644. https://doi.org/10.1016/j.jclepro.2019.04.181

Saltelli, A., Annoni, P., Azzini, I., Campolongo, F., Ratto, M., Tarantola, S., 2010. Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index. Computer Physics Communications 181, 259–270. https://doi.org/10.1016/j.cpc.2009.09.018

Statistics Sweden, 2022. Household consumption expenditure (ESA2010) by purpose COICOP (1999), 1980–2021 [Data table 000000SG]. Statistikdatabasen.

Vejbrink, U., Diener, D., Laurenti, R., Hoffmann, V., Bonnevier, L., Folkesson, L., 2026. Potentialanalys av konsumtionsbaserade utsläpp i Malmö Stad. RISE Rapport 2026:42. RISE Research Institutes of Sweden, Borås.
"""
(O / "supplementary_R1.md").write_text(md)
print("ok", e30[5], e50[5])
