# Beyond the footprint: the urban consumption gap and the limits of hotspot strategies in city climate governance

Reproducibility package for the article (manuscript CLRC-D-26-00768, revision 1, November 2026).

The package reproduces every number, table and figure in the revised manuscript and Supplementary Material A. The scripts are deterministic. The random seed of the sensitivity analysis is fixed (20261110). The full run takes under one minute on a laptop.

## Quick start

```bash
python -m pip install -r requirements.txt
./run_all.sh          # macOS, Linux or Git Bash
run_all.bat           # Windows Command Prompt or Anaconda Prompt
```

The run script runs four steps:

```bash
python scripts/revision_model.py data results        # model, factorial design, Shapley, sensitivity, frontier
python scripts/make_figures.py results figures        # Figures 1 to 7 (vector PDF and 600 dpi PNG)
python scripts/make_supplement.py . supplementary     # Supplementary Material A and Table A2
python scripts/check_run.py .                         # checks the run against the values in the manuscript
```

The last step prints one line per check and ends with "All checks passed". It stops with an error if any value differs from the manuscript.

Python 3.10 or later is required. The figures use the Inter typeface when it is installed and fall back to DejaVu Sans otherwise. Only the font changes; the numbers do not.

## Repository structure

```
Beyond_the_Footprint/
├── README.md
├── LICENSE                     MIT licence (code)
├── CITATION.cff
├── requirements.txt
├── run_all.sh                  reproduces revision 1 end to end (macOS, Linux)
├── run_all.bat                 the same for Windows
├── .gitignore
│
├── source/                     original data
│   ├── Scenario_analyzer_Malmo_february_2026_original.xlsx
│   └── Household_consumption_expenditure_ESA2010_current_prices_SEK_million_by_purpose_COICOP_and_year.xlsx
│
├── data/                       cleaned dataset (extracted from source/)
│   ├── baseline_categories.csv                 110 categories, 2022 footprint (Consumption Compass 2.0)
│   ├── scenario_parameters.csv                 reduction potentials and adoption parameters
│   ├── coicop_activity_intensity_crosswalk.csv baseline activity and implied intensity per category
│   ├── sensitivity_results.csv                 one-at-a-time tests of the submitted version
│   └── other CSVs of the submitted version     scenario and category results, summary, validation,
│                                               domain contributions, translation dictionary, notebook outputs
│
├── scripts/
│   ├── revision_model.py       revised lever-based model and all analyses (revision 1)
│   ├── make_figures.py         Figures 1 to 7 (revision 1)
│   ├── make_supplement.py      Supplementary Material A tables and notes (revision 1)
│   ├── check_run.py            checks a run against the manuscript values (revision 1)
│   ├── extract_clean_dataset_from_workbook.py   workbook to CSV extraction (submitted version)
│   ├── build_activity_intensity_crosswalk.py    COICOP crosswalk (submitted version)
│   └── generate_figures.py                      figures of the submitted version
│
├── results/                    outputs of revision_model.py
├── figures/                    Figures 1 to 7 of the revised manuscript
├── supplementary/              supplementary_R1.md and Table_A2_parameters_and_evidence.xlsx
├── notebooks/
│   └── malmo_consumption_gap_reproducible_model.ipynb   notebook of the submitted version
└── archive/
    ├── v1_figures/             figures of the submitted version
    └── v1_supplementary/       Tables A1 and A2 of the submitted version
```

The revision 1 scripts read only four files in `data/`: `baseline_categories.csv`, `scenario_parameters.csv`, `coicop_activity_intensity_crosswalk.csv` and `sensitivity_results.csv`.

## Submitted version

The notebook and the three scripts marked "submitted version" reproduce the four scenarios of the project report from the source workbook. Their model code is unchanged from the original submission. The only change is where they write output. Their figures go to `archive/v1_figures/` and their tables to `archive/v1_supplementary/`, so they never overwrite the revision 1 outputs.

```bash
python scripts/extract_clean_dataset_from_workbook.py   # workbook to data/ (validated against the workbook results)
python scripts/build_activity_intensity_crosswalk.py    # COICOP crosswalk (needs openpyxl)
python scripts/generate_figures.py                      # figures of the submitted version
```

The extraction reproduces the files in `data/` exactly, so running it before `run_all` does not change any revision 1 result. `generate_figures.py` also writes an interactive HTML figure if `plotly` is installed; otherwise it skips that figure.

To run the notebook, open `notebooks/malmo_consumption_gap_reproducible_model.ipynb` in Jupyter or VS Code and run all cells. It validates the model against the workbook (maximum difference below 10⁻¹⁵ t).

## What the revised model does

**Category emissions.** Each of the 110 categories has baseline emissions $E_{0,c}$. Behavioural change acts on activity, and technological change acts on intensity. Adoption of each change follows a logistic curve:

$$A_{c,y} = \frac{L_c}{1 + e^{-k_c (y - t_{0,c})}}$$

Category emissions are:

$$E_{c,y} = E_{0,c}\, v_y \left[ (1 - A^b R^b)\, I_{c,y} + \omega \left(\min(A^b, A^t) - A^b A^t\right) R^b R^t \right], \qquad I_{c,y} = \min\{ f_y,\ 1 - A^t R^t \}$$

Here $f_y = (1-g)^{y-2025}$ is the reference trend of autonomous supply-chain decarbonisation (central $g$ = 1.5% per year). $v_y$ is consumption-volume growth. $\omega = 1$ (nested adoption) is the central, conservative case. The main text shows the simpler form with $\omega = 0$ and $v_y = 1$ (Eq. 4); the full form is Eqs. S1 and S2 in Supplementary Note S4. The urban consumption gap is $G_{s,y} = E_{s,y} - T_y$, with targets of 3.1 t CO2e per capita in 2030 and 1.0 t in 2050.

**Five binary levers** form a 32-cell factorial design: coverage (nine hotspot categories or all categories), behaviour, technology (reference trend or deep supply-side decarbonisation), infrastructure (adoption ceilings capped at 75% or at coordinated values) and carbon capture in district heating. Six cells are named scenarios: reference, hotspot, lifestyle only, lifestyle + infrastructure, technology only and coordinated.

**Analyses**

- Shapley decomposition of the reduction by lever.
- Hotspot ceiling.
- One-at-a-time tests and a joint adverse case.
- Variance-based global sensitivity analysis: twelve parameters, Saltelli design, Jansen estimators, 16,384 base samples.
- Target-consistency frontier and technology thresholds.
- Re-spending and volume tests for rebound.
- A two-group equity test.

**Validation.** Run with the original specification, the revised model reproduces the four project scenarios exactly. The values are 5.74/5.74, 5.25/4.10, 4.37/3.01 and 3.20/1.06 t in 2030/2050 (`results/v1_validation.csv`). `check_run.py` tests these values and the headline results.

## Outputs and where they appear

| File in `results/` | Used in |
|---|---|
| `named_scenarios.csv`, `named_pathways.csv` | Table 3, Fig. 3 |
| `factorial_32.csv`, `shapley.csv` | Fig. 4, Table A4 |
| `cumulative_coverage.csv`, `hotspot_ceiling.json` | Section 4.1, Fig. 2 |
| `domain_contributions_v2.csv` | Fig. 5 |
| `oat_v2.csv` | Table 4, Table A1 |
| `mc_summary.json`, `sobol.csv`, `mc_samples.csv` (regenerated, not tracked) | Section 4.3, Fig. 6 |
| `frontier.npz`, `technology_thresholds.json` | Fig. 7, Sections 4.3 and 5.1 |
| `equity_two_group.csv` | Sections 4.3 and 5.5 |
| `category_inputs_v2.csv`, `v1_validation.csv` | Supplementary Tables A2 and A4 |

## Figures

The figures use the RISE colour scheme. They are sized for Elsevier column widths: 90 mm, 140 mm and 190 mm.

| Figure | Content |
|---|---|
| Fig. 1 | The urban consumption gap as the residual after feasible action (schematic) |
| Fig. 2 | Twenty largest categories and the hotspot ceiling |
| Fig. 3 | Scenario pathways and Malmö's target pathway |
| Fig. 4 | Shapley decomposition by lever, coloured by municipal reach |
| Fig. 5 | Domain contributions to the 2050 reduction |
| Fig. 6 | Global sensitivity analysis: output distributions and Sobol indices |
| Fig. 7 | Target-consistency frontier |

## Data sources

- **Consumption Compass 2.0.** Category-level household footprints for Swedish municipalities. Dawkins et al. (2024), *Sustainable Production and Consumption* 52, 63–79, https://doi.org/10.1016/j.spc.2024.10.013.
- **Scenario Analyzer workbook.** Developed in the RISE and City of Malmö project (August to December 2025). It is documented in Vejbrink et al. (2026), RISE Rapport 2026:42.
- **Statistics Sweden (2022).** Household consumption expenditure (ESA2010) by purpose, COICOP, 1980–2021, table 000000SG.
- **Larsson et al. (2018).** Air travel distance of Swedish residents. *Environmental Impact Assessment Review* 72, 137–144, https://doi.org/10.1016/j.eiar.2018.05.013.

The baseline emissions derive from the Consumption Compass. Reuse of those values is subject to the terms of the Stockholm Environment Institute.

## Licence

The code is released under the MIT Licence. See [LICENSE](LICENSE).

## Citation

Please cite the article and this repository (see `CITATION.cff`).
