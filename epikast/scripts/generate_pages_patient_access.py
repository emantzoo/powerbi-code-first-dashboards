"""
PBIR Visual Generator — Epikast Patient Access Funnel Dashboard (3 pages).
Funnel overview, PA/insurance analysis, adherence decay.
"""

import json, os, hashlib, shutil

BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\epikast\epikast_patient_dashb\epikast_patient_dashb.Report\definition\pages"

SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"
SCHEMA_PAGE   = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"

def _lit(value):
    return {"expr": {"Literal": {"Value": value}}}

def _solid(hex_color):
    return {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hex_color}'"}}}}}

def _theme_color(color_id, percent=0):
    return {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": color_id, "Percent": percent}}}}}

def _card_objects():
    return {
        "layout": [
            {"properties": {"style": _lit("'Table'"), "orientation": _lit("1D"), "rowCount": _lit("5L"), "contentOrder": _lit("'referenceLabel_callout_image'")}},
            {"properties": {"rectangleRoundedCurve": _lit("8L"), "paddingUniform": _lit("10L"), "backgroundTransparency": _lit("0D")}, "selector": {"id": "default"}}
        ],
        "accentBar": [{"properties": {"show": _lit("true")}, "selector": {"id": "default"}}],
        "shadowCustom": [{"properties": {"show": _lit("true")}, "selector": {"id": "default"}}],
        "shapeCustomRectangle": [{"properties": {"tileShape": _lit("'rectangleRoundedByPixel'")}, "selector": {"id": "default"}}]
    }

def _chart_objects(show_labels=False, label_position="'OutsideEnd'"):
    obj = {
        "categoryAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false")}}],
        "valueAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false"), "gridlineStyle": _lit("'dashed'"), "gridlineColor": _solid("#E2E8F0")}}]
    }
    if show_labels:
        obj["labels"] = [{"properties": {"show": _lit("true"), "labelPosition": _lit(label_position), "fontSize": _lit("9L")}}]
    return obj

def _line_chart_objects():
    return {
        "categoryAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false")}}],
        "valueAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false"), "gridlineStyle": _lit("'dashed'"), "gridlineColor": _solid("#E2E8F0")}}],
        "lineStyles": [{"properties": {"strokeWidth": _lit("3L")}}]
    }

def _table_objects():
    return {
        "columnHeaders": [{"properties": {"bold": _lit("true"), "fontSize": _lit("10L"), "fontColor": _solid("#FFFFFF"), "backColor": _theme_color(0)}}],
        "values": [{"properties": {"fontSize": _lit("10L"), "backColor": _solid("#FFFFFF"), "backColorAlternate": _solid("#F8FAFC")}}],
        "grid": [{"properties": {"gridHorizontal": _lit("true"), "gridHorizontalColor": _solid("#E2E8F0"), "gridVertical": _lit("false"), "rowPadding": _lit("4L")}}]
    }

def _matrix_objects():
    return {
        "columnHeaders": [{"properties": {"bold": _lit("true"), "fontSize": _lit("10L"), "fontColor": _solid("#FFFFFF"), "backColor": _theme_color(0)}}],
        "rowHeaders": [{"properties": {"fontSize": _lit("10L")}}],
        "values": [{"properties": {"fontSize": _lit("10L"), "backColor": _solid("#FFFFFF"), "backColorAlternate": _solid("#F8FAFC")}}],
        "grid": [{"properties": {"gridHorizontal": _lit("true"), "gridHorizontalColor": _solid("#E2E8F0"), "gridVertical": _lit("false"), "rowPadding": _lit("4L")}}]
    }

def _slicer_objects():
    return {}

def uid(seed):
    return hashlib.md5(seed.encode()).hexdigest()[:20]

def measure_field(table, measure):
    return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": table}}, "Property": measure}},
            "queryRef": f"{table}.{measure}", "nativeQueryRef": measure}

def column_field(table, column):
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": column}},
            "queryRef": f"{table}.{column}", "nativeQueryRef": column}

def make_visual(name, x, y, w, h, vtype, query_state=None, objects=None, visual_container_objects=None, z=1000, how_created=None):
    v = {"$schema": SCHEMA_VISUAL, "name": uid(name),
         "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
         "visual": {"visualType": vtype, "drillFilterOtherVisuals": True}}
    if query_state:
        v["visual"]["query"] = {"queryState": query_state}
    if objects:
        v["visual"]["objects"] = objects
    if visual_container_objects:
        v["visual"]["visualContainerObjects"] = visual_container_objects
    if how_created:
        v["howCreated"] = how_created
    return v

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

def make_card(name, x, y, w, h, table, measure):
    return make_visual(name, x, y, w, h, "cardVisual",
        {"Data": {"projections": [measure_field(table, measure)]}},
        objects=_card_objects())

def make_slicer(name, x, y, w, h, table, column):
    return make_visual(name, x, y, w, h, "slicer",
        {"Values": {"projections": [column_field(table, column)]}},
        objects=_slicer_objects())

def make_clustered_bar(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_line_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, val2_table=None, val2_measure=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Y": {"projections": [measure_field(val_table, val_measure)]}}
    if val2_table and val2_measure:
        qs["Y"]["projections"].append(measure_field(val2_table, val2_measure))
    return make_visual(name, x, y, w, h, "lineChart", qs, objects=_line_chart_objects())

def make_funnel(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "funnel",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_table(name, x, y, w, h, fields_list):
    projections = [measure_field(t, c) if m else column_field(t, c) for t, c, m in fields_list]
    return make_visual(name, x, y, w, h, "tableEx",
        {"Values": {"projections": projections}},
        objects=_table_objects())

def make_matrix(name, x, y, w, h, row_fields, col_fields, val_fields):
    rows = [column_field(t, c) for t, c in row_fields]
    cols = [column_field(t, c) for t, c in col_fields] if col_fields else []
    vals = [measure_field(t, m) for t, m in val_fields]
    qs = {"Rows": {"projections": rows}, "Values": {"projections": vals}}
    if cols:
        qs["Columns"] = {"projections": cols}
    return make_visual(name, x, y, w, h, "pivotTable", qs, objects=_matrix_objects())

def make_title_bar(name, x, y, w, h, text, bg_color="#1B3A5C"):
    return make_visual(name, x, y, w, h, "textbox",
        objects={"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "18px", "color": "#FFFFFF"}}]}]}}]},
        visual_container_objects={
            "background": [{"properties": {"show": _lit("true"), "color": _solid(bg_color), "transparency": _lit("0D")}}],
            "visualHeader": [{"properties": {"show": _lit("false")}}]
        }, z=9000)


# ═══════════════════════════════════════════════════════════════════════════
# Page 1: Funnel Overview
# ═══════════════════════════════════════════════════════════════════════════

p1_id = uid("ep_patient_funnel_overview")
p1 = [
    make_title_bar("pa_title", 0, 0, 1280, 50, "Patient Access \u2014 Funnel Overview"),
    # 5 KPI cards (w=186, gap=12)
    make_card("pa_total_cases",  20,  60, 186, 120, "_Measures", "Total Cases"),
    make_card("pa_abandon_rate", 218, 60, 186, 120, "_Measures", "Abandonment Rate"),
    make_card("pa_ttt",          416, 60, 186, 120, "_Measures", "Avg Time to Therapy"),
    make_card("pa_pa_rate",      614, 60, 186, 120, "_Measures", "PA Approval Rate"),
    make_card("pa_48h",          812, 60, 186, 120, "_Measures", "Contacted Within 48h Rate"),
    # 4 slicers stacked right
    make_slicer("pa_sl_qtr",   1010, 60,  250, 28, "DimCalendar", "Quarter"),
    make_slicer("pa_sl_ins",   1010, 93,  250, 28, "DimPatient", "InsuranceType"),
    make_slicer("pa_sl_ther",  1010, 126, 250, 28, "DimRep", "TherapyArea"),
    make_slicer("pa_sl_drug",  1010, 159, 250, 28, "DimDrug", "DrugName"),
    # Funnel (left): PA Status distribution
    make_funnel("pa_funnel", 20, 195, 740, 310,
        "FactPatientCases", "PAStatus", "_Measures", "Total Cases"),
    # Bar (right): Where patients drop off
    make_clustered_bar("pa_dropout_bar", 775, 195, 485, 310,
        "FactPatientCases", "AbandonmentStage", "_Measures", "Abandoned Cases"),
    # Table at bottom
    make_table("pa_summary", 20, 520, 1240, 180, [
        ("FactPatientCases", "PAStatus", False),
        ("_Measures", "Total Cases", True),
        ("_Measures", "Abandonment Rate", True),
        ("_Measures", "Avg Time to Therapy", True),
        ("_Measures", "PA Approval Rate", True),
    ]),
]


# ═══════════════════════════════════════════════════════════════════════════
# Page 2: PA and Insurance
# ═══════════════════════════════════════════════════════════════════════════

p2_id = uid("ep_patient_pa_insurance")
p2 = [
    make_title_bar("pb_title", 0, 0, 1280, 50, "Patient Access \u2014 PA & Insurance"),
    # Top row: 2 bars side by side
    make_clustered_bar("pb_pa_outcome", 20, 60, 610, 270,
        "FactPatientCases", "InsuranceType", "_Measures", "PA Approval Rate"),
    make_clustered_bar("pb_pa_delay", 645, 60, 615, 270,
        "FactPatientCases", "InsuranceType", "_Measures", "Avg PA Decision Delay"),
    # Bottom left: Line chart — PA approval trend
    make_line_chart("pb_approval_trend", 20, 345, 610, 250,
        "DimCalendar", "YearMonth", "_Measures", "PA Approval Rate", "_Measures", "PA Denial Rate"),
    # Bottom right: Insurance summary table
    make_table("pb_ins_table", 645, 345, 615, 250, [
        ("FactPatientCases", "InsuranceType", False),
        ("_Measures", "Total Cases", True),
        ("_Measures", "PA Approval Rate", True),
        ("_Measures", "PA Denial Rate", True),
        ("_Measures", "Avg PA Decision Delay", True),
        ("_Measures", "Abandonment Rate", True),
        ("_Measures", "Avg Time to Therapy", True),
    ]),
    # Slicers
    make_slicer("pb_sl_qtr",  20,  610, 200, 35, "DimCalendar", "Quarter"),
    make_slicer("pb_sl_drug", 230, 610, 200, 35, "DimDrug", "DrugName"),
]


# ═══════════════════════════════════════════════════════════════════════════
# Page 3: Adherence
# ═══════════════════════════════════════════════════════════════════════════

p3_id = uid("ep_patient_adherence")
p3 = [
    make_title_bar("pc_title", 0, 0, 1280, 50, "Patient Access \u2014 Adherence"),
    # 3 cards
    make_card("pc_adh30", 20,  60, 300, 120, "_Measures", "Adherence 30 Day"),
    make_card("pc_adh60", 335, 60, 300, 120, "_Measures", "Adherence 60 Day"),
    make_card("pc_adh90", 650, 60, 300, 120, "_Measures", "Adherence 90 Day"),
    # Slicers
    make_slicer("pc_sl_ins",  965, 60,  295, 55, "FactPatientCases", "InsuranceType"),
    make_slicer("pc_sl_drug", 965, 120, 295, 55, "DimDrug", "DrugName"),
    # Matrix: Adherence by Therapy Area
    make_matrix("pc_adh_matrix", 20, 195, 1240, 260,
        [("DimPatient", "TherapyArea")],
        [],
        [("_Measures", "Adherence 30 Day"), ("_Measures", "Adherence 60 Day"),
         ("_Measures", "Adherence 90 Day")]),
    # Line chart: Adherence trend over time
    make_line_chart("pc_adh_trend", 20, 470, 1240, 230,
        "DimCalendar", "YearMonth", "_Measures", "Adherence 30 Day", "_Measures", "Adherence 90 Day"),
]


# ═══════════════════════════════════════════════════════════════════════════
# Write all pages and update pages.json
# ═══════════════════════════════════════════════════════════════════════════

write_page(p1_id, "Funnel Overview", p1)
write_page(p2_id, "PA and Insurance", p2)
write_page(p3_id, "Adherence", p3)

with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({
        "$schema": SCHEMA_PAGES,
        "pageOrder": [p1_id, p2_id, p3_id],
        "activePageName": p1_id
    }, f, indent=2)

print("Done! Patient Access Funnel: 3 pages generated.")
