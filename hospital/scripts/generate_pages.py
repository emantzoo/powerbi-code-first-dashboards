import json, os, hashlib, shutil

BASE = r"C:\Users\emant\Downloads\powerBI_recipes\Hosptl\HospitalDashboard.Report\definition\pages"
SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"

def uid(seed):
    return hashlib.md5(seed.encode()).hexdigest()[:20]

def measure_field(table, measure):
    return {
        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": table}}, "Property": measure}},
        "queryRef": f"{table}.{measure}",
        "nativeQueryRef": measure
    }

def column_field(table, column):
    return {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": column}},
        "queryRef": f"{table}.{column}",
        "nativeQueryRef": column
    }

def make_card(name, x, y, w, h, table, measure, z=1000):
    return {
        "$schema": SCHEMA_VISUAL, "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {"visualType": "cardVisual",
            "query": {"queryState": {"Data": {"projections": [measure_field(table, measure)]}}},
            "drillFilterOtherVisuals": True}
    }

def make_slicer(name, x, y, w, h, table, column, z=1000):
    return {
        "$schema": SCHEMA_VISUAL, "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {"visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [column_field(table, column)]}}},
            "drillFilterOtherVisuals": True}
    }

def make_clustered_bar(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, z=1000):
    return {
        "$schema": SCHEMA_VISUAL, "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {"visualType": "clusteredBarChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [measure_field(val_table, val_measure)]}}},
            "drillFilterOtherVisuals": True}
    }

def make_line_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, z=1000):
    return {
        "$schema": SCHEMA_VISUAL, "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {"visualType": "lineChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [measure_field(val_table, val_measure)]}}},
            "drillFilterOtherVisuals": True}
    }

def make_area_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, z=1000):
    return {
        "$schema": SCHEMA_VISUAL, "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {"visualType": "areaChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [measure_field(val_table, val_measure)]}}},
            "drillFilterOtherVisuals": True}
    }

def make_donut(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, z=1000):
    return {
        "$schema": SCHEMA_VISUAL, "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {"visualType": "donutChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [measure_field(val_table, val_measure)]}}},
            "drillFilterOtherVisuals": True}
    }

def make_table(name, x, y, w, h, fields_list, z=1000):
    projections = []
    for tbl, col, is_measure in fields_list:
        projections.append(measure_field(tbl, col) if is_measure else column_field(tbl, col))
    return {
        "$schema": SCHEMA_VISUAL, "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {"visualType": "tableEx",
            "query": {"queryState": {"Values": {"projections": projections}}},
            "drillFilterOtherVisuals": True}
    }

def make_matrix(name, x, y, w, h, row_fields, col_fields, val_fields, z=1000):
    rows = [column_field(t, c) for t, c in row_fields]
    cols = [column_field(t, c) for t, c in col_fields]
    vals = [measure_field(t, m) for t, m in val_fields]
    return {
        "$schema": SCHEMA_VISUAL, "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {"visualType": "pivotTable",
            "query": {"queryState": {
                "Rows": {"projections": rows},
                "Columns": {"projections": cols},
                "Values": {"projections": vals}}},
            "drillFilterOtherVisuals": True}
    }

def write_visual(page_dir, visual_json):
    vdir = os.path.join(page_dir, "visuals", visual_json["name"])
    os.makedirs(vdir, exist_ok=True)
    with open(os.path.join(vdir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(visual_json, f, indent=2, ensure_ascii=False)

def write_page(page_id, display_name, visuals):
    page_dir = os.path.join(BASE, page_id)
    os.makedirs(os.path.join(page_dir, "visuals"), exist_ok=True)
    with open(os.path.join(page_dir, "page.json"), "w", encoding="utf-8") as f:
        json.dump({"$schema": SCHEMA_PAGE, "name": page_id, "displayName": display_name,
                    "displayOption": "FitToPage", "height": 720, "width": 1280}, f, indent=2)
    for v in visuals:
        write_visual(page_dir, v)

# ===== PAGE 1: Hospital Overview =====
p1_id = uid("hosp_page1_overview")
p1 = [
    make_card("h1_admissions", 20, 10, 235, 110, "_Measures", "Total Admissions"),
    make_card("h1_los", 270, 10, 235, 110, "_Measures", "Avg Length of Stay"),
    make_card("h1_occupancy", 520, 10, 235, 110, "_Measures", "Daily Bed Occupancy Rate"),
    make_card("h1_readmit", 770, 10, 235, 110, "_Measures", "Readmission Rate"),
    make_slicer("h1_year", 1020, 10, 230, 110, "Calendar", "Year"),
    make_clustered_bar("h1_dept_bar", 20, 140, 400, 280, "DimDepartment", "department_name", "_Measures", "Total Admissions"),
    make_line_chart("h1_trend", 440, 140, 400, 280, "Calendar", "Year_Month", "_Measures", "Total Admissions"),
    make_donut("h1_type_donut", 860, 140, 380, 280, "FactAdmissions", "admission_type", "_Measures", "Total Admissions"),
    make_area_chart("h1_charges_area", 20, 440, 600, 260, "Calendar", "Year_Month", "_Measures", "Total Charges"),
    make_clustered_bar("h1_los_bar", 640, 440, 610, 260, "DimDepartment", "department_name", "_Measures", "Avg Length of Stay"),
]

# ===== PAGE 2: Department Deep-Dive =====
p2_id = uid("hosp_page2_dept")
p2 = [
    make_card("h2_admissions", 20, 10, 235, 110, "_Measures", "Total Admissions"),
    make_card("h2_charges", 270, 10, 235, 110, "_Measures", "Total Charges"),
    make_card("h2_avg_charge", 520, 10, 235, 110, "_Measures", "Avg Charge per Admission"),
    make_card("h2_emerg_pct", 770, 10, 235, 110, "_Measures", "Emergency Pct"),
    make_slicer("h2_dept", 1020, 10, 230, 110, "DimDepartment", "department_name"),
    make_clustered_bar("h2_dept_charges", 20, 140, 610, 280, "DimDepartment", "department_name", "_Measures", "Total Charges"),
    make_clustered_bar("h2_diag_bar", 650, 140, 600, 280, "FactAdmissions", "diagnosis_code", "_Measures", "Total Admissions"),
    make_matrix("h2_matrix", 20, 440, 1230, 260,
        [("DimDepartment", "department_name")],
        [("Calendar", "Year")],
        [("_Measures", "Total Admissions"), ("_Measures", "Avg Length of Stay"), ("_Measures", "Total Charges"), ("_Measures", "Daily Bed Occupancy Rate")]),
]

# ===== PAGE 3: Wait Time Analysis =====
p3_id = uid("hosp_page3_wait")
p3 = [
    make_card("h3_wait", 20, 10, 295, 110, "_Measures", "Avg Wait Minutes"),
    make_card("h3_triage", 330, 10, 295, 110, "_Measures", "Avg Triage Minutes"),
    make_card("h3_under15", 640, 10, 295, 110, "_Measures", "Wait Under 15min Pct"),
    make_card("h3_over60", 950, 10, 295, 110, "_Measures", "Wait Over 60min Pct"),
    make_clustered_bar("h3_cat_bar", 20, 140, 400, 280, "FactWaitTimes", "wait_category", "_Measures", "Total Wait Records"),
    make_line_chart("h3_trend", 440, 140, 400, 280, "Calendar", "Year_Month", "_Measures", "Avg Wait Minutes"),
    make_donut("h3_dept_donut", 860, 140, 380, 280, "DimDepartment", "department_name", "_Measures", "Total Wait Records"),
    make_table("h3_table", 20, 440, 1230, 260, [
        ("DimDepartment", "department_name", False),
        ("_Measures", "Total Wait Records", True),
        ("_Measures", "Avg Wait Minutes", True),
        ("_Measures", "Avg Triage Minutes", True),
        ("_Measures", "Wait Under 15min Pct", True),
        ("_Measures", "Wait Over 60min Pct", True),
    ]),
]

# ===== PAGE 4: Patient Demographics =====
p4_id = uid("hosp_page4_patient")
p4 = [
    make_card("h4_patients", 20, 10, 295, 110, "_Measures", "Unique Patients"),
    make_card("h4_admissions", 330, 10, 295, 110, "_Measures", "Total Admissions"),
    make_card("h4_adm_yoy", 640, 10, 295, 110, "_Measures", "Admissions YoY Growth"),
    make_card("h4_chg_yoy", 950, 10, 295, 110, "_Measures", "Charges YoY Growth"),
    make_clustered_bar("h4_age_bar", 20, 140, 400, 280, "DimPatient", "age_group", "_Measures", "Total Admissions"),
    make_donut("h4_gender_donut", 440, 140, 380, 280, "DimPatient", "gender", "_Measures", "Total Admissions"),
    make_clustered_bar("h4_ins_bar", 840, 140, 410, 280, "DimPatient", "insurance_type", "_Measures", "Total Charges"),
    make_table("h4_table", 20, 440, 1230, 260, [
        ("DimPatient", "age_group", False),
        ("DimPatient", "insurance_type", False),
        ("_Measures", "Total Admissions", True),
        ("_Measures", "Avg Length of Stay", True),
        ("_Measures", "Total Charges", True),
        ("_Measures", "Avg Charge per Admission", True),
    ]),
]

# Remove old default page
old_page = os.path.join(BASE, "a1f55d2f97fa0fb931d3")
if os.path.exists(old_page):
    shutil.rmtree(old_page)

# Write all pages
write_page(p1_id, "Hospital Overview", p1)
write_page(p2_id, "Department Deep-Dive", p2)
write_page(p3_id, "Wait Time Analysis", p3)
write_page(p4_id, "Patient Demographics", p4)

# Update pages.json
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, p3_id, p4_id],
               "activePageName": p1_id}, f, indent=2)

print(f"Page 1 (Hospital Overview): {p1_id} - {len(p1)} visuals")
print(f"Page 2 (Department Deep-Dive): {p2_id} - {len(p2)} visuals")
print(f"Page 3 (Wait Time Analysis): {p3_id} - {len(p3)} visuals")
print(f"Page 4 (Patient Demographics): {p4_id} - {len(p4)} visuals")
print("Done!")
