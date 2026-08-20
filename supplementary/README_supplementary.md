# Supplementary material

**Beyond the Footprint: sufficiency, coordination and the limits of hotspot strategies in city climate governance**

## Contents

### Table A1: Full sensitivity analysis results

File: `table_a1_sensitivity_results.csv`

Contains all 21 one-at-a-time sensitivity variants for Scenario 4, including: variant identifier, variant description, parameter group, 2030 and 2050 emissions (t CO₂e per capita), delta versus base Scenario 4, and gap to target for both years. See manuscript Section 3.9 for the sensitivity design and Section 4.5 for the interpretation.

### Table A2: Scenario 4 category-level parameters

File: `table_a2_scenario4_parameters.csv`

Contains all 109 active categories in the coordinated transition scenario (Scenario 4), with: category ID, category name, consumption domain, baseline emissions (kg CO₂e per capita per year), behavioural reduction potential, technological reduction potential, combined reduction potential (multiplicative), maximum adoption ceiling (*L*), adoption speed (*k*), inflection year (*t₀*), assumption notes, and, added in this revision, activity metric, activity unit, baseline activity (*M₀*), baseline intensity (*I₀*), activity data source and a confidence flag (OK / LOW-CONF / SHARED / DIRECT / PHYSICAL / NOMATCH). See manuscript Section 3.6 for the combination logic, Section 3.7 for the urban-action mapping, and Section 3.8 for parameter sourcing and the activity-data limitations.

### Table A3: COICOP activity-intensity crosswalk

File: `coicop_activity_intensity_crosswalk.csv`

The full working table behind Table A2's new columns, covering all 111 baseline categories (the 109 active in Scenario 4 plus two inactive/placeholder categories carried for completeness): category ID, category, domain, baseline emissions, matched COICOP code(s), national per-capita expenditure (SEK, 2021), implied intensity (kg CO₂e per SEK), a confidence flag, and a note explaining the match (including which categories share a COICOP code and how the shared total was split). Included for reviewer scrutiny of the category-matching judgement calls; Table A2 carries the same information, restricted to the 109 active categories, in the format used in the main text.

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

All tables, including Table A1 and Table A2, can be regenerated from the source workbook using:

```bash
python scripts/extract_clean_dataset_from_workbook.py
```

Table A2's activity-intensity columns and the COICOP crosswalk (Table A3) additionally require:

```bash
python scripts/build_activity_intensity_crosswalk.py
```

run after the step above. See that script's docstring for the required source file.

All figures can be regenerated from the CSV data using:

```bash
python scripts/generate_figures.py
```

The Jupyter notebook in `notebooks/` provides an interactive walkthrough of the model, validation and figure production.
