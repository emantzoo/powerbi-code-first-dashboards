"""
PBIR Visual Generator — Epikast AI Impact Dashboard (3 pages).
AI call targeting, MSL Partner performance, MSL Partner ROI.
"""

import json, os, hashlib, shutil

BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\epikast\epikast_ai_dashb\epikast_ai_dashb.Report\definition\pages"

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

def make_donut(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "donutChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_line_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, val2_table=None, val2_measure=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Y": {"projections": [measure_field(val_table, val_measure)]}}
    if val2_table and val2_measure:
        qs["Y"]["projections"].append(measure_field(val2_table, val2_measure))
    return make_visual(name, x, y, w, h, "lineChart", qs, objects=_line_chart_objects())

def make_table(name, x, y, w, h, fields_list):
    projections = [measure_field(t, c) if m else column_field(t, c) for t, c, m in fields_list]
    return make_visual(name, x, y, w, h, "tableEx",
        {"Values": {"projections": projections}},
        objects=_table_objects())

def make_stacked_bar(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())

def make_title_bar(name, x, y, w, h, text, bg_color="#1B3A5C"):
    return make_visual(name, x, y, w, h, "textbox",
        objects={"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "18px", "color": "#FFFFFF"}}]}]}}]},
        visual_container_objects={
            "background": [{"properties": {"show": _lit("true"), "color": _solid(bg_color), "transparency": _lit("0D")}}],
            "visualHeader": [{"properties": {"show": _lit("false")}}]
        }, z=9000)

# ── Page 1: AI Call Targeting ─────────────────────────────────────────────────

p1_id = uid("ep_ai_targeting")
p1 = [
    make_title_bar("a1_title", 0, 0, 1280, 50, "AI Impact \u2014 Call Targeting"),
    # 4 cards
    make_card("a1_ai_connect",    20,  60, 230, 120, "_Measures", "AI Connect Rate"),
    make_card("a1_nonai_connect", 265, 60, 230, 120, "_Measures", "Non-AI Connect Rate"),
    make_card("a1_accept",        510, 60, 230, 120, "_Measures", "AI Acceptance Rate"),
    make_card("a1_lift",          755, 60, 230, 120, "_Measures", "AI Lift on Connect Rate"),
    # 3 slicers stacked right
    make_slicer("a1_sl_qtr",     1000, 60,  260, 35, "DimCalendar", "Quarter"),
    make_slicer("a1_sl_tier",    1000, 100, 260, 35, "DimHCP", "Tier"),
    make_slicer("a1_sl_therapy", 1000, 140, 260, 35, "DimRep", "TherapyArea"),
    # Middle left: Bar — AI Connect Rate by Therapy Area
    make_clustered_bar("a1_rates_bar", 20, 195, 610, 270,
        "DimRep", "TherapyArea", "_Measures", "AI Connect Rate"),
    # Middle right: Bar — AI Lift by Therapy Area
    make_clustered_bar("a1_lift_bar", 645, 195, 615, 270,
        "DimRep", "TherapyArea", "_Measures", "AI Lift on Connect Rate"),
    # Bottom: Line — AI Acceptance over time
    make_line_chart("a1_accept_trend", 20, 480, 1240, 210,
        "DimCalendar", "YearMonth", "_Measures", "AI Acceptance Rate"),
]

# ── Page 2: MSL Partner Performance ──────────────────────────────────────────

p2_id = uid("ep_ai_msl_performance")
p2 = [
    make_title_bar("a2_title", 0, 0, 1280, 50, "AI Impact \u2014 MSL Partner Performance"),
    # 4 cards
    make_card("a2_queries",      20,  60, 230, 120, "_Measures", "Total MSL Queries"),
    make_card("a2_full_rate",    265, 60, 230, 120, "_Measures", "Fully Answered Rate"),
    make_card("a2_resp_time",    510, 60, 230, 120, "_Measures", "Avg Time to Answer Sec"),
    make_card("a2_time_saved",   755, 60, 230, 120, "_Measures", "Total Time Saved Hours"),
    # 3 slicers stacked right
    make_slicer("a2_sl_rep",     1000, 60,  260, 35, "DimRep", "RepName"),
    make_slicer("a2_sl_qtr",    1000, 100, 260, 35, "DimCalendar", "Quarter"),
    make_slicer("a2_sl_therapy", 1000, 140, 260, 35, "DimRep", "TherapyArea"),
    # Middle left: Horiz bar — top topics by query count
    make_clustered_bar("a2_topic_bar", 20, 195, 610, 270,
        "FactMSLPartnerUsage", "Topic", "_Measures", "Total MSL Queries"),
    # Middle right: Donut — query type distribution
    make_donut("a2_query_donut", 645, 195, 615, 270,
        "FactMSLPartnerUsage", "QueryType", "_Measures", "Total MSL Queries"),
    # Bottom: Line — adoption + quality trend
    make_line_chart("a2_adoption_trend", 20, 480, 1240, 210,
        "DimCalendar", "YearMonth", "_Measures", "MSL Queries Per MSL Per Day",
        "_Measures", "Fully Answered Rate"),
]

# ── Page 3: MSL Partner ROI ──────────────────────────────────────────────────

p3_id = uid("ep_ai_msl_roi")
p3 = [
    make_title_bar("a3_title", 0, 0, 1280, 50, "AI Impact \u2014 MSL Partner ROI"),
    # 3 cards + 1 slicer
    make_card("a3_per_day",     20,  60, 300, 120, "_Measures", "MSL Queries Per MSL Per Day"),
    make_card("a3_interaction",  335, 60, 300, 120, "_Measures", "Used in HCP Interaction Rate"),
    make_card("a3_satisfaction", 650, 60, 300, 120, "_Measures", "Avg MSL Satisfaction"),
    make_slicer("a3_sl_qtr",    965, 60, 295, 120, "DimCalendar", "Quarter"),
    # Middle: Stacked bar — answer quality by MSL rep
    make_stacked_bar("a3_quality_bar", 20, 195, 1240, 270,
        "DimRep", "RepName", "FactMSLPartnerUsage", "AnswerQuality",
        "_Measures", "Total MSL Queries"),
    # Bottom: MSL scorecard table
    make_table("a3_scorecard", 20, 480, 1240, 220, [
        ("DimRep", "RepName", False),
        ("_Measures", "Total MSL Queries", True),
        ("_Measures", "Fully Answered Rate", True),
        ("_Measures", "Avg Time to Answer Sec", True),
        ("_Measures", "Total Time Saved Hours", True),
        ("_Measures", "Used in HCP Interaction Rate", True),
        ("_Measures", "Avg MSL Satisfaction", True),
    ]),
]

# ── Write pages and metadata ─────────────────────────────────────────────────

write_page(p1_id, "AI Call Targeting", p1)
write_page(p2_id, "MSL Partner Performance", p2)
write_page(p3_id, "MSL Partner ROI", p3)

with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({
        "$schema": SCHEMA_PAGES,
        "pageOrder": [p1_id, p2_id, p3_id],
        "activePageName": p1_id
    }, f, indent=2)

print("Done! AI Impact: 3 pages generated.")
