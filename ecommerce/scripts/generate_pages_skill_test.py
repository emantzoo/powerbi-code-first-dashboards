import json, os, hashlib, shutil

# 1. BASE path — update this to your .pbip report folder
BASE = r"C:\Users\emant\Downloads\powerBI_recipes\Ecommerce\ECommerceDashboard.Report\definition\pages"

# 2. Schema constants
SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"

# 3. Helper functions
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

# ===== PAGE 1: Executive Overview =====
p1_id = uid("ec_page1_overview")
p1 = [
    make_card("ec1_revenue", 20, 10, 295, 110, "_Measures", "Total Revenue"),
    make_card("ec1_profit", 330, 10, 295, 110, "_Measures", "Total Profit"),
    make_card("ec1_margin", 640, 10, 295, 110, "_Measures", "Profit Margin"),
    make_card("ec1_orders", 950, 10, 295, 110, "_Measures", "Total Orders"),
    make_clustered_bar("ec1_cat_bar", 20, 140, 400, 280, "DimProduct", "category", "_Measures", "Total Revenue"),
    make_line_chart("ec1_trend", 440, 140, 400, 280, "Calendar", "Year_Month", "_Measures", "Total Revenue"),
    make_donut("ec1_channel", 860, 140, 380, 280, "DimStore", "channel", "_Measures", "Total Revenue"),
    make_area_chart("ec1_profit_trend", 20, 440, 600, 260, "Calendar", "Year_Month", "_Measures", "Total Profit"),
    make_slicer("ec1_year", 640, 440, 200, 260, "Calendar", "Year"),
    make_clustered_bar("ec1_region", 860, 440, 380, 260, "DimStore", "region", "_Measures", "Total Orders"),
]

# ===== PAGE 2: Product Performance =====
p2_id = uid("ec_page2_product")
p2 = [
    make_card("ec2_revenue", 20, 10, 235, 110, "_Measures", "Total Revenue"),
    make_card("ec2_aov", 270, 10, 235, 110, "_Measures", "Avg Order Value"),
    make_card("ec2_qty", 520, 10, 235, 110, "_Measures", "Total Quantity"),
    make_card("ec2_return_rate", 770, 10, 235, 110, "_Measures", "Return Rate"),
    make_slicer("ec2_cat_slicer", 1020, 10, 230, 110, "DimProduct", "category"),
    make_clustered_bar("ec2_subcat", 20, 140, 610, 280, "DimProduct", "subcategory", "_Measures", "Total Revenue"),
    make_clustered_bar("ec2_brand", 650, 140, 600, 280, "DimProduct", "brand", "_Measures", "Total Profit"),
    make_table("ec2_detail", 20, 440, 1230, 260, [
        ("DimProduct", "category", False),
        ("DimProduct", "subcategory", False),
        ("DimProduct", "brand", False),
        ("_Measures", "Total Revenue", True),
        ("_Measures", "Total Profit", True),
        ("_Measures", "Profit Margin", True),
        ("_Measures", "Total Quantity", True),
        ("_Measures", "Return Rate", True),
    ]),
]

# ===== PAGE 3: Customer & Trends =====
p3_id = uid("ec_page3_customer")
p3 = [
    make_card("ec3_customers", 20, 10, 295, 110, "_Measures", "Total Customers"),
    make_card("ec3_yoy", 330, 10, 295, 110, "_Measures", "Revenue YoY Growth"),
    make_card("ec3_ytd", 640, 10, 295, 110, "_Measures", "Revenue YTD"),
    make_card("ec3_l12m", 950, 10, 295, 110, "_Measures", "Revenue L12M"),
    make_line_chart("ec3_rev_trend", 20, 140, 610, 280, "Calendar", "Year_Month", "_Measures", "Total Revenue", "_Measures", "Revenue PY"),
    make_donut("ec3_segment", 650, 140, 290, 280, "DimCustomer", "segment", "_Measures", "Total Revenue"),
    make_clustered_bar("ec3_country", 960, 140, 290, 280, "DimCustomer", "country", "_Measures", "Total Customers"),
    make_matrix("ec3_matrix", 20, 440, 1230, 260,
        [("DimCustomer", "country")], [("Calendar", "Year")],
        [("_Measures", "Total Revenue"), ("_Measures", "Total Orders")]),
]

# ===== PAGE 4: Returns Analysis =====
p4_id = uid("ec_page4_returns")
p4 = [
    make_card("ec4_returns", 20, 10, 295, 110, "_Measures", "Total Returns"),
    make_card("ec4_refunds", 330, 10, 295, 110, "_Measures", "Total Refunds"),
    make_card("ec4_return_rate", 640, 10, 295, 110, "_Measures", "Return Rate"),
    make_card("ec4_net_rev", 950, 10, 295, 110, "_Measures", "Net Revenue"),
    make_clustered_bar("ec4_reason", 20, 140, 400, 280, "FactReturns", "reason_code", "_Measures", "Total Returns"),
    make_line_chart("ec4_trend", 440, 140, 400, 280, "Calendar", "Year_Month", "_Measures", "Returns by Date"),
    make_donut("ec4_cat_donut", 860, 140, 380, 280, "DimProduct", "category", "_Measures", "Total Returns"),
    make_table("ec4_detail", 20, 440, 1230, 260, [
        ("FactReturns", "reason_code", False),
        ("_Measures", "Total Returns", True),
        ("_Measures", "Total Refunds", True),
        ("_Measures", "Return Rate", True),
    ]),
]

# Write all pages
write_page(p1_id, "Executive Overview", p1)
write_page(p2_id, "Product Performance", p2)
write_page(p3_id, "Customer & Trends", p3)
write_page(p4_id, "Returns Analysis", p4)

# Update pages.json
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, p3_id, p4_id],
               "activePageName": p1_id}, f, indent=2)

print(f"Page 1 (Executive Overview): {p1_id} - {len(p1)} visuals")
print(f"Page 2 (Product Performance): {p2_id} - {len(p2)} visuals")
print(f"Page 3 (Customer & Trends): {p3_id} - {len(p3)} visuals")
print(f"Page 4 (Returns Analysis): {p4_id} - {len(p4)} visuals")
print("Done!")
