# Beyond the Footprint: sufficiency, coordination and the limits of hotspot strategies in city climate governance

**Reproducibility package for the article submitted to *Sustainable Production and Consumption*.**

This repository provides the data, code and figures needed to reproduce the scenario model, sensitivity analysis and manuscript figures for the Malmö urban consumption gap study.

## Citation

> [Authors], 2026. Beyond the Footprint: sufficiency, coordination and the limits of hotspot strategies in city climate governance. *Sustainable Production and Consumption* [submitted].

## Repository structure

```
malmo-consumption-gap/
├── README.md                  ← this file
├── LICENSE                    ← MIT licence
├── requirements.txt           ← Python dependencies
├── .gitignore
│
├── source/                    ← original data
│   └── Scenario_analyzer_Malmo_february_2026_original.xlsx
│
├── data/                      ← cleaned analytical dataset (CSV)
│   ├── baseline_categories.csv
│   ├── category_domain_mapping.csv
│   ├── scenario_parameters.csv
│   ├── scenario_results.csv
│   ├── category_results.csv
│   ├── scenario_summary.csv
│   ├── sensitivity_results.csv
│   ├── domain_reduction_contributions_s4.csv
│   ├── translation_dictionary.csv
│   └── validation_summary.csv
│
├── scripts/
│   ├── extract_clean_dataset_from_workbook.py   ← workbook → CSV extraction
│   └── generate_figures.py                      ← all manuscript figures
│
├── notebooks/
│   └── malmo_consumption_gap_reproducible_model.ipynb
│
├── figures/                   ← generated figures (PNG 300 DPI + PDF)
│   ├── fig1_urban_consumption_gap_framework.{png,pdf}
│   ├── fig2_baseline_footprint_top_categories.{png,pdf}
│   ├── fig3_scenario_pathways_targets.{png,pdf}
│   ├── fig4_domain_reduction_contributions_s4.{png,pdf}
│   ├── fig5_sensitivity_tornado_2050.{png,pdf}
│   └── supp_coverage_vs_residual_emissions.{png,pdf}
│
├── manuscript/
│   ├── Closing_the_urban_consumption_gap_revised_manuscript_v5.docx
│   └── manuscript_v5_source.md
│
└── supplementary/             ← extended parameter tables (forthcoming)
```

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Extract cleaned data from the source workbook

```bash
python scripts/extract_clean_dataset_from_workbook.py
```

This reads the original Excel Scenario Analyzer workbook and produces all CSV files in `data/`. The script uses a minimal XML-based reader (no Excel or LibreOffice needed) and validates its outputs against cached workbook results. Expected validation: max absolute difference < 10⁻¹⁴ t CO₂e per capita for all four scenarios.

### 3. Generate all figures

```bash
python scripts/generate_figures.py
```

This reads the CSV files in `data/` and produces all manuscript and supplementary figures in `figures/` (PNG at 300 DPI and vector PDF).

### 4. Explore the model interactively

Open the Jupyter notebook:

```bash
jupyter notebook notebooks/malmo_consumption_gap_reproducible_model.ipynb
```

The notebook loads the cleaned data, implements the model equations, recalculates all scenario pathways, validates against the extracted results and reproduces all figures interactively.

## Model overview

The model calculates consumption-based emissions for Malmö under four transition scenarios over 2026 to 2050. It combines:

- **Baseline**: 111 consumption categories covering 5,735 kg CO₂e per capita per year, derived from the SEI Consumption Compass v2.0 (Dawkins et al., 2024).
- **Target pathway**: 3.1 t CO₂e per capita in 2030; 1.0 t CO₂e per capita in 2050 (linearly interpolated between milestones).
- **Logistic adoption dynamics**: S-curve diffusion with category-specific maximum adoption (*L*), speed (*k*) and inflection year (*t₀*).
- **Multiplicative reduction combination**: behavioural and technological potentials combined as *R* = 1 − (1 − *R_tech*)(1 − *R_beh*) to avoid double counting.
- **Sensitivity analysis**: one-at-a-time variation of adoption ceilings, technology assumptions, CCS, food-system parameters, aviation and adoption timing.

### Scenarios

| Scenario | Transition logic | Active categories | Baseline coverage |
|----------|-----------------|-------------------|-------------------|
| S1 | Limited change | 0 active | 0% |
| S2 | Hotspot focus | 9 active | 45% |
| S3 | Lifestyle-centred | 31 active | 71% |
| S4 | Coordinated transition | 109 active | 99.8% |

### Key equations

**Adoption** (logistic S-curve):

*A_c(y) = L_c / [1 + exp(−k_c · (y − t₀_c))]*

**Combined reduction** (multiplicative):

*R_c = 1 − (1 − R_c,tech) · (1 − R_c,beh)*

**Effective reduction in year *y***:

*r_c(y) = R_c · A_c(y)*

**Category emissions**:

*E_c(y) = E₀_c · [1 − r_c(y)]*

**Urban consumption gap**:

*G_s(y) = E_s(y) − T(y)*

## Data sources

- **Consumption Compass v2.0** (Dawkins, E., Rahmati-Abkenar, M., Axelsson, K., Grah, R., Broekhoff, D., 2024): baseline household consumption-based emissions for Swedish municipalities at COICOP category level. Available at https://live.konsumtionskompassen.se
- **Scenario Analyzer workbook**: developed in the RISE-Malmö Stad collaboration (August-December 2025), containing baseline data, scenario parameters, adoption dynamics and sensitivity test configurations.

## Figures

| Figure | Description |
|--------|-------------|
| Fig. 1 | Conceptual definition of the urban consumption gap |
| Fig. 2 | Malmö baseline consumption footprint: top 25 categories |
| Fig. 3 | Scenario pathways compared with Malmö's 2030 and 2050 targets |
| Fig. 4 | Domain contributions to reductions in the coordinated transition |
| Fig. 5 | Sensitivity of 2050 emissions to key assumptions (tornado chart) |
| Supp.  | Scenario coverage vs residual emissions |

## Licence

This repository is licensed under the MIT Licence. See [LICENSE](LICENSE).

## Contact

*[To be completed by the authors.]*
