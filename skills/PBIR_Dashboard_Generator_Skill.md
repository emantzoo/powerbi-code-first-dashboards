# PBIR Dashboard Generator — Claude Skill (v2: Professional Formatting)

## What This Skill Does

Given a Power BI data model (tables, columns, relationships, DAX measures), generate a complete `generate_pages.py` script that creates a multi-page, **professionally formatted** dashboard using PBIR JSON format. The script uses `make_*` helper functions that produce `visual.json` files with built-in formatting — Power BI renders them as polished, presentation-ready visuals.

**You are writing Python code that IS the dashboard.** No clicking, no dragging, no manual UI work. The output should look intentional and professional on first open — not like a raw data dump that needs 30 minutes of formatting.

---

## When To Use This Skill

Use this skill when the user:
- Provides a data model description (tables, columns, measures, relationships)
- Asks you to "create a dashboard" or "generate pages" for a Power BI project
- Provides TMDL files, a `*_Dashboard_Prompts.md` file, or describes their schema
- Asks to adapt the code-first dashboard approach to a new dataset

---

## Design Principles

These principles guide every layout and visual choice. The goal is a dashboard that looks designed, not generated.

**1. Less is more.** Fewer visuals per page, each one larger and more readable. 5-8 visuals per page, not 8-12. White space is a feature.

**2. Every visual gets a title.** Use the measure name or a descriptive label. "Revenue by Month" not blank. "Top 10 Suppliers by Order Volume" not "clusteredBarChart". Titles are set via the `title` parameter in each `make_*` function.

**3. Cards are hero elements.** KPI cards should be tall enough to read (h=140, not h=60). Use 3-4 cards per page, not 5-6. Each card gets an accent bar and shadow.

**4. Charts need breathing room.** Two charts side by side is the max for readability. Three charts across only if they're simple (donuts, small bars). Never four.

**5. Tables go at the bottom — or on their own page.** A detail table crammed under two charts looks like an afterthought. If the table is important, give it a dedicated page or half the page height.

**6. Consistent visual language.** All charts on a page should use the same axis conventions (time on X for trends, categories on Y for comparisons). Don't mix horizontal and vertical bars on the same page.

---

## Script Structure

Every `generate_pages.py` follows this structure:

```python
import json, os, hashlib, shutil

# 1. BASE path — points to the PBIR pages folder inside the .pbip project
BASE = r"C:\path\to\project.Report\definition\pages"

# 2. Schema constants
SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"

# 3. Formatting helpers (_lit, _solid, _theme_color, _*_objects)
# 4. Core helpers (uid, measure_field, column_field, make_visual, write_visual, write_page)
# 5. Visual builder functions (all make_* functions with formatting)
# 6. Page definitions (lists of visuals)
# 7. Write pages and update pages.json
```

---

## Formatting Helpers

These utility functions build the verbose PBIR JSON property wrappers. Include them at the top of every script:

```python
def _lit(value):
    """Wrap a value in the PBIR Literal expression format."""
    return {"expr": {"Literal": {"Value": value}}}

def _solid(hex_color):
    """Wrap a hex color in the PBIR solid color format."""
    return {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hex_color}'"}}}}}

def _theme_color(color_id, percent=0):
    """Reference a theme data color."""
    return {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": color_id, "Percent": percent}}}}}
```

---

## Default Formatting Objects

Each visual category has a formatting function that returns the `objects` dict. These produce professional-looking visuals out of the box.

```python
def _card_objects():
    """Card: accent bar, shadow, rounded corners, clean padding."""
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
    """Chart: clean axes, light gridlines, optional data labels."""
    obj = {
        "categoryAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false")}}],
        "valueAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false"),
                                       "gridlineStyle": _lit("'dashed'"), "gridlineColor": _solid("#E2E8F0")}}]
    }
    if show_labels:
        obj["labels"] = [{"properties": {"show": _lit("true"), "labelPosition": _lit(label_position), "fontSize": _lit("9L")}}]
    return obj

def _line_chart_objects():
    """Line/area chart: clean axes, thicker lines, no data labels."""
    return {
        "categoryAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false")}}],
        "valueAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false"),
                                       "gridlineStyle": _lit("'dashed'"), "gridlineColor": _solid("#E2E8F0")}}],
        "lineStyles": [{"properties": {"strokeWidth": _lit("3L")}}]
    }

def _table_objects():
    """Table: styled headers, alternating rows, clean grid."""
    return {
        "columnHeaders": [{"properties": {"bold": _lit("true"), "fontSize": _lit("10L"),
                                           "fontColor": _solid("#FFFFFF"), "backColor": _theme_color(0)}}],
        "values": [{"properties": {"fontSize": _lit("10L"), "backColor": _solid("#FFFFFF"),
                                    "backColorAlternate": _solid("#F8FAFC")}}],
        "grid": [{"properties": {"gridHorizontal": _lit("true"), "gridHorizontalColor": _solid("#E2E8F0"),
                                  "gridVertical": _lit("false"), "rowPadding": _lit("4L")}}]
    }

def _matrix_objects():
    """Matrix: styled headers, clean grid, alternating rows."""
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
    """Gauge: clean font sizing."""
    return {"gaugeAxis": [{"properties": {"fontSize": _lit("10L")}}]}
```

---

## Core Helper Functions

Always include these in every script:

```python
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
```

---

## Available Visual Types — Function Reference

### KPI / Summary

| Function | Visual Type | Parameters | Use When |
|----------|------------|------------|----------|
| `make_card` | cardVisual | `(name, x, y, w, h, table, measure)` | Single KPI metric |
| `make_gauge` | gauge | `(name, x, y, w, h, val_table, val_measure, target_table=None, target_measure=None, min_table=None, min_measure=None, max_table=None, max_measure=None)` | Measure vs target |

### Charts — Category + Value

| Function | Visual Type | Parameters | Use When |
|----------|------------|------------|----------|
| `make_clustered_bar` | clusteredBarChart | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)` | Horizontal bars, comparing categories |
| `make_clustered_column` | clusteredColumnChart | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)` | Vertical bars, comparing categories |
| `make_line_chart` | lineChart | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, val2_table=None, val2_measure=None)` | Trends over time, supports dual lines |
| `make_area_chart` | areaChart | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)` | Trends with filled area |
| `make_donut` | donutChart | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)` | Part-of-whole, few categories (<8) |
| `make_pie` | pieChart | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)` | Part-of-whole, few categories (<6) |
| `make_waterfall` | waterfallChart | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)` | Cumulative contribution breakdown |
| `make_funnel` | funnel | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)` | Pipeline / sequential stages |

### Charts — Category + Series + Value

| Function | Visual Type | Parameters | Use When |
|----------|------------|------------|----------|
| `make_stacked_column` | clusteredColumnChart | `(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure)` | Stacked vertical bars |
| `make_stacked_bar` | clusteredBarChart | `(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure)` | Stacked horizontal bars |
| `make_hundred_pct_stacked_bar` | hundredPercentStackedBarChart | `(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure)` | Proportional comparison |
| `make_hundred_pct_stacked_column` | hundredPercentStackedColumnChart | `(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure)` | Proportional comparison |
| `make_ribbon` | ribbonChart | `(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure)` | Rank changes over time |

### Scatter / Multi-Measure

| Function | Visual Type | Parameters | Use When |
|----------|------------|------------|----------|
| `make_scatter` | scatterChart | `(name, x, y, w, h, detail_table, detail_col, x_table, x_measure, y_table, y_measure, size_table=None, size_measure=None)` | Correlation between two measures |

### Tables / Matrices

| Function | Visual Type | Parameters | Use When |
|----------|------------|------------|----------|
| `make_table` | tableEx | `(name, x, y, w, h, fields_list)` where fields_list = `[(table, col_or_measure, is_measure_bool), ...]` | Detail data, mixed columns + measures |
| `make_matrix` | pivotTable | `(name, x, y, w, h, row_fields, col_fields, val_fields)` where row_fields = `[(table, col), ...]`, val_fields = `[(table, measure), ...]` | Cross-tab / pivot with aggregations |

### Maps

| Function | Visual Type | Parameters | Use When |
|----------|------------|------------|----------|
| `make_filled_map` | filledMap | `(name, x, y, w, h, loc_table, loc_col, val_table, val_measure)` | Choropleth by country/state |
| `make_map` | map | `(name, x, y, w, h, cat_table, cat_col, lat_table, lat_col, lng_table, lng_col, size_table, size_measure)` | Bubble map with lat/lng |
| `make_treemap` | treemap | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, group_table=None, group_col=None)` | Hierarchical part-of-whole |

### Slicers

| Function | Visual Type | Parameters | Use When |
|----------|------------|------------|----------|
| `make_slicer` | slicer | `(name, x, y, w, h, table, column)` | Filter control for a column |

### Dashboard Elements

| Function | Visual Type | Parameters | Use When |
|----------|------------|------------|----------|
| `make_title_bar` | textbox | `(name, x, y, w, h, text, bg_color="#1E293B")` | Full-width page header with colored background |
| `make_button` | actionButton | `(name, x, y, w, h, text)` | Navigation button. Page navigation must be configured manually in Power BI Desktop (Format > Action > Page navigation) |

### Conditional Formatting Variants

| Function | Visual Type | Parameters | Use When |
|----------|------------|------------|----------|
| `make_clustered_bar_gradient` | clusteredBarChart | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)` | Bar chart with min/max gradient coloring |
| `make_clustered_column_gradient` | clusteredColumnChart | `(name, x, y, w, h, cat_table, cat_col, val_table, val_measure)` | Column chart with min/max gradient coloring |

### Script Visuals (R / Python)

| Function | Visual Type | Parameters | Use When |
|----------|------------|------------|----------|
| `make_r_visual` | scriptVisual | `(name, x, y, w, h, fields_list, r_script)` where fields_list = `[(table, col_or_measure, is_measure_bool), ...]` | Embed R code (ggplot2, forecast, etc.) with data bindings. Requires R installed and configured in Power BI Desktop. |

---

## Function Implementations

Include all of these in every generated script. Each function now includes built-in formatting via the `objects` parameter.

```python
def make_card(name, x, y, w, h, table, measure):
    return make_visual(name, x, y, w, h, "cardVisual",
        {"Data": {"projections": [measure_field(table, measure)]}},
        objects=_card_objects())

def make_slicer(name, x, y, w, h, table, column):
    return make_visual(name, x, y, w, h, "slicer",
        {"Values": {"projections": [column_field(table, column)]}})

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

# ── Dashboard Elements ─────────────────────────────────────────────

def make_title_bar(name, x, y, w, h, text, bg_color="#1E293B"):
    """Dashboard title bar — a styled text box with colored background."""
    return make_visual(name, x, y, w, h, "textbox",
        objects={
            "general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text,
                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "18px", "color": "#FFFFFF"}}]}]}}]
        },
        visual_container_objects={
            "background": [{"properties": {"show": _lit("true"), "color": _solid(bg_color), "transparency": _lit("0D")}}],
            "visualHeader": [{"properties": {"show": _lit("false")}}]
        }, z=9000)

def make_button(name, x, y, w, h, text):
    """Navigation button — styled action button with text.
    Page navigation must be configured manually in Power BI Desktop
    (Format > Action > Page navigation).
    """
    obj = {
        "icon": [{"properties": {"shapeType": _lit("'blank'")}, "selector": {"id": "default"}},
                 {"properties": {"show": _lit("false")}}],
        "text": [{"properties": {"show": _lit("true")}},
                 {"properties": {"text": _lit(f"'{text}'"), "horizontalAlignment": _lit("'center'")}, "selector": {"id": "default"}}]
    }
    return make_visual(name, x, y, w, h, "actionButton", objects=obj, z=8000, how_created="InsertVisualButton")

# ── Conditional Formatting Variants ────────────────────────────────

def _gradient_fill(measure_table, measure_name):
    """Build a conditional formatting gradient fill rule for bar/column chart data points."""
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

# ── Script Visuals (R / Python) ──────────────────────────────────

def make_r_visual(name, x, y, w, h, fields_list, r_script):
    """R script visual — embeds R code with data field bindings.
    fields_list: [(table, col_or_measure, is_measure_bool), ...]
    r_script: string of R code (will be escaped into PBIR literal format)
    """
    projections = [measure_field(t, c) if m else column_field(t, c) for t, c, m in fields_list]
    escaped = r_script.replace("'", "\\'")
    objects = {
        "script": [{"properties": {
            "source": _lit(f"'{escaped}'"),
            "provider": _lit("'R'")
        }}]
    }
    return make_visual(name, x, y, w, h, "scriptVisual",
        {"Values": {"projections": projections}}, objects=objects)
```

---

## Layout Rules

The canvas is **1280 x 720 pixels**. These layouts are designed for readability and professional appearance.

### Standard Page Layout — Spacious (preferred)

```
┌──────────────────────────────────────────────────────────┐
│ Row 1 (y=10, h=140): KPI Cards + Slicer                 │
│   3-4 cards, generous width, slicer at right edge        │
├──────────────────────────────────────────────────────────┤
│ Row 2 (y=170, h=310): Primary Charts                    │
│   2 charts side by side (never more than 3)              │
├──────────────────────────────────────────────────────────┤
│ Row 3 (y=500, h=200): Detail Table or leave empty        │
│   Full width — or omit for a cleaner page                │
└──────────────────────────────────────────────────────────┘
```

### Spacing Rules
- Left margin: x=20
- Right edge: x + w ≤ 1260
- Gap between visuals: 15-20px
- Card row: y=10, height=**140** (not 110 — gives cards room to breathe)
- Chart row: y=**170**, height=**310** (larger charts are more readable)
- Table row: y=**500**, height=**200** (or omit entirely)
- Slicer: top-right corner, w=220-260

### Cards Layout (3 cards + 1 slicer)
```python
make_card("c1", 20, 10, 300, 140, ...)     # card 1
make_card("c2", 340, 10, 300, 140, ...)    # card 2
make_card("c3", 660, 10, 300, 140, ...)    # card 3
make_slicer("s1", 980, 10, 270, 140, ...)  # slicer
```

### Cards Layout (4 cards + 1 slicer)
```python
make_card("c1", 20, 10, 230, 140, ...)     # card 1
make_card("c2", 265, 10, 230, 140, ...)    # card 2
make_card("c3", 510, 10, 230, 140, ...)    # card 3
make_card("c4", 755, 10, 230, 140, ...)    # card 4
make_slicer("s1", 1000, 10, 250, 140, ...) # slicer
```

### Two Charts Side by Side
```python
make_line_chart("chart1", 20, 170, 610, 310, ...)
make_clustered_bar("chart2", 650, 170, 600, 310, ...)
```

### Three Charts Side by Side (use sparingly)
```python
make_chart("chart1", 20, 170, 400, 310, ...)
make_chart("chart2", 435, 170, 395, 310, ...)
make_chart("chart3", 845, 170, 405, 310, ...)
```

### Full-Width Chart (for important trends)
```python
make_line_chart("chart1", 20, 170, 1230, 310, ...)
```

### Detail Table (full width, bottom of page)
```python
make_table("tbl", 20, 500, 1230, 200, ...)
```

### Dedicated Table Page (table gets most of the space)
```python
make_slicer("s1", 20, 10, 300, 50, ...)
make_table("tbl", 20, 80, 1230, 620, ...)
```

---

## Visual Selection Heuristics

When choosing which visual type to use for a measure, follow these rules:

### Cards (make_card)
- Use for top-level KPI measures: totals, rates, counts, averages
- Pick the **3-4 most important** measures for cards (not 5-6)
- Percentage measures (rates, margins) are good card candidates
- Card height should be **140px** — gives room for the accent bar, value, and label

### Line Charts (make_line_chart)
- Use when the category axis is a time column (Year_Month, Date, Quarter)
- Use dual-line when comparing current vs prior period (e.g., Total Revenue + Revenue PY)
- Ideal for trends, time intelligence measures
- **Give trend charts generous width** — at least 600px, ideally full width for key trends

### Bar / Column Charts (make_clustered_bar, make_clustered_column)
- Use when comparing values across categories (suppliers, products, departments)
- Horizontal bars (clustered_bar) when category names are long
- Vertical columns (clustered_column) when category names are short
- Use for ranking: "Top N by value"

### Donut / Pie (make_donut, make_pie)
- Use for part-of-whole with fewer than 8 categories
- Donut preferred over pie in most cases
- Good for distribution by warehouse, region, or status
- **Pair with another chart**, not alone — a donut next to a bar chart tells a better story

### Area Charts (make_area_chart)
- Use for rate/percentage measures over time (e.g., On Time Delivery Rate)
- Good alternative to line chart when you want to emphasize magnitude

### Tables (make_table)
- Use for detail data showing multiple columns + measures
- Place at the bottom of the page (Row 3) **or give a dedicated page**
- Mix columns (False) and measures (True) in the fields_list
- Include identifying columns first, then measures
- **Don't cram a table under charts if it's important** — give it space

### Matrix (make_matrix)
- Use for cross-tabulation: dimension rows × measure values
- Good for warehouse/department comparison across multiple KPIs

### Gauges (make_gauge)
- Use for rate/percentage measures with known targets
- Group 2-3 gauges together in a row

### Scatter (make_scatter)
- Use when comparing two measures per entity (e.g., Lead Time vs OTD Rate per supplier)
- Add size measure for bubble sizing (e.g., Order Value)
- **Give scatter plots generous space** — at least 500x300

### Waterfall (make_waterfall)
- Use for showing cumulative contribution by category
- Good for "which categories drive the total?"

### Funnel (make_funnel)
- Use for pipeline / sequential stages
- Good for recruitment funnels, sales pipelines

### Ribbon (make_ribbon)
- Use for showing rank changes over time
- Requires category (time), series (what's being ranked), and value

### Maps (make_filled_map, make_map)
- Use when data has geographic dimension (country, state, city)
- Filled map for country/state level
- Bubble map when lat/lng coordinates are available

### Slicers (make_slicer)
- Add one per page for the most useful filter dimension
- Common slicer fields: Year, Category, Region, Department, Warehouse

---

## Page Grouping Logic

When organizing a dashboard with many measures, group pages by theme. Aim for **4-6 pages** with **5-8 visuals each** (not 8-12). Every page should have a clear purpose that you could state in one sentence.

1. **Overview / KPIs page** — The 3-4 most important metrics as cards, one key trend chart (full width or half), one distribution chart. This page answers "how are we doing overall?"

2. **Dimension deep-dive pages** — One page per major dimension (Supplier Scorecard, Product Analysis, Department View). Each gets its own cards relevant to that dimension, 1-2 charts, and optionally a focused table.

3. **Detail / drill-down page** — Tables and matrices with granular data. Give the table most of the page height. This page answers "show me the raw numbers."

4. **Geographic page** — Maps, treemaps (only if location data exists). Don't force this page if there's no geographic dimension.

5. **Advanced analytics page** — Scatter plots, gauges, waterfalls. Only if the model has enough measures to make these meaningful. Don't add this page just to showcase visual variety.

---

## Page Footer — Writing Pages and Updating pages.json

Always end the script with:

```python
# Write all pages
write_page(p1_id, "Page Display Name", p1)
write_page(p2_id, "Second Page", p2)
# ... etc

# Update pages.json
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, ...],
               "activePageName": p1_id}, f, indent=2)

print("Done!")
```

---

## Data Binding Rules

### Measures go in `measure_field(table, measure)`
- DAX measures defined in `_Measures` table: `measure_field("_Measures", "Total Revenue")`
- The table name must match exactly what's in the data model
- Measure names must match exactly (case-sensitive)

### Columns go in `column_field(table, column)`
- Dimension columns: `column_field("DimProduct", "category")`
- Fact table columns: `column_field("FactOrders", "order_date")`
- Calendar columns: `column_field("Calendar", "Year_Month")`

### Cross-table bindings
- Category from one table, value from another — this is normal and expected
- Example: `make_clustered_bar("bar", x, y, w, h, "DimSupplier", "supplier_name", "_Measures", "Total Orders")`

---

## Naming Conventions

- Visual names: `{page_prefix}_{description}` — e.g., `"sc1_orders"`, `"sc2_otd_bar"`
- Page IDs: `uid("prefix_page1_name")` — e.g., `uid("sc_page1_kpis")`
- Keep names short but descriptive
- Prefix all visuals on a page with the same 2-3 character prefix

---

## Example: Generating from a Data Model Description

**Input from user:**
> I have tables: FactSales, DimProduct (with category, product_name), DimStore (with store_name, region), Calendar (with Year_Month, Year).
> Measures in _Measures: Total Revenue, Total Units, Avg Price, Revenue PY, Revenue YoY Growth.

**Your output:** A complete `generate_pages.py` with:
- Page 1: Overview — 3 cards (Revenue, Units, YoY Growth) + Year slicer, full-width line chart (Revenue + Revenue PY over Year_Month), bar chart (Revenue by category) + donut (Units by region) side by side
- Page 2: Product Analysis — 3 cards, bar chart by product_name, table with product details
- Page 3: Store Performance — 3 cards, bar chart by store_name, matrix (store × measures)

Use the layout rules, visual selection heuristics, and naming conventions described above. Every visual includes built-in formatting from the `_*_objects()` functions.
