# Supplementary tables of the submitted version

These files belong to the original submission of CLRC-D-26-00768. They are kept for comparison. The supplementary material of revision 1 is in `supplementary/`.

They are regenerated from the source workbook by:

```bash
python scripts/extract_clean_dataset_from_workbook.py      # writes Table A1 and the base Table A2
python scripts/build_activity_intensity_crosswalk.py       # adds six activity-intensity columns to Table A2
```

## Table A1: one-at-a-time sensitivity results (original model)

File: `table_a1_sensitivity_results.csv`

All 21 one-at-a-time variants for Scenario 4: variant identifier, description, parameter group, 2030 and 2050 emissions (t CO₂e per capita), change against base Scenario 4, and gap to target in both years. Same content as `data/sensitivity_results.csv`.

## Table A2: Scenario 4 category-level parameters

File: `table_a2_scenario4_parameters.csv`

The 109 active categories of Scenario 4: category, domain, baseline emissions (kg CO₂e per capita), behavioural, technological and combined reduction potentials, adoption ceiling (L), speed (k), inflection year (t₀), assumption note, activity metric and unit, baseline activity (M₀), baseline intensity (I₀), activity data source and confidence flag.

Note: six assumption notes in this table do not match the model parameters. Revision 1 corrects them (Supplementary Material A, Note S2). No model value changed.

## Other files

The COICOP crosswalk is in `data/coicop_activity_intensity_crosswalk.csv`. The full cleaned dataset of the submitted version is in `data/`.
