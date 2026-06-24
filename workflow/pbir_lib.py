"""
workflow/pbir_lib.py — Shared PBIR visual helper library.

All Power BI code-first dashboard projects import from here instead of
duplicating helpers inline.  Pure stdlib (json, os, hashlib, shutil, sys).
Optional: Pillow (PIL) for make_background PNG rendering.

QUICK START
-----------
From a project's generate_pages.py:

    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "workflow"))
    import pbir_lib as pb

    pb.BASE = r"C:\\...\\my_report.Report\\definition\\pages"
    # — OR use resolve_pages_base() to avoid hard-coding paths:
    pb.BASE = pb.resolve_pages_base("my_report_name")

    p1 = [
        pb.make_card("p1_rev", 20, 60, 295, 110, "_Measures", "Total Revenue"),
        pb.make_clustered_bar("p1_bar", 20, 140, 600, 280, "DimProduct", "category",
                              "_Measures", "Total Revenue"),
    ]
    pb.write_page(uid("p1_overview"), "Overview", p1)
    pb.write_pages_json([uid("p1_overview")])

CANVAS & LAYOUT CONSTANTS
--------------------------
All pages: 1280 × 720 px
  CANVAS_W=1280  CANVAS_H=720  MARGIN=20  GAP=10
  TITLE_H=50     CARD_H=120    SLICER_H=38

  std_layout(n_card_rows=1, n_slicer_rows=1)
    → dict with card_y / slicer_y / body_y / body_h

  card_row(prefix, y, h, measures, table="_Measures")
    → list of evenly-spaced KPI cards across the canvas

  slicer_row(prefix, y, h, slicers, dropdown=True)
    → list of evenly-spaced dropdown slicers across the canvas

FUNCTION REFERENCE
------------------
Core
  uid(seed)                              → 20-char hex ID
  measure_field(table, measure)          → PBIR measure projection dict
  column_field(table, column)            → PBIR column projection dict
  make_visual(...)                       → raw visual dict (use make_* helpers instead)
  write_visual(page_dir, visual_json)
  write_page(page_id, display_name, visuals)
  write_pages_json(page_order)
  resolve_pages_base(report_name)        → pages folder path (CLI / env / default)

KPI / summary
  make_card(name, x, y, w, h, table, measure)
  make_multi_card(name, x, y, w, h, val_fields)   [(table, measure), ...]
  make_gauge(name, x, y, w, h, val_table, val_measure, target_table=None, ...)

Bar / column
  make_clustered_bar(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)
  make_clustered_column(name, ...)
  make_clustered_bar_multi(name, x, y, w, h, cat_table, cat_col, val_list)
  make_clustered_column_multi(name, ...)
  make_clustered_bar_gradient(name, ...)
  make_clustered_column_gradient(name, ...)
  make_measure_bar(name, x, y, w, h, val_list)     no category — each measure = bar
  make_measure_column(name, ...)
  make_stacked_bar(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure)
  make_stacked_column(name, ...)
  make_hundred_pct_stacked_bar(name, ...)
  make_hundred_pct_stacked_column(name, ...)
  make_ribbon(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure)
  make_waterfall(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)
  make_funnel(name, ...)

Line / area
  make_line_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure,
                  val2_table=None, val2_measure=None, val3_table=None, val3_measure=None,
                  ref_value=None, ref_label=None)
  make_area_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)
  make_combo_chart(name, x, y, w, h, cat_table, cat_col, col_table, col_measure,
                   line_table, line_measure)

Pie / donut / scatter / treemap
  make_donut(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)
  make_pie(name, ...)
  make_scatter(name, x, y, w, h, detail_table, detail_col, x_table, x_measure,
               y_table, y_measure, size_table=None, size_measure=None,
               series_table=None, series_col=None)
  make_treemap(name, x, y, w, h, cat_table, cat_col, val_table, val_measure,
               group_table=None, group_col=None)

Table / matrix
  make_table(name, x, y, w, h, fields_list)       [(table, col, is_measure_bool), ...]
  make_matrix(name, x, y, w, h, row_fields, col_fields, val_fields)
  make_matrix_heatmap(name, x, y, w, h, row_fields, col_fields, val_table, val_measure,
                      min_color=..., mid_color=..., max_color=...)

Map
  make_filled_map(name, x, y, w, h, loc_table, loc_col, val_table, val_measure)
  make_map(name, x, y, w, h, cat_table, cat_col, lat_table, lat_col,
           lng_table, lng_col, size_table, size_measure)

AI visuals (fields must be wired manually on first open)
  make_key_influencers(name, x, y, w, h, analyze, explain_fields)
  make_decomposition_tree(name, x, y, w, h, analyze, explain_fields)

Slicer / UI
  make_slicer(name, x, y, w, h, table, column)
  make_title_bar(name, x, y, w, h, text, bg_color="#1E293B")
  make_button(name, x, y, w, h, text)

Script visuals (R / Python must be configured in Power BI Desktop)
  make_r_visual(name, x, y, w, h, fields_list, r_script)
  make_py_visual(name, x, y, w, h, fields_list, py_script)

Background (optional Pillow dependency)
  make_background(page_name, visuals, style="light", display_name=None, colors=None)
  write_background(page_id, png_path)
"""

import hashlib
import json
import os
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


# ── Module-level pages path ──────────────────────────────────────────────────
BASE = None  # set by the importing script before calling write_page()


# ── PBIR schema URLs ─────────────────────────────────────────────────────────
SCHEMA_VISUAL = (
    "https://developer.microsoft.com/json-schemas/fabric/"
    "item/report/definition/visualContainer/2.7.0/schema.json"
)
SCHEMA_PAGE = (
    "https://developer.microsoft.com/json-schemas/fabric/"
    "item/report/definition/page/2.1.0/schema.json"
)
SCHEMA_PAGES = (
    "https://developer.microsoft.com/json-schemas/fabric/"
    "item/report/definition/pagesMetadata/1.0.0/schema.json"
)


# ── Path resolution ──────────────────────────────────────────────────────────
def resolve_pages_base(report_name, env_var=None):
    """Return the .Report/definition/pages folder without hard-coding a machine path.

    Resolution order (first hit wins):
      1. CLI arg  --pages=<full path>      (used as-is)
      2. CLI arg  --root=<dir>             → <dir>/<report_name>.Report/definition/pages
      3. env var  *env_var* (if given)     → same construction as (2)
      4. default  → <repo_root>/build/<report_name>.Report/definition/pages
                    (dry-run sandbox; not an openable .pbip on its own)

    Parameters
    ----------
    report_name : str
        e.g. "epikast_internal_dashb"
    env_var : str, optional
        Name of an environment variable containing the root directory,
        e.g. "EPIKAST_PBI_ROOT".
    """
    for a in sys.argv[1:]:
        if a.startswith("--pages="):
            return a.split("=", 1)[1]
    root = None
    for a in sys.argv[1:]:
        if a.startswith("--root="):
            root = a.split("=", 1)[1]
            break
    if not root and env_var:
        root = os.environ.get(env_var)
    if not root:
        # Default: <this file's grandparent>/build/
        here = os.path.dirname(os.path.abspath(__file__))
        root = os.path.normpath(os.path.join(here, "..", "build"))
    return os.path.join(root, f"{report_name}.Report", "definition", "pages")


# ── Private formatting helpers ───────────────────────────────────────────────
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
                            "rowCount": _lit("5L"),
                            "contentOrder": _lit("'referenceLabel_callout_image'")}},
            {"properties": {"rectangleRoundedCurve": _lit("8L"), "paddingUniform": _lit("10L"),
                            "backgroundTransparency": _lit("0D")},
             "selector": {"id": "default"}},
        ],
        "accentBar": [{"properties": {"show": _lit("true")}, "selector": {"id": "default"}}],
        "shadowCustom": [{"properties": {"show": _lit("true")}, "selector": {"id": "default"}}],
        "shapeCustomRectangle": [{"properties": {"tileShape": _lit("'rectangleRoundedByPixel'")},
                                  "selector": {"id": "default"}}],
    }


def _chart_objects(show_labels=False, label_position="'OutsideEnd'"):
    obj = {
        "categoryAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false")}}],
        "valueAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false"),
                                      "gridlineStyle": _lit("'dashed'"),
                                      "gridlineColor": _solid("#E2E8F0")}}],
    }
    if show_labels:
        obj["labels"] = [{"properties": {"show": _lit("true"),
                                         "labelPosition": _lit(label_position),
                                         "fontSize": _lit("9L")}}]
    return obj


def _line_chart_objects():
    return {
        "categoryAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false")}}],
        "valueAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false"),
                                      "gridlineStyle": _lit("'dashed'"),
                                      "gridlineColor": _solid("#E2E8F0")}}],
        "lineStyles": [{"properties": {"strokeWidth": _lit("3L")}}],
    }


def _table_objects():
    return {
        "columnHeaders": [{"properties": {"bold": _lit("true"), "fontSize": _lit("10L"),
                                          "fontColor": _solid("#FFFFFF"),
                                          "backColor": _theme_color(0)}}],
        "values": [{"properties": {"fontSize": _lit("10L"), "backColor": _solid("#FFFFFF"),
                                   "backColorAlternate": _solid("#F8FAFC")}}],
        "grid": [{"properties": {"gridHorizontal": _lit("true"),
                                 "gridHorizontalColor": _solid("#E2E8F0"),
                                 "gridVertical": _lit("false"), "rowPadding": _lit("4L")}}],
    }


def _matrix_objects():
    return {
        "columnHeaders": [{"properties": {"bold": _lit("true"), "fontSize": _lit("10L"),
                                          "fontColor": _solid("#FFFFFF"),
                                          "backColor": _theme_color(0)}}],
        "rowHeaders": [{"properties": {"fontSize": _lit("10L")}}],
        "values": [{"properties": {"fontSize": _lit("10L"), "backColor": _solid("#FFFFFF"),
                                   "backColorAlternate": _solid("#F8FAFC")}}],
        "grid": [{"properties": {"gridHorizontal": _lit("true"),
                                 "gridHorizontalColor": _solid("#E2E8F0"),
                                 "gridVertical": _lit("false"), "rowPadding": _lit("4L")}}],
    }


def _gauge_objects():
    return {"gaugeAxis": [{"properties": {"fontSize": _lit("10L")}}]}


def _gradient_fill(measure_table, measure_name, min_color="'minColor'", max_color="'maxColor'"):
    return {
        "dataPoint": [
            {
                "properties": {
                    "fill": {
                        "solid": {
                            "color": {
                                "expr": {
                                    "FillRule": {
                                        "Input": {
                                            "Measure": {
                                                "Expression": {"SourceRef": {"Entity": measure_table}},
                                                "Property": measure_name,
                                            }
                                        },
                                        "FillRule": {
                                            "linearGradient2": {
                                                "min": {"color": {"Literal": {"Value": min_color}}},
                                                "max": {"color": {"Literal": {"Value": max_color}}},
                                                "nullColoringStrategy": {
                                                    "strategy": {"Literal": {"Value": "'asZero'"}}
                                                },
                                            }
                                        },
                                    }
                                }
                            }
                        }
                    }
                },
                "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]},
            }
        ]
    }


# ── Core helpers ─────────────────────────────────────────────────────────────
def uid(seed):
    """Return a 20-char hex ID derived from the MD5 of *seed*."""
    return hashlib.md5(seed.encode()).hexdigest()[:20]


# ---------------------------------------------------------------------------
# Layout constants — shared across all dashboard scripts
# ---------------------------------------------------------------------------
CANVAS_W = 1280
CANVAS_H = 720
MARGIN   = 20    # left/right page margin
GAP      = 10    # vertical + horizontal gap between items

# Standard element heights
TITLE_H   = 50    # title bar
CARD_H    = 120   # KPI card  (tall enough for value + label)
SLICER_H  = 38    # dropdown slicer row
TITLE_BOT = TITLE_H + GAP   # y immediately below title bar (= 60)


def std_layout(n_card_rows=1, n_slicer_rows=1):
    """Return a dict of standard y-positions and heights.

    Positions are computed from the top of the canvas:
      title bar → card rows → slicer rows → body content area

    Args:
        n_card_rows:   number of card rows (0 or 1; more uncommon)
        n_slicer_rows: number of slicer rows (0 or 1)

    Returns a dict with keys:
        title_bot  — y immediately below title (= TITLE_H + GAP)
        card_y     — y of first card row  (= title_bot)
        slicer_y   — y of first slicer row
        body_y     — y where main content starts
        body_h     — height available for main content (fills to canvas bottom - 10px)

    Example (1 card row + 1 slicer row, the most common pattern):
        L = std_layout()
        # L["card_y"] = 60, L["slicer_y"] = 190, L["body_y"] = 238, L["body_h"] = 472
    """
    title_bot = TITLE_H + GAP
    card_y    = title_bot
    slicer_y  = card_y + n_card_rows * (CARD_H + GAP)
    body_y    = slicer_y + n_slicer_rows * (SLICER_H + GAP)
    body_h    = CANVAS_H - body_y - 10
    return {
        "title_bot": title_bot,
        "card_y":    card_y,
        "slicer_y":  slicer_y,
        "body_y":    body_y,
        "body_h":    body_h,
    }


def card_row(prefix, y, h, measures, table="_Measures"):
    """Return a list of evenly-spaced cards across the canvas width.

    Args:
        prefix:   visual name prefix, e.g. "s1"
        y:        top y position
        h:        card height
        measures: list of measure name strings
        table:    DAX table name (default "_Measures")

    Example:
        card_row("s1", 60, 110, ["Total Calls", "Connect Rate", "Avg AHT"])
    """
    n = len(measures)
    total_gaps = GAP * (n - 1)
    w = (CANVAS_W - 2 * MARGIN - total_gaps) // n
    visuals = []
    for i, m in enumerate(measures):
        x = MARGIN + i * (w + GAP)
        name = f"{prefix}_card{i}"
        visuals.append(make_card(name, x, y, w, h, table, m))
    return visuals


def slicer_row(prefix, y, h, slicers, dropdown=True):
    """Return a list of evenly-spaced slicers across the canvas width.

    Args:
        prefix:   visual name prefix
        y:        top y position
        h:        slicer height
        slicers:  list of (table, column) tuples
        dropdown: if True (default) render as compact dropdown, else list

    Example:
        slicer_row("s1", 295, 32, [("DimCalendar","Quarter"), ("DimRep","Team")])
    """
    n = len(slicers)
    total_gaps = GAP * (n - 1)
    w = (CANVAS_W - 2 * MARGIN - total_gaps) // n
    visuals = []
    for i, (tbl, col) in enumerate(slicers):
        x = MARGIN + i * (w + GAP)
        name = f"{prefix}_slicer{i}"
        visuals.append(make_slicer(name, x, y, w, h, tbl, col, dropdown=dropdown))
    return visuals


def measure_field(table, measure):
    """PBIR field projection for a DAX measure."""
    return {
        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": table}},
                              "Property": measure}},
        "queryRef": f"{table}.{measure}",
        "nativeQueryRef": measure,
    }


def column_field(table, column):
    """PBIR field projection for a table column."""
    return {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": table}},
                             "Property": column}},
        "queryRef": f"{table}.{column}",
        "nativeQueryRef": column,
    }


def make_visual(name, x, y, w, h, vtype, query_state=None, objects=None,
                visual_container_objects=None, z=1000, how_created=None):
    """Build the raw visual dict.  Prefer the make_* helpers over calling this directly."""
    v = {
        "$schema": SCHEMA_VISUAL,
        "name": uid(name),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
        "visual": {"visualType": vtype, "drillFilterOtherVisuals": True},
    }
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
    """Write a single visual.json into the page's visuals sub-folder."""
    vdir = os.path.join(page_dir, "visuals", visual_json["name"])
    os.makedirs(vdir, exist_ok=True)
    with open(os.path.join(vdir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(visual_json, f, indent=2, ensure_ascii=False)


def write_page(page_id, display_name, visuals):
    """Write page.json and all visual.json files for one report page.

    Requires pbir_lib.BASE to be set before calling.
    Clears any existing visuals/ folder first so stale visuals are removed.
    """
    if BASE is None:
        raise RuntimeError(
            "pbir_lib.BASE is not set — assign it in the caller before write_page()."
        )
    page_dir = os.path.join(BASE, page_id)
    visuals_dir = os.path.join(page_dir, "visuals")
    if os.path.exists(visuals_dir):
        shutil.rmtree(visuals_dir)
    os.makedirs(visuals_dir, exist_ok=True)
    with open(os.path.join(page_dir, "page.json"), "w", encoding="utf-8") as f:
        json.dump({
            "$schema": SCHEMA_PAGE,
            "name": page_id,
            "displayName": display_name,
            "displayOption": "FitToPage",
            "height": 720,
            "width": 1280,
        }, f, indent=2)
    for v in visuals:
        write_visual(page_dir, v)


def write_pages_json(page_order):
    """Write (or overwrite) pages.json with the given page order."""
    with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
        json.dump({
            "$schema": SCHEMA_PAGES,
            "pageOrder": page_order,
            "activePageName": page_order[0],
        }, f, indent=2)


# ── KPI / summary visuals ─────────────────────────────────────────────────────
def make_card(name, x, y, w, h, table, measure):
    """Single-value KPI card (cardVisual)."""
    return make_visual(name, x, y, w, h, "cardVisual",
        {"Data": {"projections": [measure_field(table, measure)]}},
        objects=_card_objects())


def make_multi_card(name, x, y, w, h, val_fields):
    """A-vs-B comparison card showing multiple measures as rows (multiRowCard).
    val_fields = [(table, measure), ...]
    """
    return make_visual(name, x, y, w, h, "multiRowCard",
        {"Values": {"projections": [measure_field(t, m) for t, m in val_fields]}})


def make_gauge(name, x, y, w, h, val_table, val_measure,
               target_table=None, target_measure=None,
               min_table=None, min_measure=None,
               max_table=None, max_measure=None):
    """Radial gauge.  Only the value is required; target / min / max are optional."""
    qs = {"Y": {"projections": [measure_field(val_table, val_measure)]}}
    if target_table and target_measure:
        qs["TargetValue"] = {"projections": [measure_field(target_table, target_measure)]}
    if min_table and min_measure:
        qs["MinValue"] = {"projections": [measure_field(min_table, min_measure)]}
    if max_table and max_measure:
        qs["MaxValue"] = {"projections": [measure_field(max_table, max_measure)]}
    return make_visual(name, x, y, w, h, "gauge", qs, objects=_gauge_objects())


# ── Bar / column charts ───────────────────────────────────────────────────────
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


def make_clustered_bar_multi(name, x, y, w, h, cat_table, cat_col, val_list):
    """Clustered bar with several measures side by side.
    val_list = [(table, measure), ...]
    """
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(t, m) for t, m in val_list]}},
        objects=_chart_objects(show_labels=False))


def make_clustered_column_multi(name, x, y, w, h, cat_table, cat_col, val_list):
    """Clustered column with several measures side by side.
    val_list = [(table, measure), ...]
    """
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(t, m) for t, m in val_list]}},
        objects=_chart_objects(show_labels=False))


def make_clustered_bar_gradient(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    """Clustered bar with min→max gradient conditional formatting on bars."""
    base = _chart_objects(show_labels=True)
    base.update(_gradient_fill(val_table, val_measure))
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=base)


def make_clustered_column_gradient(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    """Clustered column with min→max gradient conditional formatting on columns."""
    base = _chart_objects(show_labels=True)
    base.update(_gradient_fill(val_table, val_measure))
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=base)


def make_measure_bar(name, x, y, w, h, val_list):
    """Horizontal bar chart with NO category — each measure renders as its own bar.
    Use to compare measures with no shared dimension (e.g. AI vs Non-AI rates).
    val_list = [(table, measure), ...]
    """
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Y": {"projections": [measure_field(t, m) for t, m in val_list]}},
        objects=_chart_objects(show_labels=True))


def make_measure_column(name, x, y, w, h, val_list):
    """Column chart with NO category — each measure renders as its own column.
    val_list = [(table, measure), ...]
    """
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Y": {"projections": [measure_field(t, m) for t, m in val_list]}},
        objects=_chart_objects(show_labels=True))


def make_stacked_bar(name, x, y, w, h, cat_table, cat_col,
                     series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "barChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())


def make_stacked_column(name, x, y, w, h, cat_table, cat_col,
                        series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "columnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())


def make_hundred_pct_stacked_bar(name, x, y, w, h, cat_table, cat_col,
                                 series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "hundredPercentStackedBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())


def make_hundred_pct_stacked_column(name, x, y, w, h, cat_table, cat_col,
                                    series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "hundredPercentStackedColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())


def make_ribbon(name, x, y, w, h, cat_table, cat_col,
                series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "ribbonChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())


def make_waterfall(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "waterfallChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True))


def make_funnel(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "funnel",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True))


# ── Line / area / combo charts ────────────────────────────────────────────────
def make_line_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure,
                    val2_table=None, val2_measure=None,
                    val3_table=None, val3_measure=None,
                    ref_value=None, ref_label=None):
    """Line chart with up to 3 measures and an optional reference line.

    Parameters
    ----------
    ref_value : numeric, optional
        Y-axis value for a dashed reference line.
    ref_label : str, optional
        Label displayed next to the reference line.
    """
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Y": {"projections": [measure_field(val_table, val_measure)]}}
    if val2_table and val2_measure:
        qs["Y"]["projections"].append(measure_field(val2_table, val2_measure))
    if val3_table and val3_measure:
        qs["Y"]["projections"].append(measure_field(val3_table, val3_measure))
    obj = _line_chart_objects()
    if ref_value is not None:
        obj["y1AxisReferenceLine"] = [{
            "properties": {
                "show": _lit("true"),
                "value": _lit(f"'{ref_value}'"),
                "displayName": _lit(f"'{ref_label or ref_value}'"),
                "lineColor": _solid("#CD3333"),
                "transparency": _lit("20D"),
                "style": _lit("'dashed'"),
                "dataLabelShow": _lit("true"),
            },
            "selector": {"id": "0"},
        }]
    return make_visual(name, x, y, w, h, "lineChart", qs, objects=obj)


def make_area_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "areaChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_line_chart_objects())


def make_combo_chart(name, x, y, w, h, cat_table, cat_col,
                     col_table, col_measure, line_table, line_measure):
    """Column + line combo on a shared category; line on the secondary axis."""
    qs = {
        "Category": {"projections": [column_field(cat_table, cat_col)]},
        "Y": {"projections": [measure_field(col_table, col_measure)]},
        "Y2": {"projections": [measure_field(line_table, line_measure)]},
    }
    return make_visual(name, x, y, w, h, "lineClusteredColumnComboChart", qs,
                       objects=_chart_objects(show_labels=False))


# ── Pie / donut / scatter / treemap ──────────────────────────────────────────
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


def make_scatter(name, x, y, w, h, detail_table, detail_col,
                 x_table, x_measure, y_table, y_measure,
                 size_table=None, size_measure=None,
                 series_table=None, series_col=None):
    qs = {
        "Category": {"projections": [column_field(detail_table, detail_col)]},
        "X": {"projections": [measure_field(x_table, x_measure)]},
        "Y": {"projections": [measure_field(y_table, y_measure)]},
    }
    if size_table and size_measure:
        qs["Size"] = {"projections": [measure_field(size_table, size_measure)]}
    if series_table and series_col:
        qs["Series"] = {"projections": [column_field(series_table, series_col)]}
    return make_visual(name, x, y, w, h, "scatterChart", qs)


def make_treemap(name, x, y, w, h, cat_table, cat_col, val_table, val_measure,
                 group_table=None, group_col=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Values": {"projections": [measure_field(val_table, val_measure)]}}
    if group_table and group_col:
        qs["Group"] = {"projections": [column_field(group_table, group_col)]}
    return make_visual(name, x, y, w, h, "treemap", qs)


# ── Table / matrix ───────────────────────────────────────────────────────────
def make_table(name, x, y, w, h, fields_list):
    """Table visual.
    fields_list = [(table, col_or_measure, is_measure_bool), ...]
    """
    projections = [measure_field(t, c) if m else column_field(t, c)
                   for t, c, m in fields_list]
    return make_visual(name, x, y, w, h, "tableEx",
        {"Values": {"projections": projections}},
        objects=_table_objects())


def make_matrix(name, x, y, w, h, row_fields, col_fields, val_fields):
    """Pivot / matrix visual.
    row_fields  = [(table, column), ...]
    col_fields  = [(table, column), ...]  or []
    val_fields  = [(table, measure), ...]
    """
    rows = [column_field(t, c) for t, c in row_fields]
    cols = [column_field(t, c) for t, c in col_fields] if col_fields else []
    vals = [measure_field(t, m) for t, m in val_fields]
    qs = {"Rows": {"projections": rows}, "Values": {"projections": vals}}
    if cols:
        qs["Columns"] = {"projections": cols}
    return make_visual(name, x, y, w, h, "pivotTable", qs, objects=_matrix_objects())


def make_matrix_heatmap(name, x, y, w, h, row_fields, col_fields,
                        val_table, val_measure,
                        min_color="#F8696B", mid_color="#FFEB84", max_color="#63BE7B"):
    """Matrix with red→amber→green conditional background colour on value cells."""
    rows = [column_field(t, c) for t, c in row_fields]
    cols = [column_field(t, c) for t, c in col_fields]
    obj = _matrix_objects()
    obj["values"] = [{
        "properties": {
            "backColor": {
                "solid": {
                    "color": {
                        "expr": {
                            "FillRule": {
                                "Input": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": val_table}},
                                        "Property": val_measure,
                                    }
                                },
                                "FillRule": {
                                    "linearGradient3": {
                                        "min": {"color": {"Literal": {"Value": f"'{min_color}'"}}},
                                        "mid": {"color": {"Literal": {"Value": f"'{mid_color}'"}}},
                                        "max": {"color": {"Literal": {"Value": f"'{max_color}'"}}},
                                        "nullColoringStrategy": {
                                            "strategy": {"Literal": {"Value": "'asZero'"}}
                                        },
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "fontSize": _lit("10L"),
        }
    }]
    return make_visual(name, x, y, w, h, "pivotTable",
        {"Rows": {"projections": rows}, "Columns": {"projections": cols},
         "Values": {"projections": [measure_field(val_table, val_measure)]}},
        objects=obj)


# ── Map visuals ───────────────────────────────────────────────────────────────
def make_filled_map(name, x, y, w, h, loc_table, loc_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "filledMap",
        {"Category": {"projections": [column_field(loc_table, loc_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})


def make_map(name, x, y, w, h, cat_table, cat_col,
             lat_table, lat_col, lng_table, lng_col,
             size_table, size_measure):
    """Bubble map. Lat/Lng are columns; size is a measure."""
    return make_visual(name, x, y, w, h, "map",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [column_field(lat_table, lat_col)]},
         "X": {"projections": [column_field(lng_table, lng_col)]},
         "Size": {"projections": [measure_field(size_table, size_measure)]}})


# ── AI visuals ────────────────────────────────────────────────────────────────
def make_key_influencers(name, x, y, w, h, analyze, explain_fields):
    """Key Influencers AI visual.

    analyze = (table, field, is_measure_bool) — the outcome to explain.
    explain_fields = [(table, column), ...] — candidate drivers.

    NOTE: native AI visual.  If field bindings don't take effect, wire them
    manually in Power BI Desktop (Analyze / Explain by panels) — takes ~30 s.
    """
    at, an, am = analyze
    a_proj = measure_field(at, an) if am else column_field(at, an)
    qs = {"Analyze": {"projections": [a_proj]},
          "ExplainBy": {"projections": [column_field(t, c) for t, c in explain_fields]}}
    return make_visual(name, x, y, w, h, "keyDriversVisual", qs)


def make_decomposition_tree(name, x, y, w, h, analyze, explain_fields):
    """Decomposition Tree AI visual.

    analyze = (table, measure) — the metric to break down.
    explain_fields = [(table, column), ...] — dimensions to drill into.

    NOTE: native AI visual.  Rebind manually if role names differ on your version.
    """
    at, am = analyze
    qs = {"Analyze": {"projections": [measure_field(at, am)]},
          "Explain": {"projections": [column_field(t, c) for t, c in explain_fields]}}
    return make_visual(name, x, y, w, h, "decompositionTreeVisual", qs)


# ── Slicer / UI elements ──────────────────────────────────────────────────────
def make_slicer(name, x, y, w, h, table, column, dropdown=False):
    objects = None
    if dropdown:
        objects = {
            "data": [{"properties": {"mode": _lit("'Dropdown'")}}],
        }
    return make_visual(name, x, y, w, h, "slicer",
        {"Values": {"projections": [column_field(table, column)]}},
        objects=objects)


def make_title_bar(name, x, y, w, h, text, bg_color="#1E293B"):
    """Full-width title bar (styled textbox with coloured background)."""
    return make_visual(name, x, y, w, h, "textbox",
        objects={"general": [{"properties": {"paragraphs": [{"textRuns": [{
            "value": text,
            "textStyle": {"fontFamily": "Segoe UI Semibold",
                          "fontSize": "18px", "color": "#FFFFFF"},
        }]}]}}]},
        visual_container_objects={
            "background": [{"properties": {"show": _lit("true"),
                                           "color": _solid(bg_color),
                                           "transparency": _lit("0D")}}],
            "visualHeader": [{"properties": {"show": _lit("false")}}],
        },
        z=9000)


def make_button(name, x, y, w, h, text):
    """Navigation button.
    Page navigation target must be set manually in Power BI Desktop
    (Format > Action > Page navigation).
    """
    obj = {
        "icon": [
            {"properties": {"shapeType": _lit("'blank'")}, "selector": {"id": "default"}},
            {"properties": {"show": _lit("false")}},
        ],
        "text": [
            {"properties": {"show": _lit("true")}},
            {"properties": {"text": _lit(f"'{text}'"),
                            "horizontalAlignment": _lit("'center'")},
             "selector": {"id": "default"}},
        ],
    }
    return make_visual(name, x, y, w, h, "actionButton",
                       objects=obj, z=8000, how_created="InsertVisualButton")


# ── Script visuals ───────────────────────────────────────────────────────────
def make_r_visual(name, x, y, w, h, fields_list, r_script):
    """R script visual.
    fields_list = [(table, col_or_measure, is_measure_bool), ...]
    The fields are bound into a data.frame called `dataset`.
    R / Python must be enabled in Power BI Desktop Options.
    """
    projections = [measure_field(t, c) if m else column_field(t, c)
                   for t, c, m in fields_list]
    escaped = r_script.replace("'", "\\'")
    return make_visual(name, x, y, w, h, "scriptVisual",
        {"Values": {"projections": projections}},
        objects={"script": [{"properties": {
            "source": _lit(f"'{escaped}'"), "provider": _lit("'R'")
        }}]})


def make_py_visual(name, x, y, w, h, fields_list, py_script):
    """Python script visual (same contract as make_r_visual, provider = Python)."""
    projections = [measure_field(t, c) if m else column_field(t, c)
                   for t, c, m in fields_list]
    escaped = py_script.replace("'", "\\'")
    return make_visual(name, x, y, w, h, "scriptVisual",
        {"Values": {"projections": projections}},
        objects={"script": [{"properties": {
            "source": _lit(f"'{escaped}'"), "provider": _lit("'Python'")
        }}]})


# ── Background image generation (optional Pillow) ────────────────────────────
def _hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _cluster_visuals(visuals):
    """Cluster visual positions into row groups for background layout."""
    PAD, HEADER_H, FOOTER_H = 10, 50, 40
    W, H, ROW_GAP = 1280, 720, 80
    rects = []
    for v in visuals:
        pos = v.get("position", {})
        x, y, w, h = pos.get("x", 0), pos.get("y", 0), pos.get("width", 0), pos.get("height", 0)
        if v.get("visual", {}).get("visualType", "") in ("textbox", "actionButton"):
            continue
        if w > 0 and h > 0:
            rects.append((x, y, w, h))
    if not rects:
        return rects, []
    sorted_rects = sorted(rects, key=lambda r: r[1])
    clusters, current = [], [sorted_rects[0]]
    for rect in sorted_rects[1:]:
        if abs(rect[1] - max(r[1] for r in current)) <= ROW_GAP:
            current.append(rect)
        else:
            clusters.append(current)
            current = [rect]
    clusters.append(current)
    group_boxes = []
    for cluster in clusters:
        min_x = max(0, min(r[0] for r in cluster) - PAD)
        min_y = max(HEADER_H + 2, min(r[1] for r in cluster) - PAD)
        max_x = min(W, max(r[0] + r[2] for r in cluster) + PAD)
        max_y = min(H - FOOTER_H - 2, max(r[1] + r[3] for r in cluster) + PAD)
        group_boxes.append((min_x, min_y, max_x - min_x, max_y - min_y))
    return rects, group_boxes


def _get_palette(style="light", colors=None):
    if style == "dark":
        palette = dict(
            bg="#0F172A", container="#1E293B", border="#334155",
            accent="#60A5FA", header_bg="#1E293B", footer_bg="#1E293B",
            dot_color="#334155", divider="#334155", header_text="#FFFFFF")
    else:
        palette = dict(
            bg="#F1F5F9", container="#FFFFFF", border="#E2E8F0",
            accent="#2563EB", header_bg="#1E293B", footer_bg="#F8FAFC",
            dot_color="#E2E8F0", divider="#CBD5E1", header_text="#FFFFFF")
    if colors:
        palette.update(colors)
    return palette


def make_background(page_name, visuals, style="light", display_name=None, colors=None):
    """Generate a 1280×720 background image (PNG with Pillow, SVG fallback).

    Draws a header bar, footer bar, subtle grid dots, rounded-rect group
    containers clustered around visual positions, and accent stripes.

    Returns the path to the generated file.
    Requires Pillow for PNG output; falls back to SVG if Pillow is not installed.
    """
    W, H = 1280, 720
    RADIUS, HEADER_H, FOOTER_H, GRID_SPACING = 12, 50, 40, 40
    palette = _get_palette(style, colors)
    _, group_boxes = _cluster_visuals(visuals)
    bg_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backgrounds")
    os.makedirs(bg_dir, exist_ok=True)

    if HAS_PILLOW:
        img = Image.new("RGB", (W, H), _hex_to_rgb(palette["bg"]))
        draw = ImageDraw.Draw(img, "RGBA")
        dot_rgba = _hex_to_rgb(palette["dot_color"]) + (80,)
        for gx in range(GRID_SPACING, W, GRID_SPACING):
            for gy in range(HEADER_H + GRID_SPACING, H - FOOTER_H, GRID_SPACING):
                draw.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=dot_rgba)
        draw.rectangle([0, 0, W, HEADER_H], fill=_hex_to_rgb(palette["header_bg"]))
        if display_name:
            txt_rgb = _hex_to_rgb(palette["header_text"])
            try:
                font = ImageFont.truetype("segoeuib.ttf", 16)
            except OSError:
                try:
                    font = ImageFont.truetype("segoeui.ttf", 16)
                except OSError:
                    font = ImageFont.load_default()
            draw.text((20, 15), display_name, fill=txt_rgb, font=font)
        container_rgba = _hex_to_rgb(palette["container"]) + (153,)
        for (bx, by, bw, bh) in group_boxes:
            draw.rounded_rectangle([bx, by, bx + bw, by + bh],
                                   radius=RADIUS, fill=container_rgba,
                                   outline=_hex_to_rgb(palette["border"]), width=1)
            stripe_h = int(min(bh - 2 * RADIUS, bh * 0.6))
            stripe_y = int(by + (bh - stripe_h) / 2)
            draw.rounded_rectangle([bx, stripe_y, bx + 4, stripe_y + stripe_h],
                                   radius=2, fill=_hex_to_rgb(palette["accent"]) + (204,))
        divider_rgba = _hex_to_rgb(palette["divider"]) + (100,)
        for i, box in enumerate(sorted(group_boxes, key=lambda b: b[1])[:-1]):
            next_top = sorted(group_boxes, key=lambda b: b[1])[i + 1][1]
            box_bottom = box[1] + box[3]
            if next_top - box_bottom > 10:
                div_y = int((box_bottom + next_top) / 2)
                for dx in range(20, W - 20, 10):
                    draw.line([dx, div_y, dx + 6, div_y], fill=divider_rgba, width=1)
        draw.rectangle([0, H - FOOTER_H, W, H],
                       fill=_hex_to_rgb(palette["footer_bg"]) + (128,))
        png_path = os.path.join(bg_dir, f"{page_name}.png")
        img.save(png_path, "PNG")
        print(f"Background PNG: {png_path}")
        return png_path
    else:
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
               f'  <rect width="{W}" height="{H}" fill="{palette["bg"]}"/>',
               f'  <g opacity="0.5">']
        for gx in range(GRID_SPACING, W, GRID_SPACING):
            for gy in range(HEADER_H + GRID_SPACING, H - FOOTER_H, GRID_SPACING):
                svg.append(f'    <circle cx="{gx}" cy="{gy}" r="0.8" fill="{palette["dot_color"]}"/>')
        svg.append('  </g>')
        svg.append(f'  <rect x="0" y="0" width="{W}" height="{HEADER_H}" fill="{palette["header_bg"]}"/>')
        if display_name:
            svg.append(f'  <text x="20" y="33" font-family="Segoe UI Semibold, sans-serif" '
                       f'font-size="16" fill="{palette["header_text"]}">{display_name}</text>')
        for (bx, by, bw, bh) in group_boxes:
            svg.append(f'  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" '
                       f'rx="{RADIUS}" ry="{RADIUS}" fill="{palette["container"]}" '
                       f'stroke="{palette["border"]}" stroke-width="1" opacity="0.6"/>')
            sh = min(bh - 2 * RADIUS, bh * 0.6)
            sy = by + (bh - sh) / 2
            svg.append(f'  <rect x="{bx}" y="{sy:.0f}" width="4" height="{sh:.0f}" '
                       f'rx="2" ry="2" fill="{palette["accent"]}" opacity="0.8"/>')
        svg.append(f'  <rect x="0" y="{H - FOOTER_H}" width="{W}" height="{FOOTER_H}" '
                   f'fill="{palette["footer_bg"]}" opacity="0.5"/>')
        svg.append('</svg>')
        svg_path = os.path.join(bg_dir, f"{page_name}.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write('\n'.join(svg))
        print(f"Background SVG (install Pillow for PNG+auto-embed): {svg_path}")
        return svg_path


def write_background(page_id, png_path):
    """Embed a PNG background into a PBIR page.

    Copies the PNG to StaticResources/RegisteredResources, patches page.json
    with a background image reference, and updates report.json with the
    RegisteredResources package entry.

    Requires BASE to be set (same directory as the page folder).
    Only operates on .png files; no-ops otherwise.
    """
    if not png_path or not os.path.exists(png_path) or not png_path.endswith(".png"):
        return
    if BASE is None:
        raise RuntimeError("pbir_lib.BASE is not set — assign it before write_background().")

    report_dir = os.path.dirname(BASE)  # .Report/definition/
    page_json_path = os.path.join(BASE, page_id, "page.json")
    report_json_path = os.path.join(report_dir, "report.json")
    with open(png_path, "rb") as fh:
        file_hash = hashlib.md5(fh.read()).hexdigest()[:16]
    resource_name = f"bg_{file_hash}.png"

    res_dir = os.path.join(report_dir, "..", "StaticResources", "RegisteredResources")
    os.makedirs(res_dir, exist_ok=True)
    shutil.copy2(png_path, os.path.join(res_dir, resource_name))

    with open(page_json_path, "r", encoding="utf-8") as f:
        page = json.load(f)
    page["objects"] = {
        "background": [{"properties": {
            "image": {"image": {
                "name": {"expr": {"Literal": {"Value": f"'{os.path.basename(png_path)}'"}}},
                "url": {"expr": {"ResourcePackageItem": {
                    "PackageName": "RegisteredResources",
                    "PackageType": 1,
                    "ItemName": resource_name,
                }}},
                "scaling": {"expr": {"Literal": {"Value": "'Normal'"}}},
            }},
            "transparency": {"expr": {"Literal": {"Value": "0D"}}},
        }}],
        "displayArea": [{"properties": {
            "verticalAlignment": {"expr": {"Literal": {"Value": "'Top'"}}}
        }}],
    }
    with open(page_json_path, "w", encoding="utf-8") as f:
        json.dump(page, f, indent=2, ensure_ascii=False)

    with open(report_json_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    packages = report.get("resourcePackages", [])
    reg_pkg = next((p for p in packages if p.get("name") == "RegisteredResources"), None)
    if reg_pkg is None:
        reg_pkg = {"name": "RegisteredResources", "type": "RegisteredResources", "items": []}
        packages.append(reg_pkg)
    if resource_name not in {item["name"] for item in reg_pkg["items"]}:
        reg_pkg["items"].append({"name": resource_name, "path": resource_name, "type": "Image"})
    report["resourcePackages"] = packages
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Background embedded: {resource_name} -> page {page_id}")
