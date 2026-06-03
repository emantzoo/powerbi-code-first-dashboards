"""
Epikast Engagement Dashboard — PBIR visual generator.

Writes visual.json files into the .pbip PBIR folder structure. Power BI renders
them as a polished, 6-page dashboard. Pure stdlib — run with Power BI closed:

    python scripts/generate_pages.py

Helper library (make_* + _*_objects) is shared with the other projects in this
repo; only the page definitions at the bottom are Epikast-specific.
"""

import json, os, hashlib, shutil

# ── Path and schema constants ──────────────────────────────────────────────
BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\epikast\epikast_dashb.Report\definition\pages"

SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"
SCHEMA_PAGE   = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"


# ── Formatting helpers: build the expr/Literal wrappers ────────────────────
def _lit(value):
    """Wrap a value in the PBIR Literal expression format."""
    return {"expr": {"Literal": {"Value": value}}}

def _solid(hex_color):
    """Wrap a hex color in the PBIR solid color format."""
    return {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hex_color}'"}}}}}

def _theme_color(color_id, percent=0):
    """Reference a theme data color."""
    return {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": color_id, "Percent": percent}}}}}


# ── Default formatting objects by visual category ──────────────────────────
def _card_objects():
    return {
        "layout": [
            {"properties": {"style": _lit("'Table'"), "orientation": _lit("1D"),
                            "rowCount": _lit("5L"), "contentOrder": _lit("'referenceLabel_callout_image'")}},
            {"properties": {"rectangleRoundedCurve": _lit("8L"), "paddingUniform": _lit("10L"),
                            "backgroundTransparency": _lit("0D")},
             "selector": {"id": "default"}}
        ],
        "accentBar": [{"properties": {"show": _lit("true")}, "selector": {"id": "default"}}],
        "shadowCustom": [{"properties": {"show": _lit("true")}, "selector": {"id": "default"}}],
        "shapeCustomRectangle": [{"properties": {"tileShape": _lit("'rectangleRoundedByPixel'")}, "selector": {"id": "default"}}]
    }


def _chart_objects(show_labels=False, label_position="'OutsideEnd'"):
    obj = {
        "categoryAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false")}}],
        "valueAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false"),
                                       "gridlineStyle": _lit("'dashed'"), "gridlineColor": _solid("#E2E8F0")}}]
    }
    if show_labels:
        obj["labels"] = [{"properties": {"show": _lit("true"), "labelPosition": _lit(label_position), "fontSize": _lit("9L")}}]
    return obj


def _line_chart_objects():
    return {
        "categoryAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false")}}],
        "valueAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false"),
                                       "gridlineStyle": _lit("'dashed'"), "gridlineColor": _solid("#E2E8F0")}}],
        "lineStyles": [{"properties": {"strokeWidth": _lit("3L")}}]
    }


def _table_objects():
    return {
        "columnHeaders": [{"properties": {"bold": _lit("true"), "fontSize": _lit("10L"),
                                           "fontColor": _solid("#FFFFFF"), "backColor": _theme_color(0)}}],
        "values": [{"properties": {"fontSize": _lit("10L"), "backColor": _solid("#FFFFFF"),
                                    "backColorAlternate": _solid("#F8FAFC")}}],
        "grid": [{"properties": {"gridHorizontal": _lit("true"), "gridHorizontalColor": _solid("#E2E8F0"),
                                  "gridVertical": _lit("false"), "rowPadding": _lit("4L")}}]
    }


def _matrix_objects():
    return {
        "columnHeaders": [{"properties": {"bold": _lit("true"), "fontSize": _lit("10L"),
                                           "fontColor": _solid("#FFFFFF"), "backColor": _theme_color(0)}}],
        "rowHeaders": [{"properties": {"fontSize": _lit("10L")}}],
        "values": [{"properties": {"fontSize": _lit("10L"), "backColor": _solid("#FFFFFF"),
                                    "backColorAlternate": _solid("#F8FAFC")}}],
        "grid": [{"properties": {"gridHorizontal": _lit("true"), "gridHorizontalColor": _solid("#E2E8F0"),
                                  "gridVertical": _lit("false"), "rowPadding": _lit("4L")}}]
    }


def _gauge_objects():
    return {"gaugeAxis": [{"properties": {"fontSize": _lit("10L")}}]}


def _slicer_objects():
    return {}


# ── Core helpers ───────────────────────────────────────────────────────────
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


# ── Visual builder functions ───────────────────────────────────────────────
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

def make_clustered_column(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_line_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, val2_table=None, val2_measure=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Y": {"projections": [measure_field(val_table, val_measure)]}}
    if val2_table and val2_measure:
        qs["Y"]["projections"].append(measure_field(val2_table, val2_measure))
    return make_visual(name, x, y, w, h, "lineChart", qs, objects=_line_chart_objects())

def make_area_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "areaChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_line_chart_objects())

def make_donut(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "donutChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_pie(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "pieChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_table(name, x, y, w, h, fields_list):
    projections = [measure_field(t, c) if m else column_field(t, c) for t, c, m in fields_list]
    return make_visual(name, x, y, w, h, "tableEx",
        {"Values": {"projections": projections}}, objects=_table_objects())

def make_matrix(name, x, y, w, h, row_fields, col_fields, val_fields):
    rows = [column_field(t, c) for t, c in row_fields]
    cols = [column_field(t, c) for t, c in col_fields] if col_fields else []
    vals = [measure_field(t, m) for t, m in val_fields]
    qs = {"Rows": {"projections": rows}, "Values": {"projections": vals}}
    if cols:
        qs["Columns"] = {"projections": cols}
    return make_visual(name, x, y, w, h, "pivotTable", qs, objects=_matrix_objects())

def make_filled_map(name, x, y, w, h, loc_table, loc_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "filledMap",
        {"Category": {"projections": [column_field(loc_table, loc_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_map(name, x, y, w, h, cat_table, cat_col, lat_table, lat_col, lng_table, lng_col, size_table, size_measure):
    return make_visual(name, x, y, w, h, "map",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [column_field(lat_table, lat_col)]},
         "X": {"projections": [column_field(lng_table, lng_col)]},
         "Size": {"projections": [measure_field(size_table, size_measure)]}})

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
    return make_visual(name, x, y, w, h, "gauge", qs, objects=_gauge_objects())

def make_waterfall(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "waterfallChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_funnel(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "funnel",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

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
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())

def make_stacked_column(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())

def make_stacked_bar(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())

def make_hundred_pct_stacked_bar(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "hundredPercentStackedBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())

def make_hundred_pct_stacked_column(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "hundredPercentStackedColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())


# ── Dashboard elements: title bars, buttons, conditional formatting ────────
def make_title_bar(name, x, y, w, h, text, bg_color="#1E293B"):
    return make_visual(name, x, y, w, h, "textbox",
        objects={"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text,
            "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "18px", "color": "#FFFFFF"}}]}]}}]},
        visual_container_objects={
            "background": [{"properties": {"show": _lit("true"), "color": _solid(bg_color), "transparency": _lit("0D")}}],
            "visualHeader": [{"properties": {"show": _lit("false")}}]
        }, z=9000)


def make_button(name, x, y, w, h, text):
    obj = {
        "icon": [{"properties": {"shapeType": _lit("'blank'")}, "selector": {"id": "default"}},
                 {"properties": {"show": _lit("false")}}],
        "text": [{"properties": {"show": _lit("true")}},
                 {"properties": {"text": _lit(f"'{text}'"), "horizontalAlignment": _lit("'center'")}, "selector": {"id": "default"}}]
    }
    return make_visual(name, x, y, w, h, "actionButton", objects=obj, z=8000, how_created="InsertVisualButton")


def _gradient_fill(measure_table, measure_name):
    return {"dataPoint": [{"properties": {"fill": {"solid": {"color": {"expr": {"FillRule": {
        "Input": {"Measure": {"Expression": {"SourceRef": {"Entity": measure_table}}, "Property": measure_name}},
        "FillRule": {"linearGradient2": {
            "min": {"color": {"Literal": {"Value": "'minColor'"}}},
            "max": {"color": {"Literal": {"Value": "'maxColor'"}}},
            "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'asZero'"}}}
        }}}}}}}}, "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}]}


def make_clustered_bar_gradient(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    base_objects = _chart_objects(show_labels=True, label_position="'OutsideEnd'")
    base_objects.update(_gradient_fill(val_table, val_measure))
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}}, objects=base_objects)


def make_clustered_column_gradient(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    base_objects = _chart_objects(show_labels=True, label_position="'OutsideEnd'")
    base_objects.update(_gradient_fill(val_table, val_measure))
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}}, objects=base_objects)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE DEFINITIONS — Epikast Engagement Dashboard
# ═══════════════════════════════════════════════════════════════════════════
EPIKAST_TEAL = "#0F766E"   # title-bar accent (clinical teal)

# ===== PAGE 1: Engagement Overview =====
p1_id = uid("epi_page1_overview")
p1 = [
    make_title_bar("e1_title", 0, 0, 1280, 50, "Epikast — Engagement Overview", EPIKAST_TEAL),
    make_card("e1_interactions", 20, 60, 235, 140, "_Measures", "Total Interactions"),
    make_card("e1_connect", 270, 60, 235, 140, "_Measures", "Connect Rate"),
    make_card("e1_hcps", 520, 60, 235, 140, "_Measures", "Unique HCPs Reached"),
    make_card("e1_sentiment", 770, 60, 235, 140, "_Measures", "Avg Sentiment Score"),
    make_slicer("e1_year", 1020, 60, 230, 140, "Calendar", "Year"),
    make_clustered_bar_gradient("e1_client_bar", 20, 220, 400, 280, "DimClient", "client_name", "_Measures", "Total Interactions"),
    make_line_chart("e1_trend", 440, 220, 400, 280, "Calendar", "Year_Month", "_Measures", "Total Interactions", "_Measures", "Interactions PY"),
    make_donut("e1_channel", 860, 220, 380, 280, "FactInteractions", "channel", "_Measures", "Total Interactions"),
    make_area_chart("e1_minutes", 20, 520, 600, 160, "Calendar", "Year_Month", "_Measures", "Total Engagement Minutes"),
    make_clustered_bar("e1_type_bar", 640, 520, 600, 160, "FactInteractions", "interaction_type", "_Measures", "Total Interactions"),
    make_button("e1_btn_agents", 1100, 670, 150, 40, "Agents"),
]

# ===== PAGE 2: Agent & Rep Performance =====
p2_id = uid("epi_page2_agents")
p2 = [
    make_title_bar("e2_title", 0, 0, 1280, 50, "Epikast — Agent & Rep Performance", EPIKAST_TEAL),
    make_card("e2_interactions", 20, 60, 235, 140, "_Measures", "Total Interactions"),
    make_card("e2_duration", 270, 60, 235, 140, "_Measures", "Avg Interaction Duration"),
    make_card("e2_connect", 520, 60, 235, 140, "_Measures", "Connect Rate"),
    make_card("e2_per_hcp", 770, 60, 235, 140, "_Measures", "Interactions per HCP"),
    make_slicer("e2_role", 1020, 60, 230, 140, "DimAgent", "role"),
    make_clustered_bar("e2_role_bar", 20, 220, 400, 280, "DimAgent", "role", "_Measures", "Total Interactions"),
    make_scatter("e2_scatter", 440, 220, 800, 280, "DimAgent", "agent_name",
                 "_Measures", "Connect Rate", "_Measures", "Avg Sentiment Score",
                 "_Measures", "Total Interactions"),
    make_matrix("e2_matrix", 20, 520, 1230, 180,
        [("DimAgent", "role")],
        [("DimAgent", "team")],
        [("_Measures", "Total Interactions"), ("_Measures", "Connect Rate"),
         ("_Measures", "Avg Interaction Duration"), ("_Measures", "Avg Sentiment Score"),
         ("_Measures", "Avg Script Adherence")]),
    make_button("e2_btn_back", 20, 670, 100, 40, "Back"),
    make_button("e2_btn_hcp", 1100, 670, 150, 40, "HCPs"),
]

# ===== PAGE 3: HCP Engagement =====
p3_id = uid("epi_page3_hcp")
p3 = [
    make_title_bar("e3_title", 0, 0, 1280, 50, "Epikast — HCP Engagement", EPIKAST_TEAL),
    make_card("e3_hcps", 20, 60, 235, 140, "_Measures", "Unique HCPs Reached"),
    make_card("e3_reach", 270, 60, 235, 140, "_Measures", "HCP Reach Pct"),
    make_card("e3_per_hcp", 520, 60, 235, 140, "_Measures", "Interactions per HCP"),
    make_card("e3_sci", 770, 60, 235, 140, "_Measures", "Scientific Exchange Pct"),
    make_slicer("e3_specialty", 1020, 60, 230, 140, "DimHCP", "specialty"),
    make_clustered_bar("e3_spec_bar", 20, 220, 400, 280, "DimHCP", "specialty", "_Measures", "Total Interactions"),
    make_donut("e3_segment", 440, 220, 380, 280, "DimHCP", "segment", "_Measures", "Total Interactions"),
    make_map("e3_map", 840, 220, 410, 280, "DimHCP", "territory",
             "DimHCP", "latitude", "DimHCP", "longitude", "_Measures", "Total Interactions"),
    make_table("e3_table", 20, 520, 1230, 160, [
        ("DimHCP", "hcp_name", False),
        ("DimHCP", "specialty", False),
        ("DimHCP", "segment", False),
        ("DimHCP", "region", False),
        ("_Measures", "Total Interactions", True),
        ("_Measures", "Avg Sentiment Score", True),
        ("_Measures", "Scientific Exchange Pct", True),
    ]),
    make_button("e3_btn_back", 20, 670, 100, 40, "Back"),
    make_button("e3_btn_patient", 1100, 670, 150, 40, "Patients"),
]

# ===== PAGE 4: Patient Support & Outcomes =====
p4_id = uid("epi_page4_patient")
p4 = [
    make_title_bar("e4_title", 0, 0, 1280, 50, "Epikast — Patient Support & Outcomes", EPIKAST_TEAL),
    make_card("e4_enrolled", 20, 60, 235, 140, "_Measures", "Total Patients Enrolled"),
    make_card("e4_active", 270, 60, 235, 140, "_Measures", "Active Patient Rate"),
    make_card("e4_adherence", 520, 60, 235, 140, "_Measures", "Avg Adherence"),
    make_card("e4_nps", 770, 60, 235, 140, "_Measures", "NPS Score"),
    make_slicer("e4_status", 1020, 60, 230, 140, "FactPatientSupport", "status"),
    make_clustered_bar("e4_barrier_bar", 20, 220, 400, 280, "FactPatientSupport", "barrier_type", "_Measures", "Support Records"),
    make_donut("e4_payer", 440, 220, 380, 280, "FactPatientSupport", "payer_status", "_Measures", "Support Records"),
    make_clustered_bar("e4_client_adh", 840, 220, 410, 280, "DimClient", "client_name", "_Measures", "Avg Adherence"),
    make_table("e4_table", 20, 520, 1230, 160, [
        ("DimPatient", "age_group", False),
        ("FactPatientSupport", "status", False),
        ("_Measures", "Support Records", True),
        ("_Measures", "Avg Adherence", True),
        ("_Measures", "Avg Time to Therapy", True),
        ("_Measures", "Avg Persistence Days", True),
        ("_Measures", "Barrier Resolution Rate", True),
    ]),
    make_button("e4_btn_back", 20, 670, 100, 40, "Back"),
    make_button("e4_btn_quality", 1100, 670, 150, 40, "Quality"),
]

# ===== PAGE 5: Quality & Compliance =====
p5_id = uid("epi_page5_quality")
p5 = [
    make_title_bar("e5_title", 0, 0, 1280, 50, "Epikast — Quality & Compliance", EPIKAST_TEAL),
    make_card("e5_compliance", 20, 60, 235, 140, "_Measures", "Compliance Pass Rate"),
    make_card("e5_adherence", 270, 60, 235, 140, "_Measures", "Avg Script Adherence"),
    make_card("e5_ae", 520, 60, 235, 140, "_Measures", "Adverse Event Rate"),
    make_card("e5_pos", 770, 60, 235, 140, "_Measures", "Positive Sentiment Pct"),
    make_slicer("e5_team", 1020, 60, 230, 140, "DimAgent", "team"),
    make_clustered_bar("e5_role_adh", 20, 220, 400, 280, "DimAgent", "role", "_Measures", "Avg Script Adherence"),
    make_line_chart("e5_sentiment_trend", 440, 220, 400, 280, "Calendar", "Year_Month", "_Measures", "Avg Sentiment Score"),
    make_donut("e5_outcome", 860, 220, 380, 280, "FactInteractions", "outcome", "_Measures", "Total Interactions"),
    make_table("e5_table", 20, 520, 1230, 160, [
        ("DimAgent", "team", False),
        ("_Measures", "Compliance Pass Rate", True),
        ("_Measures", "Compliance Reviews", True),
        ("_Measures", "Adverse Events Flagged", True),
        ("_Measures", "Avg Script Adherence", True),
        ("_Measures", "Avg Sentiment Score", True),
    ]),
    make_button("e5_btn_back", 20, 670, 100, 40, "Back"),
    make_button("e5_btn_client", 1100, 670, 150, 40, "Clients"),
]

# ===== PAGE 6: Client Campaign Health =====
p6_id = uid("epi_page6_client")
p6 = [
    make_title_bar("e6_title", 0, 0, 1280, 50, "Epikast — Client Campaign Health", EPIKAST_TEAL),
    make_card("e6_interactions", 20, 60, 235, 140, "_Measures", "Total Interactions"),
    make_card("e6_active", 270, 60, 235, 140, "_Measures", "Active Patients"),
    make_card("e6_connect", 520, 60, 235, 140, "_Measures", "Connect Rate"),
    make_card("e6_payer", 770, 60, 235, 140, "_Measures", "Payer Approval Rate"),
    make_slicer("e6_client", 1020, 60, 230, 140, "DimClient", "client_name"),
    make_clustered_bar_gradient("e6_client_bar", 20, 220, 610, 280, "DimClient", "client_name", "_Measures", "Total Interactions"),
    make_clustered_bar("e6_ta_bar", 650, 220, 600, 280, "DimClient", "therapeutic_area", "_Measures", "Connect Rate"),
    make_matrix("e6_matrix", 20, 520, 1230, 180,
        [("DimClient", "client_name")],
        None,
        [("_Measures", "Total Interactions"), ("_Measures", "Connect Rate"),
         ("_Measures", "Unique HCPs Reached"), ("_Measures", "Active Patients"),
         ("_Measures", "Avg Adherence"), ("_Measures", "NPS Score")]),
    make_button("e6_btn_back", 20, 670, 100, 40, "Back"),
]

# Write all pages
write_page(p1_id, "Engagement Overview", p1)
write_page(p2_id, "Agent & Rep Performance", p2)
write_page(p3_id, "HCP Engagement", p3)
write_page(p4_id, "Patient Support & Outcomes", p4)
write_page(p5_id, "Quality & Compliance", p5)
write_page(p6_id, "Client Campaign Health", p6)

# Update pages.json
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, p3_id, p4_id, p5_id, p6_id],
               "activePageName": p1_id}, f, indent=2)

print(f"Page 1 (Engagement Overview):        {p1_id} - {len(p1)} visuals")
print(f"Page 2 (Agent & Rep Performance):    {p2_id} - {len(p2)} visuals")
print(f"Page 3 (HCP Engagement):             {p3_id} - {len(p3)} visuals")
print(f"Page 4 (Patient Support & Outcomes): {p4_id} - {len(p4)} visuals")
print(f"Page 5 (Quality & Compliance):       {p5_id} - {len(p5)} visuals")
print(f"Page 6 (Client Campaign Health):     {p6_id} - {len(p6)} visuals")
print(f"Total: {len(p1)+len(p2)+len(p3)+len(p4)+len(p5)+len(p6)} visuals across 6 pages")
print("Done!")
