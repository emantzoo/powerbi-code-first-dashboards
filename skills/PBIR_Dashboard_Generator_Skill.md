# PBIR Dashboard Generator — Claude Skill

## What This Skill Does

Given a Power BI data model, generate a complete `generate_pages.py` script that creates a multi-page dashboard using PBIR JSON format. The script uses a library of `make_*` helper functions to produce `visual.json` files that Power BI renders directly.

**You are writing Python code that IS the dashboard.** No clicking, no dragging, no manual UI work.

---

## Primary Input: `*_Dashboard_Prompts.md`

The `*_Dashboard_Prompts.md` files in this repo are the primary data model specification. Each one contains:
- **Phase 0**: Table definitions with column names, data types, and row counts
- **Phase 1A**: Relationship definitions (which IDs connect which tables, cardinality, active/inactive)
- **Phase 1B**: Calendar table DAX expression
- **Phase 1C-H**: All DAX measures organized in logical batches (core KPIs, time intelligence, ratios, conditional formatting)
- **Visual Layout Reference**: Page-by-page layout specification with exact positions and data bindings

**To generate a script:** Read the prompt file, extract the table names, column names, and DAX measure names, then use the visual layout reference (if present) or the heuristics below to design the pages.

**End-to-end from CSVs:** If the user provides raw CSV files instead of a prompt file:
1. Inspect CSV headers to identify Fact vs Dim tables (Fact = transactional with IDs + dates + amounts; Dim = lookup with descriptive columns)
2. Design a star schema with relationships (Fact foreign keys → Dim primary keys)
3. Write a `*_Dashboard_Prompts.md` with all phases
4. Then generate the `generate_pages.py` from it

---

## When To Use This Skill

Use this skill when the user:
- Says "read the prompt file and generate a generate_pages.py"
- Provides a `*_Dashboard_Prompts.md` file or points to one in the repo
- Provides CSV files and asks for a complete dashboard
- Provides a data model description (tables, columns, measures, relationships)
- Asks you to "create a dashboard" or "generate pages" for a Power BI project
- Provides TMDL files or describes their schema
- Asks to adapt the code-first dashboard approach to a new dataset

---

## Script Structure

Every `generate_pages.py` follows this structure:

```python
import json, os, hashlib, shutil

# 1. BASE path — points to the PBIR pages folder inside the .pbip project
BASE = r"C:\path\to\project.Report\definition\pages"

# 2. Schema constants
SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"

# 3. Helper functions (uid, measure_field, column_field, make_visual, all make_* functions)
# 4. Page definitions (lists of visuals)
# 5. Write pages and update pages.json
```

---

## Core Helper Functions

Always include these at the top of every script:

```python
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

---

## Function Implementations

Include all of these in every generated script:

```python
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
```

---

## Layout Rules

The canvas is **1280 x 720 pixels**. Follow these layout conventions:

### Standard Page Layout

```
┌──────────────────────────────────────────────────────────┐
│ Row 1 (y=10, h=110): KPI Cards + Slicer                 │
│   4-5 cards evenly spaced, slicer at right edge          │
├──────────────────────────────────────────────────────────┤
│ Row 2 (y=140, h=280): Primary Charts                    │
│   2-3 charts side by side                                │
├──────────────────────────────────────────────────────────┤
│ Row 3 (y=440, h=260): Detail Table or Matrix             │
│   Full width (x=20, w=1230)                              │
└──────────────────────────────────────────────────────────┘
```

### Spacing Rules
- Left margin: x=20
- Right edge: x + w ≤ 1260
- Gap between visuals: 10-20px
- Card row: y=10, height=110
- Chart row: y=140, height=280
- Table row: y=440, height=260
- Slicer: typically top-right corner, w=210-270

### Cards Layout (5 cards + 1 slicer)
```python
make_card("c1", 20, 10, 190, 110, ...)    # card 1
make_card("c2", 225, 10, 190, 110, ...)   # card 2
make_card("c3", 430, 10, 190, 110, ...)   # card 3
make_card("c4", 635, 10, 190, 110, ...)   # card 4
make_card("c5", 840, 10, 190, 110, ...)   # card 5
make_slicer("s1", 1045, 10, 210, 110, ...) # slicer
```

### Cards Layout (4 cards + 1 slicer)
```python
make_card("c1", 20, 10, 235, 110, ...)
make_card("c2", 270, 10, 235, 110, ...)
make_card("c3", 520, 10, 235, 110, ...)
make_card("c4", 770, 10, 235, 110, ...)
make_slicer("s1", 1020, 10, 230, 110, ...)
```

### Two Charts Side by Side
```python
make_line_chart("chart1", 20, 140, 610, 280, ...)
make_clustered_bar("chart2", 650, 140, 600, 280, ...)
```

### Three Charts Side by Side
```python
make_chart("chart1", 20, 140, 400, 280, ...)
make_chart("chart2", 440, 140, 380, 280, ...)
make_chart("chart3", 840, 140, 410, 280, ...)
```

---

## Visual Selection Heuristics

When choosing which visual type to use for a measure, follow these rules:

### Cards (make_card)
- Use for top-level KPI measures: totals, rates, counts, averages
- Pick the 4-6 most important measures for cards
- Percentage measures (rates, margins) are good card candidates

### Line Charts (make_line_chart)
- Use when the category axis is a time column (Year_Month, Date, Quarter)
- Use dual-line when comparing current vs prior period (e.g., Total Revenue + Revenue PY)
- Ideal for trends, time intelligence measures

### Bar / Column Charts (make_clustered_bar, make_clustered_column)
- Use when comparing values across categories (suppliers, products, departments)
- Horizontal bars (clustered_bar) when category names are long
- Vertical columns (clustered_column) when category names are short
- Use for ranking: "Top N by value"

### Donut / Pie (make_donut, make_pie)
- Use for part-of-whole with fewer than 8 categories
- Donut preferred over pie in most cases
- Good for distribution by warehouse, region, or status

### Area Charts (make_area_chart)
- Use for rate/percentage measures over time (e.g., On Time Delivery Rate)
- Good alternative to line chart when you want to emphasize magnitude

### Tables (make_table)
- Use for detail data showing multiple columns + measures
- Place at the bottom of the page (Row 3)
- Mix columns (False) and measures (True) in the fields_list
- Include identifying columns first, then measures

### Matrix (make_matrix)
- Use for cross-tabulation: dimension rows × measure values
- Good for warehouse/department comparison across multiple KPIs

### Gauges (make_gauge)
- Use for rate/percentage measures with known targets
- Group 2-3 gauges together in a row

### Scatter (make_scatter)
- Use when comparing two measures per entity (e.g., Lead Time vs OTD Rate per supplier)
- Add size measure for bubble sizing (e.g., Order Value)

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

When organizing a dashboard with many measures, group pages by theme:

1. **Overview / KPIs page** — Top-level metrics, trends over time, key distributions
2. **Dimension deep-dive pages** — One page per major dimension (Supplier Scorecard, Product Analysis, Department View)
3. **Detail / drill-down page** — Tables and matrices with granular data
4. **Geographic page** — Maps, treemaps (if location data exists)
5. **Advanced analytics page** — Scatter plots, gauges, waterfalls (if the model has enough measures)

Typical dashboard: 4-7 pages. Each page: 8-12 visuals.

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

## Example 1: Generating from a Prompt File

**Input from user:**
> Read `ecommerce/ECommerce_Dashboard_Prompts.md` and generate a `generate_pages.py` for this dashboard.

**What you do:**
1. Read the prompt file — extract table names (FactSales, FactReturns, DimProduct, DimCustomer, DimStore, Calendar), column names, and all DAX measure names from `_Measures`
2. Check if the prompt file has a Visual Layout Reference section — if yes, follow it exactly
3. If no layout reference, use the heuristics in this skill to design pages
4. Write a complete `generate_pages.py` with all helper functions and page definitions

## Example 2: Generating from a Data Model Description

**Input from user:**
> I have tables: FactSales, DimProduct (with category, product_name), DimStore (with store_name, region), Calendar (with Year_Month, Year).
> Measures in _Measures: Total Revenue, Total Units, Avg Price, Revenue PY, Revenue YoY Growth, Revenue by Region.

**Your output:** A complete `generate_pages.py` with:
- Page 1: Overview — 4 cards (Revenue, Units, Avg Price, YoY Growth), slicer (Year), line chart (Revenue + Revenue PY over Year_Month), bar chart (Revenue by category), donut (Units by region)
- Page 2: Product Analysis — cards, bar chart by product_name, table with product details
- Page 3: Store Performance — cards, bar chart by store_name, matrix (store × measures)

## Example 3: End-to-end from CSVs

**Input from user:**
> Here are my CSV files in `data/`. Create a complete dashboard for this data.

**What you do:**
1. Inspect CSV headers to identify Fact tables (transactional) vs Dim tables (lookup/reference)
2. Identify foreign key relationships (shared ID columns between tables)
3. Write a `*_Dashboard_Prompts.md` with all phases: data loading, relationships, Calendar table, DAX measures
4. Generate a `generate_pages.py` from the prompt file you just wrote

## Example 4: Brief-Driven Generation (CSVs + One Paragraph)

This is the most powerful workflow. The user provides raw CSV files and a short business brief. You do everything: design the data model, write the prompt file, and generate the dashboard script.

### How it works

1. User drops CSVs into the project folder
2. User gives a 1-3 sentence brief describing what they want to track
3. You inspect the CSVs, design the data model, write the `*_Dashboard_Prompts.md`, and generate the `generate_pages.py`

### What the brief should contain

- The business domain (e-commerce, healthcare, HR, finance, logistics, etc.)
- The key questions or KPIs they care about (revenue, retention, delivery performance, etc.)
- Optionally: any specific comparisons they want (YoY, by region, by department)

### Example briefs and how to respond

**Brief 1: E-Commerce**
> "This is e-commerce sales data. I want to track revenue, profit margins, returns, and customer retention. Compare current vs last year."

Your response:
- Inspect CSVs to find: FactSales, FactReturns, DimProduct, DimCustomer, DimStore
- Design relationships from matching ID columns
- Write prompt file with measures: Total Revenue, Total Cost, Profit Margin, Return Rate, Customer Count, Revenue PY, Revenue YoY Growth, L3M/L12M rolling averages
- Generate pages: Executive Overview, Product Performance, Customer Trends, Returns Analysis

**Brief 2: Hospital Operations**
> "Hospital admissions and wait times data. I need to monitor patient flow, department workload, readmission rates, and wait time bottlenecks."

Your response:
- Inspect CSVs to find: FactAdmissions, FactWaitTimes, DimDepartment, DimDoctor, DimPatient
- Design relationships including inactive date relationships (admission_date, discharge_date)
- Write prompt file with measures: Total Admissions, Avg Length of Stay (DATEDIFF), Readmission Rate (EARLIER self-join), Avg Wait Time, Department Utilization
- Generate pages: Hospital Overview, Department Deep-Dive, Wait Time Analysis, Patient Demographics

**Brief 3: HR / People Analytics**
> "Employee data with monthly snapshots and recruitment pipeline. Track headcount, attrition, compensation equity, and hiring funnel."

Your response:
- Inspect CSVs to find: FactEmployeeSnapshot, FactRecruitment, DimEmployee, DimDepartment, DimJobLevel
- Design relationships with multiple inactive relationships for snapshot pattern
- Write prompt file with measures: Current Headcount (LASTDATE snapshot), Attrition Rate (POWER annualized), Gender Pay Gap (VAR+RETURN), Avg Tenure (DATEDIFF), Offer Acceptance Rate
- Generate pages: Workforce Overview, Attrition Analysis, Compensation & Equity, Recruitment Funnel

**Brief 4: Finance / Budgeting**
> "Actuals vs budget data by cost center. Need variance analysis, spend trends, and department-level drill-down."

Your response:
- Inspect CSVs to find: FactActuals, FactBudget, DimCostCenter, DimAccount, DimDepartment
- Design multi-fact model with shared dimensions
- Write prompt file with measures: Total Actuals, Total Budget, Variance (Actuals - Budget), Variance %, Spend YTD, Budget Utilization Rate
- Generate pages: Financial Overview, Variance Analysis, Department Spend, Account Detail

**Brief 5: Marketing / Campaign Analytics**
> "Campaign performance data — impressions, clicks, conversions, spend. Want to see ROI by channel and funnel drop-off."

Your response:
- Inspect CSVs to find: FactCampaigns, DimChannel, DimAudience, DimCreative
- Design relationships from campaign/channel IDs
- Write prompt file with measures: Total Impressions, Click-Through Rate, Conversion Rate, Cost Per Acquisition, ROAS (Return on Ad Spend), Funnel Drop-off Rate
- Generate pages: Campaign Overview, Channel Comparison, Funnel Analysis, ROI Deep-Dive

### DAX pattern selection based on domain

When designing measures from a brief, choose DAX patterns based on what the data supports:

| Data Pattern | DAX Pattern | Example |
|-------------|-------------|---------|
| Date column exists | SAMEPERIODLASTYEAR, TOTALYTD, DATESINPERIOD | Revenue PY, Revenue YTD, L3M Revenue |
| Multiple date columns on fact table | USERELATIONSHIP with inactive relationships | Avg Lead Time = DATEDIFF(order_date, delivery_date) |
| Snapshot/periodic data | LASTDATE pattern | Current Headcount, Latest Inventory |
| Self-referencing logic | EARLIER | 30-Day Readmission Rate |
| Cross-table calculation | SUMX with RELATED | Total Cost = SUMX(Sales, Sales[Qty] * RELATED(Product[UnitCost])) |
| Rate/ratio | DIVIDE (always safe division) | Profit Margin = DIVIDE([Profit], [Revenue], 0) |
| Annualized rate from periodic data | POWER | Annualized Attrition = 1 - POWER(1 - [Period Rate], 12) |
| Conditional status | SWITCH returning hex colors | RAG Status for conditional formatting |
| Part-of-whole | DIVIDE with ALL | % of Total = DIVIDE([Revenue], CALCULATE([Revenue], ALL(DimProduct))) |

### Output structure

For a brief-driven generation, always produce two files:

1. `{Domain}_Dashboard_Prompts.md` — Full data model specification following the existing Phase 0/1A/1B/1C+ structure
2. `scripts/generate_pages.py` — Complete visual generation script with all pages and visuals

The user then executes Phase 0-1 (via MCP, manually, or any other method) and runs the Python script. Dashboard ready.

---

Use the layout rules, visual selection heuristics, and naming conventions described above.
