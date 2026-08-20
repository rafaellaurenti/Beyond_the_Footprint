from pathlib import Path
import csv
import json
import math
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
from copy import deepcopy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKBOOK_PATH = REPO_ROOT / 'source' / 'Scenario_analyzer_Malmo_february_2026_original.xlsx'
DATA_DIR = REPO_ROOT / 'data'
FIG_DIR = REPO_ROOT / 'figures'
NB_DIR = REPO_ROOT / 'notebooks'
SCRIPT_DIR = REPO_ROOT / 'scripts'
SOURCE_DIR = REPO_ROOT / 'source'
SUPP_DIR = REPO_ROOT / 'supplementary'
for d in [DATA_DIR, FIG_DIR, NB_DIR, SCRIPT_DIR, SOURCE_DIR, SUPP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

YEARS = list(range(2026, 2051))
TARGET_2030 = 3.1
TARGET_2050 = 1.0
MODEL_START_YEAR = 2026
BASELINE_YEAR = 2022

NS = {
    'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'rel': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

class SimpleXlsxReader:
    """Minimal .xlsx reader that uses cached sheet values from the workbook XML.

    It is intentionally small so the extraction does not depend on Excel, LibreOffice,
    openpyxl, or formula recalculation.
    """
    def __init__(self, path):
        self.path = Path(path)
        self.z = zipfile.ZipFile(self.path)
        self.shared_strings = self._read_shared_strings()
        self.sheets = self._read_sheet_map()

    def _read_shared_strings(self):
        if 'xl/sharedStrings.xml' not in self.z.namelist():
            return []
        root = ET.fromstring(self.z.read('xl/sharedStrings.xml'))
        return [
            ''.join([t.text or '' for t in si.findall('.//main:t', NS)])
            for si in root.findall('main:si', NS)
        ]

    def _read_sheet_map(self):
        workbook = ET.fromstring(self.z.read('xl/workbook.xml'))
        rels = ET.fromstring(self.z.read('xl/_rels/workbook.xml.rels'))
        id_to_target = {r.attrib['Id']: r.attrib['Target'] for r in rels}
        out = {}
        for sh in workbook.findall('.//main:sheet', NS):
            name = sh.attrib.get('name', '').strip() or 'Sheet 1'
            rid = sh.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            target = id_to_target[rid]
            sheet_path = 'xl/' + target.lstrip('/') if not target.startswith('xl/') else target
            out[name] = sheet_path
        return out

    @staticmethod
    def _cell_to_row_col(ref):
        match = re.match(r'([A-Z]+)(\d+)', ref)
        col = 0
        for ch in match.group(1):
            col = col * 26 + ord(ch) - 64
        return int(match.group(2)), col

    def read_sheet(self, name):
        if name not in self.sheets:
            raise KeyError(f'Sheet not found: {name}. Available: {list(self.sheets)}')
        root = ET.fromstring(self.z.read(self.sheets[name]))
        data = {}
        max_row = 0
        max_col = 0
        for row in root.findall('.//main:sheetData/main:row', NS):
            for c in row.findall('main:c', NS):
                row_i, col_i = self._cell_to_row_col(c.attrib['r'])
                max_row = max(max_row, row_i)
                max_col = max(max_col, col_i)
                cell_type = c.attrib.get('t')
                v = c.find('main:v', NS)
                value = None
                if v is not None:
                    raw = v.text
                    if cell_type == 's':
                        value = self.shared_strings[int(raw)]
                    elif cell_type == 'b':
                        value = raw == '1'
                    else:
                        try:
                            value = float(raw)
                            if value.is_integer():
                                value = int(value)
                        except Exception:
                            value = raw
                elif cell_type == 'inlineStr':
                    inline = c.find('main:is', NS)
                    if inline is not None:
                        value = ''.join([t.text or '' for t in inline.findall('.//main:t', NS)])
                data[(row_i, col_i)] = value
        return [[data.get((r, c)) for c in range(1, max_col + 1)] for r in range(1, max_row + 1)]


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))

# -------------------------
# Translation dictionaries
# -------------------------
DOMAIN_MAP = {
    'Flyg': 'Flights',
    'Bostaden': 'Housing',
    'Lokala transporter': 'Local transport',
    'Mat och dryck': 'Food and drink',
    'Övrigt': 'Other consumption',
    'Kläder och skor': 'Clothing and shoes',
    'Fritid, sport, kultur': 'Leisure, sport and culture',
    'Carbon capture': 'Carbon capture placeholder',
}

ITEM_MAP = {
    'Flygresor': 'Passenger flights',
    'fjärrvärme och annan energi för uppvärmning och kylning': 'District heating and other energy for heating and cooling',
    'direkta utsläpp från fordonsanvändning': 'Direct emissions from vehicle use',
    'kött': 'Meat',
    'uppskattad hyra för egen bostad (ägd permanentbostad)': 'Imputed rent for owned permanent dwelling',
    'mjölk, ost, övriga mejeriprodukter, ägg': 'Milk, cheese, other dairy products and eggs',
    'Hotell, kaféer och restauranger': 'Hotels, cafés and restaurants',
    'kläder': 'Clothing',
    'grönsaker, rotfrukter, baljväxter': 'Vegetables, root crops and legumes',
    'bränslen och smörjmedel': 'Fuels and lubricants',
    'frukter och nötter': 'Fruit and nuts',
    'paketresor': 'Package holidays',
    'faktisk hyra, hyresrätt (permanentbostad)': 'Actual rent for rented permanent dwelling',
    'bilar': 'Cars',
    'bröd och spannmålsprodukter': 'Bread and cereal products',
    'socker, konfektyr och efterrätter': 'Sugar, confectionery and desserts',
    'furniture, furnishings, carpets': 'Furniture, furnishings and carpets',
    'informations- och kommunikationsutrustning': 'Information and communication equipment',
    'medicines': 'Medicines',
    'färdigmat och andra livsmedelsprodukter': 'Ready-made meals and other food products',
    'passagerartransport till sjöss': 'Passenger transport by sea',
    'other appliances and products for personal care': 'Other appliances and products for personal care',
    'elektricitet': 'Electricity',
    'direkta utsläpp från uppvärmning': 'Direct emissions from heating',
    'trädgårdsprodukter, växter och blommor': 'Garden products, plants and flowers',
    'fisk och skaldjur': 'Fish and seafood',
    'skor och andra skodon': 'Shoes and other footwear',
    'informations- och kommunikationstjänster': 'Information and communication services',
    'household appliances': 'Household appliances',
    'goods and services for household maintenance': 'Goods and services for household maintenance',
    'vin': 'Wine',
    'kollektivtrafik och andra kombinationsresor': 'Public transport and other combined trips',
    'rekreations- och sporttjänster': 'Recreation and sport services',
    'spel, leksaker och hobbyartiklar': 'Games, toys and hobby articles',
    'oljor och fetter': 'Oils and fats',
    'underhåll och reparationer': 'Maintenance and repairs',
    'frukt- och grönsaksjuicer': 'Fruit and vegetable juices',
    'sällskapsdjur och produkter för sällskapsdjur': 'Pets and pet products',
    'accommodation services': 'Accommodation services',
    'tobak': 'Tobacco',
    'större varaktiga fritidsprodukter': 'Major durable goods for leisure',
    'hasardspel: tips och lotter': 'Games of chance, betting and lotteries',
    'glassware, tableware, other utensils': 'Glassware, tableware and other utensils',
    'underhåll, reparation, säkerhet': 'Maintenance, repair and security',
    'läskedrycker': 'Soft drinks',
    'hairdressing salons and personal grooming establishments': 'Hairdressing salons and personal grooming establishments',
    'uppskattad hyra för fritidshus o andra boenden, garage, förråd': 'Imputed rent for holiday homes, other dwellings, garages and storage',
    'utrustning för sport, camping och friluftsliv': 'Equipment for sport, camping and outdoor recreation',
    'household textiles': 'Household textiles',
    'reservdelar och tillbehör': 'Spare parts and accessories',
    'vägtransporter: bilpooler, buss, taxi': 'Road transport services: car pools, buses and taxis',
    'home and garden tools': 'Home and garden tools',
    'financial services': 'Financial services',
    'bilförmån': 'Company-car benefit',
    'kaffe och kaffesurrogat': 'Coffee and coffee substitutes',
    'andra klädesplagg och klädestillbehörs': 'Other garments and clothing accessories',
    'uthyrning av personliga transportmedel': 'Rental of personal transport equipment',
    'starköl': 'Strong beer',
    'other personal effects n.e.c.': 'Other personal effects n.e.c.',
    'spritdrycker': 'Spirits',
    'jewellery and watches': 'Jewellery and watches',
    'persontransport järn- och spårväg': 'Passenger transport by rail and tram',
    'cyklar': 'Bicycles',
    'outpatient dental services': 'Outpatient dental services',
    'other services': 'Other services',
    'medical aids and maintenance': 'Medical aids and maintenance',
    'kulturella tjänster': 'Cultural services',
    'home care for elderly and disabled': 'Home care for older people and people with disabilities',
    'directa utsläpp från hushåll': 'Direct household emissions',
    'other outpatient care services': 'Other outpatient care services',
    'tidningar och tidskrifter': 'Newspapers and periodicals',
    'böcker': 'Books',
    'öl klass I o II': 'Low- and medium-strength beer',
    'parkeringstjänster': 'Parking services',
    'vatten': 'Water',
    'skriv- och ritmaterial': 'Writing and drawing materials',
    'residential care for elderly and disabled (no health care)': 'Residential care for older people and people with disabilities, excluding health care',
    'motorcyklar': 'Motorcycles',
    'insurance': 'Insurance',
    'material till kläder': 'Clothing materials',
    'fritidsvaror: uthyrning, underhåll och reparation': 'Leisure goods: rental, maintenance and repair',
    'medical products': 'Medical products',
    'narkotika': 'Narcotics',
    'electric appliances for personal care': 'Electric appliances for personal care',
    'annan transport av varor': 'Other transport of goods',
    'tjänster för sällskapsdjur': 'Services for pets',
    'te, maté och andra teer på växter': 'Tea, maté and other herbal teas',
    'fotografisk och optisk utrustning': 'Photographic and optical equipment',
    'Utbildningstjänster': 'Education services',
    'faktiska hyror för andra boenden, garage, förråd': 'Actual rents for other dwellings, garages and storage',
    'audiovisuella medier': 'Audiovisual media',
    'programvaror': 'Software',
    'post- och budtjänster': 'Postal and courier services',
    'andra alkoholhaltiga drycker': 'Other alcoholic beverages',
    'körlektioner, körkort, bilprovning': 'Driving lessons, driving licences and vehicle inspections',
    'musikinstrument': 'Musical instruments',
    'chokladdrycker': 'Chocolate drinks',
    'biltullar': 'Road tolls',
    'inpatient curative and rehabilitative services': 'Inpatient curative and rehabilitative services',
    'childcare services': 'Childcare services',
    'andra persontransporttjänster': 'Other passenger transport services',
    'preventive care services': 'Preventive care services',
    'diverse trycksaker': 'Miscellaneous printed matter',
    'religious and ritual articles': 'Religious and ritual articles',
    'flytande bränslen': 'Liquid fuels',
    'fasta bränslen': 'Solid fuels',
    'laboratory services and imaging': 'Laboratory services and imaging',
    'tvätt, lagning och uthyrning av kläder': 'Laundry, repair and rental of clothing',
    'rengöring, lagning och uthyrning av skodon': 'Cleaning, repair and rental of footwear',
    'gas': 'Gas',
    'Carbon capture': 'Carbon capture',
}

REASONING_MAP = {
    '10% färre bilar 2050 men varje bil ger samma avtryck som idag eftersom elbils produktion kräver mer, men effektiviseras lite': '10% fewer cars by 2050, but each car has the same footprint as today because electric-vehicle production requires more resources, although it becomes slightly more efficient.',
    'Massiv reduktion av bensin/diesel men inte smörjmedel': 'Large reduction in petrol and diesel, but not in lubricants.',
    '90% elbilar 2050': '90% electric cars by 2050.',
    '95% av hushållen täcks av CCS kring 2030': '95% of households are covered by CCS around 2030.',
    '50 % av hushåll som eldar olja och pellets övergår till klimatsmart uppvärmning': '50% of households using oil and pellets shift to climate-smart heating.',
    '75% av medborgarna halverar sin köttkonsumtion till 2050': '75% of residents halve their meat consumption by 2050.',
    '75% av medborgarna halverar sin mejerikonsumtion till 2050': '75% of residents halve their dairy consumption by 2050.',
    'Organisationer som erbjuder bilförmån minskas för att minska bilägande': 'Organisations offering company-car benefits are reduced to decrease car ownership.',
    'De flesta -90%- flyger mindre, och flyg blir mindre CO2 tunga (alt. drivmedel)': 'Most residents, 90%, fly less, and aviation becomes less CO2-intensive through alternative fuels.',
    'Vi minskar med 50% och flygen blir effektivare': 'Flying is reduced by 50% and aviation becomes more efficient.',
    'CCS': 'CCS.',
    'Elektrifiering av 100% av flottan till 2050': '100% electrification of the fleet by 2050.',
    '75% av folket minskar sin köttkonsumtion m 50%': '75% of residents reduce their meat consumption by 50%.',
    '50% av folket minskar boyta m 25%': '50% of residents reduce living space by 25%.',
    '50% av folket minskar sin mejerikonsumtion m 25%': '50% of residents reduce dairy consumption by 25%.',
    'Vi minskar nyinköp med 50% och produktionen blir effektivare': 'New purchases are reduced by 50% and production becomes more efficient.',
    'Elektrifiering av 100% gör att bara smörjmedel finns kvar': '100% electrification means that only lubricants remain.',
    'Folk minskar paketresor med 50% och systemet blir effektivare': 'People reduce package holidays by 50% and the system becomes more efficient.',
    '50% av folket äger inte egen bil': '50% of residents do not own a private car.',
    '100% av folket minskar med 50%': '100% of residents reduce consumption by 50%.',
    '75% av folket minskar med 50%': '75% of residents reduce consumption by 50%.',
    'Sjötransport blir effektivare, och drivs mer med alt bränsle': 'Sea transport becomes more efficient and is increasingly powered by alternative fuels.',
    'Vi minskar med 50% och produktionen blir effektivare': 'Consumption is reduced by 50% and production becomes more efficient.',
    '50% uppgraderar uppvärmning m 80%': '50% upgrade heating systems with an 80% reduction effect.',
    'alla flyger mycket mindre, och flyg blir mindre CO2 tunga (alt. drivmedel)': 'All residents fly much less, and aviation becomes less CO2-intensive through alternative fuels.',
    '100% elbilar 2050': '100% electric cars by 2050.',
    '90% av medborgarna minskar sin köttkonsumtion med 80% till 2050, matsvinn minskas, produktion blir mer effektivt': '90% of residents reduce meat consumption by 80% by 2050; food waste is reduced and production becomes more efficient.',
    '75% av befolkningen bor 25% mindre men en långsam förändring, pga bygg livslängd': '75% of the population lives in 25% less space, but the change is slow because of building lifetimes.',
    '75% av medborgarna minskar sin mejeri konsumtion m. 75% till 2050, matsvinn minskas, produktion blir mer effektivt': '75% of residents reduce dairy consumption by 75% by 2050; food waste is reduced and production becomes more efficient.',
    '70% via transition till förnybar energi': '70% reduction through transition to renewable energy.',
    '100% elbilar,  smörjmedel kvarstår': '100% electric cars; lubricants remain.',
    '75% av befolkningen bor lite mindre men en långsam förändring, pga bygg livslängd': '75% of the population lives in slightly less space, but the change is slow because of building lifetimes.',
    'Paketresor räknas som flyg': 'Package holidays are treated as flights.',
    '50 % färre bilar 2050 men varje bil ger samma avtryck som idag': '50% fewer cars by 2050, but each car has the same footprint as today.',
    'Sötsaker och fika halveras för hälsa och klimatavtryck': 'Sweets and fika consumption are halved for health and climate-footprint reasons.',
    'Färdigmaten innehåller mindre kött och mejeri': 'Ready-made meals contain less meat and dairy.',
    'mer förnybar energi och energieffektivisering av varor ger en minskning trots ökad elekrifiering': 'More renewable energy and energy efficiency in goods reduce emissions despite increased electrification.',
    '100 % av hushåll som eldar olja och pellets övergår till klimatsmart uppvärmning': '100% of households using oil and pellets shift to climate-smart heating.',
    'Vi minskar nyinköp med 75% och produktionen blir effektivare': 'New purchases are reduced by 75% and production becomes more efficient.',
    'Vi minskar tobakkonsumtion m 75%': 'Tobacco consumption is reduced by 75%.',
}

SCENARIOS = {
    'S1': {'name': 'Scenario 1', 'sheet': 'Scenario1', 'logic': 'Limited change / static reference'},
    'S2': {'name': 'Scenario 2', 'sheet': 'Scenario2', 'logic': 'Major-emission-category focus'},
    'S3': {'name': 'Scenario 3', 'sheet': 'Scenario3', 'logic': 'Lifestyle-centred transition'},
    'S4': {'name': 'Scenario 4', 'sheet': 'Scenario 4', 'logic': 'Coordinated target-seeking transition'},
}


def slugify(text):
    text = text.lower()
    replacements = {'å': 'a', 'ä': 'a', 'ö': 'o', 'é': 'e', 'ü': 'u'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text[:90]


def split_category(category_original):
    if category_original == 'Carbon capture':
        return 'Carbon capture', 'Carbon capture'
    if ' - ' not in category_original:
        return category_original, category_original
    domain_original, item_original = category_original.split(' - ', 1)
    return domain_original, item_original


def translate_category(category_original):
    domain_original, item_original = split_category(category_original)
    domain_en = DOMAIN_MAP.get(domain_original, domain_original)
    item_en = ITEM_MAP.get(item_original, item_original)
    # For source entries already in English but not explicitly mapped, use original as item_en.
    category_en = item_en if domain_en == 'Carbon capture placeholder' else f'{domain_en} - {item_en}'
    return domain_original, item_original, domain_en, item_en, category_en


def translate_reasoning(text):
    if not isinstance(text, str) or not text.strip():
        return ''
    return REASONING_MAP.get(text.strip(), text.strip())


def target_pathway(year):
    if year <= 2030:
        return TARGET_2030
    # Linear interpolation between 2030 and 2050 target levels.
    return TARGET_2030 + (TARGET_2050 - TARGET_2030) * ((year - 2030) / (2050 - 2030))

reader = SimpleXlsxReader(WORKBOOK_PATH)

# Baseline
baseline_rows = reader.read_sheet('Baseline CO2, COICOPs')
baseline = []
for row in baseline_rows[1:]:
    if len(row) >= 2 and isinstance(row[0], str) and is_number(row[1]):
        domain_original, item_original, domain_en, item_en, category_en = translate_category(row[0])
        baseline.append({
            'category_id': slugify(category_en),
            'category_original': row[0],
            'category': category_en,
            'domain_original': domain_original,
            'item_original': item_original,
            'domain': domain_en,
            'item': item_en,
            'baseline_kgco2e_per_capita': float(row[1]),
            'is_placeholder': row[0] == 'Carbon capture' or float(row[1]) == 0.0,
        })

baseline_by_orig = {r['category_original']: r['baseline_kgco2e_per_capita'] for r in baseline}
baseline_by_id = {r['category_id']: r['baseline_kgco2e_per_capita'] for r in baseline}
baseline_total_kg = sum(baseline_by_orig.values())
for r in baseline:
    r['baseline_tco2e_per_capita'] = r['baseline_kgco2e_per_capita'] / 1000.0
    r['baseline_share_pct'] = 100.0 * r['baseline_kgco2e_per_capita'] / baseline_total_kg if baseline_total_kg else 0.0

# Scenario parameters

def parse_scenario(sheet_name, scenario_id):
    rows = reader.read_sheet(sheet_name)
    params = []
    for idx, row in enumerate(rows[1:], start=2):
        if len(row) >= 6 and isinstance(row[0], str) and is_number(row[1]) and is_number(row[2]) and is_number(row[3]) and is_number(row[4]) and is_number(row[5]):
            category_original = row[0]
            domain_original, item_original, domain_en, item_en, category_en = translate_category(category_original)
            reasoning_original = row[12] if len(row) > 12 and isinstance(row[12], str) else ''
            references = row[13] if len(row) > 13 and isinstance(row[13], str) else ''
            p = {
                'scenario_id': scenario_id,
                'scenario_name': SCENARIOS[scenario_id]['name'],
                'transition_logic': SCENARIOS[scenario_id]['logic'],
                'source_sheet': sheet_name,
                'source_row': idx,
                'category_id': slugify(category_en),
                'category_original': category_original,
                'category': category_en,
                'domain': domain_en,
                'item': item_en,
                'baseline_kgco2e_per_capita': float(row[1]),
                'L_max_adoption': float(row[2]),
                'k_adoption_speed': float(row[3]),
                't0_inflection_year': int(row[4]) if float(row[4]).is_integer() else float(row[4]),
                'combined_reduction_fraction': float(row[5]),
                'technical_reduction_fraction': float(row[6]) if len(row) > 6 and is_number(row[6]) else 0.0,
                'behavioral_reduction_fraction': float(row[9]) if len(row) > 9 and is_number(row[9]) else 0.0,
                'assumption_note_original': reasoning_original,
                'assumption_note': translate_reasoning(reasoning_original),
                'references': references,
            }
            params.append(p)
    return params

params = []
for sid, meta in SCENARIOS.items():
    params.extend(parse_scenario(meta['sheet'], sid))

# Recalculate combined reduction from behavior and technology where available; keep source value too.
for p in params:
    tech = p['technical_reduction_fraction'] or 0.0
    beh = p['behavioral_reduction_fraction'] or 0.0
    if tech != 0.0 or beh != 0.0:
        p['combined_reduction_recalculated'] = 1 - (1 - tech) * (1 - beh)
    else:
        p['combined_reduction_recalculated'] = p['combined_reduction_fraction']
    p['combined_reduction_difference'] = p['combined_reduction_fraction'] - p['combined_reduction_recalculated']

# Scenario calculation functions

def adoption_fraction(year, L, k, t0):
    return L / (1 + math.exp(-k * (year - t0)))


def calculate(params_for_scenario, dynamic_baseline_rate=0.0):
    pmap = {p['category_id']: p for p in params_for_scenario}
    annual = []
    category_results = []
    for year in YEARS:
        total_kg = 0.0
        for b in baseline:
            base = b['baseline_kgco2e_per_capita'] * ((1 + dynamic_baseline_rate) ** (year - MODEL_START_YEAR))
            p = pmap.get(b['category_id'])
            if p is None:
                adoption = 0.0
                R = 0.0
            else:
                adoption = adoption_fraction(year, p['L_max_adoption'], p['k_adoption_speed'], p['t0_inflection_year'])
                R = p['combined_reduction_fraction']
            new_kg = base * (1 - R * adoption)
            reduction_kg = base - new_kg
            total_kg += new_kg
            category_results.append({
                'scenario_id': params_for_scenario[0]['scenario_id'] if params_for_scenario else '',
                'scenario_name': params_for_scenario[0]['scenario_name'] if params_for_scenario else '',
                'year': year,
                'category_id': b['category_id'],
                'category': b['category'],
                'domain': b['domain'],
                'baseline_kgco2e_per_capita': base,
                'adoption_fraction': adoption,
                'combined_reduction_fraction': R,
                'emissions_kgco2e_per_capita': new_kg,
                'reduction_kgco2e_per_capita': reduction_kg,
            })
        target = target_pathway(year)
        emissions_t = total_kg / 1000.0
        annual.append({
            'scenario_id': params_for_scenario[0]['scenario_id'] if params_for_scenario else '',
            'scenario_name': params_for_scenario[0]['scenario_name'] if params_for_scenario else '',
            'year': year,
            'emissions_tco2e_per_capita': emissions_t,
            'target_tco2e_per_capita': target,
            'gap_vs_target_tco2e_per_capita': emissions_t - target,
            'reduction_from_baseline_tco2e_per_capita': baseline_total_kg / 1000.0 - emissions_t,
            'reduction_from_baseline_pct': 100.0 * (baseline_total_kg / 1000.0 - emissions_t) / (baseline_total_kg / 1000.0),
        })
    return annual, category_results

params_by_scenario = {sid: [p for p in params if p['scenario_id'] == sid] for sid in SCENARIOS}
scenario_results = []
category_results = []
for sid, ps in params_by_scenario.items():
    annual, cats = calculate(ps)
    scenario_results.extend(annual)
    category_results.extend(cats)

# Read workbook result sheets for validation
RESULT_SHEETS = {'S1': 'S1_res', 'S2': 'S2_res', 'S3': 'S3_res', 'S4': 'S4mål_res'}

def read_workbook_result(sheet):
    rows = reader.read_sheet(sheet)
    out = {}
    for row in rows[1:]:
        if len(row) >= 2 and is_number(row[0]) and is_number(row[1]):
            out[int(row[0])] = float(row[1])
    return out

validation = []
for sid, sheet in RESULT_SHEETS.items():
    wb_res = read_workbook_result(sheet)
    model = {r['year']: r['emissions_tco2e_per_capita'] for r in scenario_results if r['scenario_id'] == sid}
    diffs = [abs(model[y] - wb_res[y]) for y in wb_res.keys() if y in model]
    validation.append({
        'scenario_id': sid,
        'scenario_name': SCENARIOS[sid]['name'],
        'workbook_result_sheet': sheet,
        'years_compared': len(diffs),
        'max_abs_difference_tco2e_per_capita': max(diffs) if diffs else None,
        'mean_abs_difference_tco2e_per_capita': float(np.mean(diffs)) if diffs else None,
    })

# Scenario summary
scenario_summary = []
for sid in SCENARIOS:
    ps = params_by_scenario[sid]
    active_ids = {p['category_id'] for p in ps if p['combined_reduction_fraction'] > 0 and p['L_max_adoption'] > 0}
    active_baseline = sum(r['baseline_kgco2e_per_capita'] for r in baseline if r['category_id'] in active_ids)
    res2030 = next(r for r in scenario_results if r['scenario_id'] == sid and r['year'] == 2030)
    res2050 = next(r for r in scenario_results if r['scenario_id'] == sid and r['year'] == 2050)
    scenario_summary.append({
        'scenario_id': sid,
        'scenario_name': SCENARIOS[sid]['name'],
        'transition_logic': SCENARIOS[sid]['logic'],
        'active_categories': len(active_ids),
        'active_baseline_coverage_pct': 100.0 * active_baseline / baseline_total_kg,
        'emissions_2030_tco2e_per_capita': res2030['emissions_tco2e_per_capita'],
        'gap_2030_tco2e_per_capita': res2030['gap_vs_target_tco2e_per_capita'],
        'emissions_2050_tco2e_per_capita': res2050['emissions_tco2e_per_capita'],
        'gap_2050_tco2e_per_capita': res2050['gap_vs_target_tco2e_per_capita'],
    })

# Sensitivity tests

def recalc_combined(p):
    return 1 - (1 - (p['technical_reduction_fraction'] or 0.0)) * (1 - (p['behavioral_reduction_fraction'] or 0.0))


def is_hard_to_change_category(category, domain):
    c = category.lower()
    if domain == 'Flights':
        return True
    if 'meat' in c or 'dairy' in c or 'milk' in c or 'cheese' in c:
        return True
    if domain == 'Clothing and shoes':
        return True
    if domain == 'Other consumption' and any(term in c for term in ['furniture', 'communication equipment', 'household appliances', 'jewellery', 'personal effects', 'glassware', 'household textiles', 'home and garden tools']):
        return True
    if domain == 'Local transport' and any(term in c for term in ['cars', 'fuels', 'vehicle use', 'company-car']):
        return True
    if domain == 'Housing' and any(term in c for term in ['rent', 'dwelling', 'holiday homes']):
        return True
    return False


def mutate_s4(variant):
    ps = deepcopy(params_by_scenario['S4'])
    if variant['type'] == 'base':
        return ps
    if variant['type'] == 't0_shift_all':
        for p in ps:
            p['t0_inflection_year'] += variant['delta']
    elif variant['type'] == 'set_k_all_noninstant':
        for p in ps:
            if p['k_adoption_speed'] < 1:
                p['k_adoption_speed'] = variant['k']
    elif variant['type'] == 'scale_L_hard':
        for p in ps:
            if is_hard_to_change_category(p['category'], p['domain']):
                p['L_max_adoption'] *= variant['scale']
    elif variant['type'] == 'generic_tech_70_to':
        for p in ps:
            if abs(p['technical_reduction_fraction'] - 0.7) < 1e-9:
                p['technical_reduction_fraction'] = variant['tech']
                p['combined_reduction_fraction'] = recalc_combined(p)
    elif variant['type'] == 'ccs':
        for p in ps:
            if p['category'].startswith('Housing - District heating') or p['category'].startswith('Housing - Direct emissions from heating'):
                if variant['mode'] == 'no_ccs':
                    p['technical_reduction_fraction'] = 0.0
                    p['combined_reduction_fraction'] = recalc_combined(p)
                elif variant['mode'] == 'partial_ccs':
                    p['technical_reduction_fraction'] = variant.get('tech', 0.5)
                    p['combined_reduction_fraction'] = recalc_combined(p)
                elif variant['mode'] == 'delayed_ccs':
                    p['t0_inflection_year'] += variant.get('delay', 5)
    elif variant['type'] == 'aviation':
        for p in ps:
            if p['domain'] == 'Flights':
                p['technical_reduction_fraction'] = variant.get('tech', p['technical_reduction_fraction'])
                p['behavioral_reduction_fraction'] = variant.get('behavior', p['behavioral_reduction_fraction'])
                p['combined_reduction_fraction'] = recalc_combined(p)
    elif variant['type'] == 'food_system':
        for p in ps:
            if p['domain'] == 'Food and drink':
                p['technical_reduction_fraction'] = min(p['technical_reduction_fraction'], variant.get('tech_cap', p['technical_reduction_fraction']))
                p['behavioral_reduction_fraction'] *= variant.get('behavior_scale', 1.0)
                p['combined_reduction_fraction'] = recalc_combined(p)
    elif variant['type'] == 'target_2030':
        return ps
    elif variant['type'] == 'dynamic_baseline':
        return ps
    else:
        raise ValueError(variant['type'])
    return ps

variants = [
    {'variant_id': 'base', 'variant': 'Base Scenario 4', 'type': 'base', 'parameter_group': 'Base'},
    {'variant_id': 't0_minus_5', 'variant': 'All adoption 5 years earlier', 'type': 't0_shift_all', 'delta': -5, 'parameter_group': 'Adoption timing'},
    {'variant_id': 't0_minus_2', 'variant': 'All adoption 2 years earlier', 'type': 't0_shift_all', 'delta': -2, 'parameter_group': 'Adoption timing'},
    {'variant_id': 't0_plus_2', 'variant': 'All adoption 2 years later', 'type': 't0_shift_all', 'delta': 2, 'parameter_group': 'Adoption timing'},
    {'variant_id': 't0_plus_5', 'variant': 'All adoption 5 years later', 'type': 't0_shift_all', 'delta': 5, 'parameter_group': 'Adoption timing'},
    {'variant_id': 'k_0_1', 'variant': 'Slow adoption speed k=0.1', 'type': 'set_k_all_noninstant', 'k': 0.1, 'parameter_group': 'Adoption speed'},
    {'variant_id': 'k_0_2', 'variant': 'Adoption speed k=0.2', 'type': 'set_k_all_noninstant', 'k': 0.2, 'parameter_group': 'Adoption speed'},
    {'variant_id': 'k_0_3', 'variant': 'Adoption speed k=0.3', 'type': 'set_k_all_noninstant', 'k': 0.3, 'parameter_group': 'Adoption speed'},
    {'variant_id': 'k_0_4', 'variant': 'Fast adoption speed k=0.4', 'type': 'set_k_all_noninstant', 'k': 0.4, 'parameter_group': 'Adoption speed'},
    {'variant_id': 'L_hard_75', 'variant': 'Hard-to-change maximum adoption reduced by 25%', 'type': 'scale_L_hard', 'scale': 0.75, 'parameter_group': 'Maximum adoption'},
    {'variant_id': 'L_hard_50', 'variant': 'Hard-to-change maximum adoption reduced by 50%', 'type': 'scale_L_hard', 'scale': 0.50, 'parameter_group': 'Maximum adoption'},
    {'variant_id': 'tech70_to_50', 'variant': 'Generic 70% technology reduction reduced to 50%', 'type': 'generic_tech_70_to', 'tech': 0.50, 'parameter_group': 'Technology'},
    {'variant_id': 'tech70_to_90', 'variant': 'Generic 70% technology reduction increased to 90%', 'type': 'generic_tech_70_to', 'tech': 0.90, 'parameter_group': 'Technology'},
    {'variant_id': 'no_ccs', 'variant': 'No CCS in heating', 'type': 'ccs', 'mode': 'no_ccs', 'parameter_group': 'CCS'},
    {'variant_id': 'partial_ccs', 'variant': 'Partial CCS in heating', 'type': 'ccs', 'mode': 'partial_ccs', 'tech': 0.5, 'parameter_group': 'CCS'},
    {'variant_id': 'delayed_ccs', 'variant': 'CCS delayed by 5 years', 'type': 'ccs', 'mode': 'delayed_ccs', 'delay': 5, 'parameter_group': 'CCS'},
    {'variant_id': 'aviation_low', 'variant': 'Lower aviation demand and technology improvement', 'type': 'aviation', 'tech': 0.5, 'behavior': 0.5, 'parameter_group': 'Aviation'},
    {'variant_id': 'food_low', 'variant': 'Weaker food-system assumptions', 'type': 'food_system', 'tech_cap': 0.5, 'behavior_scale': 0.75, 'parameter_group': 'Food'},
    {'variant_id': 'target2030_3_0', 'variant': 'Alternative 2030 target of 3.0 t', 'type': 'target_2030', 'parameter_group': 'Target interpretation'},
    {'variant_id': 'baseline_growth_0_5_pct', 'variant': 'Dynamic baseline with 0.5% annual growth', 'type': 'dynamic_baseline', 'rate': 0.005, 'parameter_group': 'Baseline'},
    {'variant_id': 'baseline_decline_0_5_pct', 'variant': 'Dynamic baseline with 0.5% annual decline', 'type': 'dynamic_baseline', 'rate': -0.005, 'parameter_group': 'Baseline'},
]

base_s4_annual = [r for r in scenario_results if r['scenario_id'] == 'S4']
base_2030 = next(r['emissions_tco2e_per_capita'] for r in base_s4_annual if r['year'] == 2030)
base_2050 = next(r['emissions_tco2e_per_capita'] for r in base_s4_annual if r['year'] == 2050)
sensitivity = []
for v in variants:
    if v['type'] == 'dynamic_baseline':
        annual, _cats = calculate(params_by_scenario['S4'], dynamic_baseline_rate=v['rate'])
    else:
        annual, _cats = calculate(mutate_s4(v))
    e2030 = next(r['emissions_tco2e_per_capita'] for r in annual if r['year'] == 2030)
    e2050 = next(r['emissions_tco2e_per_capita'] for r in annual if r['year'] == 2050)
    target2030 = 3.0 if v['type'] == 'target_2030' else TARGET_2030
    sensitivity.append({
        'variant_id': v['variant_id'],
        'variant': v['variant'],
        'parameter_group': v.get('parameter_group', ''),
        'emissions_2030_tco2e_per_capita': e2030,
        'emissions_2050_tco2e_per_capita': e2050,
        'delta_2030_vs_base_tco2e_per_capita': e2030 - base_2030,
        'delta_2050_vs_base_tco2e_per_capita': e2050 - base_2050,
        'gap_2030_tco2e_per_capita': e2030 - target2030,
        'gap_2050_tco2e_per_capita': e2050 - TARGET_2050,
    })

# Domain contributions for S4
s4_cat_2030 = [r for r in category_results if r['scenario_id'] == 'S4' and r['year'] == 2030]
s4_cat_2050 = [r for r in category_results if r['scenario_id'] == 'S4' and r['year'] == 2050]
domain_contribs = []
for domain in sorted({r['domain'] for r in baseline}):
    for year, rows in [(2030, s4_cat_2030), (2050, s4_cat_2050)]:
        sub = [r for r in rows if r['domain'] == domain]
        domain_contribs.append({
            'scenario_id': 'S4',
            'scenario_name': 'Scenario 4',
            'year': year,
            'domain': domain,
            'baseline_tco2e_per_capita': sum(r['baseline_kgco2e_per_capita'] for r in sub) / 1000.0,
            'emissions_tco2e_per_capita': sum(r['emissions_kgco2e_per_capita'] for r in sub) / 1000.0,
            'reduction_tco2e_per_capita': sum(r['reduction_kgco2e_per_capita'] for r in sub) / 1000.0,
        })

# Export CSVs
def write_csv(path, rows, fieldnames=None):
    path = Path(path)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, '') for k in fieldnames})

write_csv(DATA_DIR / 'baseline_categories.csv', baseline)
write_csv(DATA_DIR / 'category_domain_mapping.csv', [
    {k: r[k] for k in ['category_id', 'category_original', 'category', 'domain_original', 'domain', 'item_original', 'item']}
    for r in baseline
])
write_csv(DATA_DIR / 'scenario_parameters.csv', params)
write_csv(DATA_DIR / 'scenario_results.csv', scenario_results)
write_csv(DATA_DIR / 'category_results.csv', category_results)
write_csv(DATA_DIR / 'scenario_summary.csv', scenario_summary)
write_csv(DATA_DIR / 'sensitivity_results.csv', sensitivity)
write_csv(DATA_DIR / 'validation_summary.csv', validation)
write_csv(DATA_DIR / 'domain_reduction_contributions_s4.csv', domain_contribs)

# Table A2: Scenario 4 category-level parameters (supplementary material).
# It is derived here from `params`, computed above, so it is reproducible end-to-end from the source
# workbook. If `scripts/build_activity_intensity_crosswalk.py` has been run
# afterwards, it will overwrite this file with six additional columns; run
# this script first if you want the base version on its own.
s4_active = sorted(
    (p for p in params if p['scenario_id'] == 'S4' and p['combined_reduction_fraction'] > 0),
    key=lambda p: -p['baseline_kgco2e_per_capita']
)
table_a2 = [{
    'category_id': p['category_id'],
    'Category': p['category'],
    'Domain': p['domain'],
    'Baseline (kg CO₂e/cap)': p['baseline_kgco2e_per_capita'],
    'Behavioural reduction': p['behavioral_reduction_fraction'],
    'Technological reduction': p['technical_reduction_fraction'],
    'Combined reduction': p['combined_reduction_fraction'],
    'Max adoption (L)': p['L_max_adoption'],
    'Adoption speed (k)': p['k_adoption_speed'],
    'Inflection year (t\u2080)': p['t0_inflection_year'],
    'Assumption note': p['assumption_note'],
} for p in s4_active]
write_csv(SUPP_DIR / 'table_a2_scenario4_parameters.csv', table_a2)
print(f"Table A2: {len(table_a2)} active S4 categories written to supplementary/")

# Table A1: full sensitivity results (supplementary material). Same content as
# data/sensitivity_results.csv; duplicated here because the manuscript's
# Table A1 is referenced from supplementary/.
write_csv(SUPP_DIR / 'table_a1_sensitivity_results.csv', sensitivity)
print(f"Table A1: {len(sensitivity)} sensitivity variants written to supplementary/")

translation_rows = []
for b in baseline:
    translation_rows.append({
        'type': 'category',
        'original': b['category_original'],
        'english': b['category'],
        'domain_original': b['domain_original'],
        'domain_english': b['domain'],
        'item_original': b['item_original'],
        'item_english': b['item'],
    })
for original, english in REASONING_MAP.items():
    translation_rows.append({
        'type': 'assumption_note',
        'original': original,
        'english': english,
        'domain_original': '',
        'domain_english': '',
        'item_original': '',
        'item_english': '',
    })
write_csv(DATA_DIR / 'translation_dictionary.csv', translation_rows)

# -------------------------
# Generate figures for the package
# -------------------------
plt.rcParams.update({
    'figure.dpi': 120,
    'savefig.dpi': 300,
    'font.size': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

DOMAIN_ORDER = ['Food and drink', 'Housing', 'Local transport', 'Flights', 'Other consumption', 'Leisure, sport and culture', 'Clothing and shoes']
DOMAIN_COLORS = {
    'Food and drink': '#6C9A73',
    'Housing': '#4C78A8',
    'Local transport': '#F58518',
    'Flights': '#B279A2',
    'Other consumption': '#8E6C4A',
    'Leisure, sport and culture': '#72B7B2',
    'Clothing and shoes': '#E45756',
    'Carbon capture placeholder': '#9A9A9A',
}
SCENARIO_COLORS = {'S1': '#9A9A9A', 'S2': '#4C78A8', 'S3': '#F58518', 'S4': '#54A24B'}

def savefig(name):
    plt.tight_layout()
    plt.savefig(FIG_DIR / name, bbox_inches='tight')
    plt.close()

# Baseline footprint top 25
base_sorted = sorted([r for r in baseline if not r['is_placeholder']], key=lambda x: x['baseline_kgco2e_per_capita'], reverse=True)[:25]
labels = [r['category'] for r in base_sorted][::-1]
vals = [r['baseline_kgco2e_per_capita'] for r in base_sorted][::-1]
colors = [DOMAIN_COLORS.get(r['domain'], '#9A9A9A') for r in base_sorted][::-1]
fig, ax = plt.subplots(figsize=(10, 7.5))
y = np.arange(len(labels))
ax.barh(y, vals, color=colors, edgecolor='white', linewidth=0.5)
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel('Baseline emissions (kg CO₂e/capita/year)')
ax.set_title('Malmö baseline consumption footprint: top contributing categories')
ax.grid(axis='x', alpha=0.25)
for i, v in enumerate(vals):
    ax.text(v + 8, i, f'{v:.0f}', va='center', fontsize=7)
savefig('fig2_baseline_footprint_top_categories.png')

# Scenario pathways
fig, ax = plt.subplots(figsize=(8.8, 5.2))
for sid in ['S1','S2','S3','S4']:
    rows = [r for r in scenario_results if r['scenario_id'] == sid]
    ax.plot([r['year'] for r in rows], [r['emissions_tco2e_per_capita'] for r in rows], label=SCENARIOS[sid]['name'], color=SCENARIO_COLORS[sid], linewidth=2.5)
ax.plot(YEARS, [target_pathway(y) for y in YEARS], linestyle='--', color='black', linewidth=2, label='Target pathway')
ax.set_ylim(0, 6.2)
ax.set_xlabel('Year')
ax.set_ylabel('Consumption-based emissions\n(t CO₂e/capita/year)')
ax.set_title('Scenario pathways compared with Malmö’s target pathway')
ax.grid(axis='y', alpha=0.25)
ax.legend(frameon=False)
savefig('fig3_scenario_pathways_targets.png')

# Domain reductions S4 2050
rows2050 = [r for r in domain_contribs if r['year'] == 2050 and r['domain'] != 'Carbon capture placeholder']
rows2050 = sorted(rows2050, key=lambda r: r['reduction_tco2e_per_capita'])
fig, ax = plt.subplots(figsize=(8.5, 5.2))
y = np.arange(len(rows2050))
ax.barh(y, [r['reduction_tco2e_per_capita'] for r in rows2050], color=[DOMAIN_COLORS.get(r['domain'], '#999999') for r in rows2050])
ax.set_yticks(y)
ax.set_yticklabels([r['domain'] for r in rows2050])
ax.set_xlabel('Reduction in 2050 (t CO₂e/capita/year)')
ax.set_title('Domain contributions to reductions in Scenario 4')
ax.grid(axis='x', alpha=0.25)
for i, r in enumerate(rows2050):
    ax.text(r['reduction_tco2e_per_capita'] + 0.02, i, f"{r['reduction_tco2e_per_capita']:.2f}", va='center', fontsize=8)
savefig('fig4_domain_reduction_contributions_s4.png')

# Sensitivity tornado
plot_rows = [r for r in sensitivity if r['variant_id'] != 'base']
plot_rows = sorted(plot_rows, key=lambda r: abs(r['delta_2050_vs_base_tco2e_per_capita']), reverse=True)[:12]
plot_rows = list(reversed(plot_rows))
fig, ax = plt.subplots(figsize=(9, 6.2))
y = np.arange(len(plot_rows))
deltas = [r['delta_2050_vs_base_tco2e_per_capita'] for r in plot_rows]
ax.barh(y, deltas, color=['#E45756' if d > 0 else '#54A24B' for d in deltas])
ax.axvline(0, color='black', linewidth=1)
ax.set_yticks(y)
ax.set_yticklabels([r['variant'] for r in plot_rows], fontsize=8)
ax.set_xlabel('Change in 2050 emissions relative to Scenario 4\n(t CO₂e/capita/year)')
ax.set_title('Sensitivity of the coordinated transition pathway')
ax.grid(axis='x', alpha=0.25)
for i, d in enumerate(deltas):
    ax.text(d + (0.015 if d >= 0 else -0.015), i, f'{d:+.2f}', va='center', ha='left' if d >= 0 else 'right', fontsize=8)
savefig('fig5_sensitivity_tornado_2050.png')

# Coverage vs residual emissions
fig, ax = plt.subplots(figsize=(7.5, 5.2))
for r in scenario_summary:
    ax.scatter(r['active_baseline_coverage_pct'], r['emissions_2050_tco2e_per_capita'], s=120, color=SCENARIO_COLORS[r['scenario_id']], edgecolor='white', linewidth=1)
    ax.text(r['active_baseline_coverage_pct'] + 1.2, r['emissions_2050_tco2e_per_capita'], r['scenario_name'], va='center')
ax.axhline(TARGET_2050, color='black', linestyle='--', linewidth=1.3, label='2050 target')
ax.set_xlim(0,105)
ax.set_ylim(0,6.0)
ax.set_xlabel('Share of baseline footprint actively addressed (%)')
ax.set_ylabel('2050 residual emissions\n(t CO₂e/capita/year)')
ax.set_title('Scenario coverage and residual emissions')
ax.grid(alpha=0.25)
ax.legend(frameon=False)
savefig('supp_coverage_vs_residual_emissions.png')

# Extraction completed.
print('Cleaned data and figures regenerated from', WORKBOOK_PATH)
print('Validation:', validation)
