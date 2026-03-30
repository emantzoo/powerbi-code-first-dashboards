# CLAUDE.md

## Project Overview

This repo contains code-first Power BI dashboards built using PBIR (Power BI Enhanced Report) JSON format. Python scripts generate `visual.json` files that Power BI renders directly — no drag-and-drop, no manual UI work.

There are 4 dashboard projects: `ecommerce/`, `hospital/`, `hr/`, `supply_chain/`. Each has:
- `data/` — CSV files (Fact and Dim tables)
- `scripts/generate_pages.py` — Python script that generates all dashboard pages and visuals
- `*_Dashboard_Prompts.md` — Data model specification (tables, relationships, DAX measures)

Supporting files:
- `workflow/PowerBI_From_Code_Workflow.md` — Methodology guide
- `skills/PBIR_Dashboard_Generator_Skill.md` — Claude skill for auto-generating scripts from data models

## Repo Structure

```
powerbi-code-first-dashboards/
  ecommerce/
    data/                          # 5 CSVs
    scripts/generate_pages.py
    ECommerce_Dashboard_Prompts.md
  hospital/
    data/                          # 5 CSVs
    scripts/generate_pages.py
    Hospital_Dashboard_Prompts.md
  hr/
    data/                          # 5 CSVs
    scripts/generate_pages.py
    HR_Dashboard_Prompts.md
  supply_chain/
    data/                          # 6 CSVs
    scripts/generate_pages.py
    SupplyChain_Dashboard_Prompts.md
  workflow/
    PowerBI_From_Code_Workflow.md
  skills/
    PBIR_Dashboard_Generator_Skill.md
  images/                          # Dashboard screenshots
  README.md
  CLAUDE.md                        # This file
```

---

## How generate_pages.py Works

Each script follows this pattern:

1. **Imports and constants** — `json`, `os`, `hashlib`, `shutil` + PBIR schema URLs
2. **Helper functions** — `uid()`, `measure_field()`, `column_field()`, `make_visual()`, and 18+ `make_*` visual builder functions
3. **Page definitions** — Lists of visuals with positions and data bindings
4. **Write pages** — `write_page()` creates the PBIR folder structure, `pages.json` is updated

The script writes directly into the `.Report/definition/pages/` folder of a saved `.pbip` project. Power BI Desktop must be CLOSED when running the script.

### Key concept: measure_field vs column_field
- `measure_field("_Measures", "Total Revenue")` — binds to a DAX measure (uses `Measure` in JSON)
- `column_field("DimProduct", "category")` — binds to a table column (uses `Column` in JSON)
- Charts typically use column for Category axis and measure for Y axis
- Cross-table bindings are normal: category from DimProduct, value from _Measures

### Canvas
- All pages are **1280 x 720 pixels**
- Standard layout: cards at top (y=10, h=110), charts in middle (y=140, h=280), tables at bottom (y=440, h=260)

---

## Available make_* Functions

| Function | Visual Type | Key Parameters |
|----------|------------|----------------|
| `make_card` | cardVisual | table, measure |
| `make_gauge` | gauge | val_table, val_measure + optional target/min/max |
| `make_clustered_bar` | clusteredBarChart | cat_table, cat_col, val_table, val_measure |
| `make_clustered_column` | clusteredColumnChart | cat_table, cat_col, val_table, val_measure |
| `make_line_chart` | lineChart | cat + 1-2 measures (supports dual Y) |
| `make_area_chart` | areaChart | cat + measure |
| `make_donut` | donutChart | cat + measure |
| `make_pie` | pieChart | cat + measure |
| `make_waterfall` | waterfallChart | cat + measure |
| `make_funnel` | funnel | cat + measure |
| `make_scatter` | scatterChart | detail_col + x_measure + y_measure + optional size |
| `make_ribbon` | ribbonChart | cat + series + measure |
| `make_stacked_column` | clusteredColumnChart | cat + series + measure |
| `make_stacked_bar` | clusteredBarChart | cat + series + measure |
| `make_hundred_pct_stacked_bar` | hundredPercentStackedBarChart | cat + series + measure |
| `make_hundred_pct_stacked_column` | hundredPercentStackedColumnChart | cat + series + measure |
| `make_table` | tableEx | fields_list: [(table, col, is_measure_bool), ...] |
| `make_matrix` | pivotTable | row_fields, col_fields, val_fields |
| `make_treemap` | treemap | cat + measure + optional group |
| `make_filled_map` | filledMap | location_col + measure |
| `make_map` | map | cat + lat + lng + size_measure |
| `make_slicer` | slicer | table, column |

---

## Tasks You Can Do in This Repo

### 1. Generate a generate_pages.py from a prompt file

The `*_Dashboard_Prompts.md` files are the primary data model input. They contain everything needed: tables, columns, data types, relationships, Calendar table DAX, all measures, and the visual layout specification.

**Workflow:**
1. Read the project's `*_Dashboard_Prompts.md` file to extract tables, columns, relationships, and DAX measure names
2. Read the `skills/PBIR_Dashboard_Generator_Skill.md` for the full function library and layout conventions
3. Generate a `generate_pages.py` script that:
   - Includes ALL helper functions (uid, measure_field, column_field, make_visual, write_visual, write_page, and all 20+ make_* functions)
   - Defines pages matching the Visual Layout Reference in the prompt file (if present)
   - Chooses visual types using the heuristics in the skill file
   - Groups pages thematically: Overview, Dimension deep-dives, Detail tables, Maps, Advanced analytics
   - Sets `BASE` to a placeholder path with a comment to update it
   - Uses the naming convention: `{page_prefix}_{description}` for visual names

**End-to-end from CSVs:** If the user provides raw CSV files instead of a prompt file, first inspect the CSV headers, design the star schema, write the `*_Dashboard_Prompts.md` with all phases (data loading, relationships, Calendar, DAX measures, visual layout), THEN generate the `generate_pages.py` from it.

### 2. Create or modify DAX measures and prompt files

When writing `*_Dashboard_Prompts.md` files:

- Follow the existing prompt file structure: Phase 0 (data loading), Phase 1A (relationships), Phase 1B (Calendar), Phase 1C-H (DAX measure batches)
- Organize measures in logical batches: core KPIs first, then time intelligence, then ratios, then conditional formatting
- Use the star schema pattern: Fact tables with foreign keys, Dim tables with primary keys, Calendar table for time intelligence
- Always include: DIVIDE for safe division, SAMEPERIODLASTYEAR for YoY, TOTALYTD/TOTALMTD for period accumulations
- Specify relationship properties explicitly: cardinality, active/inactive, cross-filter direction
- Mark date relationships as INACTIVE when multiple date columns exist on a fact table (use USERELATIONSHIP in measures)

DAX conventions used in this project:
- Measures table: `_Measures`
- Calendar table columns: `Date`, `Year`, `Month_Num`, `Month_Name`, `Quarter`, `Year_Month`, `Year_Quarter`
- Naming: descriptive measure names without abbreviations (e.g., "On Time Delivery Rate" not "OTD_Rate")
- SWITCH for RAG status returns hex color strings: `"#2ECC71"` green, `"#F39C12"` amber, `"#E74C3C"` red

### 3. Add new visual types to existing scripts

When adding a new visual type:

1. Create the visual manually in Power BI Desktop with PBIR enabled
2. Save the .pbip and inspect the generated `visual.json`
3. Identify the `visualType` string and the `queryState` slot names
4. Write a new `make_*` function following the existing pattern
5. Add it to ALL generate_pages.py scripts (keep the function library consistent)
6. Update the Available Visual Types table in README.md
7. Update the skill file with the new function

### 4. Add new pages to existing dashboards

- Define a new page ID: `p_id = uid("prefix_page_name")`
- Create a list of visuals using the make_* functions
- Call `write_page(p_id, "Display Name", visuals_list)`
- Add the page ID to the `pageOrder` list in the pages.json update at the bottom of the script

---

## Code Style

- Python scripts use only stdlib (`json`, `os`, `hashlib`, `shutil`) — no external dependencies
- Helper functions are defined at the top of each script, not imported from a shared module (each script is self-contained)
- Visual names use snake_case with a 2-3 char page prefix: `"sc1_orders"`, `"ec2_bar"`
- Page IDs are generated via `uid("descriptive_seed")` using MD5 hash truncated to 20 chars
- JSON is written with `indent=2` and `ensure_ascii=False`

---

## Important Rules

- **Never modify .pbip/.pbir/.tmdl files directly** — the Python scripts only write into the `pages/` folder
- **Power BI Desktop must be CLOSED** when running generate_pages.py — it locks the files
- **Table and measure names are case-sensitive** — they must match the data model exactly
- **The `_Measures` table** is where all DAX measures live — reference it as `measure_field("_Measures", "Measure Name")`
- **Cross-table bindings are normal** — a chart's category comes from a Dim table, its value from `_Measures`
- **PBIR schema version** — currently using `visualContainer/2.6.0`, `page/2.1.0`, `pagesMetadata/1.0.0`
- **Do not add formatting/styling objects** to visual JSON unless specifically asked — keep visuals clean and let Power BI themes handle formatting

---

## Testing

After generating or modifying a `generate_pages.py`:

1. Verify the script runs without errors: `python scripts/generate_pages.py`
2. Check that the expected number of page folders and visual.json files were created
3. Open the .pbip in Power BI Desktop to confirm visuals render correctly

There are no automated tests currently. The scripts are validated by opening the resulting .pbip in Power BI Desktop.
