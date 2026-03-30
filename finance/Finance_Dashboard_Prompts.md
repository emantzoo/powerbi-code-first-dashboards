# Finance Budget vs Actuals — Power BI Build Prompts

Use these prompts in order. Each one is a copy-paste block for Claude Desktop (Cowork or Code tab).

Replace `C:\YOUR_DATA_PATH` with the actual folder where you saved the 5 CSVs.
Replace `C:\YOUR_SAVE_PATH` with where you want the .pbip project saved.

---

## PHASE 0 — Load Data

> Open a blank Power BI Desktop first. Then paste this into Claude Desktop:

```
Connect to my open Power BI Desktop file.

Load all CSV files from C:\YOUR_DATA_PATH into my Power BI model.
The folder contains these 5 files:
- FactActuals.csv (5751 rows — actual spend transactions)
- FactBudget.csv (3792 rows — monthly budget allocations)
- DimCostCenter.csv (20 rows — cost center details)
- DimAccount.csv (15 rows — GL account definitions)
- DimDepartment.csv (8 rows — department info)

Read the headers from each CSV and create tables with the correct column names and data types.
For date columns (transaction_date, budget_month), use Date type.
For ID columns (actual_id, budget_id, cost_center_id, account_id, department_id), use Text type.
For numeric columns (amount, budget_amount, headcount), use Decimal Number type.
For text columns (vendor, cost_center_name, account_name, etc.), use Text type.

Refresh the model after loading. Confirm row counts for each table.
```

---

## PHASE 1A — Relationships

> Paste this after Phase 0 completes:

```
Delete all auto-detected relationships in the model first.

Then create these relationships:

1. FactActuals[cost_center_id] -> DimCostCenter[cost_center_id] (Many:1, ACTIVE, single direction cross-filter)
2. FactActuals[account_id] -> DimAccount[account_id] (Many:1, ACTIVE, single direction cross-filter)
3. FactActuals[department_id] -> DimDepartment[department_id] (Many:1, ACTIVE, single direction cross-filter)
4. FactBudget[cost_center_id] -> DimCostCenter[cost_center_id] (Many:1, INACTIVE, single direction cross-filter)
5. FactBudget[account_id] -> DimAccount[account_id] (Many:1, INACTIVE, single direction cross-filter)
6. FactBudget[department_id] -> DimDepartment[department_id] (Many:1, INACTIVE, single direction cross-filter)

Do NOT create date relationships yet — we'll do that after the Calendar table.
```

---

## PHASE 1B — Calendar Table

> Paste this next:

```
Create a DAX calculated table called Calendar:

Calendar = ADDCOLUMNS(
    CALENDAR(DATE(2023,1,1), DATE(2025,6,30)),
    "Year", YEAR([Date]),
    "Quarter", "Q" & CEILING(MONTH([Date])/3, 1),
    "Month_Num", MONTH([Date]),
    "Month_Name", FORMAT([Date], "MMMM"),
    "Year_Quarter", FORMAT([Date], "YYYY") & "-Q" & CEILING(MONTH([Date])/3, 1),
    "Year_Month", FORMAT([Date], "YYYY-MM"),
    "Day_of_Week", FORMAT([Date], "dddd"),
    "Is_Weekend", IF(WEEKDAY([Date], 2) >= 6, "Weekend", "Weekday")
)

Mark it as a Date Table using the Date column.

Then create these date relationships:
7. FactActuals[transaction_date] -> Calendar[Date] (Many:1, ACTIVE, single direction cross-filter)
8. FactBudget[budget_month] -> Calendar[Date] (Many:1, INACTIVE, single direction cross-filter)
```

---

## PHASE 1C — DAX Measures (Batch 1: Core KPIs)

```
Create a _Measures table (or add to it if it exists) with these DAX measures:

Total Actuals = SUM(FactActuals[amount])

Total Budget = CALCULATE(
    SUM(FactBudget[budget_amount]),
    USERELATIONSHIP(FactBudget[budget_month], Calendar[Date]),
    USERELATIONSHIP(FactBudget[cost_center_id], DimCostCenter[cost_center_id]),
    USERELATIONSHIP(FactBudget[account_id], DimAccount[account_id]),
    USERELATIONSHIP(FactBudget[department_id], DimDepartment[department_id])
)

Budget Variance = [Total Actuals] - [Total Budget]

Budget Variance Pct = DIVIDE([Budget Variance], [Total Budget], 0)

Budget Utilization = DIVIDE([Total Actuals], [Total Budget], 0)

Total Transactions = COUNTROWS(FactActuals)

Avg Transaction Amount = DIVIDE([Total Actuals], [Total Transactions], 0)

Unique Vendors = DISTINCTCOUNT(FactActuals[vendor])

Unique Cost Centers = DISTINCTCOUNT(FactActuals[cost_center_id])
```

---

## PHASE 1D — DAX Measures (Batch 2: Time Intelligence)

```
Add these measures to _Measures:

Actuals MTD = TOTALMTD([Total Actuals], Calendar[Date])

Actuals YTD = TOTALYTD([Total Actuals], Calendar[Date])

Actuals PY = CALCULATE([Total Actuals], SAMEPERIODLASTYEAR(Calendar[Date]))

Actuals YoY Growth = DIVIDE([Total Actuals] - [Actuals PY], [Actuals PY], 0)

Budget PY = CALCULATE([Total Budget], SAMEPERIODLASTYEAR(Calendar[Date]))

Budget YoY Growth = DIVIDE([Total Budget] - [Budget PY], [Budget PY], 0)
```

---

## PHASE 1E — DAX Measures (Batch 3: Department & Account Analysis)

```
Add these measures to _Measures:

Pct of Total Spend = DIVIDE(
    [Total Actuals],
    CALCULATE([Total Actuals], ALL(DimDepartment)),
    0
)

Pct of Total Budget = DIVIDE(
    [Total Budget],
    CALCULATE([Total Budget], ALL(DimDepartment)),
    0
)

Avg Monthly Spend = DIVIDE([Total Actuals], DISTINCTCOUNT(Calendar[Year_Month]), 0)
```

---

## PHASE 1F — DAX Measures (Batch 4: Conditional Formatting)

```
Add these measures to _Measures:

Variance RAG Color = SWITCH(
    TRUE(),
    [Budget Variance Pct] <= 0, "#27AE60",
    [Budget Variance Pct] <= 0.10, "#F39C12",
    "#E74C3C"
)

Utilization RAG Color = SWITCH(
    TRUE(),
    [Budget Utilization] <= 0.90, "#27AE60",
    [Budget Utilization] <= 1.05, "#F39C12",
    "#E74C3C"
)

YoY RAG Color = SWITCH(
    TRUE(),
    [Actuals YoY Growth] <= 0, "#27AE60",
    [Actuals YoY Growth] <= 0.10, "#F39C12",
    "#E74C3C"
)
```

---

## PHASE 1G — Save

> Do this manually:

1. In Power BI Desktop: **File > Save As > Power BI Project (.pbip)**
2. Save to `C:\YOUR_SAVE_PATH\FinanceDashboard`
3. **Close Power BI Desktop completely**

This creates the PBIR folder structure needed for Phase 2.

---

## PHASE 2 — Generate Visuals (PBIR)

> Run the Python script — no AI needed:

1. Edit `scripts/generate_pages.py` — update the `BASE` path on line 3 to match your `.pbip` save location
2. Close Power BI Desktop
3. Run:

```bash
python scripts/generate_pages.py
```

The script generates 4 pages with visuals as PBIR `visual.json` files.

### Visual Layout Reference

This is the layout specification used to generate `scripts/generate_pages.py`. Canvas is 1280x720.

**Page 1 — Financial Overview**

Row 1 (y=10, h=110):
- Card (x=20, w=235): Total Actuals
- Card (x=270, w=235): Total Budget
- Card (x=520, w=235): Budget Variance
- Card (x=770, w=235): Budget Utilization
- Slicer (x=1020, w=230): Calendar[Year]

Row 2 (y=140, h=280):
- Line chart (x=20, w=610): Calendar[Year_Month] vs Total Actuals + Total Budget
- Waterfall chart (x=650, w=600): DimDepartment[department_name] vs Budget Variance

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimDepartment[department_name], Total Actuals, Total Budget, Budget Variance, Budget Variance Pct, Budget Utilization

**Page 2 — Variance Analysis**

Row 1 (y=10, h=110):
- Card (x=20, w=235): Budget Variance
- Card (x=270, w=235): Budget Variance Pct
- Card (x=520, w=235): Actuals YoY Growth
- Card (x=770, w=235): Avg Monthly Spend
- Slicer (x=1020, w=230): DimDepartment[department_name]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=610): DimCostCenter[cost_center_name] vs Budget Variance
- Clustered bar chart (x=650, w=600): DimAccount[account_name] vs Budget Variance

Row 3 (y=440, h=260):
- Matrix (x=20, w=1230): Rows: DimAccount[account_name], Columns: Calendar[Year], Values: Total Actuals, Total Budget, Budget Variance

**Page 3 — Department Spend**

Row 1 (y=10, h=110):
- Card (x=20, w=235): Total Actuals
- Card (x=270, w=235): Total Transactions
- Card (x=520, w=235): Unique Vendors
- Card (x=770, w=235): Pct of Total Spend
- Slicer (x=1020, w=230): DimDepartment[department_name]

Row 2 (y=140, h=280):
- Donut chart (x=20, w=400): DimDepartment[department_name] vs Total Actuals
- Clustered bar chart (x=440, w=400): DimAccount[account_name] vs Total Actuals
- Gauge (x=860, w=380): Budget Utilization

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimCostCenter[cost_center_name], DimCostCenter[region], Total Actuals, Total Budget, Budget Variance, Budget Variance Pct

**Page 4 — Account Detail**

Row 1 (y=10, h=110):
- Card (x=20, w=295): Total Actuals
- Card (x=330, w=295): Actuals YTD
- Card (x=640, w=295): Actuals PY
- Card (x=950, w=295): Actuals YoY Growth

Row 2 (y=140, h=280):
- Line chart (x=20, w=610): Calendar[Year_Month] vs Total Actuals + Actuals PY
- Pie chart (x=650, w=290): DimAccount[account_type] vs Total Actuals
- Clustered bar chart (x=960, w=290): DimAccount[account_group] vs Total Actuals

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimAccount[account_name], DimAccount[account_type], Total Actuals, Total Budget, Budget Variance, Budget Variance Pct, Avg Transaction Amount

---

## PHASE 3 — Open and Polish

1. Open `FinanceDashboard.pbip` in Power BI Desktop
2. All 4 pages should appear with data-bound visuals
3. Manual polish (~15-30 min):
   - Apply a color theme (View > Themes)
   - Add visual titles and format labels
   - Set conditional formatting on KPI cards using the RAG Color measures
   - Sync the Year slicer across pages (View > Sync Slicers)
   - Adjust any overlapping visuals

---

## Schema Reference

### Star Schema Diagram

```
                    Calendar
                      |
                      | Date (ACTIVE from Actuals, INACTIVE from Budget)
                      |
DimAccount -----> FactActuals <----- DimDepartment
  account_id    /    |                department_id
               /     |
DimCostCenter /  cost_center_id
              \
               \
DimAccount -----> FactBudget <----- DimDepartment
  (INACTIVE)      |                 (INACTIVE)
               DimCostCenter
                (INACTIVE)
```

### All Relationships

| From | To | Cardinality | Active | Cross-Filter |
|------|----|-------------|--------|--------------|
| FactActuals[cost_center_id] | DimCostCenter[cost_center_id] | Many:1 | Yes | Single |
| FactActuals[account_id] | DimAccount[account_id] | Many:1 | Yes | Single |
| FactActuals[department_id] | DimDepartment[department_id] | Many:1 | Yes | Single |
| FactActuals[transaction_date] | Calendar[Date] | Many:1 | Yes | Single |
| FactBudget[cost_center_id] | DimCostCenter[cost_center_id] | Many:1 | No | Single |
| FactBudget[account_id] | DimAccount[account_id] | Many:1 | No | Single |
| FactBudget[department_id] | DimDepartment[department_id] | Many:1 | No | Single |
| FactBudget[budget_month] | Calendar[Date] | Many:1 | No | Single |

### All Measures

| Measure | DAX | Category |
|---------|-----|----------|
| Total Actuals | SUM(FactActuals[amount]) | Core KPI |
| Total Budget | CALCULATE(SUM(...), USERELATIONSHIP x4) | Core KPI |
| Budget Variance | [Total Actuals] - [Total Budget] | Core KPI |
| Budget Variance Pct | DIVIDE([Variance], [Budget], 0) | Core KPI |
| Budget Utilization | DIVIDE([Actuals], [Budget], 0) | Core KPI |
| Total Transactions | COUNTROWS(FactActuals) | Core KPI |
| Avg Transaction Amount | DIVIDE([Actuals], [Transactions], 0) | Core KPI |
| Unique Vendors | DISTINCTCOUNT(FactActuals[vendor]) | Core KPI |
| Unique Cost Centers | DISTINCTCOUNT(FactActuals[cost_center_id]) | Core KPI |
| Actuals MTD | TOTALMTD([Total Actuals], Calendar[Date]) | Time Intel |
| Actuals YTD | TOTALYTD([Total Actuals], Calendar[Date]) | Time Intel |
| Actuals PY | CALCULATE([Total Actuals], SAMEPERIODLASTYEAR(...)) | Time Intel |
| Actuals YoY Growth | DIVIDE([Actuals] - [PY], [PY], 0) | Time Intel |
| Budget PY | CALCULATE([Total Budget], SAMEPERIODLASTYEAR(...)) | Time Intel |
| Budget YoY Growth | DIVIDE([Budget] - [PY], [PY], 0) | Time Intel |
| Pct of Total Spend | DIVIDE([Actuals], CALCULATE([Actuals], ALL(DimDepartment))) | Analysis |
| Pct of Total Budget | DIVIDE([Budget], CALCULATE([Budget], ALL(DimDepartment))) | Analysis |
| Avg Monthly Spend | DIVIDE([Actuals], DISTINCTCOUNT(Year_Month)) | Analysis |
| Variance RAG Color | SWITCH(TRUE(), <=0 green, <=0.10 amber, red) | Formatting |
| Utilization RAG Color | SWITCH(TRUE(), <=0.90 green, <=1.05 amber, red) | Formatting |
| YoY RAG Color | SWITCH(TRUE(), <=0 green, <=0.10 amber, red) | Formatting |
