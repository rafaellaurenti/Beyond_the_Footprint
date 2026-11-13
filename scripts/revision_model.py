"""
Revision model for "Beyond the footprint" (CLRC-D-26-00768, revision 1).

Implements:
  - validation of the original (v1) four-scenario model
  - the revised lever-based model (v2): coverage, behaviour, technology,
    adoption reach (infrastructure) and CCS, plus an autonomous reference trend
  - full factorial (32 cells), named scenarios and Shapley decomposition
  - global sensitivity analysis (Monte Carlo, Sobol first and total order)
  - target-consistency frontier, joint adverse case, combination-rule tests,
    re-spending (rebound) test, stricter targets, hotspot ceiling metric,
    two-group adoption (equity) sensitivity

Usage:  python revision_model.py <data_dir> <out_dir>
"""
import sys, itertools, math, json
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(sys.argv[1]); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
YEARS = np.arange(2026, 2051)
T2030, T2050 = 3.1, 1.0
REF_YEAR = 2025          # autonomous trend and volume growth start after 2025
L_CURRENT_CAP = 0.75     # current-conditions ceiling (report: about 25% unreached)
G_CENTRAL = 0.015        # central autonomous intensity decline, per year
RNG = np.random.default_rng(20261110)

def target(y):
    y = np.asarray(y, dtype=float)
    return np.where(y <= 2030, T2030, T2030 + (T2050 - T2030) * (y - 2030) / 20)

# ------------------------------------------------------------------ data
base = pd.read_csv(DATA / "baseline_categories.csv")
par = pd.read_csv(DATA / "scenario_parameters.csv")
xw = pd.read_csv(DATA / "coicop_activity_intensity_crosswalk.csv")
E0_TOTAL = base.baseline_kgco2e_per_capita.sum()

# ------------------------------------------------------------------ v1 validation
def v1_run(sid, years=YEARS):
    d = par[par.scenario_id == sid]
    out = []
    for y in years:
        A = d.L_max_adoption / (1 + np.exp(-d.k_adoption_speed * (y - d.t0_inflection_year)))
        out.append((E0_TOTAL - (d.baseline_kgco2e_per_capita * d.combined_reduction_fraction * A).sum()) / 1000)
    return np.array(out)

v1 = {s: v1_run(s) for s in ["S1", "S2", "S3", "S4"]}
v1_tab = pd.DataFrame({s: [v[YEARS == 2030][0], v[YEARS == 2050][0]] for s, v in v1.items()},
                      index=["2030", "2050"]).T
v1_tab.to_csv(OUT / "v1_validation.csv")

# ------------------------------------------------------------------ category table (S4 basis)
s4 = par[par.scenario_id == "S4"].set_index("category_id")
hot_ids = set(par[par.scenario_id == "S2"].category_id)
cat = base[["category_id", "category", "domain", "baseline_kgco2e_per_capita"]].copy()
cat = cat[cat.baseline_kgco2e_per_capita > 0].reset_index(drop=True)
cat = cat.merge(s4[["behavioral_reduction_fraction", "technical_reduction_fraction",
                    "L_max_adoption", "k_adoption_speed", "t0_inflection_year"]],
                left_on="category_id", right_index=True, how="left")
cat = cat.rename(columns={"baseline_kgco2e_per_capita": "E0", "behavioral_reduction_fraction": "Rb",
                          "technical_reduction_fraction": "Rt", "L_max_adoption": "L",
                          "k_adoption_speed": "k", "t0_inflection_year": "t0"})
cat[["Rb", "Rt"]] = cat[["Rb", "Rt"]].fillna(0.0)
cat["L"] = cat["L"].fillna(1.0); cat["k"] = cat["k"].fillna(0.2); cat["t0"] = cat["t0"].fillna(2029)
cat["hot"] = cat.category_id.isin(hot_ids)
cat["dh"] = cat.category_id.str.startswith("housing_district_heating")
HH_TECH = ["local_transport_direct_emissions_from_vehicle_use", "local_transport_fuels_and_lubricants",
           "housing_direct_emissions_from_heating"]
cat["hh_tech"] = cat.category_id.isin(HH_TECH)
HARD = ["flights_passenger_flights", "leisure_sport_and_culture_package_holidays", "food_and_drink_meat",
        "food_and_drink_milk_cheese_other_dairy_products_and_eggs", "local_transport_cars",
        "housing_imputed_rent_for_owned_permanent_dwelling", "housing_actual_rent_for_rented_permanent_dwelling",
        "clothing_and_shoes_clothing", "clothing_and_shoes_shoes_and_other_footwear"]
missing = [h for h in HARD + HH_TECH if h not in set(cat.category_id)]
assert not missing, missing
cat["hard"] = cat.category_id.isin(HARD)
cat["generic"] = np.isclose(cat.Rt, 0.7) & ~cat.hh_tech & ~cat.dh
m0 = xw.set_index("category_id")["sek_per_capita_2021"]
cat["M0"] = cat.category_id.map(m0)                       # SEK (flights: km, treated at 1 SEK/pkm)
cat["M0"] = cat["M0"].where(cat["M0"] > 0)
cat.to_csv(OUT / "category_inputs_v2.csv", index=False)
NC = len(cat)
C = {c: cat[c].to_numpy(dtype=float) for c in ["E0", "Rb", "Rt", "L", "k", "t0", "M0"]}
MASK = {c: cat[c].to_numpy(dtype=bool) for c in ["hot", "dh", "hh_tech", "hard", "generic"]}

# ------------------------------------------------------------------ v2 model (vectorised over samples)
DEFAULT = dict(cover="B", beh=1, tech="deep", infra="enab", ccs=1,
               g=G_CENTRAL, tau=0.7, hh_scale=1.0, kappa=1.0, beta=1.0, lam_h=1.0, lam_o=1.0,
               k=None, t0_shift=0.0, v=0.0, rho=0.0, omega=1.0, ccs_delay=0.0,
               group=None)

def model(years, n=1, **kw):
    """Return emissions (n, len(years)) in t/cap and per-category 2050 array (n, NC) in kg."""
    p = {**DEFAULT, **kw}
    def arr(x):
        a = np.asarray(x, dtype=float)
        return a.reshape(-1, 1) if a.ndim == 1 else np.full((n, 1), float(a))
    g, tau, hh, kap, beta = arr(p["g"]), arr(p["tau"]), arr(p["hh_scale"]), arr(p["kappa"]), arr(p["beta"])
    lam_h, lam_o, t0s, v, rho, om = (arr(p[x]) for x in ["lam_h", "lam_o", "t0_shift", "v", "rho", "omega"])
    cd = arr(p["ccs_delay"])
    kk = np.broadcast_to(C["k"], (n, NC)) if p["k"] is None else np.broadcast_to(arr(p["k"]), (n, NC))
    covered = np.ones(NC, bool) if p["cover"] == "B" else MASK["hot"]
    # behavioural adoption ceilings
    Lb = C["L"] * np.where(MASK["hard"], lam_h, lam_o)
    if p["infra"] == "cur":
        Lb = np.minimum(Lb, L_CURRENT_CAP)
    Lb = np.clip(Lb, 0, 1)
    Rb = np.clip(C["Rb"] * beta, 0, 1) * (covered & bool(p["beh"]))
    # technological potentials (deep), with household-technology ceilings following infrastructure
    Rt = np.where(MASK["generic"], tau, C["Rt"])
    Rt = np.where(MASK["hh_tech"], np.clip(C["Rt"] * hh, 0, 1), Rt)
    Rt = np.where(MASK["dh"], kap * bool(p["ccs"]), Rt)
    deep = covered & (p["tech"] == "deep")
    deep_mat = np.broadcast_to(deep | MASK["dh"], (n, NC)) & np.broadcast_to(~MASK["dh"] | bool(p["ccs"]), (n, NC))
    Lt = np.where(MASK["hh_tech"], np.minimum(C["L"], L_CURRENT_CAP) if p["infra"] == "cur" else C["L"], 1.0)
    Lt = np.where(MASK["dh"], C["L"], Lt)
    Lt = np.broadcast_to(Lt, (n, NC))
    t0 = C["t0"] + t0s
    t0_t = np.where(MASK["dh"], C["t0"] + cd, t0)
    res, cat2050 = [], None
    grp = p["group"]
    for y in years:
        Ab = Lb / (1 + np.exp(-kk * (y - t0)))
        At = Lt / (1 + np.exp(-np.where(MASK["dh"], C["k"], kk) * (y - t0_t)))
        f = (1 - g) ** (y - REF_YEAR)
        Itech = np.where(deep_mat, np.minimum(f, 1 - At * Rt), f)
        B = 1 - Ab * Rb
        if grp is not None:
            # two-group population: share pH with emission multiplier mH; adoption shortfall in one group
            pH, mH, who, short = grp
            mC = (1 - pH * mH) / (1 - pH)
            sH = 1 - short if who == "H" else 1.0
            sC = 1 - short if who == "C" else 1.0
            BH = 1 - sH * Ab * Rb; BC = 1 - sC * Ab * Rb
            AtH = np.where(MASK["hh_tech"], sH * At, At); AtC = np.where(MASK["hh_tech"], sC * At, At)
            IH = np.where(deep_mat, np.minimum(f, 1 - AtH * Rt), f); IC = np.where(deep_mat, np.minimum(f, 1 - AtC * Rt), f)
            RtOn = np.where(deep_mat, Rt, 0)
            ovH = (np.minimum(sH * Ab, AtH) - sH * Ab * AtH) * Rb * RtOn
            ovC = (np.minimum(sC * Ab, AtC) - sC * Ab * AtC) * Rb * RtOn
            Ec = C["E0"] * (pH * mH * (BH * IH + om * ovH) + (1 - pH) * mC * (BC * IC + om * ovC))
        else:
            Ec = C["E0"] * B * Itech
            # adoption-overlap correction (omega=1: same households adopt both = original v1 logic)
            tech_on = deep_mat
            ov = (np.minimum(Ab, At) - Ab * At) * Rb * np.where(tech_on, Rt, 0)
            Ec = Ec + om * C["E0"] * ov
        vol = (1 + v) ** (y - REF_YEAR)
        Ec = Ec * vol
        tot = Ec.sum(1, keepdims=True)
        # re-spending of money saved through behavioural change at the residual average intensity
        M = np.nan_to_num(C["M0"]); has = ~np.isnan(C["M0"])
        saved = (M * Ab * Rb * vol * has).sum(1, keepdims=True)
        resid_M = (M * (1 - Ab * Rb) * vol * has).sum(1, keepdims=True)
        resid_E = (Ec * has).sum(1, keepdims=True)
        tot = tot + rho * saved * resid_E / resid_M
        res.append(tot[:, 0] / 1000)
        if y == 2050:
            cat2050 = Ec
    return np.array(res).T, cat2050

def run(years=YEARS, **kw):
    e, c = model(years, n=1, **kw)
    return e[0], c[0]

def at(e, y):
    return float(e[list(YEARS).index(y)])

# ------------------------------------------------------------------ named scenarios
NAMED = {
    "N0": ("Reference (current trends)", dict(beh=0, tech="ref", ccs=0, infra="cur")),
    "N1": ("Hotspot, full depth", dict(cover="H", beh=1, tech="deep", infra="cur", ccs=1)),
    "N2": ("Lifestyle only", dict(cover="B", beh=1, tech="ref", infra="cur", ccs=0)),
    "N3": ("Lifestyle + infrastructure", dict(cover="B", beh=1, tech="ref", infra="enab", ccs=0)),
    "N4": ("Technology only", dict(cover="B", beh=0, tech="deep", infra="enab", ccs=1)),
    "N5": ("Coordinated", dict(cover="B", beh=1, tech="deep", infra="enab", ccs=1)),
}
rows, paths = [], {}
for k_, (lab, cfg) in NAMED.items():
    e, c = run(**cfg); paths[k_] = e
    for g_ in [0.0, G_CENTRAL, 0.03]:
        e2, _ = run(**{**cfg, "g": g_})
        rows.append(dict(id=k_, scenario=lab, g=g_, e2030=at(e2, 2030), e2050=at(e2, 2050),
                         gap2030=at(e2, 2030) - T2030, gap2050=at(e2, 2050) - T2050,
                         gap2030_strict=at(e2, 2030) - 2.5, gap2050_strict=at(e2, 2050) - 0.7))
named = pd.DataFrame(rows); named.to_csv(OUT / "named_scenarios.csv", index=False)
pd.DataFrame({"year": YEARS, **{k_: v_ for k_, v_ in paths.items()}, "target": target(YEARS)}).to_csv(
    OUT / "named_pathways.csv", index=False)

# ------------------------------------------------------------------ factorial and Shapley
players = ["Coverage", "Behaviour", "Technology", "Infrastructure", "CCS"]
def cfg_from(S):
    return dict(cover="B" if "Coverage" in S else "H", beh=int("Behaviour" in S),
                tech="deep" if "Technology" in S else "ref", infra="enab" if "Infrastructure" in S else "cur",
                ccs=int("CCS" in S))
fact = {}
for r in range(6):
    for S in itertools.combinations(players, r):
        e, _ = run(**cfg_from(S)); fact[frozenset(S)] = e
pd.DataFrame([dict(**{p_: int(p_ in S) for p_ in players}, e2030=at(e, 2030), e2050=at(e, 2050))
              for S, e in fact.items()]).to_csv(OUT / "factorial_32.csv", index=False)
def shapley(year):
    full = frozenset(players); nP = len(players); out = {}
    for p_ in players:
        val = 0.0
        others = [q for q in players if q != p_]
        for r in range(nP):
            for S in itertools.combinations(others, r):
                S = frozenset(S)
                w = math.factorial(len(S)) * math.factorial(nP - len(S) - 1) / math.factorial(nP)
                val += w * (at(fact[S], year) - at(fact[S | {p_}], year))
        out[p_] = val
    return out
sh = pd.DataFrame({y: shapley(y) for y in [2030, 2050]})
sh.loc["Total"] = sh.sum()
sh["start_2050"] = at(fact[frozenset()], 2050); sh["end_2050"] = at(fact[frozenset(players)], 2050)
sh.to_csv(OUT / "shapley.csv")

# ------------------------------------------------------------------ hotspot ceiling metric
srt = cat.sort_values("E0", ascending=False).reset_index(drop=True)
cum = srt.E0.cumsum() / E0_TOTAL
need_full = int((cum >= (E0_TOTAL / 1000 - T2050) / (E0_TOTAL / 1000)).idxmax() + 1)
Rfull = 1 - (1 - srt.Rb) * (1 - np.where(srt.dh, 1.0, srt.Rt))
cumred = (srt.E0 * Rfull).cumsum()
need_depth = int((cumred >= E0_TOTAL - 1000 * T2050).idxmax() + 1) if (cumred >= E0_TOTAL - 1000 * T2050).any() else None
hot_share = cat.loc[cat.hot, "E0"].sum() / E0_TOTAL
f2050 = (1 - G_CENTRAL) ** (2050 - REF_YEAR)
ceiling = dict(hot_share=hot_share, hot_floor_t=(1 - hot_share) * E0_TOTAL / 1000,
               hot_floor_with_reference_trend_t=(1 - hot_share) * E0_TOTAL / 1000 * f2050,
               required_coverage=(E0_TOTAL / 1000 - T2050) / (E0_TOTAL / 1000),
               n_categories_full_removal=need_full, n_categories_at_s4_depth=need_depth,
               max_reduction_all_at_s4_depth_t=float(cumred.iloc[-1] / 1000))
json.dump(ceiling, open(OUT / "hotspot_ceiling.json", "w"), indent=2)
srt.assign(cum_share=cum).to_csv(OUT / "cumulative_coverage.csv", index=False)

# ------------------------------------------------------------------ OAT (v2 coordinated) incl. new tests
oat_specs = {
    "Central coordinated": {},
    "Autonomous trend 0%/yr": dict(g=0.0), "Autonomous trend 3%/yr": dict(g=0.03),
    "Generic technology 50%": dict(tau=0.5), "Generic technology 90%": dict(tau=0.9),
    "No CCS in district heating": dict(ccs=0), "Partial CCS (50%)": dict(kappa=0.5), "CCS 5 years later": dict(ccs_delay=5),
    "Hard-to-change ceilings -25%": dict(lam_h=0.75), "Hard-to-change ceilings -50%": dict(lam_h=0.5),
    "Behavioural potentials -50%": dict(beta=0.5),
    "Adoption speed k=0.1": dict(k=0.1), "Adoption 5 years later": dict(t0_shift=5), "Adoption 2 years earlier": dict(t0_shift=-2),
    "Volume growth +1%/yr": dict(v=0.01), "Volume decline -0.5%/yr": dict(v=-0.005),
    "Re-spending 25%": dict(rho=0.25), "Re-spending 50%": dict(rho=0.5),
    "Independent adoption (no overlap)": dict(omega=0.0),
    "Joint adverse: tech 50%, ceilings -25%, CCS 50%": dict(tau=0.5, lam_h=0.75, kappa=0.5),
}
oat = []
for lab, kw in oat_specs.items():
    e, _ = run(**kw); oat.append(dict(test=lab, e2030=at(e, 2030), e2050=at(e, 2050)))
oat = pd.DataFrame(oat); b = oat.iloc[0]
oat["d2030"] = oat.e2030 - b.e2030; oat["d2050"] = oat.e2050 - b.e2050
oat["gap2030"] = oat.e2030 - T2030; oat["gap2050"] = oat.e2050 - T2050
oat.to_csv(OUT / "oat_v2.csv", index=False)

# ------------------------------------------------------------------ equity: two-group adoption
eq = []
for mH in [1.25, 1.5, 2.0]:
    for who in ["H", "C"]:
        e, _ = run(group=(0.4, mH, who, 0.25))
        eq.append(dict(mH=mH, shortfall_in=who, e2030=at(e, 2030), e2050=at(e, 2050)))
e_eq0, _ = run(group=(0.4, 1.5, "H", 0.0))
eq = pd.DataFrame(eq); eq["e2050_uniform"] = at(e_eq0, 2050); eq.to_csv(OUT / "equity_two_group.csv", index=False)

# ------------------------------------------------------------------ global sensitivity (Sobol, Saltelli/Jansen)
SA = {  # name: (low, high, rationale)
    "g": (0.0, 0.03, "autonomous intensity decline per year"),
    "tau": (0.4, 0.9, "generic supply-side intensity cut by 2050"),
    "hh_scale": (0.8, 1.0, "household technology (EV, heating) potential"),
    "kappa": (0.0, 0.95, "CCS capture in district heating"),
    "beta": (0.5, 1.0, "behavioural potentials, share of central"),
    "lam_h": (0.5, 1.0, "hard-to-change adoption ceilings"),
    "lam_o": (0.75, 1.0, "other adoption ceilings"),
    "k": (0.1, 0.4, "adoption speed"),
    "t0_shift": (-2.0, 5.0, "adoption timing shift, years"),
    "v": (-0.005, 0.01, "consumption volume growth per year"),
    "rho": (0.0, 0.5, "re-spending of behavioural savings"),
    "omega": (0.0, 1.0, "adoption overlap (0 independent, 1 nested)"),
}
names = list(SA); D = len(names); N = 16384
lo = np.array([SA[n_][0] for n_ in names]); hi = np.array([SA[n_][1] for n_ in names])
Amat = lo + RNG.random((N, D)) * (hi - lo); Bmat = lo + RNG.random((N, D)) * (hi - lo)
def evaluate(X):
    kw = {n_: X[:, i] for i, n_ in enumerate(names)}
    e, _ = model([2030, 2050], n=X.shape[0], **kw)
    return e
fA = evaluate(Amat); fB = evaluate(Bmat)
S1, ST = {}, {}
for i, n_ in enumerate(names):
    ABi = Amat.copy(); ABi[:, i] = Bmat[:, i]; fABi = evaluate(ABi)
    for j, y in enumerate([2030, 2050]):
        var = np.var(np.r_[fA[:, j], fB[:, j]])
        S1[(n_, y)] = np.mean(fB[:, j] * (fABi[:, j] - fA[:, j])) / var
        ST[(n_, y)] = 0.5 * np.mean((fA[:, j] - fABi[:, j]) ** 2) / var
sob = pd.DataFrame([dict(param=n_, description=SA[n_][2], low=SA[n_][0], high=SA[n_][1],
                         S1_2030=S1[(n_, 2030)], ST_2030=ST[(n_, 2030)], S1_2050=S1[(n_, 2050)], ST_2050=ST[(n_, 2050)])
                    for n_ in names]).sort_values("ST_2050", ascending=False)
sob.to_csv(OUT / "sobol.csv", index=False)
mc = pd.DataFrame(np.c_[Amat, fA], columns=names + ["e2030", "e2050"]); mc.to_csv(OUT / "mc_samples.csv", index=False)
mcs = dict(n=N, p05_2050=float(np.percentile(fA[:, 1], 5)), median_2050=float(np.median(fA[:, 1])),
           p95_2050=float(np.percentile(fA[:, 1], 95)), share_2050_le_target=float((fA[:, 1] <= T2050).mean()),
           share_2050_le_strict=float((fA[:, 1] <= 0.7).mean()),
           p05_2030=float(np.percentile(fA[:, 0], 5)), median_2030=float(np.median(fA[:, 0])),
           p95_2030=float(np.percentile(fA[:, 0], 95)), share_2030_le_target=float((fA[:, 0] <= T2030).mean()),
           sum_S1_2050=float(sob.S1_2050.sum()))
json.dump(mcs, open(OUT / "mc_summary.json", "w"), indent=2)

# ------------------------------------------------------------------ frontier
taus = np.linspace(0.3, 0.95, 27); lams = np.linspace(0.4, 1.0, 25)
TT, LL = np.meshgrid(taus, lams)
fr = {}
for ccs_ in [1, 0]:
    e, _ = model([2050], n=TT.size, tau=TT.ravel(), lam_h=LL.ravel(), ccs=ccs_)
    fr[ccs_] = e[:, 0].reshape(TT.shape)
np.savez(OUT / "frontier.npz", taus=taus, lams=lams, ccs_on=fr[1], ccs_off=fr[0])

# ------------------------------------------------------------------ technology thresholds for the 2050 target
tgrid = np.linspace(0.5, 1.0, 501); thr = {}
for lab_, kw_ in [("coordinated_ccs", dict()), ("coordinated_no_ccs", dict(ccs=0)),
                  ("no_behaviour_ccs", dict(beh=0)), ("no_behaviour_no_ccs", dict(beh=0, ccs=0))]:
    e_, _ = model([2050], n=len(tgrid), tau=tgrid, **kw_)
    ok_ = tgrid[e_[:, 0] <= T2050]
    thr[lab_] = float(ok_.min()) if len(ok_) else None
json.dump(thr, open(OUT / "technology_thresholds.json", "w"), indent=2)

# ------------------------------------------------------------------ domain contributions (coordinated 2050)
e5, c5 = run(**NAMED["N5"][1]); e0, c0 = run(**NAMED["N0"][1])
dom = pd.DataFrame({"domain": cat.domain, "baseline": C["E0"], "reference_2050": c0, "coordinated_2050": c5})
dom = dom.groupby("domain").sum() / 1000
dom["reduction_vs_baseline"] = dom.baseline - dom.coordinated_2050
dom["reduction_vs_reference"] = dom.reference_2050 - dom.coordinated_2050
dom.sort_values("reduction_vs_baseline", ascending=False).to_csv(OUT / "domain_contributions_v2.csv")

print("v1 validation\n", v1_tab.round(2))
print(named[named.g == G_CENTRAL].round(2).to_string(index=False))
print(named[named.id == "N5"].round(2).to_string(index=False))
print("Shapley\n", sh.round(2))
print("ceiling", {k_: (round(v_, 3) if isinstance(v_, float) else v_) for k_, v_ in ceiling.items()})
print(oat.round(2).to_string(index=False))
print(eq.round(2).to_string(index=False))
print(sob.round(3).to_string(index=False))
print({k_: round(v_, 3) for k_, v_ in mcs.items()})
print(dom.round(2))
