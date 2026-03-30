# Power BI Dashboards from Code — Zero Manual UI Work

Build complete, multi-page Power BI dashboards entirely from code. Python scripts generate PBIR JSON files that Power BI renders directly — no dragging fields, no clicking through menus.

> **No AI required.** The scripts are pure Python with no external dependencies. You can use Claude Code / Cowork to auto-generate the scripts, or write them by hand.

### Supply Chain Dashboard — Sample Pages

![Supply Chain KPIs](images/supply_chain_kpis.png)
*KPI cards, line chart with YoY comparison, bar charts, donut, area chart*

![Advanced Analytics](images/supply_chain_advanced.png)
*Gauges, scatter plot (lead time vs OTD), waterfall, funnel, ribbon chart*

![Visual Showcase](images/supply_chain_showcase.png)
*Stacked columns, pie chart, 100% stacked bars, clustered column*

## Auto-Generate Dashboards from Your Data

This repo includes a **Claude skill** (`skills/PBIR_Dashboard_Generator_Skill.md`) that auto-generates dashboards from any dataset. Drop your CSVs into Claude Code, give a one-paragraph brief, and it writes everything:

> "This is e-commerce sales data. I want to track revenue, profit margins, returns, and customer retention. Compare current vs last year."

Claude inspects your CSV headers and structure — works best when tables follow star schema naming (`FactXxx`, `DimXxx`) with matching ID columns (`product_id`, `customer_id`). It designs relationships from matching keys, classifies columns by data type, writes DAX measures appropriate to the domain, and generates a multi-page dashboard script with appropriate visual types for each measure.

**Three ways to use it:**

| Method | Input | Output |
|--------|-------|--------|
| **Brief-driven** | CSVs + one paragraph | Prompt file + generate_pages.py |
| **From prompt file** | Existing `*_Dashboard_Prompts.md` | generate_pages.py |
| **From description** | Table/column/measure names | generate_pages.py |

The skill includes layout rules, visual selection heuristics, DAX pattern matching, and page grouping logic for 5+ business domains (e-commerce, healthcare, HR, finance, marketing).

## The Workflow

```
CSV files ──> Power BI Desktop ──> Save .pbip ──> Python Script ──> Open .pbip
              - Load CSVs            (PBIR)       generate_pages.py   (done!)
              - Relationships
              - Calendar table
              - DAX measures
```

**Phase 0-1 (Data Model):** Load CSVs, create relationships and DAX measures. Do this manually in Power BI Desktop, via MCP Server, or with any MCP-compatible client. The `*_Dashboard_Prompts.md` files specify exactly what to create.

**Phase 2 (Visuals):** Run `python scripts/generate_pages.py`. Pure Python, no dependencies. Writes `visual.json` files into the PBIR folder structure.

**Phase 3 (Polish):** Open the `.pbip` — all pages appear with data-bound visuals. Manual polish takes 15-30 minutes vs 2-3 hours from scratch.

## One Line of Python Per Visual

```python
make_card("sc1_rev", 20, 10, 295, 110, "_Measures", "Total Revenue")
```

This generates 15+ lines of PBIR JSON that Power BI reads as a fully data-bound KPI card. With 34 visuals across 7 pages, writing raw JSON would be tedious and error-prone.

## 18 Supported Visual Types

| Function | Visual Type | Required Fields |
|----------|------------|----------------|
| `make_card` | KPI card | 1 measure |
| `make_gauge` | Gauge | 1 value measure (+ optional target/min/max) |
| `make_clustered_bar` | Horizontal bar chart | 1 category + 1 measure |
| `make_clustered_column` | Vertical bar chart | 1 category + 1 measure |
| `make_line_chart` | Line chart (supports dual Y) | 1 category + 1-2 measures |
| `make_area_chart` | Area chart | 1 category + 1 measure |
| `make_donut` | Donut chart | 1 category + 1 measure |
| `make_pie` | Pie chart | 1 category + 1 measure |
| `make_waterfall` | Waterfall chart | 1 category + 1 measure |
| `make_funnel` | Funnel chart | 1 category + 1 measure |
| `make_scatter` | Scatter / bubble plot | 1 detail + 2 measures (+ optional size) |
| `make_ribbon` | Ribbon chart | 1 category + 1 series + 1 measure |
| `make_stacked_column` | Stacked column chart | 1 category + 1 series + 1 measure |
| `make_stacked_bar` | Stacked bar chart | 1 category + 1 series + 1 measure |
| `make_hundred_pct_stacked_bar` | 100% stacked bar | 1 category + 1 series + 1 measure |
| `make_hundred_pct_stacked_column` | 100% stacked column | 1 category + 1 series + 1 measure |
| `make_table` | Flat table | Any mix of columns + measures |
| `make_matrix` | Pivot table | Row fields + value measures |
| `make_treemap` | Treemap | 1 category + 1 measure (+ optional group) |
| `make_filled_map` | Choropleth map | 1 location column + 1 measure |
| `make_map` | Bubble map | 1 category + lat/lng + 1 size measure |
| `make_slicer` | Filter slicer | 1 column |

## 4 Example Dashboards

The repo includes 4 complete dashboard projects across different business domains, each with sample CSV data, a prompt file specifying the full data model, and a `generate_pages.py` script:

| Dashboard | Tables | DAX Measures | Key Patterns |
|-----------|--------|-------------|--------------|
| **E-Commerce** | 5 (Sales, Returns, Product, Customer, Store) | 27 | SUMX+RELATED, USERELATIONSHIP, rolling L3M/L12M |
| **Hospital** | 5 (Admissions, WaitTimes, Department, Doctor, Patient) | 32 | DATEDIFF, EARLIER self-join for readmissions, TOTALMTD |
| **HR** | 5 (EmployeeSnapshot, Recruitment, Employee, Department, JobLevel) | 34 | LASTDATE snapshot, POWER annualized attrition, VAR+RETURN |
| **Supply Chain** | 6 (Orders, Inventory, Shipments, Product, Supplier, Warehouse) | 42 | Multi-fact model, 8x USERELATIONSHIP, semi-additive LASTDATE |
| **Finance** | 5 (Actuals, Budget, CostCenter, Account, Department) | 21 | Multi-fact (Actuals+Budget), USERELATIONSHIP x4, DIVIDE with ALL |

Each prompt file is a self-contained DAX tutorial — all measures are spelled out with full expressions.

## How to Reproduce

### Prerequisites
- Power BI Desktop (with PBIR preview features enabled)
- Python 3.x

Enable in Power BI Desktop (File > Options > Preview features): Store reports using enhanced metadata format (PBIR), Power BI Project (.pbip) save option, Store semantic model in TMDL format.

### Steps

**Option A: Manual** — Open Power BI Desktop, load CSVs, follow the prompt file to create relationships and DAX measures, save as `.pbip`, close Power BI, run `python scripts/generate_pages.py`, reopen.

**Option B: MCP-assisted** — Paste each phase from the prompt file into your MCP client (Claude Desktop, Claude Code, or any other). Save as `.pbip`, run the script, reopen.

**Option C: Brief-driven** — Drop CSVs into Claude Code with the skill file loaded, give a one-paragraph brief, let Claude write both the prompt file and the generate_pages.py.

## Repo Structure

```
powerbi-code-first-dashboards/
  ecommerce/                       # E-Commerce dashboard project
  hospital/                        # Hospital Operations dashboard project
  hr/                              # HR People Analytics dashboard project
  supply_chain/                    # Supply Chain & Inventory dashboard project
  finance/                         # Finance Budget vs Actuals dashboard project
    data/                          #   CSV files (sample data included)
    scripts/generate_pages.py      #   PBIR visual generator (pure Python)
    Finance_Dashboard_Prompts.md   #   Full data model specification
  skills/
    PBIR_Dashboard_Generator_Skill.md  # Claude skill for auto-generating dashboards
  workflow/
    PowerBI_From_Code_Workflow.md   # Detailed methodology guide
  images/                          # Dashboard screenshots
  CLAUDE.md                        # Claude Code project instructions
```

Each dashboard folder follows the same structure: `data/`, `scripts/generate_pages.py`, and `*_Dashboard_Prompts.md`.

## Related Projects

- **[powerbpy](https://github.com/Russell-Shean/powerbpy)** — Python package for creating Power BI dashboards programmatically via an OOP API. Pip-installable.
- **[Lukas Reese's PBIR Report Builder](https://lukasreese.com/2026/03/14/pbir-code-first-power-bi/)** — Claude skill that generates PBIR JSON from natural language. AI-native approach.
- **[pbir_tools](https://github.com/david-iwdb/pbir_tools)** — Python library for PBIR format file manipulation.
- **[power-bi-visual-templates](https://github.com/data-goblin/power-bi-visual-templates)** — Tabular Editor C# scripts for PBIR visual templates.

## Tech Stack

| Component | Role | Required? |
|-----------|------|-----------|
| Power BI Desktop | Runtime engine | Yes |
| PBIR (JSON) | Visual layout definition | Yes |
| Python | Visual page generation scripts | Yes |
| Power BI Modeling MCP | Automated data model creation | Optional |
| Claude skill | Auto-generate dashboards from data models | Optional |
