"""Check that a run reproduces the values reported in the revised manuscript (CLRC-D-26-00768, R1).

Usage: python scripts/check_run.py [repo_dir]
Exits with code 1 if any check fails.
"""
import sys, json
from pathlib import Path
import pandas as pd

W = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
R = W / "results"
fails = []

def check(label, value, expected, tol):
    ok = abs(value - expected) <= tol
    print(f"{'OK  ' if ok else 'FAIL'}  {label}: {value:.3f} (expected {expected} ± {tol})")
    if not ok:
        fails.append(label)

# 1. The original four project scenarios are reproduced exactly (Supplementary Table A4a).
v1 = pd.read_csv(R / "v1_validation.csv", index_col=0)
for sid, e30, e50 in [("S1", 5.74, 5.74), ("S2", 5.25, 4.10), ("S3", 4.37, 3.01), ("S4", 3.20, 1.06)]:
    check(f"Original {sid}, 2030", v1.loc[sid, "2030"], e30, 0.005)
    check(f"Original {sid}, 2050", v1.loc[sid, "2050"], e50, 0.005)

# 2. Named scenarios at the central reference trend (Table 3).
named = pd.read_csv(R / "named_scenarios.csv")
central = named[named.g.round(4) == 0.015].set_index("id")
for sid, label, e30, e50 in [("N0", "Reference", 5.3, 3.9), ("N1", "Hotspot, full depth", 4.4, 2.6),
                             ("N2", "Lifestyle only", 4.6, 2.9), ("N3", "Lifestyle + infrastructure", 4.4, 2.6),
                             ("N4", "Technology only", 3.5, 1.5), ("N5", "Coordinated", 3.2, 1.0)]:
    check(f"{label}, 2030", central.loc[sid, "e2030"], e30, 0.05)
    check(f"{label}, 2050", central.loc[sid, "e2050"], e50, 0.05)

# 3. Shapley decomposition, 2050 (Fig. 4).
sh = pd.read_csv(R / "shapley.csv", index_col=0)
for lever, val in [("Technology", 1.15), ("Coverage", 0.71), ("Behaviour", 0.63), ("CCS", 0.31), ("Infrastructure", 0.15)]:
    check(f"Shapley {lever}, 2050", sh.loc[lever, "2050"], val, 0.005)

# 4. Global sensitivity analysis (Section 4.3, Fig. 6).
mc = json.load(open(R / "mc_summary.json"))
check("Share of runs meeting 1.0 t in 2050", mc["share_2050_le_target"], 0.08, 0.005)
check("Median 2050 emissions", mc["median_2050"], 1.8, 0.05)
sob = pd.read_csv(R / "sobol.csv").set_index("param")
check("Total-order index, supply-side cut, 2050", sob.loc["tau", "ST_2050"], 0.80, 0.005)
check("Total-order index, adoption timing, 2030", sob.loc["t0_shift", "ST_2030"], 0.72, 0.005)

# 5. Hotspot ceiling (Section 4.1, Fig. 2).
ceil = json.load(open(R / "hotspot_ceiling.json"))
check("Hotspot share of baseline", ceil["hot_share"], 0.45, 0.005)
check("Categories needed at complete elimination", ceil["n_categories_full_removal"], 30, 0)
check("Categories needed at coordinated depth", ceil["n_categories_at_s4_depth"], 67, 0)

print()
if fails:
    print(f"{len(fails)} check(s) failed.")
    sys.exit(1)
print("All checks passed: the run reproduces the values in the revised manuscript.")
