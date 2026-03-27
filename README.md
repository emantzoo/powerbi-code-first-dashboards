# Power BI Dashboards from Code — Zero Manual UI Work

Build complete, multi-page Power BI dashboards entirely from code. No dragging fields, no clicking through menus — just prompts and scripts.

This repo contains **4 production-ready dashboard projects** built using a code-first workflow that combines:

- **MCP Server** (Power BI Modeling MCP) for data loading, relationships, and DAX measures
- **PBIR format** (Power BI Enhanced Report) for generating visual layouts as JSON files
- **Claude Code / Claude Desktop** as the orchestration layer

## The Workflow

```
CSV files ──> MCP Server ──> Data Model ──> Save .pbip ──> Python Script ──> Visual Pages
              (Phase 0-1)    (relationships,   (PBIR)      (generate_pages.py)
                              Calendar, DAX)
```

### Phase 0: Load Data (MCP)
Open a blank Power BI Desktop. Claude connects via MCP and loads all CSVs — no manual Get Data clicks.

### Phase 1: Build Data Model (MCP)
Claude creates relationships, a Calendar table (DAX calculated table), and all measures in batches:
- Core KPIs (SUM, AVERAGE, DIVIDE, DISTINCTCOUNT)
- Time intelligence (TOTALMTD, TOTALYTD, SAMEPERIODLASTYEAR, DATESINPERIOD)
- Measures using USERELATIONSHIP for inactive relationships
- Conditional formatting measures (SWITCH for RAG status with hex colors)

### Phase 2: Generate Visuals (Python/PBIR)
After saving as `.pbip`, a Python script generates all pages and visuals as JSON files directly into the PBIR folder structure. Each `visual.json` defines one chart/card/table with its type, position, size, and data bindings.

### Phase 3: Open and Polish
Open the `.pbip` file — all pages appear with data-bound visuals. Manual polish (themes, formatting, slicer sync) takes 15-30 minutes vs 2-3 hours of building from scratch.

## The 4 Dashboards

### 1. E-Commerce Sales & Customer Analytics
| Metric | Value |
|--------|-------|
| Tables | 5 (FactSales, FactReturns, DimProduct, DimCustomer, DimStore) |
| Relationships | 6 (4 active + 2 date) |
| DAX Measures | 27 |
| Pages | 4 (Executive Overview, Product Performance, Customer & Trends, Returns Analysis) |
| Key DAX | SUMX with RELATED, USERELATIONSHIP, SAMEPERIODLASTYEAR, DATESINPERIOD |

### 2. Hospital Operations
| Metric | Value |
|--------|-------|
| Tables | 5 (FactAdmissions, FactWaitTimes, DimDepartment, DimDoctor, DimPatient) |
| Relationships | 7 (5 active + 2 date) |
| DAX Measures | 32 |
| Pages | 4 (Hospital Overview, Department Deep-Dive, Wait Time Analysis, Patient Demographics) |
| Key DAX | DATEDIFF, EARLIER (readmission self-join), USERELATIONSHIP, TOTALMTD |

### 3. HR People Analytics
| Metric | Value |
|--------|-------|
| Tables | 5 (FactEmployeeSnapshot, FactRecruitment, DimEmployee, DimDepartment, DimJobLevel) |
| Relationships | 8 (4 active + 4 inactive) |
| DAX Measures | 34 |
| Pages | 4 (Workforce Overview, Attrition Analysis, Compensation & Equity, Recruitment Funnel) |
| Key DAX | LASTDATE snapshot pattern, POWER (annualized rate), RELATED in FILTER, multiple inactive relationships |

### 4. Supply Chain & Inventory
| Metric | Value |
|--------|-------|
| Tables | 6 (FactOrders, FactInventorySnapshot, FactShipmentRoutes, DimProduct, DimSupplier, DimWarehouse) |
| Relationships | 11 (4 active + 7 inactive) |
| DAX Measures | 42 |
| Pages | 5 (Supply Chain KPIs, Supplier Scorecard, Inventory Health, Global Logistics Map, Warehouse Comparison) |
| Key DAX | Multi-fact model, semi-additive LASTDATE, 8x USERELATIONSHIP, DATESINPERIOD rolling window, map visuals |

## DAX Skills Demonstrated

| Skill | Where Used |
|-------|-----------|
| LASTDATE (snapshot pattern) | HR headcount, Supply Chain inventory |
| USERELATIONSHIP | All projects — inactive relationships for multi-fact models |
| DATEDIFF | Hospital LOS & wait times, HR tenure, Supply Chain lead times |
| EARLIER (self-join) | Hospital 30-day readmission detection |
| SAMEPERIODLASTYEAR | All projects — YoY comparisons |
| TOTALYTD / TOTALMTD | All projects — period-to-date accumulations |
| DATESINPERIOD | E-Commerce L3M/L12M, Supply Chain rolling 3-month |
| SUMX with RELATED | E-Commerce Total Cost (cross-table calculation) |
| POWER function | HR annualized attrition rate |
| SWITCH (RAG colors) | All projects — conditional formatting with hex codes |
| VAR + RETURN | HR Gender Pay Gap |
| DIVIDE (safe division) | All ratio/rate measures across all projects |

## Star Schema Patterns

**Single-Fact (E-Commerce, Hospital, HR):**
```
DimTable1 ──> FactTable <── DimTable2
                  |
              Calendar
```

**Multi-Fact (Supply Chain):**
```
DimSupplier ──> FactOrders <── DimProduct
                    |              |
               DimWarehouse   (INACTIVE)
                    |              |
               (INACTIVE)   FactInventorySnapshot
                    |
            FactShipmentRoutes (pre-aggregated)
```

## How to Reproduce

### Prerequisites
- Power BI Desktop (March 2026+ or with PBIR preview features enabled)
- VS Code with Power BI Modeling MCP extension
- Claude Desktop or Claude Code with MCP configured
- Python 3.x

### Steps
1. Pick a dashboard folder (e.g., `ecommerce/`)
2. Open a blank Power BI Desktop
3. Follow the prompts in the `*_Dashboard_Prompts.md` file — paste each phase into Claude
4. Save as `.pbip` when prompted
5. Close Power BI Desktop
6. Run `python scripts/generate_pages.py` targeting your `.pbip` folder
7. Reopen the `.pbip` — full dashboard ready

### Alternative: powerbpy
The `build_all_powerbpy.py` script uses the [powerbpy](https://pypi.org/project/powerbpy/) library to generate the PBIR structure in one step. It creates the `.pbip` projects with CSVs loaded and visuals placed. Then use the MCP prompts (Phase 1 only) to add relationships and DAX measures.

## Repo Structure

```
powerbi-code-first-dashboards/
  ecommerce/
    data/                          # 5 CSV files
    scripts/generate_pages.py      # PBIR visual generator
    ECommerce_Dashboard_Prompts.md # Step-by-step MCP prompts
  hospital/
    data/                          # 5 CSV files
    scripts/generate_pages.py
    Hospital_Dashboard_Prompts.md
  hr/
    data/                          # 5 CSV files
    scripts/generate_pages.py
    HR_Dashboard_Prompts.md
  supply_chain/
    data/                          # 6 CSV files
    scripts/generate_pages.py
    SupplyChain_Dashboard_Prompts.md
  workflow/
    PowerBI_From_Code_Workflow.md   # Detailed methodology guide
```

## Why Code-First?

- **Reproducible** — the entire pipeline is text-based and version-controllable
- **Fast** — 4 complete dashboards in under an hour vs days of manual work
- **Consistent** — same layout patterns, naming conventions, and measure structures
- **Learnable** — each prompt file is a self-contained DAX tutorial
- **Portable** — `.pbip` folders are just text files (JSON + TMDL)

## Tech Stack

| Component | Role |
|-----------|------|
| Power BI Desktop | Runtime engine |
| Power BI Modeling MCP | Data loading, relationships, DAX measures |
| PBIR (JSON) | Visual layout definition |
| Python | Visual page generation scripts |
| Claude Code | Orchestration and automation |

---

Built with [Claude Code](https://claude.ai/claude-code) and the [Power BI Modeling MCP](https://marketplace.visualstudio.com/items?itemName=analysis-services.powerbi-modeling-mcp) extension.
