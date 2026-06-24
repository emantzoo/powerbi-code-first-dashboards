"""
PBIR Visual Generator — Epikast A/B Test Tracker Dashboard (2 pages).
Experiment registry, script A/B deep dive.
"""

import json, os, hashlib, shutil

BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\epikast\epikast_ab_dashb\epikast_ab_dashb.Report\definition\pages"

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

def make_table(name, x, y, w, h, fields_list):
    projections = [measure_field(t, c) if m else column_field(t, c) for t, c, m in fields_list]
    return make_visual(name, x, y, w, h, "tableEx",
        {"Values": {"projections": projections}},
        objects=_table_objects())

def make_title_bar(name, x, y, w, h, text, bg_color="#1B3A5C"):
    return make_visual(name, x, y, w, h, "textbox",
        objects={"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "18px", "color": "#FFFFFF"}}]}]}}]},
        visual_container_objects={
            "background": [{"properties": {"show": _lit("true"), "color": _solid(bg_color), "transparency": _lit("0D")}}],
            "visualHeader": [{"properties": {"show": _lit("false")}}]
        }, z=9000)


# ── Page 1: Experiment Overview ──────────────────────────────────────────────

p1_id = uid("ep_ab_experiment_overview")
p1 = [
    make_title_bar("t1_title", 0, 0, 1280, 50, "A/B Test Tracker \u2014 Experiment Overview"),
    # 4 cards
    make_card("t1_total_exp",  20,  60, 230, 120, "_Measures", "Total Experiments"),
    make_card("t1_concluded",  265, 60, 230, 120, "_Measures", "Concluded Experiments"),
    make_card("t1_win_rate",   510, 60, 230, 120, "_Measures", "Win Rate"),
    make_card("t1_running",    755, 60, 230, 120, "_Measures", "Running Experiments"),
    # 2 slicers stacked right
    make_slicer("t1_sl_status",  1000, 60,  260, 55, "DimExperiment", "Status"),
    make_slicer("t1_sl_therapy", 1000, 120, 260, 55, "DimExperiment", "TherapyArea"),
    # Experiment registry table (main element, full width)
    make_table("t1_registry", 20, 195, 1240, 280, [
        ("DimExperiment", "ExperimentName", False),
        ("DimExperiment", "Status", False),
        ("DimExperiment", "PrimaryKPI", False),
        ("DimExperiment", "StartDate", False),
        ("DimExperiment", "EndDate", False),
        ("DimExperiment", "SampleSizeActual", False),
        ("DimExperiment", "SampleSizeTarget", False),
        ("DimExperiment", "ObservedLift", False),
        ("DimExperiment", "Winner", False),
    ]),
    # Bar: Observed lift by experiment
    make_clustered_bar("t1_lift_bar", 20, 490, 1240, 200,
        "DimExperiment", "ExperimentName", "_Measures", "Avg Observed Lift"),
]


# ── Page 2: Script A/B Deep Dive ────────────────────────────────────────────

p2_id = uid("ep_ab_script_deep_dive")
p2 = [
    make_title_bar("t2_title", 0, 0, 1280, 50, "A/B Test Tracker \u2014 Script A/B Deep Dive"),
    # 2 comparison cards
    make_card("t2_a_connect", 20,  60, 300, 120, "_Measures", "Script A Connect Rate"),
    make_card("t2_b_connect", 335, 60, 300, 120, "_Measures", "Script B Connect Rate"),
    # 3 slicers
    make_slicer("t2_sl_month",   650, 60,  200, 55, "DimCalendar", "YearMonth"),
    make_slicer("t2_sl_therapy", 860, 60,  200, 55, "DimRep", "TherapyArea"),
    make_slicer("t2_sl_region",  1070, 60, 190, 55, "DimHCP", "Region"),
    # Middle left: Clustered bar — Script performance comparison
    make_clustered_bar("t2_script_rates", 20, 195, 610, 270,
        "FactHCPCalls", "Script", "_Measures", "Connect Rate"),
    # Middle right: Duration comparison
    make_clustered_bar("t2_script_duration", 645, 195, 615, 270,
        "FactHCPCalls", "Script", "_Measures", "Avg Call Duration"),
    # Bottom: Table by Specialty showing Script A vs B rates
    make_table("t2_specialty_tbl", 20, 480, 1240, 220, [
        ("DimHCP", "Specialty", False),
        ("_Measures", "Script A Connect Rate", True),
        ("_Measures", "Script B Connect Rate", True),
        ("_Measures", "Script A Meaningful Rate", True),
        ("_Measures", "Script B Meaningful Rate", True),
        ("_Measures", "Script A Avg Duration", True),
        ("_Measures", "Script B Avg Duration", True),
    ]),
]


# ── Write pages and metadata ────────────────────────────────────────────────

write_page(p1_id, "Experiment Overview", p1)
write_page(p2_id, "Script A/B Deep Dive", p2)

with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({
        "$schema": SCHEMA_PAGES,
        "pageOrder": [p1_id, p2_id],
        "activePageName": p1_id
    }, f, indent=2)

print("Done! A/B Test Tracker: 2 pages generated.")
