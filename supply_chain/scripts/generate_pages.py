import json, os, hashlib, shutil

BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\supply_chain\supplyChain_dashb.Report\definition\pages"
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

def make_map(name, x, y, w, h, cat_table, cat_col, lat_table, lat_col, lng_table, lng_col, size_table, size_measure):
    return make_visual(name, x, y, w, h, "map",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [column_field(lat_table, lat_col)]},
         "X": {"projections": [column_field(lng_table, lng_col)]},
         "Size": {"projections": [measure_field(size_table, size_measure)]}})

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
    os.makedirs(os.path.join(page_dir, "visuals"), exist_ok=True)
    with open(os.path.join(page_dir, "page.json"), "w", encoding="utf-8") as f:
        json.dump({"$schema": SCHEMA_PAGE, "name": page_id, "displayName": display_name,
                    "displayOption": "FitToPage", "height": 720, "width": 1280}, f, indent=2)
    for v in visuals:
        write_visual(page_dir, v)

# ===== PAGE 1: Supply Chain KPIs =====
p1_id = uid("sc_page1_kpis")
p1 = [
    make_card("sc1_orders", 20, 10, 190, 110, "_Measures", "Total Orders"),
    make_card("sc1_value", 225, 10, 190, 110, "_Measures", "Total Order Value"),
    make_card("sc1_otd", 430, 10, 190, 110, "_Measures", "On Time Delivery Rate"),
    make_card("sc1_stockout", 635, 10, 190, 110, "_Measures", "Stockout Rate"),
    make_card("sc1_util", 840, 10, 190, 110, "_Measures", "Warehouse Utilization"),
    make_slicer("sc1_year", 1045, 10, 210, 110, "Calendar", "Year"),
    make_line_chart("sc1_value_trend", 20, 140, 410, 280, "Calendar", "Year_Month", "_Measures", "Total Order Value", "_Measures", "Order Value PY"),
    make_clustered_bar("sc1_cat_bar", 450, 140, 400, 280, "DimProduct", "category", "_Measures", "Total Order Value"),
    make_donut("sc1_wh_donut", 870, 140, 370, 280, "DimWarehouse", "warehouse_name", "_Measures", "Total Quantity Ordered"),
    make_area_chart("sc1_otd_area", 20, 440, 610, 260, "Calendar", "Year_Month", "_Measures", "On Time Delivery Rate"),
    make_clustered_bar("sc1_lead_bar", 650, 440, 600, 260, "DimSupplier", "supplier_name", "_Measures", "Avg Lead Time Days"),
]

# ===== PAGE 2: Supplier Scorecard =====
p2_id = uid("sc_page2_supplier")
p2 = [
    make_card("sc2_suppliers", 20, 10, 235, 110, "_Measures", "Unique Suppliers Used"),
    make_card("sc2_reliability", 270, 10, 235, 110, "_Measures", "Supplier Avg Reliability"),
    make_card("sc2_variance", 520, 10, 235, 110, "_Measures", "Avg Lead Time Variance"),
    make_card("sc2_otd_change", 770, 10, 235, 110, "_Measures", "On Time Rate Change"),
    make_slicer("sc2_country", 1020, 10, 230, 110, "DimSupplier", "country"),
    make_clustered_bar("sc2_otd_bar", 20, 140, 610, 280, "DimSupplier", "supplier_name", "_Measures", "On Time Delivery Rate"),
    make_clustered_bar("sc2_value_bar", 650, 140, 600, 280, "DimSupplier", "supplier_name", "_Measures", "Total Order Value"),
    make_table("sc2_table", 20, 440, 1230, 260, [
        ("DimSupplier", "supplier_name", False),
        ("DimSupplier", "country", False),
        ("DimSupplier", "lead_time_days", False),
        ("DimSupplier", "reliability_rating", False),
        ("_Measures", "Total Orders", True),
        ("_Measures", "On Time Delivery Rate", True),
        ("_Measures", "Avg Lead Time Days", True),
        ("_Measures", "Avg Lead Time Variance", True),
        ("_Measures", "Total Order Value", True),
    ]),
]

# ===== PAGE 3: Inventory Health =====
p3_id = uid("sc_page3_inventory")
p3 = [
    make_card("sc3_onhand", 20, 10, 235, 110, "_Measures", "Latest Inventory On Hand"),
    make_card("sc3_avail", 270, 10, 235, 110, "_Measures", "Available Inventory"),
    make_card("sc3_stockout", 520, 10, 235, 110, "_Measures", "Stockout Rate"),
    make_card("sc3_dos", 770, 10, 235, 110, "_Measures", "Days of Supply"),
    make_slicer("sc3_cat", 1020, 10, 230, 110, "DimProduct", "category"),
    make_line_chart("sc3_inv_trend", 20, 140, 610, 280, "Calendar", "Year_Month", "_Measures", "Latest Inventory On Hand"),
    make_clustered_bar("sc3_stockout_bar", 650, 140, 600, 280, "DimProduct", "category", "_Measures", "Stockout Count"),
    make_matrix("sc3_matrix", 20, 440, 1230, 260,
        [("DimWarehouse", "warehouse_name")], [],
        [("_Measures", "Latest Inventory On Hand"), ("_Measures", "Available Inventory"),
         ("_Measures", "Warehouse Utilization"), ("_Measures", "Stockout Count"),
         ("_Measures", "Stockout Rate"), ("_Measures", "Below Reorder Point"),
         ("_Measures", "Inventory Turnover")]),
]

# ===== PAGE 4: Global Logistics Map =====
p4_id = uid("sc_page4_map")
p4 = [
    make_card("sc4_shipments", 20, 10, 295, 60, "_Measures", "Route Shipment Count"),
    make_card("sc4_transit", 330, 10, 295, 60, "_Measures", "Route Avg Transit Days"),
    make_card("sc4_ontime", 640, 10, 295, 60, "_Measures", "Route On Time Pct"),
    make_card("sc4_cost", 950, 10, 295, 60, "_Measures", "Route Total Cost"),
    make_treemap("sc4_supplier_treemap", 20, 80, 420, 350, "DimSupplier", "city", "_Measures", "Total Orders", "DimSupplier", "country"),
    make_filled_map("sc4_wh_map", 460, 80, 790, 350, "DimWarehouse", "country", "_Measures", "Total Orders"),
    make_table("sc4_table", 20, 440, 1230, 260, [
        ("FactShipmentRoutes", "supplier_name", False),
        ("FactShipmentRoutes", "supplier_country", False),
        ("FactShipmentRoutes", "warehouse_name", False),
        ("FactShipmentRoutes", "warehouse_country", False),
        ("FactShipmentRoutes", "total_shipments", False),
        ("FactShipmentRoutes", "avg_transit_days", False),
        ("FactShipmentRoutes", "on_time_pct", False),
        ("FactShipmentRoutes", "total_cost", False),
    ]),
]

# ===== PAGE 5: Warehouse Comparison =====
p5_id = uid("sc_page5_warehouse")
p5 = [
    make_card("sc5_orders", 20, 10, 235, 110, "_Measures", "Total Orders"),
    make_card("sc5_value", 270, 10, 235, 110, "_Measures", "Total Order Value"),
    make_card("sc5_util", 520, 10, 235, 110, "_Measures", "Warehouse Utilization"),
    make_card("sc5_stockout", 770, 10, 235, 110, "_Measures", "Stockout Rate"),
    make_slicer("sc5_wh", 1020, 10, 230, 110, "DimWarehouse", "warehouse_name"),
    make_clustered_bar("sc5_cat_bar", 20, 140, 400, 280, "DimProduct", "category", "_Measures", "Total Quantity Ordered"),
    make_donut("sc5_sup_donut", 440, 140, 380, 280, "DimSupplier", "supplier_name", "_Measures", "Total Orders"),
    make_line_chart("sc5_inv_trend", 840, 140, 410, 280, "Calendar", "Year_Month", "_Measures", "Latest Inventory On Hand"),
    make_table("sc5_table", 20, 440, 1230, 260, [
        ("DimProduct", "product_name", False),
        ("DimProduct", "category", False),
        ("_Measures", "Total Quantity Ordered", True),
        ("_Measures", "Latest Inventory On Hand", True),
        ("_Measures", "Available Inventory", True),
        ("_Measures", "Stockout Count", True),
        ("_Measures", "Below Reorder Point", True),
    ]),
]

# Remove old default page
old_page = os.path.join(BASE, "f198b33e9cfe0eb15121")
if os.path.exists(old_page):
    shutil.rmtree(old_page)

# Write all pages
write_page(p1_id, "Supply Chain KPIs", p1)
write_page(p2_id, "Supplier Scorecard", p2)
write_page(p3_id, "Inventory Health", p3)
write_page(p4_id, "Global Logistics Map", p4)
write_page(p5_id, "Warehouse Comparison", p5)

# Update pages.json
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, p3_id, p4_id, p5_id],
               "activePageName": p1_id}, f, indent=2)

print(f"Page 1 (Supply Chain KPIs): {p1_id} - {len(p1)} visuals")
print(f"Page 2 (Supplier Scorecard): {p2_id} - {len(p2)} visuals")
print(f"Page 3 (Inventory Health): {p3_id} - {len(p3)} visuals")
print(f"Page 4 (Global Logistics Map): {p4_id} - {len(p4)} visuals")
print(f"Page 5 (Warehouse Comparison): {p5_id} - {len(p5)} visuals")
print("Done!")
