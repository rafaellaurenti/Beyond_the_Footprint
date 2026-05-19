# Supplementary material

**Beyond the Footprint: sufficiency, coordination and the limits of hotspot strategies in city climate governance**

Submitted to *Sustainable Production and Consumption*.

## Contents

### Table A1: Full sensitivity analysis results

File: `table_a1_sensitivity_results.csv`

Contains all 21 one-at-a-time sensitivity variants for Scenario 4, including: variant identifier, variant description, parameter group, 2030 and 2050 emissions (t CO₂e per capita), delta versus base Scenario 4, and gap to target for both years. See manuscript Section 3.9 for the sensitivity design and Section 4.5 for the interpretation.

### Table A2: Scenario 4 category-level parameters

File: `table_a2_scenario4_parameters.csv`

Contains all 109 active categories in the coordinated transition scenario (Scenario 4), with: category name, consumption domain, baseline emissions (kg CO₂e per capita per year), behavioural reduction potential, technological reduction potential, combined reduction potential (multiplicative), maximum adoption ceiling (*L*), adoption speed (*k*), inflection year (*t₀*) and assumption notes. See manuscript Section 3.7 for the combination logic and Section 3.8 for parameter sourcing.

### Additional data files

The full cleaned analytical dataset is in the `data/` directory and includes:

- `baseline_categories.csv`: all 111 categories with baseline emissions, domain mapping and category metadata
- `scenario_parameters.csv`: full parameterisation for all four scenarios (182 rows)
- `scenario_results.csv`: year-by-year scenario emissions (100 rows, 4 scenarios x 25 years)
- `category_results.csv`: year-by-year, category-level emissions for all scenarios
- `domain_reduction_contributions_s4.csv`: domain-level reduction contributions for Scenario 4
- `validation_summary.csv`: numerical validation of Python implementation against source workbook
- `translation_dictionary.csv`: Swedish-to-English translation of all category names, domain names and assumption notes

### Reproducibility

All tables can be regenerated from the source workbook using:

```bash
python scripts/extract_clean_dataset_from_workbook.py
```

All figures can be regenerated from the CSV data using:

```bash
python scripts/generate_figures.py
```

The Jupyter notebook in `notebooks/` provides an interactive walkthrough of the model, validation and figure production.
