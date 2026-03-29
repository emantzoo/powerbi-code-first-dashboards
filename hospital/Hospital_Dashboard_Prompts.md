# Hospital Operations Dashboard — Power BI Build Prompts

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
- FactAdmissions.csv (10000 rows — patient admissions with admit/discharge dates and charges)
- FactWaitTimes.csv (6000 rows — ED and walk-in wait time records with timestamps)
- DimDepartment.csv (8 rows — hospital departments with bed capacity)
- DimDoctor.csv (50 rows — doctors with specialty and experience)
- DimPatient.csv (4000 rows — patient demographics)

Read the headers from each CSV and create tables with the correct column names and data types.
For date columns (admit_date, discharge_date), use Date type.
For datetime columns (arrival_time, triage_time, seen_time), use DateTime type.
For ID columns (admission_id, patient_id, department_id, doctor_id, wait_id), use Text type.
For numeric columns (bed_capacity, years_experience, total_charge, floor), use Whole Number or Decimal as appropriate.
For text columns (diagnosis_code, admission_type, wait_category, age_group, gender, insurance_type, zip_code, specialty, department_name, doctor_name), use Text type.

Refresh the model after loading. Confirm row counts for each table.
```

---

## PHASE 1A — Relationships

```
Delete all auto-detected relationships in the model first.

Then create these relationships:

1. FactAdmissions[department_id] -> DimDepartment[department_id] (Many:1, ACTIVE, single direction)
2. FactAdmissions[doctor_id] -> DimDoctor[doctor_id] (Many:1, ACTIVE, single direction)
3. FactAdmissions[patient_id] -> DimPatient[patient_id] (Many:1, ACTIVE, single direction)
4. FactWaitTimes[department_id] -> DimDepartment[department_id] (Many:1, INACTIVE, single direction)
5. FactWaitTimes[patient_id] -> DimPatient[patient_id] (Many:1, INACTIVE, single direction)

Do NOT create date relationships yet — we'll do that after the Calendar table.
```

---

## PHASE 1B — Calendar Table

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
6. FactAdmissions[admit_date] -> Calendar[Date] (Many:1, ACTIVE, single direction)
7. FactAdmissions[discharge_date] -> Calendar[Date] (Many:1, INACTIVE, single direction)
```

---

## PHASE 1C — DAX Measures (Batch 1: Core Admissions KPIs)

```
Create a _Measures table (or add to it if it exists) with these DAX measures:

Total Admissions = COUNTROWS(FactAdmissions)

Total Charges = SUM(FactAdmissions[total_charge])

Avg Charge per Admission = DIVIDE([Total Charges], [Total Admissions], 0)

Unique Patients = DISTINCTCOUNT(FactAdmissions[patient_id])

Emergency Admissions = CALCULATE([Total Admissions], FactAdmissions[admission_type] = "Emergency")

Elective Admissions = CALCULATE([Total Admissions], FactAdmissions[admission_type] = "Elective")

Transfer Admissions = CALCULATE([Total Admissions], FactAdmissions[admission_type] = "Transfer")

Emergency Pct = DIVIDE([Emergency Admissions], [Total Admissions], 0)
```

---

## PHASE 1D — DAX Measures (Batch 2: Length of Stay & Bed Occupancy)

```
Add these measures to _Measures:

Avg Length of Stay = AVERAGEX(
    FactAdmissions,
    DATEDIFF(FactAdmissions[admit_date], FactAdmissions[discharge_date], DAY)
)

Max Length of Stay = MAXX(
    FactAdmissions,
    DATEDIFF(FactAdmissions[admit_date], FactAdmissions[discharge_date], DAY)
)

Total Bed Days = SUMX(
    FactAdmissions,
    DATEDIFF(FactAdmissions[admit_date], FactAdmissions[discharge_date], DAY)
)

Total Bed Capacity = SUM(DimDepartment[bed_capacity])

Daily Bed Occupancy Rate = DIVIDE(
    [Total Bed Days],
    [Total Bed Capacity] * COUNTROWS(Calendar),
    0
)

Active Admissions Today = CALCULATE(
    COUNTROWS(FactAdmissions),
    FILTER(
        FactAdmissions,
        FactAdmissions[admit_date] <= MAX(Calendar[Date])
        && FactAdmissions[discharge_date] >= MAX(Calendar[Date])
    )
)
```

---

## PHASE 1E — DAX Measures (Batch 3: Readmissions & Time Intelligence)

```
Add these measures to _Measures:

Readmissions 30Day = COUNTROWS(
    FILTER(
        FactAdmissions,
        CALCULATE(
            COUNTROWS(FactAdmissions),
            FILTER(
                ALL(FactAdmissions),
                FactAdmissions[patient_id] = EARLIER(FactAdmissions[patient_id])
                && FactAdmissions[admit_date] > EARLIER(FactAdmissions[discharge_date])
                && FactAdmissions[admit_date] <= EARLIER(FactAdmissions[discharge_date]) + 30
            )
        ) > 0
    )
)

Readmission Rate = DIVIDE([Readmissions 30Day], [Total Admissions], 0)

Admissions MTD = TOTALMTD([Total Admissions], Calendar[Date])

Admissions YTD = TOTALYTD([Total Admissions], Calendar[Date])

Admissions PY = CALCULATE([Total Admissions], SAMEPERIODLASTYEAR(Calendar[Date]))

Admissions YoY Growth = DIVIDE([Total Admissions] - [Admissions PY], [Admissions PY], 0)

Charges YTD = TOTALYTD([Total Charges], Calendar[Date])

Charges PY = CALCULATE([Total Charges], SAMEPERIODLASTYEAR(Calendar[Date]))

Charges YoY Growth = DIVIDE([Total Charges] - [Charges PY], [Charges PY], 0)
```

---

## PHASE 1F — DAX Measures (Batch 4: Wait Times)

```
Add these measures to _Measures:

Total Wait Records = CALCULATE(
    COUNTROWS(FactWaitTimes),
    USERELATIONSHIP(FactWaitTimes[department_id], DimDepartment[department_id])
)

Avg Wait Minutes = AVERAGEX(
    FactWaitTimes,
    DATEDIFF(FactWaitTimes[arrival_time], FactWaitTimes[seen_time], MINUTE)
)

Avg Triage Minutes = AVERAGEX(
    FactWaitTimes,
    DATEDIFF(FactWaitTimes[arrival_time], FactWaitTimes[triage_time], MINUTE)
)

Wait Under 15min Pct = DIVIDE(
    CALCULATE(COUNTROWS(FactWaitTimes), FactWaitTimes[wait_category] = "Under15min"),
    COUNTROWS(FactWaitTimes),
    0
)

Wait Over 60min Pct = DIVIDE(
    CALCULATE(COUNTROWS(FactWaitTimes), FactWaitTimes[wait_category] = "Over60min"),
    COUNTROWS(FactWaitTimes),
    0
)
```

---

## PHASE 1G — DAX Measures (Batch 5: Conditional Formatting)

```
Add these measures to _Measures:

Occupancy RAG Color = SWITCH(
    TRUE(),
    [Daily Bed Occupancy Rate] >= 0.90, "#E74C3C",
    [Daily Bed Occupancy Rate] >= 0.75, "#F39C12",
    "#27AE60"
)

LOS RAG Color = SWITCH(
    TRUE(),
    [Avg Length of Stay] >= 7, "#E74C3C",
    [Avg Length of Stay] >= 4, "#F39C12",
    "#27AE60"
)

Wait RAG Color = SWITCH(
    TRUE(),
    [Avg Wait Minutes] >= 60, "#E74C3C",
    [Avg Wait Minutes] >= 30, "#F39C12",
    "#27AE60"
)

Readmission RAG Color = SWITCH(
    TRUE(),
    [Readmission Rate] >= 0.15, "#E74C3C",
    [Readmission Rate] >= 0.08, "#F39C12",
    "#27AE60"
)
```

---

## PHASE 1H — Save

> Do this manually:

1. In Power BI Desktop: **File > Save As > Power BI Project (.pbip)**
2. Save to `C:\YOUR_SAVE_PATH\HospitalDashboard`
3. **Close Power BI Desktop completely**

---

## PHASE 2 — Generate Visuals (PBIR)

> Run the Python script — no AI needed:

1. Edit `scripts/generate_pages.py` — update the `BASE` path on line 2 to match your `.pbip` save location
2. Close Power BI Desktop
3. Run:

```bash
python scripts/generate_pages.py
```

The script generates 4 pages with 33 visuals (cards, bar charts, line charts, area charts, donut charts, tables, matrices, slicers) as PBIR `visual.json` files.

### Visual Layout Reference

This is the layout specification that was used to generate `scripts/generate_pages.py`. Canvas is 1280x720.

**Page 1 — Hospital Overview**

Row 1 (y=10, h=110):
- Card (x=20, w=235): Total Admissions
- Card (x=270, w=235): Avg Length of Stay
- Card (x=520, w=235): Daily Bed Occupancy Rate
- Card (x=770, w=235): Readmission Rate
- Slicer (x=1020, w=230): Calendar[Year]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): DimDepartment[department_name] vs Total Admissions
- Line chart (x=440, w=400): Calendar[Year_Month] vs Total Admissions
- Donut chart (x=860, w=380): FactAdmissions[admission_type] vs Total Admissions

Row 3 (y=440, h=260):
- Area chart (x=20, w=600): Calendar[Year_Month] vs Total Charges
- Clustered bar chart (x=640, w=610): DimDepartment[department_name] vs Avg Length of Stay

**Page 2 — Department Deep-Dive**

Row 1 (y=10, h=110):
- Card (x=20, w=235): Total Admissions
- Card (x=270, w=235): Total Charges
- Card (x=520, w=235): Avg Charge per Admission
- Card (x=770, w=235): Emergency Pct
- Slicer (x=1020, w=230): DimDepartment[department_name]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=610): DimDepartment[department_name] vs Total Charges
- Clustered bar chart (x=650, w=600): FactAdmissions[diagnosis_code] vs Total Admissions

Row 3 (y=440, h=260):
- Matrix (x=20, w=1230): Rows: DimDepartment[department_name], Columns: Calendar[Year], Values: Total Admissions, Avg Length of Stay, Total Charges, Daily Bed Occupancy Rate

**Page 3 — Wait Time Analysis**

Row 1 (y=10, h=110):
- Card (x=20, w=295): Avg Wait Minutes
- Card (x=330, w=295): Avg Triage Minutes
- Card (x=640, w=295): Wait Under 15min Pct
- Card (x=950, w=295): Wait Over 60min Pct

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): FactWaitTimes[wait_category] vs Total Wait Records
- Line chart (x=440, w=400): Calendar[Year_Month] vs Avg Wait Minutes
- Donut chart (x=860, w=380): DimDepartment[department_name] vs Total Wait Records

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimDepartment[department_name], Total Wait Records, Avg Wait Minutes, Avg Triage Minutes, Wait Under 15min Pct, Wait Over 60min Pct

**Page 4 — Patient Demographics**

Row 1 (y=10, h=110):
- Card (x=20, w=295): Unique Patients
- Card (x=330, w=295): Total Admissions
- Card (x=640, w=295): Admissions YoY Growth
- Card (x=950, w=295): Charges YoY Growth

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): DimPatient[age_group] vs Total Admissions
- Donut chart (x=440, w=380): DimPatient[gender] vs Total Admissions
- Clustered bar chart (x=840, w=410): DimPatient[insurance_type] vs Total Charges

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimPatient[age_group], DimPatient[insurance_type], Total Admissions, Avg Length of Stay, Total Charges, Avg Charge per Admission

---

## PHASE 3 — Open and Polish

1. Open `HospitalDashboard.pbip` in Power BI Desktop
2. All 4 pages should appear with data-bound visuals
3. Manual polish (~15-30 min):
   - Apply a color theme — consider a clinical blue/teal palette
   - Set conditional formatting on KPI cards using the RAG Color measures
   - Sync the Year slicer across pages (View > Sync Slicers)
   - Configure Page 4 as a drill-through page (add DimDepartment[department_name] as drill-through field)
   - Add page navigation buttons
   - Format wait time measures with "min" suffix
   - Format percentage measures as 0.0%
   - Format currency measures with $ prefix and comma separator

---

## Schema Reference

### Star Schema Diagram

```
                        Calendar
                          |
                    admit_date (active)
                    discharge_date (INACTIVE)
                          |
DimDoctor -----> FactAdmissions <----- DimPatient
  doctor_id          |                   patient_id
                     |                       |
               department_id          (INACTIVE link)
                     |                       |
               DimDepartment <----- FactWaitTimes
                                  department_id (INACTIVE)
```

### All Relationships

| From | To | Cardinality | Active | Cross-Filter |
|------|----|-------------|--------|--------------|
| FactAdmissions[department_id] | DimDepartment[department_id] | Many:1 | Yes | Single |
| FactAdmissions[doctor_id] | DimDoctor[doctor_id] | Many:1 | Yes | Single |
| FactAdmissions[patient_id] | DimPatient[patient_id] | Many:1 | Yes | Single |
| FactAdmissions[admit_date] | Calendar[Date] | Many:1 | Yes | Single |
| FactAdmissions[discharge_date] | Calendar[Date] | Many:1 | No | Single |
| FactWaitTimes[department_id] | DimDepartment[department_id] | Many:1 | No | Single |
| FactWaitTimes[patient_id] | DimPatient[patient_id] | Many:1 | No | Single |

### Key DAX Skills Demonstrated

| Skill | Measure |
|-------|---------|
| DATEDIFF | Avg Length of Stay, Avg Wait Minutes |
| USERELATIONSHIP | Total Wait Records (inactive dept link) |
| CALCULATE + FILTER | Readmissions 30Day, Active Admissions Today |
| EARLIER | Readmission self-join pattern |
| TOTALMTD / TOTALYTD | Admissions MTD, Charges YTD |
| SAMEPERIODLASTYEAR | Admissions PY, Charges PY |
| DIVIDE | All rate/ratio measures |
| SWITCH (RAG) | Occupancy, LOS, Wait, Readmission color coding |
| Semi-additive concept | Bed Occupancy Rate (capacity vs time) |
