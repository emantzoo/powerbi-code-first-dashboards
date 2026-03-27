# Power BI Dashboard from Code — Complete Workflow

## What this does

Builds a complete Power BI dashboard with ZERO manual UI work:

- **Phase 0 (MCP Server):** Loads data files (CSV/Excel) into a blank Power BI Desktop — no manual Get Data
- **Phase 1 (MCP Server):** Creates the data model — relationships, DAX measures, date tables
- **Phase 2 (PBIR Generator):** Creates all report pages and visuals as JSON files
- **Result:** Open the .pbip file and the full dashboard is there, data-bound, ready to use

The entire pipeline — from raw CSV files to a finished multi-page dashboard — requires only opening a blank Power BI Desktop file. Everything else is automated via Claude Code or Cowork.

---

## Prerequisites

### Software

- Power BI Desktop (March 2026+, or earlier with preview features enabled)
- VS Code with the **Power BI Modeling MCP** extension (by Analysis Services / Microsoft)
- Claude Desktop app (with MCP server configured)
- Python 3.x installed

### Power BI Preview Features (File > Options > Preview features)

Enable all of these:

- Store reports using enhanced metadata format (PBIR)
- Power BI Project (.pbip) save option
- Store semantic model in TMDL format

### Claude Desktop MCP Config

File location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "powerbi-modeling-mcp": {
      "command": "C:\\Users\\YOUR_USERNAME\\.vscode\\extensions\\analysis-services.powerbi-modeling-mcp-VERSION-win32-x64\\server\\powerbi-modeling-mcp.exe",
      "args": ["--start"]
    }
  }
}
```

Replace `YOUR_USERNAME` and `VERSION` with your actual values. The path must be one unbroken line with double backslashes.

---

## Phase 0: Load Data via MCP (fully automated)

The MCP server can load CSV/Excel files directly into Power BI Desktop — no manual Get Data clicks needed.

### Step 1: Open blank Power BI Desktop

Just open Power BI Desktop. Don't load anything manually.

### Step 2: Connect MCP

1. Open Claude Desktop (Cowork or Code tab)
2. Type: `Connect to my open Power BI Desktop file`
3. Claude confirms connection

### Step 3: Load all data files

Tell Claude Code or Cowork:

```
Load all CSV files from C:\path\to\your\data\folder into my Power BI model.
Read the headers from each CSV and create tables with the correct column names and data types.
Refresh the model after loading.
```

Claude will:
- Scan the folder for CSV files
- Read headers to determine column names and types
- Create M Expression tables pointing to each CSV
- Refresh the model to load the actual data
- Confirm row counts for each table

This replaces all manual Get Data > CSV > Load clicks. Works with any number of files.

**Tip:** Keep all your CSVs in one folder. Claude Code will find and load them all in one go.

---

## Phase 1: Data Model via MCP Server

### Step 1: Create relationships

Tell Claude exactly what relationships you want. Template:

```
Create these relationships in my Power BI model:
- FactTable[foreign_key] -> DimTable[primary_key] (Many:1, active, single direction)
- FactTable2[date_col] -> Calendar[Date] (Many:1, INACTIVE, single direction)
```

Tips:
- Specify active vs INACTIVE explicitly
- Ask Claude to delete auto-detected relationships first if they conflict
- Use single-direction cross-filter unless you have a specific reason for both

### Step 2: Create date table (if needed)

```
Create a DAX calculated table called Calendar:
Calendar = ADDCOLUMNS(CALENDAR(DATE(2018,1,1), DATE(2025,12,31)),
    "Year", YEAR([Date]),
    "Quarter", "Q" & CEILING(MONTH([Date])/3, 1),
    "Month_Num", MONTH([Date]),
    "Month_Name", FORMAT([Date], "MMMM"),
    "Year_Quarter", FORMAT([Date], "YYYY") & "-Q" & CEILING(MONTH([Date])/3, 1),
    "Year_Month", FORMAT([Date], "YYYY-MM")
)
Then mark it as a Date Table using the Date column.
```

### Step 3: Create measures

Send measures in batches. Template:

```
Create these DAX measures in a new _Measures table:

Total Revenue = SUM(Sales[Revenue])
Total Cost = SUM(Sales[Cost])
Profit = [Total Revenue] - [Total Cost]
Profit Margin = DIVIDE([Profit], [Total Revenue], 0)
```

Recommended batches:
1. Core KPI measures (SUM, COUNT, AVERAGE, DIVIDE)
2. Time intelligence (TOTALMTD, TOTALYTD, SAMEPERIODLASTYEAR, DATESINPERIOD)
3. Measures using USERELATIONSHIP (for inactive relationships)
4. Conditional formatting measures (SWITCH for RAG status and hex colors)

### Step 4: Save as .pbip

In Power BI Desktop: **File > Save As > Power BI Project (.pbip)**

Choose a folder. This creates the PBIR folder structure you need for Phase 2.

**Close Power BI Desktop after saving.**

---

## Phase 2: Visuals via PBIR Python Script

### How PBIR works

When you save as .pbip with PBIR enabled, your report becomes a folder:

```
YourProject/
  YourProject.pbip
  YourProject.Report/
    definition/
      definition.pbir
      report.json
      pages/
        pages.json
        PageFolder1/
          page.json
          visuals/
            VisualFolder1/
              visual.json     <-- THIS is one chart/card/table
            VisualFolder2/
              visual.json
        PageFolder2/
          ...
  YourProject.SemanticModel/
    ...
```

Each `visual.json` defines one visual: its type, position, size, and data bindings. We generate these programmatically.

### The visual.json structure

Every visual follows this pattern:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "unique20charidentifr",
  "position": {
    "x": 20,
    "y": 10,
    "z": 1000,
    "height": 110,
    "width": 295,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "cardVisual",
    "query": {
      "queryState": {
        "Data": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": {
                    "SourceRef": { "Entity": "_Measures" }
                  },
                  "Property": "Total Budget"
                }
              },
              "queryRef": "_Measures.Total Budget",
              "nativeQueryRef": "Total Budget"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}
```

Key properties:
- **name**: Unique 20-char identifier (or any unique string up to 50 chars, must match folder name)
- **position**: x, y coordinates on 1280x720 canvas; z for stacking order
- **visualType**: `cardVisual`, `clusteredBarChart`, `lineChart`, `donutChart`, `areaChart`, `tableEx`, `pivotTable`, `slicer`, etc.
- **query.queryState**: Data bindings — which fields/measures power the visual

### Data binding patterns

**Measure (from a measures table):**
```json
{
  "field": {
    "Measure": {
      "Expression": { "SourceRef": { "Entity": "TableName" } },
      "Property": "Measure Name"
    }
  },
  "queryRef": "TableName.Measure Name",
  "nativeQueryRef": "Measure Name"
}
```

**Column (from a data table):**
```json
{
  "field": {
    "Column": {
      "Expression": { "SourceRef": { "Entity": "TableName" } },
      "Property": "column_name"
    }
  },
  "queryRef": "TableName.column_name",
  "nativeQueryRef": "column_name"
}
```

### Query state roles by visual type

| Visual Type | Roles |
|-------------|-------|
| cardVisual | Data: [measure] |
| clusteredBarChart | Category: [column], Y: [measure] |
| lineChart | Category: [column], Y: [measure] |
| areaChart | Category: [column], Y: [measure] |
| donutChart | Category: [column], Y: [measure] |
| tableEx | Values: [columns and measures mixed] |
| pivotTable (matrix) | Rows: [columns], Columns: [columns], Values: [measures] |
| slicer | Values: [column] |

### The Python generator script

The `generate_pbir_pages.py` script has helper functions:

```python
make_card(name, x, y, w, h, z, table, measure)
make_clustered_bar(name, x, y, w, h, z, cat_table, cat_col, val_table, val_measure)
make_line_chart(name, x, y, w, h, z, cat_table, cat_col, val_table, val_measure)
make_donut(name, x, y, w, h, z, cat_table, cat_col, val_table, val_measure)
make_area_chart(name, x, y, w, h, z, cat_table, cat_col, val_table, val_measure)
make_slicer(name, x, y, w, h, z, table, column)
make_table_visual(name, x, y, w, h, z, fields_list)
make_matrix(name, x, y, w, h, z, row_fields, col_fields, val_fields)
```

To create a new dashboard, modify the `build_all_pages()` function:

1. Define page IDs and display names
2. Create visual lists using the helper functions
3. Set x, y, width, height for layout (canvas is 1280 x 720)
4. Pass your actual table and column/measure names

### Running the script

```powershell
# Make sure Power BI Desktop is CLOSED
python generate_pbir_pages.py "C:\path\to\your\pbip\folder"

# Then open the .pbip file in Power BI Desktop
```

### Using Claude Code instead

If you prefer Claude Code (the Code tab in Claude Desktop), you can:

1. Open Claude Code and navigate to your .pbip project folder
2. Tell Claude:

```
I have a Power BI project saved as .pbip with PBIR format.
The data model has these tables: [list your tables]
And these measures in _Measures: [list your measures]

Generate PBIR visual.json files for a 4-page dashboard:
- Page 1: Executive Overview with 4 KPI cards and 3 charts
- Page 2: Trend Analysis with line charts and area charts
- Page 3: Detail Table with a matrix and table visuals
- Page 4: Drill-through page

Use the visual.json schema version 2.7.0.
Write the files directly into xx.Report/definition/pages/
```

Claude Code can write the files directly into your project folder.

### Using Cowork instead

In Cowork mode, give the same instructions but also point Claude to the generate_pbir_pages.py script:

```
Run the PBIR generator script at C:\path\to\generate_pbir_pages.py
targeting my Power BI project at C:\path\to\my\project
```

---

## Phase 3: Polish in Power BI Desktop

After generating, open the .pbip and do final touches manually:

- Adjust visual titles and formatting
- Set conditional formatting (background colors, data bars)
- Configure drill-through fields on the detail page
- Sync slicers across pages (View > Sync Slicers)
- Apply a custom color theme
- Add page navigation buttons
- Resize/reposition visuals if the auto-layout needs tweaking

This is 15-30 minutes of polish work vs 2-3 hours of building from scratch.

---

## Adapting for a new dataset

To build a completely different dashboard from scratch:

1. **Open blank Power BI Desktop** — don't load anything
2. **MCP loads data** — tell Claude Code to load all CSVs/Excel from your data folder
3. **MCP builds model** — relationships, Calendar table, all DAX measures
4. **Save as .pbip** — File > Save As > Power BI Project
5. **Close Power BI Desktop**
6. **PBIR script generates visuals** — adapt generate_pbir_pages.py with your tables/measures
7. **Reopen .pbip** — full dashboard ready

Total manual work: opening Power BI Desktop and clicking Save As. Everything else is code.

---

## Claude Code Mega-Prompt Template

Copy this template, fill in the bracketed sections, and paste into Claude Code. It handles the entire pipeline in one go:

```
I need you to build a complete Power BI dashboard using the PBIR code-first approach.

## Files
- Read PowerBI_From_Code_Workflow.md for methodology
- Read generate_pbir_pages.py for the visual generator template

## Phase 0: Load Data
Connect to my open Power BI Desktop file.
Load all CSV files from [YOUR_DATA_FOLDER_PATH] into the model.
Verify all tables loaded with correct row counts.

## Phase 1: Data Model

1. Delete all auto-detected relationships and create:
   [LIST YOUR RELATIONSHIPS]
   - Table1[key] -> Table2[key] (Many:1, active, single direction)
   All single-direction cross-filter.

2. Create a Calendar table from [YOUR_DATE_TABLE][date_column] range.
   Mark as date table. Create relationship to Calendar[Date].

3. Create _Measures table with these measures:

   [LIST ALL YOUR DAX MEASURES]
   Measure1 = SUM(Table[Column])
   Measure2 = DIVIDE([Measure1], [Measure3], 0)

## Phase 2: Save and Generate Visuals

Tell me to save as .pbip to [YOUR_SAVE_PATH] and close Power BI Desktop.

Then adapt generate_pbir_pages.py to create these pages:

[DESCRIBE EACH PAGE]
Page 1 - [Name]:
- [N] cards: [list measures]
- [chart type]: [x-axis table.column] vs [y-axis measure]
- [chart type]: [category] vs [value]

Page 2 - [Name]:
- ...

Use schema version 2.7.0. Canvas 1280x720.
Run the script against [YOUR_SAVE_PATH].
Then tell me to reopen the .pbip file.
```

---

## Troubleshooting

### Visual shows error or blank
- Check that the table name in `Entity` matches exactly (case-sensitive)
- Check that the measure/column name in `Property` matches exactly
- Verify the visual type string is correct (e.g. `clusteredBarChart` not `barChart`)

### Page doesn't appear
- Check `pages.json` includes the page folder name in `pageOrder`
- Check the page folder has a valid `page.json`

### Power BI won't open the .pbip
- Make sure the `$schema` URLs are correct and match your PBI version
- Validate JSON syntax (no trailing commas, proper quotes)
- Check the `definition.pbir` file still exists and points to the semantic model

### Schema version mismatch
- If Power BI updates, the schema version may change (e.g. 2.7.0 -> 2.8.0)
- Save any visual manually, check the new schema URL in the generated visual.json
- Update the `SCHEMA_VISUAL` constant in the Python script

---

## Key takeaways

- **MCP Server** handles everything server-side: loading data, relationships, DAX measures, date tables
- **PBIR format** handles the visual layer: charts, layout, data bindings — all as JSON files
- **Together** they cover 100% of a Power BI report from code — zero manual UI work
- **The .pbip folder is just text files** — version-controllable, reproducible, scriptable
- **Claude Code or Cowork** can orchestrate the entire pipeline from a single prompt
- **This workflow became possible in early 2026** — MCP server launched late 2025, PBIR became default March 2026
- **Most Power BI developers don't know this exists yet** — it's a genuine portfolio differentiator
