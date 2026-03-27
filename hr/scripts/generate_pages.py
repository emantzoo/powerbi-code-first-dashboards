import json, os, hashlib

BASE = r"C:\Users\emant\Downloads\powerBI_recipes\HR\HRAnalyticsDashboard.Report\definition\pages"
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
        "$schema": SCHEMA_VISUAL,
        "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {
            "visualType": "cardVisual",
            "query": {"queryState": {"Data": {"projections": [measure_field(table, measure)]}}},
            "drillFilterOtherVisuals": True
        }
    }

def make_slicer(name, x, y, w, h, table, column, z=1000):
    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {
            "visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [column_field(table, column)]}}},
            "drillFilterOtherVisuals": True
        }
    }

def make_clustered_bar(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, z=1000):
    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [measure_field(val_table, val_measure)]}
            }},
            "drillFilterOtherVisuals": True
        }
    }

def make_line_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, z=1000):
    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {
            "visualType": "lineChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [measure_field(val_table, val_measure)]}
            }},
            "drillFilterOtherVisuals": True
        }
    }

def make_donut(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, z=1000):
    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {
            "visualType": "donutChart",
            "query": {"queryState": {
                "Category": {"projections": [column_field(cat_table, cat_col)]},
                "Y": {"projections": [measure_field(val_table, val_measure)]}
            }},
            "drillFilterOtherVisuals": True
        }
    }

def make_table(name, x, y, w, h, fields_list, z=1000):
    projections = []
    for tbl, col, is_measure in fields_list:
        if is_measure:
            projections.append(measure_field(tbl, col))
        else:
            projections.append(column_field(tbl, col))
    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {
            "visualType": "tableEx",
            "query": {"queryState": {"Values": {"projections": projections}}},
            "drillFilterOtherVisuals": True
        }
    }

def make_matrix(name, x, y, w, h, row_fields, col_fields, val_fields, z=1000):
    rows = [column_field(t, c) for t, c in row_fields]
    cols = [column_field(t, c) for t, c in col_fields]
    vals = [measure_field(t, m) for t, m in val_fields]
    return {
        "$schema": SCHEMA_VISUAL,
        "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {
            "visualType": "pivotTable",
            "query": {"queryState": {
                "Rows": {"projections": rows},
                "Columns": {"projections": cols},
                "Values": {"projections": vals}
            }},
            "drillFilterOtherVisuals": True
        }
    }

def write_visual(page_dir, visual_json):
    vname = visual_json["name"]
    vdir = os.path.join(page_dir, "visuals", vname)
    os.makedirs(vdir, exist_ok=True)
    with open(os.path.join(vdir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(visual_json, f, indent=2, ensure_ascii=False)

def write_page(page_id, display_name, visuals):
    page_dir = os.path.join(BASE, page_id)
    os.makedirs(os.path.join(page_dir, "visuals"), exist_ok=True)
    page_json = {
        "$schema": SCHEMA_PAGE,
        "name": page_id,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280
    }
    with open(os.path.join(page_dir, "page.json"), "w", encoding="utf-8") as f:
        json.dump(page_json, f, indent=2, ensure_ascii=False)
    for v in visuals:
        write_visual(page_dir, v)

# ===== PAGE 1: Workforce Overview =====
p1_id = uid("page1_workforce")
p1_visuals = [
    make_card("p1_headcount", 20, 10, 235, 110, "_Measures", "Current Headcount"),
    make_card("p1_avg_salary", 270, 10, 235, 110, "_Measures", "Avg Salary"),
    make_card("p1_engagement", 520, 10, 235, 110, "_Measures", "Avg Engagement"),
    make_card("p1_yoy_growth", 770, 10, 235, 110, "_Measures", "Headcount YoY Growth"),
    make_slicer("p1_year_slicer", 1020, 10, 230, 110, "Calendar", "Year"),
    make_clustered_bar("p1_dept_bar", 20, 140, 400, 280, "DimDepartment", "department_name", "_Measures", "Current Headcount"),
    make_line_chart("p1_trend_line", 440, 140, 400, 280, "Calendar", "Year_Month", "_Measures", "Current Headcount"),
    make_donut("p1_level_donut", 860, 140, 380, 280, "DimJobLevel", "level_name", "_Measures", "Current Headcount"),
    make_clustered_bar("p1_gender_bar", 20, 440, 400, 260, "DimEmployee", "gender", "_Measures", "Current Headcount"),
    make_donut("p1_edu_donut", 440, 440, 380, 260, "DimEmployee", "education_level", "_Measures", "Current Headcount"),
    make_clustered_bar("p1_city_bar", 840, 440, 410, 260, "DimEmployee", "city", "_Measures", "Current Headcount"),
]

# ===== PAGE 2: Attrition Analysis =====
p2_id = uid("page2_attrition")
p2_visuals = [
    make_card("p2_terminations", 20, 10, 235, 110, "_Measures", "Terminations"),
    make_card("p2_annual_attr", 270, 10, 235, 110, "_Measures", "Annualized Attrition Rate"),
    make_card("p2_vol_attr", 520, 10, 235, 110, "_Measures", "Voluntary Attrition Rate"),
    make_card("p2_tenure", 770, 10, 235, 110, "_Measures", "Avg Tenure Years"),
    make_slicer("p2_year_slicer", 1020, 10, 230, 110, "Calendar", "Year"),
    make_clustered_bar("p2_exit_bar", 20, 140, 400, 280, "DimEmployee", "exit_reason", "_Measures", "Terminations"),
    make_line_chart("p2_trend_line", 440, 140, 400, 280, "Calendar", "Year_Month", "_Measures", "Terminations"),
    make_donut("p2_dept_donut", 860, 140, 380, 280, "DimDepartment", "department_name", "_Measures", "Terminations"),
    make_matrix("p2_matrix", 20, 440, 1230, 260,
        [("DimDepartment", "department_name")],
        [("Calendar", "Year")],
        [("_Measures", "Terminations"), ("_Measures", "Annualized Attrition Rate"), ("_Measures", "Avg Tenure Years")]),
]

# ===== PAGE 3: Compensation & Equity =====
p3_id = uid("page3_compensation")
p3_visuals = [
    make_card("p3_avg_salary", 20, 10, 235, 110, "_Measures", "Avg Salary"),
    make_card("p3_compa", 270, 10, 235, 110, "_Measures", "Compa Ratio"),
    make_card("p3_gap", 520, 10, 235, 110, "_Measures", "Gender Pay Gap"),
    make_card("p3_below", 770, 10, 235, 110, "_Measures", "Below Band Pct"),
    make_slicer("p3_dept_slicer", 1020, 10, 230, 110, "DimDepartment", "department_name"),
    make_clustered_bar("p3_level_bar", 20, 140, 400, 280, "DimJobLevel", "level_name", "_Measures", "Avg Salary"),
    make_clustered_bar("p3_dept_bar", 440, 140, 400, 280, "DimDepartment", "department_name", "_Measures", "Avg Salary"),
    make_clustered_bar("p3_gender_bar", 860, 140, 380, 280, "DimEmployee", "gender", "_Measures", "Avg Salary"),
    make_table("p3_table", 20, 440, 1230, 260, [
        ("DimJobLevel", "level_name", False),
        ("DimJobLevel", "salary_band_min", False),
        ("DimJobLevel", "salary_band_max", False),
        ("_Measures", "Avg Salary", True),
        ("_Measures", "Median Salary", True),
        ("_Measures", "Compa Ratio", True),
        ("_Measures", "Below Band Pct", True),
        ("_Measures", "Above Band Pct", True),
    ]),
]

# ===== PAGE 4: Recruitment Funnel =====
p4_id = uid("page4_recruitment")
p4_visuals = [
    make_card("p4_reqs", 20, 10, 235, 110, "_Measures", "Total Requisitions"),
    make_card("p4_open", 270, 10, 235, 110, "_Measures", "Open Requisitions"),
    make_card("p4_ttf", 520, 10, 235, 110, "_Measures", "Avg Time to Fill"),
    make_card("p4_accept", 770, 10, 235, 110, "_Measures", "Offer Acceptance Rate"),
    make_slicer("p4_dept_slicer", 1020, 10, 230, 110, "DimDepartment", "department_name"),
    make_clustered_bar("p4_hires_bar", 20, 140, 400, 280, "DimDepartment", "department_name", "_Measures", "Total Hires"),
    make_line_chart("p4_hires_line", 440, 140, 400, 280, "Calendar", "Year_Month", "_Measures", "Total Hires"),
    make_donut("p4_level_donut", 860, 140, 380, 280, "DimJobLevel", "level_name", "_Measures", "Total Requisitions"),
    make_table("p4_table", 20, 440, 1230, 260, [
        ("DimDepartment", "department_name", False),
        ("_Measures", "Total Requisitions", True),
        ("_Measures", "Open Requisitions", True),
        ("_Measures", "Total Applications", True),
        ("_Measures", "Total Hires", True),
        ("_Measures", "Avg Time to Fill", True),
        ("_Measures", "Offer Acceptance Rate", True),
        ("_Measures", "Applications per Hire", True),
    ]),
]

# Remove old default page
import shutil
old_page = os.path.join(BASE, "fb246be40cecd8b9c4f8")
if os.path.exists(old_page):
    shutil.rmtree(old_page)

# Write all pages
write_page(p1_id, "Workforce Overview", p1_visuals)
write_page(p2_id, "Attrition Analysis", p2_visuals)
write_page(p3_id, "Compensation & Equity", p3_visuals)
write_page(p4_id, "Recruitment Funnel", p4_visuals)

# Update pages.json
pages_meta = {
    "$schema": SCHEMA_PAGES,
    "pageOrder": [p1_id, p2_id, p3_id, p4_id],
    "activePageName": p1_id
}
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump(pages_meta, f, indent=2, ensure_ascii=False)

print(f"Page 1 (Workforce Overview): {p1_id} — {len(p1_visuals)} visuals")
print(f"Page 2 (Attrition Analysis): {p2_id} — {len(p2_visuals)} visuals")
print(f"Page 3 (Compensation & Equity): {p3_id} — {len(p3_visuals)} visuals")
print(f"Page 4 (Recruitment Funnel): {p4_id} — {len(p4_visuals)} visuals")
print("Done! pages.json updated.")
