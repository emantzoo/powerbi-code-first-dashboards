"""
Shared PBIR helper library for the Epikast Pharma Ops dashboards.

Both report layout scripts (generate_pages_internal.py and
generate_pages_client.py) import from here. They run against ONE shared semantic
model (see Epikast_Dashboard_Prompts.md) and write into TWO separate report
definitions.

Usage from a layout script:
    import pbir_lib as pb
    from pbir_lib import *
    pb.BASE = r"C:\\...\\epikast_internal_dashb.Report\\definition\\pages"
    ...
    write_page(p1_id, "Exec Summary", p1)
    write_pages_json([...])

Beyond the standard make_* functions this module adds four helpers the Pharma
Ops spec needs:
    make_combo_chart      bars + line on a secondary axis
    make_multi_card       A-vs-B comparison card (multiRowCard)
    make_matrix_heatmap   matrix with a red→green value color scale
    make_line_chart(..., ref_value=, ref_label=)  reference line
NOTE: those four emit valid PBIR but are less battle-tested than the core
visuals — eyeball them on first open and tweak if Power BI renders oddly.

Pure stdlib. Run the layout scripts with Power BI closed.
"""

import json, os, hashlib, shutil

BASE = None  # set by the importing layout script before any write_page()

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


def _card_objects():
    return {
        "layout": [
            {"properties": {"style": _lit("'Table'"), "orientation": _lit("1D"),
                            "rowCount": _lit("5L"), "contentOrder": _lit("'referenceLabel_callout_image'")}},
            {"properties": {"rectangleRoundedCurve": _lit("8L"), "paddingUniform": _lit("10L"),
                            "backgroundTransparency": _lit("0D")}, "selector": {"id": "default"}}
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
    if BASE is None:
        raise RuntimeError("pbir_lib.BASE is not set — assign it in the layout script before write_page().")
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

def write_pages_json(page_order):
    with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
        json.dump({"$schema": SCHEMA_PAGES, "pageOrder": page_order,
                   "activePageName": page_order[0]}, f, indent=2)


# ── Standard visual builders ───────────────────────────────────────────────
def make_card(name, x, y, w, h, table, measure):
    return make_visual(name, x, y, w, h, "cardVisual",
        {"Data": {"projections": [measure_field(table, measure)]}}, objects=_card_objects())

def make_slicer(name, x, y, w, h, table, column):
    return make_visual(name, x, y, w, h, "slicer",
        {"Values": {"projections": [column_field(table, column)]}})

def make_clustered_bar(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True))

def make_clustered_column(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True))

def make_clustered_column_multi(name, x, y, w, h, cat_table, cat_col, val_list):
    """Clustered column with several measures side by side. val_list = [(table, measure), ...]"""
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(t, m) for t, m in val_list]}},
        objects=_chart_objects(show_labels=False))

def make_clustered_bar_multi(name, x, y, w, h, cat_table, cat_col, val_list):
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(t, m) for t, m in val_list]}},
        objects=_chart_objects(show_labels=False))

def make_line_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure,
                    val2_table=None, val2_measure=None, ref_value=None, ref_label=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Y": {"projections": [measure_field(val_table, val_measure)]}}
    if val2_table and val2_measure:
        qs["Y"]["projections"].append(measure_field(val2_table, val2_measure))
    obj = _line_chart_objects()
    if ref_value is not None:
        obj["y1AxisReferenceLine"] = [{
            "properties": {"show": _lit("true"), "value": _lit(f"'{ref_value}'"),
                           "displayName": _lit(f"'{ref_label or ref_value}'"),
                           "lineColor": _solid("#CD3333"), "transparency": _lit("20D"),
                           "style": _lit("'dashed'"), "dataLabelShow": _lit("true")},
            "selector": {"id": "0"}}]
    return make_visual(name, x, y, w, h, "lineChart", qs, objects=obj)

def make_area_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "areaChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_line_chart_objects())

def make_donut(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "donutChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True))

def make_pie(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "pieChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True))

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

def make_funnel(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "funnel",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True))

def make_waterfall(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "waterfallChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True))

def make_scatter(name, x, y, w, h, detail_table, detail_col, x_table, x_measure, y_table, y_measure,
                 size_table=None, size_measure=None, series_table=None, series_col=None):
    qs = {"Category": {"projections": [column_field(detail_table, detail_col)]},
          "X": {"projections": [measure_field(x_table, x_measure)]},
          "Y": {"projections": [measure_field(y_table, y_measure)]}}
    if size_table and size_measure:
        qs["Size"] = {"projections": [measure_field(size_table, size_measure)]}
    if series_table and series_col:
        qs["Series"] = {"projections": [column_field(series_table, series_col)]}
    return make_visual(name, x, y, w, h, "scatterChart", qs)

def make_treemap(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "treemap",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Values": {"projections": [measure_field(val_table, val_measure)]}})


# ── Dashboard elements ─────────────────────────────────────────────────────
def make_title_bar(name, x, y, w, h, text, bg_color="#1B3A5C"):
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


def _gradient_fill(measure_table, measure_name, min_color="'minColor'", max_color="'maxColor'"):
    return {"dataPoint": [{"properties": {"fill": {"solid": {"color": {"expr": {"FillRule": {
        "Input": {"Measure": {"Expression": {"SourceRef": {"Entity": measure_table}}, "Property": measure_name}},
        "FillRule": {"linearGradient2": {
            "min": {"color": {"Literal": {"Value": min_color}}},
            "max": {"color": {"Literal": {"Value": max_color}}},
            "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'asZero'"}}}
        }}}}}}}}, "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}]}

def make_clustered_bar_gradient(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    base = _chart_objects(show_labels=True)
    base.update(_gradient_fill(val_table, val_measure))
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}}, objects=base)

def make_clustered_column_gradient(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    base = _chart_objects(show_labels=True)
    base.update(_gradient_fill(val_table, val_measure))
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}}, objects=base)


# ── New helpers required by the Pharma Ops spec (verify on first open) ──────
def make_combo_chart(name, x, y, w, h, cat_table, cat_col, col_table, col_measure, line_table, line_measure):
    """Column + line combo on a shared category, line on the secondary axis."""
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Y": {"projections": [measure_field(col_table, col_measure)]},
          "Y2": {"projections": [measure_field(line_table, line_measure)]}}
    return make_visual(name, x, y, w, h, "lineClusteredColumnComboChart", qs,
                       objects=_chart_objects(show_labels=False))

def make_multi_card(name, x, y, w, h, val_fields):
    """A-vs-B comparison card. val_fields = [(table, measure), ...] shown as rows."""
    return make_visual(name, x, y, w, h, "multiRowCard",
        {"Values": {"projections": [measure_field(t, m) for t, m in val_fields]}})

def make_matrix_heatmap(name, x, y, w, h, row_fields, col_fields, val_table, val_measure,
                        min_color="#F8696B", mid_color="#FFEB84", max_color="#63BE7B"):
    """Matrix whose value cells are shaded on a red→amber→green scale (conditional backColor)."""
    rows = [column_field(t, c) for t, c in row_fields]
    cols = [column_field(t, c) for t, c in col_fields]
    obj = _matrix_objects()
    obj["values"] = [{"properties": {"backColor": {"solid": {"color": {"expr": {"FillRule": {
        "Input": {"Measure": {"Expression": {"SourceRef": {"Entity": val_table}}, "Property": val_measure}},
        "FillRule": {"linearGradient3": {
            "min": {"color": {"Literal": {"Value": f"'{min_color}'"}}},
            "mid": {"color": {"Literal": {"Value": f"'{mid_color}'"}}},
            "max": {"color": {"Literal": {"Value": f"'{max_color}'"}}},
            "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'asZero'"}}}
        }}}}}}}, "fontSize": _lit("10L")}}]
    return make_visual(name, x, y, w, h, "pivotTable",
        {"Rows": {"projections": rows}, "Columns": {"projections": cols},
         "Values": {"projections": [measure_field(val_table, val_measure)]}}, objects=obj)
