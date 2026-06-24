"""
PBIR Visual Generator — Epikast Ops Overview Dashboard (4 pages).

Smart Ops Overview — surfaces insights, not just numbers:
  Page 1: Command Center — anomaly alerts, AI lift, funnel leak, experiment bar
  Page 2: Call Outcomes — outcome distribution, specialty performance, day-of-week matrix
  Page 3: Rep Performance — top/bottom movers, scatter, scorecard
  Page 4: Trends & Optimization — trend lines, best/worst day, schedule insight
"""

import json, os, hashlib, shutil

# ── Path and schema constants ──────────────────────────────────────────────
BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\epikast\epikast_ops_dashb\epikast_ops_dashb.Report\definition\pages"

SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"
SCHEMA_PAGE   = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"


# ── Formatting helpers ─────────────────────────────────────────────────────
def _lit(value):
    return {"expr": {"Literal": {"Value": value}}}

def _solid(hex_color):
    return {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hex_color}'"}}}}}

def _theme_color(color_id, percent=0):
    return {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": color_id, "Percent": percent}}}}}


# ── Default formatting objects ─────────────────────────────────────────────

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

def _card_objects_accent(hex_color):
    obj = _card_objects()
    obj["accentBar"].append({"properties": {"color": _solid(hex_color)}, "selector": {"id": "default"}})
    return obj

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

def make_card_accent(name, x, y, w, h, table, measure, hex_color):
    return make_visual(name, x, y, w, h, "cardVisual",
        {"Data": {"projections": [measure_field(table, measure)]}},
        objects=_card_objects_accent(hex_color))

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

def make_donut(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "donutChart",
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

def make_scatter(name, x, y, w, h, detail_table, detail_col, x_table, x_measure, y_table, y_measure, size_table=None, size_measure=None):
    qs = {"Category": {"projections": [column_field(detail_table, detail_col)]},
          "X": {"projections": [measure_field(x_table, x_measure)]},
          "Y": {"projections": [measure_field(y_table, y_measure)]}}
    if size_table and size_measure:
        qs["Size"] = {"projections": [measure_field(size_table, size_measure)]}
    return make_visual(name, x, y, w, h, "scatterChart", qs)

def make_funnel(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "funnel",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_stacked_bar(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())

def make_title_bar(name, x, y, w, h, text, bg_color="#1B3A5C"):
    return make_visual(name, x, y, w, h, "textbox",
        objects={
            "general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "18px", "color": "#FFFFFF"}}]}]}}]
        },
        visual_container_objects={
            "background": [{"properties": {"show": _lit("true"), "color": _solid(bg_color), "transparency": _lit("0D")}}],
            "visualHeader": [{"properties": {"show": _lit("false")}}]
        },
        z=9000)

def make_section_label(name, x, y, w, h, text, bg_color="#2E86AB"):
    """Smaller section header — teal by default."""
    return make_visual(name, x, y, w, h, "textbox",
        objects={
            "general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "13px", "color": "#FFFFFF"}}]}]}}]
        },
        visual_container_objects={
            "background": [{"properties": {"show": _lit("true"), "color": _solid(bg_color), "transparency": _lit("0D")}}],
            "visualHeader": [{"properties": {"show": _lit("false")}}]
        },
        z=8500)

def make_button(name, x, y, w, h, text):
    obj = {
        "icon": [{"properties": {"shapeType": _lit("'blank'")}, "selector": {"id": "default"}}, {"properties": {"show": _lit("false")}}],
        "text": [{"properties": {"show": _lit("true")}}, {"properties": {"text": _lit(f"'{text}'"), "horizontalAlignment": _lit("'center'")}, "selector": {"id": "default"}}]
    }
    return make_visual(name, x, y, w, h, "actionButton", objects=obj, z=8000, how_created="InsertVisualButton")


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1: COMMAND CENTER
# ════════════════════════════════════════════════════════════════════════════
# Layout: title bar (50px) → core KPIs (row 55-155) → smart insight panels (160-450) → trend (460-700)

p1_id = uid("ep_smart_command_center")
p1 = [
    make_title_bar("s1_title", 0, 0, 1280, 50, "Command Center"),

    # ── Row 1: Core KPI cards (5) + slicers (3) ──────────────────────────
    make_card("s1_total_calls",  20,  55, 160, 100, "_Measures", "Total Calls"),
    make_card("s1_connect_rate", 190, 55, 160, 100, "_Measures", "Connect Rate"),
    make_card("s1_meaningful",   360, 55, 160, 100, "_Measures", "Meaningful Interaction Rate"),
    make_card("s1_aht",          530, 55, 160, 100, "_Measures", "Avg AHT"),
    make_card("s1_sched_adh",    700, 55, 160, 100, "_Measures", "Schedule Adherence Rate"),

    make_slicer("s1_sl_quarter", 880,  55, 190, 30, "DimCalendar", "Quarter"),
    make_slicer("s1_sl_team",    880,  90, 190, 30, "DimRep", "Team"),
    make_slicer("s1_sl_therapy", 880, 125, 190, 30, "DimRep", "TherapyArea"),

    # ── Row 2: Smart Insight Panels (3 columns) ─────────────────────────

    # Column A (x=20, w=400): Anomaly Detection
    make_section_label("s1_anom_hdr", 20, 165, 400, 28, "\u26A0  Anomaly Alerts"),
    make_card_accent("s1_wow_flag",     20, 197, 195, 85, "_Measures", "Connect Rate WoW Flag", "#CD3333"),
    make_card_accent("s1_worst_spec",  220, 197, 200, 85, "_Measures", "Worst Performing Specialty This Week", "#DAA520"),
    make_card("s1_worst_spec_cr",       20, 287, 195, 75, "_Measures", "Worst Specialty Connect Rate"),
    make_card("s1_wow_change",         220, 287, 200, 75, "_Measures", "Connect Rate WoW Change"),

    # Column B (x=435, w=400): Cross-Dashboard Alerts
    make_section_label("s1_xdash_hdr", 435, 165, 400, 28, "\u2194  Cross-Dashboard Alerts"),
    # Patient funnel leak alert
    make_card_accent("s1_funnel_rate",  435, 197, 195, 85, "_Measures", "Funnel Alert Abandonment Rate", "#A23B72"),
    make_card_accent("s1_funnel_stage", 635, 197, 200, 85, "_Measures", "Funnel Alert Worst Stage", "#A23B72"),
    make_card("s1_funnel_cases",        435, 287, 195, 75, "_Measures", "Funnel Alert Worst Stage Cases"),
    # AI lift mini-card
    make_card_accent("s1_ai_lift",      635, 287, 200, 75, "_Measures", "AI Lift on Connect Rate", "#2E86AB"),

    # Column C (x=850, w=410): Movers + Experiments
    make_section_label("s1_movers_hdr", 850, 165, 410, 28, "\u2195  Top/Bottom Movers"),
    make_card_accent("s1_top_rep",      850, 197, 200, 85, "_Measures", "Top Rep Connect Rate Improvement", "#2E8B57"),
    make_card_accent("s1_top_val",     1055, 197, 205, 85, "_Measures", "Top Rep Improvement Value", "#2E8B57"),
    make_card_accent("s1_bot_rep",      850, 287, 200, 75, "_Measures", "Bottom Rep Connect Rate Decline", "#CD3333"),
    make_card_accent("s1_bot_val",     1055, 287, 205, 75, "_Measures", "Bottom Rep Decline Value", "#CD3333"),

    # ── Row 3: Experiment Status Bar ─────────────────────────────────────
    make_section_label("s1_exp_hdr", 20, 372, 200, 28, "\U0001F9EA  Experiments"),
    make_card("s1_exp_progress",   225, 372, 770, 28, "_Measures", "Running Experiment Progress"),
    make_card("s1_exp_running",   1000, 372, 130, 28, "_Measures", "Running Experiments"),
    make_card("s1_exp_winrate",   1135, 372, 125, 28, "_Measures", "Win Rate"),

    # ── Row 4: Main trend chart (bottom half) ────────────────────────────
    make_line_chart("s1_trend", 20, 410, 850, 295,
        "DimCalendar", "YearMonth", "_Measures", "Total Calls", "_Measures", "Connect Rate"),
    make_clustered_bar("s1_team_bar", 885, 410, 375, 295,
        "DimRep", "Team", "_Measures", "Total Calls"),
]


# ════════════════════════════════════════════════════════════════════════════
# PAGE 2: CALL OUTCOMES
# ════════════════════════════════════════════════════════════════════════════

p2_id = uid("ep_ops_call_outcomes_v2")
p2 = [
    make_title_bar("o2_title", 0, 0, 1280, 50, "Call Outcomes"),
    # Donut — Call Outcome Distribution
    make_donut("o2_outcome_donut", 20, 60, 600, 300,
        "FactHCPCalls", "CallOutcome", "_Measures", "Total Calls"),
    # Bar — Connect Rate by Specialty
    make_clustered_bar("o2_specialty_bar", 635, 60, 625, 300,
        "DimHCP", "Specialty", "_Measures", "Connect Rate"),
    # Matrix — DayOfWeek performance
    make_matrix("o2_heatmap", 20, 375, 1240, 290,
        [("DimCalendar", "DayOfWeek")],
        [],
        [("_Measures", "Total Calls"), ("_Measures", "Connect Rate"),
         ("_Measures", "Meaningful Interaction Rate")]),
    # Slicers
    make_slicer("o2_sl_month", 20, 675, 200, 35, "DimCalendar", "YearMonth"),
    make_slicer("o2_sl_team",  230, 675, 200, 35, "DimRep", "Team"),
]


# ════════════════════════════════════════════════════════════════════════════
# PAGE 3: REP PERFORMANCE
# ════════════════════════════════════════════════════════════════════════════
# Redesigned: top/bottom movers panel + schedule insight + scatter + table

p3_id = uid("ep_smart_rep_performance")
p3 = [
    make_title_bar("o3_title", 0, 0, 1280, 50, "Rep Performance"),

    # ── Cards: key metrics ───────────────────────────────────────────────
    make_card("o3_calls_per_rep", 20, 60, 190, 100, "_Measures", "Calls Per Rep Per Day"),
    make_card("o3_notes_comply", 220, 60, 190, 100, "_Measures", "Notes Compliance Rate"),

    # Schedule optimization insight cards
    make_section_label("o3_sched_hdr", 425, 60, 200, 25, "\U0001F4C5  Schedule Insight"),
    make_card_accent("o3_best_day",  425,  88, 200, 72, "_Measures", "Best Day", "#2E8B57"),
    make_card_accent("o3_worst_day", 635,  88, 200, 72, "_Measures", "Worst Day", "#CD3333"),
    make_card("o3_best_cr",          425, 60, 100, 25, "_Measures", "Best Time Slot Connect Rate"),  # tiny
    make_card("o3_worst_cr",         635, 60, 100, 25, "_Measures", "Worst Day Connect Rate"),  # tiny

    # Slicers
    make_slicer("o3_sl_month", 855, 60, 190, 50, "DimCalendar", "YearMonth"),
    make_slicer("o3_sl_team",  1055, 60, 205, 50, "DimRep", "Team"),

    # Scatter: Volume vs Quality
    make_scatter("o3_scatter", 20, 170, 1240, 260,
        "DimRep", "RepName",
        "_Measures", "Total Calls",
        "_Measures", "Connect Rate",
        "_Measures", "Meaningful Interactions"),

    # Rep scorecard table
    make_table("o3_table", 20, 445, 1240, 260, [
        ("DimRep", "RepName", False),
        ("DimRep", "Team", False),
        ("_Measures", "Total Calls", True),
        ("_Measures", "Connected Calls", True),
        ("_Measures", "Connect Rate", True),
        ("_Measures", "Meaningful Interaction Rate", True),
        ("_Measures", "Avg AHT", True),
        ("_Measures", "Schedule Adherence Rate", True),
        ("_Measures", "Notes Compliance Rate", True),
    ]),
]


# ════════════════════════════════════════════════════════════════════════════
# PAGE 4: TRENDS & OPTIMIZATION
# ════════════════════════════════════════════════════════════════════════════

p4_id = uid("ep_smart_trends")
p4 = [
    make_title_bar("o4_title", 0, 0, 1280, 50, "Trends & Optimization"),
    # 3 trend lines
    make_line_chart("o4_connect_trend", 20, 60, 1010, 195,
        "DimCalendar", "YearMonth", "_Measures", "Connect Rate", "_Measures", "Connect Rate L4W"),
    make_line_chart("o4_aht_trend", 20, 265, 1010, 195,
        "DimCalendar", "YearMonth", "_Measures", "Avg AHT"),
    make_line_chart("o4_sched_trend", 20, 470, 1010, 195,
        "DimCalendar", "YearMonth", "_Measures", "Schedule Adherence Rate"),
    # Right column: slicers + MoM change cards
    make_slicer("o4_sl_team",    1045, 60,  215, 45, "DimRep", "Team"),
    make_slicer("o4_sl_therapy", 1045, 115, 215, 45, "DimRep", "TherapyArea"),
    make_card("o4_calls_mom",    1045, 175, 215, 80, "_Measures", "Calls MoM Change"),
    make_card("o4_cr_mom",       1045, 265, 215, 80, "_Measures", "Connect Rate MoM Change"),
    # Monthly summary table at bottom right
    make_table("o4_summary", 1045, 360, 215, 305, [
        ("DimCalendar", "YearMonth", False),
        ("_Measures", "Total Calls", True),
        ("_Measures", "Connect Rate", True),
    ]),
]


# ════════════════════════════════════════════════════════════════════════════
# WRITE ALL PAGES AND pages.json
# ════════════════════════════════════════════════════════════════════════════

write_page(p1_id, "Command Center", p1)
write_page(p2_id, "Call Outcomes", p2)
write_page(p3_id, "Rep Performance", p3)
write_page(p4_id, "Trends & Optimization", p4)

with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({
        "$schema": SCHEMA_PAGES,
        "pageOrder": [p1_id, p2_id, p3_id, p4_id],
        "activePageName": p1_id
    }, f, indent=2)

print("Done! Smart Ops Overview: 4 pages generated.")
