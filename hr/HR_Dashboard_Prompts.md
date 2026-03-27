# HR People Analytics Dashboard — Power BI Build Prompts

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
- FactEmployeeSnapshot.csv (3411 rows — monthly headcount snapshots with salary, performance, engagement)
- FactRecruitment.csv (150 rows — hiring requisitions with pipeline metrics)
- DimEmployee.csv (200 rows — employee master data with hire/termination dates)
- DimDepartment.csv (8 rows — departments with cost centers)
- DimJobLevel.csv (5 rows — job levels with salary bands)

Read the headers from each CSV and create tables with the correct column names and data types.
For date columns (snapshot_date, hire_date, birth_date, termination_date, open_date, close_date), use Date type. Treat empty strings as blank/null.
For ID columns (employee_id, department_id, job_level_id, job_level, requisition_id, manager_id, cost_center), use Text type.
For numeric columns (salary, salary_band_min, salary_band_max, performance_rating, engagement_score, is_active, applications_received, offers_made, hires), use Decimal Number or Whole Number as appropriate.
For text columns (employee_name, gender, education_level, city, exit_reason, department_name, level_name), use Text type.

Refresh the model after loading. Confirm row counts for each table.
```

---

## PHASE 1A — Relationships

```
Delete all auto-detected relationships in the model first.

Then create these relationships:

1. FactEmployeeSnapshot[employee_id] -> DimEmployee[employee_id] (Many:1, ACTIVE, single direction)
2. FactEmployeeSnapshot[department_id] -> DimDepartment[department_id] (Many:1, ACTIVE, single direction)
3. FactEmployeeSnapshot[job_level] -> DimJobLevel[job_level_id] (Many:1, ACTIVE, single direction)
4. FactRecruitment[department_id] -> DimDepartment[department_id] (Many:1, INACTIVE, single direction)
5. FactRecruitment[job_level] -> DimJobLevel[job_level_id] (Many:1, INACTIVE, single direction)
6. DimEmployee[department_id] -> DimDepartment[department_id] (Many:1, INACTIVE, single direction)

Do NOT create date relationships yet — we'll do that after the Calendar table.
```

---

## PHASE 1B — Calendar Table

```
Create a DAX calculated table called Calendar:

Calendar = ADDCOLUMNS(
    CALENDAR(DATE(2022,1,1), DATE(2025,6,30)),
    "Year", YEAR([Date]),
    "Quarter", "Q" & CEILING(MONTH([Date])/3, 1),
    "Month_Num", MONTH([Date]),
    "Month_Name", FORMAT([Date], "MMMM"),
    "Year_Quarter", FORMAT([Date], "YYYY") & "-Q" & CEILING(MONTH([Date])/3, 1),
    "Year_Month", FORMAT([Date], "YYYY-MM"),
    "Is_Month_Start", IF(DAY([Date]) = 1, "Yes", "No")
)

Mark it as a Date Table using the Date column.

Then create these date relationships:
7. FactEmployeeSnapshot[snapshot_date] -> Calendar[Date] (Many:1, ACTIVE, single direction)
8. FactRecruitment[open_date] -> Calendar[Date] (Many:1, INACTIVE, single direction)
```

---

## PHASE 1C — DAX Measures (Batch 1: Headcount Core)

```
Create a _Measures table (or add to it if it exists) with these DAX measures:

Current Headcount = CALCULATE(
    COUNTROWS(FactEmployeeSnapshot),
    LASTDATE(Calendar[Date])
)

Total Employees All Time = DISTINCTCOUNT(DimEmployee[employee_id])

Active Employees = COUNTROWS(
    FILTER(DimEmployee, ISBLANK(DimEmployee[termination_date]))
)

Avg Salary = AVERAGE(FactEmployeeSnapshot[salary])

Median Salary = MEDIAN(FactEmployeeSnapshot[salary])

Total Payroll = SUM(FactEmployeeSnapshot[salary])

Avg Performance = AVERAGE(FactEmployeeSnapshot[performance_rating])

Avg Engagement = AVERAGE(FactEmployeeSnapshot[engagement_score])

High Performers = CALCULATE(
    COUNTROWS(FactEmployeeSnapshot),
    FactEmployeeSnapshot[performance_rating] >= 4
)

High Performer Pct = DIVIDE([High Performers], COUNTROWS(FactEmployeeSnapshot), 0)
```

---

## PHASE 1D — DAX Measures (Batch 2: Attrition)

```
Add these measures to _Measures:

Terminations = COUNTROWS(
    FILTER(
        DimEmployee,
        NOT(ISBLANK(DimEmployee[termination_date]))
        && DimEmployee[termination_date] >= MIN(Calendar[Date])
        && DimEmployee[termination_date] <= MAX(Calendar[Date])
    )
)

Monthly Attrition Rate = DIVIDE(
    [Terminations],
    [Current Headcount] + [Terminations],
    0
)

Annualized Attrition Rate = 1 - POWER(1 - [Monthly Attrition Rate], 12)

Voluntary Exits = CALCULATE(
    COUNTROWS(
        FILTER(DimEmployee, NOT(ISBLANK(DimEmployee[termination_date])))
    ),
    FILTER(
        DimEmployee,
        DimEmployee[exit_reason] <> "Laid Off"
        && DimEmployee[termination_date] >= MIN(Calendar[Date])
        && DimEmployee[termination_date] <= MAX(Calendar[Date])
    )
)

Voluntary Attrition Rate = DIVIDE([Voluntary Exits], [Current Headcount] + [Terminations], 0)

Avg Tenure Years = AVERAGEX(
    FILTER(DimEmployee, ISBLANK(DimEmployee[termination_date])),
    DATEDIFF(DimEmployee[hire_date], TODAY(), DAY) / 365.25
)
```

---

## PHASE 1E — DAX Measures (Batch 3: Compensation Analytics)

```
Add these measures to _Measures:

Salary Band Midpoint = AVERAGE(DimJobLevel[salary_band_min]) + (AVERAGE(DimJobLevel[salary_band_max]) - AVERAGE(DimJobLevel[salary_band_min])) / 2

Compa Ratio = DIVIDE([Avg Salary], [Salary Band Midpoint], 0)

Below Band Pct = DIVIDE(
    CALCULATE(
        COUNTROWS(FactEmployeeSnapshot),
        FILTER(
            FactEmployeeSnapshot,
            FactEmployeeSnapshot[salary] < RELATED(DimJobLevel[salary_band_min])
        )
    ),
    COUNTROWS(FactEmployeeSnapshot),
    0
)

Above Band Pct = DIVIDE(
    CALCULATE(
        COUNTROWS(FactEmployeeSnapshot),
        FILTER(
            FactEmployeeSnapshot,
            FactEmployeeSnapshot[salary] > RELATED(DimJobLevel[salary_band_max])
        )
    ),
    COUNTROWS(FactEmployeeSnapshot),
    0
)

Gender Pay Gap = 
VAR MaleSalary = CALCULATE([Avg Salary], DimEmployee[gender] = "Male")
VAR FemaleSalary = CALCULATE([Avg Salary], DimEmployee[gender] = "Female")
RETURN DIVIDE(MaleSalary - FemaleSalary, MaleSalary, 0)
```

---

## PHASE 1F — DAX Measures (Batch 4: Recruitment)

```
Add these measures to _Measures:

Total Requisitions = CALCULATE(
    COUNTROWS(FactRecruitment),
    USERELATIONSHIP(FactRecruitment[department_id], DimDepartment[department_id])
)

Open Requisitions = CALCULATE(
    COUNTROWS(FILTER(FactRecruitment, ISBLANK(FactRecruitment[close_date]))),
    USERELATIONSHIP(FactRecruitment[department_id], DimDepartment[department_id])
)

Total Hires = CALCULATE(
    SUM(FactRecruitment[hires]),
    USERELATIONSHIP(FactRecruitment[department_id], DimDepartment[department_id])
)

Total Applications = CALCULATE(
    SUM(FactRecruitment[applications_received]),
    USERELATIONSHIP(FactRecruitment[department_id], DimDepartment[department_id])
)

Avg Time to Fill = CALCULATE(
    AVERAGEX(
        FILTER(FactRecruitment, NOT(ISBLANK(FactRecruitment[close_date]))),
        DATEDIFF(FactRecruitment[open_date], FactRecruitment[close_date], DAY)
    ),
    USERELATIONSHIP(FactRecruitment[department_id], DimDepartment[department_id])
)

Offer Acceptance Rate = DIVIDE(
    CALCULATE(SUM(FactRecruitment[hires]), USERELATIONSHIP(FactRecruitment[department_id], DimDepartment[department_id])),
    CALCULATE(SUM(FactRecruitment[offers_made]), USERELATIONSHIP(FactRecruitment[department_id], DimDepartment[department_id])),
    0
)

Applications per Hire = DIVIDE([Total Applications], [Total Hires], 0)
```

---

## PHASE 1G — DAX Measures (Batch 5: Time Intelligence & Headcount Trend)

```
Add these measures to _Measures:

Headcount PY = CALCULATE([Current Headcount], SAMEPERIODLASTYEAR(Calendar[Date]))

Headcount YoY Growth = DIVIDE([Current Headcount] - [Headcount PY], [Headcount PY], 0)

Payroll YTD = TOTALYTD([Total Payroll], Calendar[Date])

Tenure Bucket = SWITCH(
    TRUE(),
    [Avg Tenure Years] < 1, "< 1 Year",
    [Avg Tenure Years] < 3, "1-3 Years",
    [Avg Tenure Years] < 5, "3-5 Years",
    [Avg Tenure Years] < 10, "5-10 Years",
    "10+ Years"
)
```

---

## PHASE 1H — DAX Measures (Batch 6: Conditional Formatting)

```
Add these measures to _Measures:

Attrition RAG Color = SWITCH(
    TRUE(),
    [Annualized Attrition Rate] >= 0.20, "#E74C3C",
    [Annualized Attrition Rate] >= 0.12, "#F39C12",
    "#27AE60"
)

Engagement RAG Color = SWITCH(
    TRUE(),
    [Avg Engagement] >= 7, "#27AE60",
    [Avg Engagement] >= 5, "#F39C12",
    "#E74C3C"
)

Compa Ratio RAG Color = SWITCH(
    TRUE(),
    [Compa Ratio] >= 0.95 && [Compa Ratio] <= 1.10, "#27AE60",
    [Compa Ratio] >= 0.85, "#F39C12",
    "#E74C3C"
)

Time to Fill RAG Color = SWITCH(
    TRUE(),
    [Avg Time to Fill] <= 45, "#27AE60",
    [Avg Time to Fill] <= 75, "#F39C12",
    "#E74C3C"
)
```

---

## PHASE 1I — Save

> Do this manually:

1. In Power BI Desktop: **File > Save As > Power BI Project (.pbip)**
2. Save to `C:\YOUR_SAVE_PATH\HRAnalyticsDashboard`
3. **Close Power BI Desktop completely**

---

## PHASE 2 — Generate Visuals (PBIR)

> Paste this into Claude Code:

```
I have a Power BI project saved as .pbip with PBIR format at:
C:\YOUR_SAVE_PATH\HRAnalyticsDashboard

The data model has these tables:
- FactEmployeeSnapshot (snapshot_date, employee_id, department_id, job_level, salary, performance_rating, engagement_score, is_active)
- FactRecruitment (requisition_id, department_id, job_level, open_date, close_date, applications_received, offers_made, hires)
- DimEmployee (employee_id, employee_name, hire_date, birth_date, gender, education_level, city, department_id, job_level, termination_date, exit_reason)
- DimDepartment (department_id, department_name, cost_center, manager_id)
- DimJobLevel (job_level_id, level_name, salary_band_min, salary_band_max)
- Calendar (Date, Year, Quarter, Month_Num, Month_Name, Year_Quarter, Year_Month, Is_Month_Start)
- _Measures (all measures listed below)

Measures in _Measures:
Current Headcount, Total Employees All Time, Active Employees,
Avg Salary, Median Salary, Total Payroll, Avg Performance, Avg Engagement,
High Performers, High Performer Pct,
Terminations, Monthly Attrition Rate, Annualized Attrition Rate,
Voluntary Exits, Voluntary Attrition Rate, Avg Tenure Years,
Salary Band Midpoint, Compa Ratio, Below Band Pct, Above Band Pct, Gender Pay Gap,
Total Requisitions, Open Requisitions, Total Hires, Total Applications,
Avg Time to Fill, Offer Acceptance Rate, Applications per Hire,
Headcount PY, Headcount YoY Growth, Payroll YTD, Tenure Bucket,
Attrition RAG Color, Engagement RAG Color, Compa Ratio RAG Color, Time to Fill RAG Color

Generate PBIR visual.json files for a 4-page dashboard. Use schema version 2.7.0. Canvas is 1280x720.

### Page 1 — Workforce Overview
Layout: headcount KPIs, department breakdown, trend over time.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=235): Current Headcount
- Card 2 (x=270, w=235): Avg Salary
- Card 3 (x=520, w=235): Avg Engagement
- Card 4 (x=770, w=235): Headcount YoY Growth
- Slicer (x=1020, w=230): Calendar[Year]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): DimDepartment[department_name] vs Current Headcount
- Line chart (x=440, w=400): Calendar[Year_Month] vs Current Headcount
- Donut chart (x=860, w=380): DimJobLevel[level_name] vs Current Headcount

Row 3 (y=440, h=260):
- Clustered bar chart (x=20, w=400): DimEmployee[gender] vs Current Headcount
- Donut chart (x=440, w=380): DimEmployee[education_level] vs Current Headcount
- Clustered bar chart (x=840, w=410): DimEmployee[city] vs Current Headcount

### Page 2 — Attrition Analysis
Layout: attrition metrics, exit reasons, department comparison.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=235): Terminations
- Card 2 (x=270, w=235): Annualized Attrition Rate
- Card 3 (x=520, w=235): Voluntary Attrition Rate
- Card 4 (x=770, w=235): Avg Tenure Years
- Slicer (x=1020, w=230): Calendar[Year]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): DimEmployee[exit_reason] vs Terminations
- Line chart (x=440, w=400): Calendar[Year_Month] vs Terminations
- Donut chart (x=860, w=380): DimDepartment[department_name] vs Terminations

Row 3 (y=440, h=260):
- Matrix / Pivot table (x=20, w=1230):
  Rows: DimDepartment[department_name]
  Columns: Calendar[Year]
  Values: Terminations, Annualized Attrition Rate, Avg Tenure Years

### Page 3 — Compensation & Equity
Layout: salary analysis, pay gap, band compliance.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=235): Avg Salary
- Card 2 (x=270, w=235): Compa Ratio
- Card 3 (x=520, w=235): Gender Pay Gap
- Card 4 (x=770, w=235): Below Band Pct
- Slicer (x=1020, w=230): DimDepartment[department_name]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): DimJobLevel[level_name] vs Avg Salary
- Clustered bar chart (x=440, w=400): DimDepartment[department_name] vs Avg Salary
- Clustered bar chart (x=860, w=380): DimEmployee[gender] vs Avg Salary

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimJobLevel[level_name], DimJobLevel[salary_band_min], DimJobLevel[salary_band_max], Avg Salary, Median Salary, Compa Ratio, Below Band Pct, Above Band Pct

### Page 4 — Recruitment Funnel
Layout: hiring pipeline, time to fill, department demand.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=235): Total Requisitions
- Card 2 (x=270, w=235): Open Requisitions
- Card 3 (x=520, w=235): Avg Time to Fill
- Card 4 (x=770, w=235): Offer Acceptance Rate
- Slicer (x=1020, w=230): DimDepartment[department_name]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): DimDepartment[department_name] vs Total Hires
- Line chart (x=440, w=400): Calendar[Year_Month] vs Total Hires
- Donut chart (x=860, w=380): DimJobLevel[level_name] vs Total Requisitions

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimDepartment[department_name], Total Requisitions, Open Requisitions, Total Applications, Total Hires, Avg Time to Fill, Offer Acceptance Rate, Applications per Hire

Write all files directly into HRAnalyticsDashboard.Report/definition/pages/
Update pages.json with the 4 page folders in pageOrder.
```

---

## PHASE 3 — Open and Polish

1. Open `HRAnalyticsDashboard.pbip` in Power BI Desktop
2. All 4 pages should appear with data-bound visuals
3. Manual polish (~15-30 min):
   - Apply a color theme — consider a modern teal/purple palette
   - Set conditional formatting on KPI cards using the RAG Color measures
   - Sync the Year slicer across Pages 1 and 2
   - Sync the Department slicer across Pages 3 and 4
   - Configure Page 2 as a drill-through page (add DimDepartment[department_name])
   - Format salary measures as $#,##0
   - Format percentage measures as 0.0%
   - Format Avg Tenure Years as 0.0
   - Add page navigation buttons

---

## Schema Reference

### Star Schema Diagram

```
                          Calendar
                            |
                      snapshot_date (active)
                      open_date (INACTIVE)
                            |
DimJobLevel -----> FactEmployeeSnapshot <----- DimEmployee
  job_level_id         |                         employee_id
  (also INACTIVE       |
   to FactRecruitment) |
                  department_id
                       |
                  DimDepartment <------- FactRecruitment
                                    department_id (INACTIVE)
```

### All Relationships

| From | To | Cardinality | Active | Cross-Filter |
|------|----|-------------|--------|--------------|
| FactEmployeeSnapshot[employee_id] | DimEmployee[employee_id] | Many:1 | Yes | Single |
| FactEmployeeSnapshot[department_id] | DimDepartment[department_id] | Many:1 | Yes | Single |
| FactEmployeeSnapshot[job_level] | DimJobLevel[job_level_id] | Many:1 | Yes | Single |
| FactEmployeeSnapshot[snapshot_date] | Calendar[Date] | Many:1 | Yes | Single |
| FactRecruitment[department_id] | DimDepartment[department_id] | Many:1 | No | Single |
| FactRecruitment[job_level] | DimJobLevel[job_level_id] | Many:1 | No | Single |
| FactRecruitment[open_date] | Calendar[Date] | Many:1 | No | Single |
| DimEmployee[department_id] | DimDepartment[department_id] | Many:1 | No | Single |

### Key DAX Skills Demonstrated

| Skill | Measure |
|-------|---------|
| Snapshot pattern (LASTDATE) | Current Headcount — point-in-time headcount via LASTDATE |
| DATEDIFF | Avg Tenure Years, Avg Time to Fill |
| USERELATIONSHIP (x6) | All recruitment measures — separate fact table with inactive links |
| FILTER + ISBLANK | Terminations — date-range filtering on termination_date |
| VAR + RETURN | Gender Pay Gap — multi-variable computation |
| RELATED in FILTER | Below Band Pct — comparing salary to related dimension band |
| POWER function | Annualized Attrition Rate — compounding monthly rate |
| SWITCH (RAG x4) | Attrition, Engagement, Compa Ratio, Time to Fill color coding |
| SAMEPERIODLASTYEAR | Headcount PY, YoY Growth |
| TOTALYTD | Payroll YTD |
| Multiple inactive relationships | Recruitment fact uses 3 inactive links simultaneously |
