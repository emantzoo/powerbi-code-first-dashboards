import json, os, hashlib, shutil

# Update this path to your .pbip report folder
BASE = r"C:\YOUR_SAVE_PATH\FinanceDashboard.Report\definition\pages"

SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"

def uid(seed):
    return hashlib.md5(seed.encode()).hexdigest()[:20]

def measure_field(table, measure):
    return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": table}}, "Property": measure}},
            "queryRef": f"{table}.{measure}", "nativeQueryRef": measure}

def column_field(table, column):
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": column}},
            "queryRef": f"{table}.{column}", "nativeQueryRef": column}

def make_visual(name, x, y, w, h, vtype, query_state, z=1000):
    return {"$schema": SCHEMA_VISUAL, "name": uid(name),
            "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
            "visual": {"visualType": vtype, "query": {"queryState": query_state}, "drillFilterOtherVisuals": True}}

def make_card(name, x, y, w, h, table, measure):
    return make_visual(name, x, y, w, h, "cardVisual", {"Data": {"projections": [measure_field(table, measure)]}})

def make_slicer(name, x, y, w, h, table, column):
    return make_visual(name, x, y, w, h, "slicer", {"Values": {"projections": [column_field(table, column)]}})

def make_clustered_bar(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_clustered_column(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_line_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, val2_table=None, val2_measure=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Y": {"projections": [measure_field(val_table, val_measure)]}}
    if val2_table and val2_measure:
        qs["Y"]["projections"].append(measure_field(val2_table, val2_measure))
    return make_visual(name, x, y, w, h, "lineChart", qs)

def make_area_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "areaChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_donut(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "donutChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_pie(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "pieChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_table(name, x, y, w, h, fields_list):
    projections = [measure_field(t, c) if m else column_field(t, c) for t, c, m in fields_list]
    return make_visual(name, x, y, w, h, "tableEx", {"Values": {"projections": projections}})

def make_matrix(name, x, y, w, h, row_fields, col_fields, val_fields):
    rows = [column_field(t, c) for t, c in row_fields]
    cols = [column_field(t, c) for t, c in col_fields] if col_fields else []
    vals = [measure_field(t, m) for t, m in val_fields]
    qs = {"Rows": {"projections": rows}, "Values": {"projections": vals}}
    if cols:
        qs["Columns"] = {"projections": cols}
    return make_visual(name, x, y, w, h, "pivotTable", qs)

def make_gauge(name, x, y, w, h, val_table, val_measure, target_table=None, target_measure=None, min_table=None, min_measure=None, max_table=None, max_measure=None):
    qs = {"Y": {"projections": [measure_field(val_table, val_measure)]}}
    if target_table and target_measure:
        qs["TargetValue"] = {"projections": [measure_field(target_table, target_measure)]}
    if min_table and min_measure:
        qs["MinValue"] = {"projections": [measure_field(min_table, min_measure)]}
    if max_table and max_measure:
        qs["MaxValue"] = {"projections": [measure_field(max_table, max_measure)]}
    return make_visual(name, x, y, w, h, "gauge", qs)

def make_waterfall(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "waterfallChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_funnel(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "funnel",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_scatter(name, x, y, w, h, detail_table, detail_col, x_table, x_measure, y_table, y_measure, size_table=None, size_measure=None):
    qs = {"Category": {"projections": [column_field(detail_table, detail_col)]},
          "X": {"projections": [measure_field(x_table, x_measure)]},
          "Y": {"projections": [measure_field(y_table, y_measure)]}}
    if size_table and size_measure:
        qs["Size"] = {"projections": [measure_field(size_table, size_measure)]}
    return make_visual(name, x, y, w, h, "scatterChart", qs)

def make_ribbon(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "ribbonChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_stacked_column(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_stacked_bar(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_hundred_pct_stacked_bar(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "hundredPercentStackedBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_hundred_pct_stacked_column(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "hundredPercentStackedColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_filled_map(name, x, y, w, h, loc_table, loc_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "filledMap",
        {"Category": {"projections": [column_field(loc_table, loc_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_treemap(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, group_table=None, group_col=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Values": {"projections": [measure_field(val_table, val_measure)]}}
    if group_table and group_col:
        qs["Group"] = {"projections": [column_field(group_table, group_col)]}
    return make_visual(name, x, y, w, h, "treemap", qs)

def write_visual(page_dir, visual_json):
    vdir = os.path.join(page_dir, "visuals", visual_json["name"])
    os.makedirs(vdir, exist_ok=True)
    with open(os.path.join(vdir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(visual_json, f, indent=2, ensure_ascii=False)

def write_page(page_id, display_name, visuals):
    page_dir = os.path.join(BASE, page_id)
    visuals_dir = os.path.join(page_dir, "visuals")
    if os.path.exists(visuals_dir):
        shutil.rmtree(visuals_dir)
    os.makedirs(visuals_dir, exist_ok=True)
    with open(os.path.join(page_dir, "page.json"), "w", encoding="utf-8") as f:
        json.dump({"$schema": SCHEMA_PAGE, "name": page_id, "displayName": display_name,
                    "displayOption": "FitToPage", "height": 720, "width": 1280}, f, indent=2)
    for v in visuals:
        write_visual(page_dir, v)

# ===== PAGE 1: Financial Overview =====
p1_id = uid("fin_page1_overview")
p1 = [
    make_card("fin1_actuals", 20, 10, 235, 110, "_Measures", "Total Actuals"),
    make_card("fin1_budget", 270, 10, 235, 110, "_Measures", "Total Budget"),
    make_card("fin1_variance", 520, 10, 235, 110, "_Measures", "Budget Variance"),
    make_card("fin1_util", 770, 10, 235, 110, "_Measures", "Budget Utilization"),
    make_slicer("fin1_year", 1020, 10, 230, 110, "Calendar", "Year"),
    make_line_chart("fin1_trend", 20, 140, 610, 280, "Calendar", "Year_Month",
        "_Measures", "Total Actuals", "_Measures", "Total Budget"),
    make_waterfall("fin1_waterfall", 650, 140, 600, 280, "DimDepartment", "department_name",
        "_Measures", "Budget Variance"),
    make_table("fin1_table", 20, 440, 1230, 260, [
        ("DimDepartment", "department_name", False),
        ("_Measures", "Total Actuals", True),
        ("_Measures", "Total Budget", True),
        ("_Measures", "Budget Variance", True),
        ("_Measures", "Budget Variance Pct", True),
        ("_Measures", "Budget Utilization", True),
    ]),
]

# ===== PAGE 2: Variance Analysis =====
p2_id = uid("fin_page2_variance")
p2 = [
    make_card("fin2_variance", 20, 10, 235, 110, "_Measures", "Budget Variance"),
    make_card("fin2_var_pct", 270, 10, 235, 110, "_Measures", "Budget Variance Pct"),
    make_card("fin2_yoy", 520, 10, 235, 110, "_Measures", "Actuals YoY Growth"),
    make_card("fin2_avg_monthly", 770, 10, 235, 110, "_Measures", "Avg Monthly Spend"),
    make_slicer("fin2_dept", 1020, 10, 230, 110, "DimDepartment", "department_name"),
    make_clustered_bar("fin2_cc_var", 20, 140, 610, 280, "DimCostCenter", "cost_center_name",
        "_Measures", "Budget Variance"),
    make_clustered_bar("fin2_acc_var", 650, 140, 600, 280, "DimAccount", "account_name",
        "_Measures", "Budget Variance"),
    make_matrix("fin2_matrix", 20, 440, 1230, 260,
        [("DimAccount", "account_name")], [("Calendar", "Year")],
        [("_Measures", "Total Actuals"), ("_Measures", "Total Budget"), ("_Measures", "Budget Variance")]),
]

# ===== PAGE 3: Department Spend =====
p3_id = uid("fin_page3_department")
p3 = [
    make_card("fin3_actuals", 20, 10, 235, 110, "_Measures", "Total Actuals"),
    make_card("fin3_txns", 270, 10, 235, 110, "_Measures", "Total Transactions"),
    make_card("fin3_vendors", 520, 10, 235, 110, "_Measures", "Unique Vendors"),
    make_card("fin3_pct", 770, 10, 235, 110, "_Measures", "Pct of Total Spend"),
    make_slicer("fin3_dept", 1020, 10, 230, 110, "DimDepartment", "department_name"),
    make_donut("fin3_dept_donut", 20, 140, 400, 280, "DimDepartment", "department_name",
        "_Measures", "Total Actuals"),
    make_clustered_bar("fin3_acc_bar", 440, 140, 400, 280, "DimAccount", "account_name",
        "_Measures", "Total Actuals"),
    make_gauge("fin3_gauge", 860, 140, 380, 280, "_Measures", "Budget Utilization"),
    make_table("fin3_table", 20, 440, 1230, 260, [
        ("DimCostCenter", "cost_center_name", False),
        ("DimCostCenter", "region", False),
        ("_Measures", "Total Actuals", True),
        ("_Measures", "Total Budget", True),
        ("_Measures", "Budget Variance", True),
        ("_Measures", "Budget Variance Pct", True),
    ]),
]

# ===== PAGE 4: Account Detail =====
p4_id = uid("fin_page4_account")
p4 = [
    make_card("fin4_actuals", 20, 10, 295, 110, "_Measures", "Total Actuals"),
    make_card("fin4_ytd", 330, 10, 295, 110, "_Measures", "Actuals YTD"),
    make_card("fin4_py", 640, 10, 295, 110, "_Measures", "Actuals PY"),
    make_card("fin4_yoy", 950, 10, 295, 110, "_Measures", "Actuals YoY Growth"),
    make_line_chart("fin4_trend", 20, 140, 610, 280, "Calendar", "Year_Month",
        "_Measures", "Total Actuals", "_Measures", "Actuals PY"),
    make_pie("fin4_type_pie", 650, 140, 290, 280, "DimAccount", "account_type",
        "_Measures", "Total Actuals"),
    make_clustered_bar("fin4_group_bar", 960, 140, 290, 280, "DimAccount", "account_group",
        "_Measures", "Total Actuals"),
    make_table("fin4_table", 20, 440, 1230, 260, [
        ("DimAccount", "account_name", False),
        ("DimAccount", "account_type", False),
        ("_Measures", "Total Actuals", True),
        ("_Measures", "Total Budget", True),
        ("_Measures", "Budget Variance", True),
        ("_Measures", "Budget Variance Pct", True),
        ("_Measures", "Avg Transaction Amount", True),
    ]),
]

# Write all pages
write_page(p1_id, "Financial Overview", p1)
write_page(p2_id, "Variance Analysis", p2)
write_page(p3_id, "Department Spend", p3)
write_page(p4_id, "Account Detail", p4)

# Update pages.json
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, p3_id, p4_id],
               "activePageName": p1_id}, f, indent=2)

print(f"Page 1 (Financial Overview): {p1_id} - {len(p1)} visuals")
print(f"Page 2 (Variance Analysis): {p2_id} - {len(p2)} visuals")
print(f"Page 3 (Department Spend): {p3_id} - {len(p3)} visuals")
print(f"Page 4 (Account Detail): {p4_id} - {len(p4)} visuals")
print("Done!")
