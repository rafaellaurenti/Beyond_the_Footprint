---
title: "Supplementary Material A"
subtitle: "Beyond the footprint: the urban consumption gap and the limits of hotspot strategies in city climate governance (revision 1)"
---

This document contains six supplementary notes and four supplementary tables. All values can be regenerated with `revision_model.py` and `make_supplement.py` in the repository (https://github.com/rafaellaurenti/Beyond_the_Footprint).

# Note S1. Baseline, activity data and crosswalk

**Baseline.** The baseline is the 2022 personal consumption-based footprint of Malmö residents from the Consumption Compass 2.0 (Dawkins et al., 2024): 5,735 kg CO~2~e per capita over 110 categories with positive emissions. It covers household final consumption, including residents' consumption outside Malmö, and excludes public consumption, capital formation and visitors' consumption. Statistics Sweden calculates the national footprint with an environmentally extended input-output model (PRINCE; Fauré et al., 2019; Palm et al., 2019). The Consumption Compass downscales it to statistical areas with a hybrid approach: local data for categories such as direct vehicle emissions, building energy, diets and flight frequency, and expenditure or income proxies for the rest.

**Baseline by domain.** The table below gives the baseline by consumption domain.

| Domain | kg CO~2~e per capita | Share of baseline |
|---|---|---|
| Food and drink | 1,371 | 24% |
| Housing | 1,037 | 18% |
| Local transport | 911 | 16% |
| Other consumption | 910 | 16% |
| Flights | 850 | 15% |
| Leisure, sport and culture | 406 | 7% |
| Clothing and shoes | 250 | 4% |
| Total | 5,735 | 100% |

**Activity decomposition.** For interpretation only, we recovered activity levels from Statistics Sweden's national household expenditure by COICOP for 2021 (Statistics Sweden, 2022), matched at 4-digit level. Ten categories share a COICOP code with others; we split the shared total in proportion to baseline emissions. Four categories (4.3 kg, 0.08% of the baseline) have no counterpart. Direct emissions from vehicle use and heating are measured physically in the source data. Flights are anchored to national air-travel distance (5,800 km per capita, data from 2010 to 2013; Larsson et al., 2018), giving an implied intensity of 0.146 kg CO~2~e per passenger-km. Kamb and Larsson (2019) report 0.17 kg CO~2~e per passenger-km in 2017 including non-CO~2~ effects (0.09 kg CO~2~ only), with a decline of about 1.9% per year; projected to 2022 this gives about 0.155 kg. The flight emissions themselves come from the Consumption Compass, which uses Kamb and Larsson (2019) scaled with passenger-kilometre statistics for 2019 to 2023. The decomposition does not enter baseline emissions or scenario results except through the re-spending test (Note S4). Table A2b lists the activity data and confidence flags.

**Coverage of the activity data by type.** Direct COICOP match 3,449 kg (60%); low-confidence proxy 837 kg (15%); physical flight distance 850 kg (15%); direct physical emissions 468 kg (8%); shared codes 128 kg (2%); no match 4 kg (0.1%).

# Note S2. Evidence status of parameters and corrections

**Evidence codes (Table A2).** **C**: co-produced choice, made in workshops and working meetings with municipal staff and documented in the project report (Vejbrink et al., 2026). This applies to category coverage and scenario logic. **J**: project-team judgement, documented in the report without a specific source. This applies to behavioural potentials and to adoption ceilings, speeds and inflection years. **A**: author assumption, anchored where possible in literature or projections. This applies to technological potentials. No parameter was empirically calibrated or individually validated by municipal staff. The project report states that the team set reductions partly from what the targets required and partly from what seemed possible; the coordinated scenario is therefore a backcast.

**Corrections to assumption notes.** In the original Table A2, six notes did not match the parameters used in the model. We corrected the notes; no model value changed. (1) Meat: the note said 90% of residents cut meat by 80%, but the ceiling was 1.0. (2) Dairy: the note said 75% of residents cut by 75%, but the behavioural potential was 0.5 and the ceiling 1.0. (3) Clothing: the note said new purchases fall by 50%, but the behavioural potential was 0.75. (4) Cars: the note said each car keeps today's footprint, but a 70% technological potential applied. (5) Actual rent: the note said 75% of the population, but the ceiling was 1.0. (6) Fuels and lubricants: the note described electrification, which the parameters represented as a 90% behavioural and 90% technological potential. The original manuscript also stated that ceilings for hard-to-change categories sat below 1.0; in the coordinated scenario most were 1.0. The revised Table A2 replaces all notes with parameter-derived descriptions.

# Note S3. Combination of behavioural and technological reductions

Let a share $a_b$ of a category's population or stock adopt behavioural change (potential $R^b$) and a share $a_t$ adopt technological change (potential $R^t$). Let $o$ be the share that adopts both, with $\max(0, a_b + a_t - 1) \le o \le \min(a_b, a_t)$. Relative emissions are

$$e(o) = o(1-R^b)(1-R^t) + (a_b - o)(1-R^b) + (a_t - o)(1-R^t) + (1 - a_b - a_t + o) = 1 - a_b R^b - a_t R^t + o R^b R^t .$$

Because $\partial e/\partial o = R^b R^t \ge 0$, emissions increase with overlap. Nested adoption, $o = \min(a_b, a_t)$, gives the highest emissions and the smallest combined reduction. Independent adoption, $o = a_b a_t$, gives $e = (1 - a_b R^b)(1 - a_t R^t)$. With equal adoption shares $a$, nested adoption gives $e = 1 - a[1 - (1-R^b)(1-R^t)]$, the rule of the original project tool. That rule is therefore the conservative bound with respect to adoption correlation. At full adoption both cases converge to $(1-R^b)(1-R^t)$, which follows from emissions being activity times intensity. Correlation in magnitude, as opposed to adoption, can act in either direction; for example, consumers who cut meat may also buy lower-intensity products. The re-spending and volume tests (Table A1) cover the main anti-conservative channel, rebound.

# Note S4. Revised model specification

**Equations.** Adoption follows main text Eq. (3). The full emissions equation for category $c$ in year $y$ is

$$E_{c,y} = E_{0,c}\, v_y \left[ (1 - A^b_{c,y} R^b_c)\, I_{c,y} + \omega \left(\min(A^b_{c,y}, A^t_{c,y}) - A^b_{c,y} A^t_{c,y}\right) R^b_c R^t_c \right] \qquad \text{(S1)}$$

$$I_{c,y} = \min\left\{ f_y,\; 1 - A^t_{c,y} R^t_c \right\}, \qquad f_y = (1 - g)^{y - 2025}, \qquad v_y = (1 + v)^{y - 2025} \qquad \text{(S2)}$$

$A^b_{c,y}$ and $A^t_{c,y}$ are the behavioural and technological adoption shares from Eq. (3). The intensity factor $I_{c,y}$ cannot be worse than the reference trend $f_y$; categories without deep technological change follow $f_y$ alone. The term $v_y$ allows for growth or decline in consumption volume ($v$ = 0 in the central case). The overlap parameter $\omega$ sets how the two adoptions combine during diffusion: $\omega$ = 0 is independent adoption, and $\omega$ = 1 is nested adoption (Note S3). The central case uses $\omega$ = 1. Main text Eq. (4) is the special case $\omega$ = 0 and $v$ = 0. Years run from 2026 to 2050; the reference trend and volume factor start after 2025. Scenario emissions are the sum over categories.

**Behavioural adoption** uses the category's ceiling $L_c$, speed $k_c$ and inflection year $t_{0,c}$ from the coordinated scenario. Under current conditions, ceilings are capped at 0.75.

**Technological adoption.** Generic supply-side intensity cuts (70% in the coordinated scenario) do not depend on household adoption, so their ceiling is 1.0 with the category's speed and timing. Household technologies (direct vehicle emissions, vehicle fuels, direct heating emissions) use the category ceiling, capped at 0.75 under current conditions. District-heating CCS uses its own parameters (ceiling 0.95, k = 1.0, t~0~ = 2030). The original model applied each category's single ceiling to both behavioural and technological change. This made household ceilings limit supply-side decarbonisation, for example of flights and food production. It explains why a 25% cut in hard-to-change ceilings raised 2050 emissions by 0.64 t in the original model and by 0.11 t in the revised model.

**Hotspot set** (nine categories, 45% of the baseline): passenger flights; district heating; direct emissions from vehicle use; meat; dairy and eggs; vehicle fuels and lubricants; cars; direct emissions from heating; company-car benefit.

**Hard-to-change set:** passenger flights; package holidays; meat; dairy and eggs; cars; imputed rent for owned dwellings; actual rent; clothing; footwear.

**Reference trend:** $f_y = (1-g)^{y-2025}$, $g$ = 1.5% per year (0% and 3% tested). In cells with deep technology, the intensity factor is the lower of the reference trend and the deep-technology factor.

**Re-spending:** money saved through behavioural change equals $\sum_c M_{0,c} v_y A^b_{c,y} R^b_c$ (flights at 1 SEK per passenger-km). A share $\rho$ is re-spent at the residual average intensity of the basket in that year.

**Two-group test:** a high-footprint group (share 0.4, footprint multiplier m = 1.25, 1.5 or 2) and a lower-footprint group (multiplier (1 - 0.4m)/0.6). Category composition is proportional. A 25% shortfall reduces behavioural adoption and household-technology adoption in one group.

**Shapley values:** computed exactly over the 32 cells (Table A4b), with the low level of each lever as the starting point. The all-low cell equals the reference.

**Global sensitivity analysis:** 16,384 base samples, Saltelli design, Jansen estimators for first-order and total-order indices (Saltelli et al., 2010). Ranges in Table A3. Summary: median 2050 emissions 1.83 t (5th to 95th percentile 0.91 to 2.87); 8.1% of runs at or below 1.0 t; 0.7% at or below 0.7 t. Median 2030 emissions 3.86 t; 10.9% at or below 3.1 t. The sum of first-order indices for 2050 is 1.04; values slightly above 1 reflect sampling error.

**Technology thresholds:** the smallest generic supply-side cut that meets 1.0 t in 2050 is 70% in the coordinated scenario with CCS and 80% without CCS. Without behavioural change it is 82% with CCS and 89% without CCS (`technology_thresholds.json`).

**Validation:** with the original specification, the code reproduces the original scenario results exactly (Table A4a).

# Note S5. Worked example: meat in the coordinated scenario

Baseline 289.9 kg CO~2~e per capita; $R^b$ = 0.80, $R^t$ = 0.70, $L$ = 1.0, $k$ = 0.2, $t_0$ = 2029; nested adoption ($\omega$ = 1); $g$ = 1.5% per year.

| Year | Adoption A | Reference factor f | Intensity factor I | Behaviour factor | Overlap term | Emissions (kg) |
|---|---|---|---|---|---|---|
| 2030 | 0.550 | 0.927 | 0.615 | 0.560 | 0.139 | 140.1 |
| 2050 | 0.985 | 0.685 | 0.310 | 0.212 | 0.008 | 21.4 |

These values equal those of the original model (140 kg and 21 kg), because nested adoption with equal adoption shares reproduces the original rule.

# Note S6. Hotspot ceiling

If the hotspot set holds a share $h$ of the baseline $E_0$, a hotspot strategy cannot reduce emissions below $(1-h)E_0$ on a static baseline, or $(1-h)E_0 f_y$ with the reference trend. For Malmö, $h$ = 0.450, so the floor is 3.15 t (static) and 2.16 t in 2050 with the reference trend. The 2050 target requires a 82.6% cut. Addressing categories from largest to smallest, 30 categories are needed to cover this share at complete elimination, and 67 at coordinated-scenario depth with full adoption.

# Table A1. One-at-a-time tests of the coordinated scenario (revised model)

t CO~2~e per capita. Gaps against 3.1 t (2030) and 1.0 t (2050).

| Test | 2030 | 2050 | Change 2030 | Change 2050 | Gap 2030 | Gap 2050 |
|----------------------------------------|---|---|---|---|---|---|
| Central coordinated | 3.16 | 0.99 | +0.00 | +0.00 | +0.06 | -0.01 |
| Autonomous trend 0%/yr | 3.16 | 0.99 | +0.00 | +0.01 | +0.06 | -0.01 |
| Autonomous trend 3%/yr | 3.16 | 0.96 | -0.00 | -0.02 | +0.06 | -0.04 |
| Generic technology 50% | 3.47 | 1.54 | +0.31 | +0.55 | +0.37 | +0.54 |
| Generic technology 90% | 2.86 | 0.43 | -0.31 | -0.55 | -0.24 | -0.57 |
| No CCS in district heating | 3.34 | 1.27 | +0.18 | +0.29 | +0.24 | +0.27 |
| Partial CCS (50%) | 3.27 | 1.20 | +0.11 | +0.22 | +0.17 | +0.20 |
| CCS 5 years later | 3.34 | 0.99 | +0.18 | +0.00 | +0.24 | -0.01 |
| Hard-to-change ceilings -25% | 3.22 | 1.09 | +0.06 | +0.11 | +0.12 | +0.09 |
| Hard-to-change ceilings -50% | 3.27 | 1.20 | +0.11 | +0.21 | +0.17 | +0.20 |
| Behavioural potentials -50% | 3.31 | 1.26 | +0.15 | +0.27 | +0.21 | +0.26 |
| Adoption speed k=0.1 | 3.25 | 1.41 | +0.09 | +0.42 | +0.15 | +0.41 |
| Adoption 5 years later | 4.31 | 1.07 | +1.15 | +0.09 | +1.21 | +0.07 |
| Adoption 2 years earlier | 2.66 | 0.97 | -0.51 | -0.02 | -0.44 | -0.03 |
| Volume growth +1%/yr | 3.32 | 1.26 | +0.16 | +0.28 | +0.22 | +0.26 |
| Volume decline -0.5%/yr | 3.08 | 0.87 | -0.08 | -0.12 | -0.02 | -0.13 |
| Re-spending 25% | 3.27 | 1.06 | +0.11 | +0.07 | +0.17 | +0.06 |
| Re-spending 50% | 3.37 | 1.13 | +0.21 | +0.14 | +0.27 | +0.13 |
| Independent adoption (no overlap) | 2.82 | 0.97 | -0.34 | -0.02 | -0.28 | -0.03 |
| Joint adverse: tech 50%, ceilings -25%, CCS 50% | 3.67 | 1.93 | +0.51 | +0.94 | +0.57 | +0.93 |

**Table A1b.** Original one-at-a-time tests (original model, as submitted), retained for comparison.

| Variant (original model) | 2030 | 2050 | Change 2050 |
|---|---|---|---|
| Base Scenario 4 | 3.20 | 1.06 | +0.00 |
| All adoption 5 years earlier | 1.91 | 1.03 | -0.03 |
| All adoption 2 years earlier | 2.54 | 1.04 | -0.02 |
| All adoption 2 years later | 3.88 | 1.09 | +0.02 |
| All adoption 5 years later | 4.57 | 1.15 | +0.09 |
| Slow adoption speed k=0.1 | 3.29 | 1.48 | +0.42 |
| Adoption speed k=0.2 | 3.20 | 1.07 | +0.01 |
| Adoption speed k=0.3 | 3.11 | 1.02 | -0.04 |
| Fast adoption speed k=0.4 | 3.03 | 1.01 | -0.05 |
| Hard-to-change maximum adoption reduced by 25% | 3.55 | 1.70 | +0.64 |
| Hard-to-change maximum adoption reduced by 50% | 3.90 | 2.35 | +1.29 |
| Generic 70% technology reduction reduced to 50% | 3.49 | 1.59 | +0.53 |
| Generic 70% technology reduction increased to 90% | 2.91 | 0.53 | -0.53 |
| No CCS in heating | 3.44 | 1.54 | +0.48 |
| Partial CCS in heating | 3.32 | 1.30 | +0.24 |
| CCS delayed by 5 years | 3.45 | 1.06 | +0.00 |
| Lower aviation demand and technology improvement | 3.27 | 1.21 | +0.15 |
| Weaker food-system assumptions | 3.33 | 1.29 | +0.23 |
| Alternative 2030 target of 3.0 t | 3.20 | 1.06 | +0.00 |
| Dynamic baseline with 0.5% annual growth | 3.26 | 1.20 | +0.13 |
| Dynamic baseline with 0.5% annual decline | 3.14 | 0.94 | -0.12 |

# Table A2. Category-level parameters of the coordinated scenario with evidence status

R^b^ behavioural potential; R^t^ technological potential (district heating: CCS); L adoption ceiling; k speed; t~0~ inflection year. Evidence codes: C co-produced; J project-team judgement; A author assumption (Note S2). Technology codes: A-GEN generic supply-side cut of 70%, anchored in energy and agriculture projections cited in the project report, benchmarked against Cap et al. (2024) and tested from 40% to 90%; A-HH household technology switch (electric vehicles, fossil-free heating); A-CCS carbon capture in district heating, a sectoral expectation without a confirmed local plan, tested from 0% to 95%; A-CAT category-specific assumption. The file Table_A2_parameters_and_evidence.xlsx gives the same table with parameter-derived notes.

| Category | Baseline (kg) | R^b^ | R^t^ | L | k | t~0~ | Hot | Hard | Evidence (cov./beh./tech./adopt.) |
|--------------------|--------|-------|-------|-------|-----|--------|-----|-----|----------------|
| Flights - Passenger flights | 849.8 | 0.75 | 0.70 | 1.00 | 0.4 | 2030 | x | x | C / J / A-GEN / J |
| Housing - District heating and other energy for heating and cooling | 506.4 | 0.10 | 1.00 | 0.95 | 1.0 | 2030 | x |  | C / J / A-CCS / J |
| Local transport - Direct emissions from vehicle use | 410.0 | 0.00 | 1.00 | 1.00 | 0.2 | 2029 | x |  | C / - / A-HH / J |
| Food and drink - Meat | 289.9 | 0.80 | 0.70 | 1.00 | 0.2 | 2029 | x | x | C / J / A-GEN / J |
| Housing - Imputed rent for owned permanent dwelling | 240.1 | 0.25 | 0.70 | 0.75 | 0.2 | 2029 |  | x | C / J / A-GEN / J |
| Food and drink - Milk, cheese, other dairy products and eggs | 229.3 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 | x | x | C / J / A-GEN / J |
| Other consumption - Hotels, cafés and restaurants | 200.4 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Clothing and shoes - Clothing | 177.6 | 0.75 | 0.70 | 1.00 | 0.2 | 2029 |  | x | C / J / A-GEN / J |
| Food and drink - Vegetables, root crops and legumes | 145.0 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Fuels and lubricants | 124.9 | 0.90 | 0.90 | 1.00 | 0.2 | 2029 | x |  | C / J / A-HH / J |
| Housing - Actual rent for rented permanent dwelling | 124.8 | 0.25 | 0.25 | 1.00 | 0.2 | 2029 |  | x | C / J / A-CAT / J |
| Food and drink - Fruit and nuts | 122.8 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Package holidays | 121.6 | 0.75 | 0.70 | 1.00 | 0.2 | 2029 |  | x | C / J / A-GEN / J |
| Food and drink - Bread and cereal products | 104.7 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Cars | 104.2 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 | x | x | C / J / A-GEN / J |
| Food and drink - Sugar, confectionery and desserts | 102.6 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Other consumption - Furniture, furnishings and carpets | 93.9 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Other consumption - Information and communication equipment | 85.6 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Other consumption - Medicines | 85.3 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Food and drink - Ready-made meals and other food products | 83.5 | 0.50 | 0.70 | 0.75 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Local transport - Passenger transport by sea | 75.3 | 0.00 | 0.70 | 0.75 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Other appliances and products for personal care | 72.4 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Housing - Electricity | 57.2 | 0.25 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Food and drink - Fish and seafood | 56.7 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Garden products, plants and flowers | 56.0 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Housing - Direct emissions from heating | 50.5 | 0.00 | 0.95 | 1.00 | 0.2 | 2029 | x |  | C / - / A-HH / J |
| Clothing and shoes - Shoes and other footwear | 50.4 | 0.75 | 0.70 | 1.00 | 0.2 | 2029 |  | x | C / J / A-GEN / J |
| Other consumption - Information and communication services | 47.9 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Household appliances | 42.6 | 0.75 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Other consumption - Goods and services for household maintenance | 42.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Public transport and other combined trips | 41.2 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Food and drink - Wine | 39.4 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Leisure, sport and culture - Recreation and sport services | 38.7 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Games, toys and hobby articles | 38.3 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Food and drink - Oils and fats | 37.4 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Food and drink - Fruit and vegetable juices | 34.0 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Maintenance and repairs | 33.4 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Pets and pet products | 30.0 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Food and drink - Tobacco | 30.0 | 0.75 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Other consumption - Accommodation services | 29.1 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Major durable goods for leisure | 28.4 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Leisure, sport and culture - Games of chance, betting and lotteries | 26.8 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Glassware, tableware and other utensils | 26.5 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Food and drink - Soft drinks | 26.1 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Hairdressing salons and personal grooming establishments | 25.6 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Housing - Imputed rent for holiday homes, other dwellings, garages and storage | 24.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Road transport services: car pools, buses and taxis | 24.1 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Housing - Maintenance, repair and security | 23.6 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Equipment for sport, camping and outdoor recreation | 23.1 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Other consumption - Household textiles | 22.9 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Local transport - Spare parts and accessories | 21.6 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Home and garden tools | 20.1 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Food and drink - Coffee and coffee substitutes | 20.0 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Financial services | 19.7 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Company-car benefit | 18.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 | x |  | C / - / A-GEN / J |
| Clothing and shoes - Other garments and clothing accessories | 16.7 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Food and drink - Strong beer | 15.0 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Local transport - Rental of personal transport equipment | 15.0 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Other personal effects n.e.c. | 14.2 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Food and drink - Spirits | 13.0 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Local transport - Passenger transport by rail and tram | 12.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Jewellery and watches | 12.2 | 0.50 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / J / A-GEN / J |
| Local transport - Bicycles | 11.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Outpatient dental services | 10.1 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Other services | 9.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Medical aids and maintenance | 9.4 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Cultural services | 8.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Home care for older people and people with disabilities | 7.8 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Newspapers and periodicals | 7.7 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Books | 7.6 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Other outpatient care services | 7.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Housing - Direct household emissions | 7.1 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Food and drink - Low- and medium-strength beer | 6.6 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Parking services | 5.8 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Food and drink - Water | 5.7 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Writing and drawing materials | 5.6 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Residential care for older people and people with disabilities, excluding health care | 5.2 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Motorcycles | 5.1 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Insurance | 5.0 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Clothing and shoes - Clothing materials | 4.7 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Leisure goods: rental, maintenance and repair | 4.2 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Medical products | 4.1 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Food and drink - Narcotics | 3.8 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Electric appliances for personal care | 3.8 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Other transport of goods | 3.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Services for pets | 3.3 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Food and drink - Tea, maté and other herbal teas | 3.3 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Photographic and optical equipment | 3.1 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Education services | 2.8 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Housing - Actual rents for other dwellings, garages and storage | 2.8 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Software | 1.9 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Audiovisual media | 1.9 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Postal and courier services | 1.6 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Food and drink - Other alcoholic beverages | 1.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Driving lessons, driving licences and vehicle inspections | 1.4 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Musical instruments | 1.2 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Food and drink - Chocolate drinks | 0.9 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Inpatient curative and rehabilitative services | 0.8 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Road tolls | 0.8 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Childcare services | 0.7 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Local transport - Other passenger transport services | 0.6 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Preventive care services | 0.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Leisure, sport and culture - Miscellaneous printed matter | 0.5 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Religious and ritual articles | 0.4 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Housing - Liquid fuels | 0.4 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Housing - Solid fuels | 0.2 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Other consumption - Laboratory services and imaging | 0.1 | 0.00 | 0.00 | 1.00 | 0.2 | 2029 |  |  | C / - / - / J |
| Clothing and shoes - Laundry, repair and rental of clothing | 0.1 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Clothing and shoes - Cleaning, repair and rental of footwear | 0.1 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |
| Housing - Gas | 0.0 | 0.00 | 0.70 | 1.00 | 0.2 | 2029 |  |  | C / - / A-GEN / J |

**Table A2b.** Activity and implied intensity by category (Note S1).

| Category | COICOP code(s) or metric | Activity M~0~ (SEK/cap; flights km/cap) | Intensity I~0~ (kg CO~2~e/unit) | Flag |
|--------------------------|----------|-----------|-----------|----------------------|
| Flights - Passenger flights | 0733 | 5800.0 | 0.14652 | PHYSICAL |
| Housing - District heating and other energy for heating and cooling | 0455 | 4358.6 | 0.11618 | LOW-CONF |
| Local transport - Direct emissions from vehicle use | - |  |  | DIRECT |
| Food and drink - Meat | 0112 | 4617.5 | 0.06279 | OK |
| Housing - Imputed rent for owned permanent dwelling | 0421 | 20131.5 | 0.01193 | OK |
| Food and drink - Milk, cheese, other dairy products and eggs | 0114 | 4050.5 | 0.05661 | OK |
| Other consumption - Hotels, cafés and restaurants | 111 | 11083.9 | 0.01808 | OK |
| Clothing and shoes - Clothing | 0312 | 6871.2 | 0.02585 | OK |
| Food and drink - Vegetables, root crops and legumes | 0117 | 3194.5 | 0.04541 | OK |
| Local transport - Fuels and lubricants | 0722 | 4585.0 | 0.02723 | OK |
| Housing - Actual rent for rented permanent dwelling | 0411 | 11380.6 | 0.01096 | OK |
| Food and drink - Fruit and nuts | 0116 | 2444.6 | 0.05022 | OK |
| Leisure, sport and culture - Package holidays | 096 | 303.9 | 0.40020 | LOW-CONF |
| Food and drink - Bread and cereal products | 0111 | 4098.0 | 0.02554 | OK |
| Local transport - Cars | 0711 | 8304.5 | 0.01254 | OK |
| Food and drink - Sugar, confectionery and desserts | 0118 | 3472.9 | 0.02955 | OK |
| Other consumption - Furniture, furnishings and carpets | 0511, 0512 | 5353.2 | 0.01754 | OK |
| Other consumption - Information and communication equipment | 0812, 0913 | 3858.9 | 0.02217 | LOW-CONF |
| Other consumption - Medicines | 0611 | 2063.3 | 0.04136 | OK |
| Food and drink - Ready-made meals and other food products | 0119 | 1233.8 | 0.06765 | LOW-CONF |
| Local transport - Passenger transport by sea | 0734 | 136.2 | 0.55266 | OK |
| Other consumption - Other appliances and products for personal care | 1213 | 2512.6 | 0.02881 | OK |
| Housing - Electricity | 0451 | 8292.7 | 0.00689 | OK |
| Food and drink - Fish and seafood | 0113 | 1472.1 | 0.03852 | OK |
| Leisure, sport and culture - Garden products, plants and flowers | 0933 | 1724.3 | 0.03247 | OK |
| Housing - Direct emissions from heating | - |  |  | DIRECT |
| Clothing and shoes - Shoes and other footwear | 0321 | 1388.2 | 0.03631 | OK |
| Other consumption - Information and communication services | 0813 | 4846.1 | 0.00988 | OK |
| Other consumption - Household appliances | 0531, 0532 | 1546.2 | 0.02753 | OK |
| Other consumption - Goods and services for household maintenance | 0561, 0562 | 2910.0 | 0.01460 | OK |
| Local transport - Public transport and other combined trips | 0735 | 1651.4 | 0.02493 | OK |
| Food and drink - Wine | 0212 | 2428.4 | 0.01624 | OK |
| Leisure, sport and culture - Recreation and sport services | 0941 | 4531.7 | 0.00854 | OK |
| Leisure, sport and culture - Games, toys and hobby articles | 0931 | 1582.7 | 0.02422 | OK |
| Food and drink - Oils and fats | 0115 | 749.6 | 0.04984 | OK |
| Food and drink - Fruit and vegetable juices | 0122 | 1201.9 | 0.02833 | SHARED |
| Local transport - Maintenance and repairs | 0723 | 3658.2 | 0.00912 | OK |
| Leisure, sport and culture - Pets and pet products | 0934 | 1015.9 | 0.02955 | OK |
| Food and drink - Tobacco | 022 | 2588.1 | 0.01159 | OK |
| Other consumption - Accommodation services | 112 | 1748.6 | 0.01666 | OK |
| Leisure, sport and culture - Major durable goods for leisure | 0921 | 1452.7 | 0.01955 | OK |
| Leisure, sport and culture - Games of chance, betting and lotteries | 0943 | 1639.3 | 0.01632 | OK |
| Other consumption - Glassware, tableware and other utensils | 054 | 2157.2 | 0.01227 | OK |
| Food and drink - Soft drinks | 0122 | 920.2 | 0.02833 | SHARED |
| Other consumption - Hairdressing salons and personal grooming establishments | 1211 | 2850.3 | 0.00897 | OK |
| Housing - Imputed rent for holiday homes, other dwellings, garages and storage | 0422 | 2333.1 | 0.01049 | OK |
| Local transport - Road transport services: car pools, buses and taxis | 0732 | 676.2 | 0.03558 | OK |
| Housing - Maintenance, repair and security | 043 | 1260.2 | 0.01870 | OK |
| Leisure, sport and culture - Equipment for sport, camping and outdoor recreation | 0932 | 1471.3 | 0.01567 | OK |
| Other consumption - Household textiles | 052 | 1596.4 | 0.01434 | OK |
| Local transport - Spare parts and accessories | 0721 | 1476.1 | 0.01467 | OK |
| Other consumption - Home and garden tools | 0551, 0552 | 1784.5 | 0.01124 | OK |
| Food and drink - Coffee and coffee substitutes | 0121 | 719.2 | 0.02774 | SHARED |
| Other consumption - Financial services | 126 | 8112.6 | 0.00243 | OK |
| Local transport - Company-car benefit | 07245 | 1543.0 | 0.01200 | SHARED |
| Clothing and shoes - Other garments and clothing accessories | 0313 | 502.4 | 0.03319 | OK |
| Food and drink - Strong beer | 02131 | 1098.3 | 0.01366 | OK |
| Local transport - Rental of personal transport equipment | 07245 | 1246.9 | 0.01200 | SHARED |
| Other consumption - Other personal effects n.e.c. | 1232 | 845.1 | 0.01685 | OK |
| Food and drink - Spirits | 0211 | 1015.8 | 0.01284 | OK |
| Local transport - Passenger transport by rail and tram | 0731 | 453.8 | 0.02749 | LOW-CONF |
| Other consumption - Jewellery and watches | 1231 | 799.4 | 0.01532 | OK |
| Local transport - Bicycles | 0713 | 304.0 | 0.03786 | OK |
| Other consumption - Outpatient dental services | 0622 | 1703.7 | 0.00591 | OK |
| Other consumption - Other services | 127 | 1792.3 | 0.00528 | LOW-CONF |
| Other consumption - Medical aids and maintenance | 0613 | 962.9 | 0.00974 | OK |
| Leisure, sport and culture - Cultural services | 0942 | 4390.4 | 0.00193 | OK |
| Other consumption - Home care for older people and people with disabilities | 12402 | 1611.7 | 0.00481 | LOW-CONF |
| Leisure, sport and culture - Newspapers and periodicals | 0952 | 1204.8 | 0.00641 | OK |
| Leisure, sport and culture - Books | 0951 | 735.1 | 0.01032 | OK |
| Other consumption - Other outpatient care services | 0621, 0623 | 1511.5 | 0.00494 | OK |
| Housing - Direct household emissions | - |  |  | DIRECT |
| Food and drink - Low- and medium-strength beer | 02132 | 273.2 | 0.02398 | OK |
| Local transport - Parking services | 07244 | 811.2 | 0.00719 | OK |
| Food and drink - Water | 0122 | 201.4 | 0.02833 | SHARED |
| Leisure, sport and culture - Writing and drawing materials | 0954 | 203.8 | 0.02750 | OK |
| Other consumption - Residential care for older people and people with disabilities, excluding health care | 12403 | 2736.2 | 0.00189 | LOW-CONF |
| Local transport - Motorcycles | 0712 | 329.1 | 0.01543 | OK |
| Other consumption - Insurance | 125 | 2904.9 | 0.00173 | OK |
| Clothing and shoes - Clothing materials | 0311 | 107.0 | 0.04406 | OK |
| Leisure, sport and culture - Leisure goods: rental, maintenance and repair | 0923 | 264.2 | 0.01595 | OK |
| Other consumption - Medical products | 0612 | 347.4 | 0.01171 | OK |
| Food and drink - Narcotics | 023 | 179.3 | 0.02104 | OK |
| Other consumption - Electric appliances for personal care | 1212 | 97.5 | 0.03850 | OK |
| Local transport - Other transport of goods | 0736 | 286.9 | 0.01228 | SHARED |
| Leisure, sport and culture - Services for pets | 0935 | 770.7 | 0.00426 | OK |
| Food and drink - Tea, maté and other herbal teas | 0121 | 117.3 | 0.02774 | SHARED |
| Leisure, sport and culture - Photographic and optical equipment | 0912 | 174.0 | 0.01786 | OK |
| Other consumption - Education services | 101 | 679.8 | 0.00415 | OK |
| Housing - Actual rents for other dwellings, garages and storage | 0412 | 8911.5 | 0.00031 | LOW-CONF |
| Other consumption - Software | - |  |  | NOMATCH |
| Leisure, sport and culture - Audiovisual media | 0914 | 264.5 | 0.00710 | LOW-CONF |
| Local transport - Postal and courier services | 0811 | 199.5 | 0.00820 | OK |
| Food and drink - Other alcoholic beverages | - |  |  | NOMATCH |
| Local transport - Driving lessons, driving licences and vehicle inspections | 07241, 07242 | 547.0 | 0.00248 | OK |
| Leisure, sport and culture - Musical instruments | 0922 | 93.4 | 0.01336 | OK |
| Food and drink - Chocolate drinks | 0121 | 32.5 | 0.02774 | SHARED |
| Other consumption - Inpatient curative and rehabilitative services | 063 | 190.5 | 0.00438 | OK |
| Local transport - Road tolls | 07243 | 78.3 | 0.01024 | OK |
| Other consumption - Childcare services | 12401 | 364.9 | 0.00205 | OK |
| Local transport - Other passenger transport services | 0736 | 46.1 | 0.01228 | SHARED |
| Other consumption - Preventive care services | - |  |  | NOMATCH |
| Leisure, sport and culture - Miscellaneous printed matter | 0953 | 66.3 | 0.00761 | OK |
| Other consumption - Religious and ritual articles | - |  |  | NOMATCH |
| Housing - Liquid fuels | 0453 | 100.6 | 0.00366 | OK |
| Housing - Solid fuels | 0454 | 306.2 | 0.00069 | OK |
| Other consumption - Laboratory services and imaging | 0621 | 968.6 | 0.00009 | LOW-CONF |
| Clothing and shoes - Laundry, repair and rental of clothing | 0314 | 139.2 | 0.00047 | OK |
| Clothing and shoes - Cleaning, repair and rental of footwear | 0322 | 7.7 | 0.00747 | OK |
| Housing - Gas | 0452 | 103.2 | 0.00002 | OK |

# Table A3. Global sensitivity analysis: parameter ranges and Sobol indices

Coordinated scenario; uniform distributions; 16,384 base samples. Most ranges extend from the central value toward less favourable values, because central values were set to reach the target.

| Parameter | Range | First-order 2030 | Total-order 2030 | First-order 2050 | Total-order 2050 |
|---|---|---|---|---|---|
| generic supply-side intensity cut by 2050 | 0.4 to 0.9 | 0.269 | 0.221 | 0.820 | 0.797 |
| consumption volume growth per year | -0.005 to 0.01 | 0.020 | 0.021 | 0.109 | 0.117 |
| adoption speed | 0.1 to 0.4 | 0.000 | 0.077 | 0.042 | 0.042 |
| CCS capture in district heating | 0 to 0.95 | -0.007 | 0.011 | 0.014 | 0.030 |
| autonomous intensity decline per year | 0 to 0.03 | 0.002 | 0.000 | 0.014 | 0.017 |
| behavioural potentials, share of central | 0.5 to 1 | 0.016 | 0.006 | 0.019 | 0.014 |
| hard-to-change adoption ceilings | 0.5 to 1 | 0.004 | 0.003 | 0.009 | 0.009 |
| re-spending of behavioural savings | 0 to 0.5 | 0.008 | 0.004 | 0.006 | 0.005 |
| adoption timing shift, years | -2 to 5 | 0.705 | 0.722 | 0.005 | 0.004 |
| household technology (EV, heating) potential | 0.8 to 1 | 0.003 | 0.001 | 0.004 | 0.003 |
| adoption overlap (0 independent, 1 nested) | 0 to 1 | 0.004 | 0.008 | -0.000 | 0.000 |
| other adoption ceilings | 0.75 to 1 | 0.000 | 0.000 | 0.000 | 0.000 |

# Table A4. Reconciliation with the original scenarios and full factorial results

**Table A4a.** Original scenarios reproduced with the original specification.

| Original scenario | Original label | 2030 (original model) | 2050 (original model) | Closest revised cell | Main difference |
|---|---|---|---|---|---|
| S1 | Limited change | 5.74 | 5.74 | Reference (g = 0) | Revised reference includes autonomous decarbonisation |
| S2 | Hotspot-focused | 5.25 | 4.10 | Hotspot, full depth | Original used shallower measures on the hotspot set |
| S3 | Lifestyle-centred | 4.37 | 3.01 | Lifestyle + infrastructure | Original included CCS and electrification; 1.46 t of its 2.73 t 2050 cut came from technology |
| S4 | Coordinated | 3.20 | 1.06 | Coordinated | Revised model separates household and supply-side adoption (see Note S4) |

**Table A4b.** All 32 factorial cells (revised model; g = 1.5% per year).

| Coverage | Behaviour | Technology | Infrastructure | CCS | 2030 | 2050 |
|---|---|---|---|---|---|---|
| hotspot | off | reference | current | off | 5.32 | 3.93 |
| broad | off | reference | current | off | 5.32 | 3.93 |
| hotspot | on | reference | current | off | 4.88 | 3.32 |
| hotspot | off | deep | current | off | 4.69 | 3.13 |
| hotspot | off | reference | enabling | off | 5.32 | 3.93 |
| hotspot | off | reference | current | on | 5.11 | 3.61 |
| broad | on | reference | current | off | 4.60 | 2.94 |
| broad | off | deep | current | off | 3.74 | 1.99 |
| broad | off | reference | enabling | off | 5.32 | 3.93 |
| broad | off | reference | current | on | 5.11 | 3.61 |
| hotspot | on | deep | current | off | 4.55 | 2.86 |
| hotspot | on | reference | enabling | off | 4.74 | 3.12 |
| hotspot | on | reference | current | on | 4.70 | 3.02 |
| hotspot | off | deep | enabling | off | 4.61 | 2.98 |
| hotspot | off | deep | current | on | 4.49 | 2.80 |
| hotspot | off | reference | enabling | on | 5.11 | 3.61 |
| broad | on | deep | current | off | 3.50 | 1.55 |
| broad | on | reference | enabling | off | 4.38 | 2.63 |
| broad | on | reference | current | on | 4.41 | 2.65 |
| broad | off | deep | enabling | off | 3.66 | 1.85 |
| broad | off | deep | current | on | 3.53 | 1.67 |
| broad | off | reference | enabling | on | 5.11 | 3.61 |
| hotspot | on | deep | enabling | off | 4.42 | 2.63 |
| hotspot | on | deep | current | on | 4.36 | 2.56 |
| hotspot | on | reference | enabling | on | 4.56 | 2.83 |
| hotspot | off | deep | enabling | on | 4.41 | 2.66 |
| broad | on | deep | enabling | off | 3.34 | 1.27 |
| broad | on | deep | current | on | 3.31 | 1.26 |
| broad | on | reference | enabling | on | 4.19 | 2.34 |
| broad | off | deep | enabling | on | 3.45 | 1.53 |
| hotspot | on | deep | enabling | on | 4.24 | 2.34 |
| broad | on | deep | enabling | on | 3.16 | 0.99 |

**Table A4c.** Named scenarios at three reference rates.

| Scenario | g (per year) | 2030 | 2050 | Gap 2030 | Gap 2050 |
|---|---|---|---|---|---|
| Reference (current trends) | 0.000 | 5.74 | 5.74 | +2.64 | +4.74 |
| Reference (current trends) | 0.015 | 5.32 | 3.93 | +2.22 | +2.93 |
| Reference (current trends) | 0.030 | 4.93 | 2.68 | +1.83 | +1.68 |
| Hotspot, full depth | 0.000 | 4.59 | 3.56 | +1.49 | +2.56 |
| Hotspot, full depth | 0.015 | 4.36 | 2.56 | +1.26 | +1.56 |
| Hotspot, full depth | 0.030 | 4.14 | 1.88 | +1.04 | +0.88 |
| Lifestyle only | 0.000 | 4.96 | 4.30 | +1.86 | +3.30 |
| Lifestyle only | 0.015 | 4.60 | 2.94 | +1.50 | +1.94 |
| Lifestyle only | 0.030 | 4.26 | 2.01 | +1.16 | +1.01 |
| Lifestyle + infrastructure | 0.000 | 4.72 | 3.84 | +1.62 | +2.84 |
| Lifestyle + infrastructure | 0.015 | 4.38 | 2.63 | +1.28 | +1.63 |
| Lifestyle + infrastructure | 0.030 | 4.05 | 1.79 | +0.95 | +0.79 |
| Technology only | 0.000 | 3.45 | 1.54 | +0.35 | +0.54 |
| Technology only | 0.015 | 3.45 | 1.53 | +0.35 | +0.53 |
| Technology only | 0.030 | 3.45 | 1.50 | +0.35 | +0.50 |
| Coordinated | 0.000 | 3.16 | 0.99 | +0.06 | -0.01 |
| Coordinated | 0.015 | 3.16 | 0.99 | +0.06 | -0.01 |
| Coordinated | 0.030 | 3.16 | 0.96 | +0.06 | -0.04 |

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
