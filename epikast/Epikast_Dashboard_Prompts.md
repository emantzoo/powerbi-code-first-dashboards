# Epikast Engagement Dashboard — Power BI Build Prompts

Epikast is a technology-enabled biopharma services company: outsourced, remote/hybrid
HCP engagement (inside sales reps + MSLs), patient support & adherence, medical affairs,
and AI-driven insight — delivered from a cost-effective hub and integrated with the
client's Veeva Vault CRM. This dashboard gives Epikast delivery teams (internal) and their
biopharma clients (external) a single view of engagement volume, quality/compliance,
patient outcomes, and per-client campaign health.

Use these prompts in order. Each one is a copy-paste block for Claude Desktop (Cowork or Code tab).

Replace `C:\YOUR_DATA_PATH` with the folder where you saved the 6 CSVs.
Replace `C:\YOUR_SAVE_PATH` with where you want the `.pbip` project saved.

> The sample CSVs in `data/` are generated deterministically by
> `data/generate_epikast_data.py` (stdlib only, `random.seed(42)`) — rerun it to
> regenerate identical data, or edit it to change volumes.

---

## PHASE 0 — Load Data

> Open a blank Power BI Desktop first. Then paste this into Claude Desktop:

```
Connect to my open Power BI Desktop file.

Load all CSV files from C:\YOUR_DATA_PATH into my Power BI model.
The folder contains these 6 files:
- FactInteractions.csv (12000 rows — HCP engagement events: phone/email/video/portal)
- FactPatientSupport.csv (1400 rows — patient adherence & navigation records)
- DimAgent.csv (60 rows — Epikast delivery talent: reps, MSLs, navigators)
- DimHCP.csv (300 rows — targeted physicians with specialty, segment, geo)
- DimClient.csv (8 rows — biopharma clients with therapeutic area and brand)
- DimPatient.csv (1500 rows — patients enrolled in support programs)

Read the headers from each CSV and create tables with the correct column names and data types.
For date columns (interaction_date, enrollment_date, contract_start), use Date type.
For ID columns (interaction_id, support_id, agent_id, hcp_id, client_id, patient_id), use Text type.
For numeric columns (duration_minutes, tenure_months, decile, time_to_therapy_days,
  persistence_days, nps_score), use Whole Number.
For ratio columns (sentiment_score, script_adherence_pct, adherence_pct, latitude, longitude),
  use Decimal Number.
For text columns (agent_name, role, credential, team, hub_location, hcp_name, specialty,
  segment, region, territory, client_name, therapeutic_area, brand, engagement_model,
  age_group, gender, insurance_type, channel, interaction_type, connected, outcome,
  next_best_action, compliance_status, adverse_event_flagged, status, barrier_type,
  barrier_resolved, payer_status), use Text type.

Set latitude/longitude on DimHCP to the Latitude/Longitude data categories so they map correctly.

Refresh the model after loading. Confirm row counts for each table.
```

---

## PHASE 1A — Relationships

```
Delete all auto-detected relationships in the model first.

Then create these relationships. DimAgent, DimClient, and Calendar are CONFORMED
dimensions shared by both fact tables — every relationship below is single-direction
(dimension filters fact), so there is no ambiguous path and all can stay ACTIVE.

1. FactInteractions[agent_id]        -> DimAgent[agent_id]      (Many:1, ACTIVE, single direction)
2. FactInteractions[hcp_id]          -> DimHCP[hcp_id]          (Many:1, ACTIVE, single direction)
3. FactInteractions[client_id]       -> DimClient[client_id]    (Many:1, ACTIVE, single direction)
4. FactPatientSupport[patient_id]    -> DimPatient[patient_id]  (Many:1, ACTIVE, single direction)
5. FactPatientSupport[agent_id]      -> DimAgent[agent_id]      (Many:1, ACTIVE, single direction)
6. FactPatientSupport[client_id]     -> DimClient[client_id]    (Many:1, ACTIVE, single direction)

Do NOT create date relationships yet — we'll do that after the Calendar table.
```

---

## PHASE 1B — Calendar Table

```
Create a DAX calculated table called Calendar:

Calendar = ADDCOLUMNS(
    CALENDAR(DATE(2024,1,1), DATE(2025,6,30)),
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

Then create these date relationships (both ACTIVE — separate fact tables to a shared Calendar):
7. FactInteractions[interaction_date]   -> Calendar[Date] (Many:1, ACTIVE, single direction)
8. FactPatientSupport[enrollment_date]  -> Calendar[Date] (Many:1, ACTIVE, single direction)
```

---

## PHASE 1C — DAX Measures (Batch 1: Core Engagement KPIs)

```
Create a _Measures table (or add to it if it exists) with these DAX measures:

Total Interactions = COUNTROWS(FactInteractions)

Connected Interactions = CALCULATE([Total Interactions], FactInteractions[connected] = "Yes")

Connect Rate = DIVIDE([Connected Interactions], [Total Interactions], 0)

Total Engagement Minutes = SUM(FactInteractions[duration_minutes])

Avg Interaction Duration = DIVIDE([Total Engagement Minutes], [Connected Interactions], 0)

Unique HCPs Reached = DISTINCTCOUNT(FactInteractions[hcp_id])

HCP Reach Pct = DIVIDE([Unique HCPs Reached], COUNTROWS(DimHCP), 0)

Interactions per HCP = DIVIDE([Total Interactions], [Unique HCPs Reached], 0)
```

---

## PHASE 1D — DAX Measures (Batch 2: Channel & Engagement Quality)

```
Add these measures to _Measures:

Phone Interactions = CALCULATE([Total Interactions], FactInteractions[channel] = "Phone")

Email Interactions = CALCULATE([Total Interactions], FactInteractions[channel] = "Email")

Video Interactions = CALCULATE([Total Interactions], FactInteractions[channel] = "Video")

Portal Interactions = CALCULATE([Total Interactions], FactInteractions[channel] = "Portal")

Scientific Exchange Pct = DIVIDE(
    CALCULATE([Total Interactions], FactInteractions[interaction_type] = "Scientific Exchange"),
    [Total Interactions], 0
)

Promotional Pct = DIVIDE(
    CALCULATE([Total Interactions], FactInteractions[interaction_type] = "Promotional"),
    [Total Interactions], 0
)

Avg Sentiment Score = AVERAGE(FactInteractions[sentiment_score])

Positive Sentiment Pct = DIVIDE(
    CALCULATE([Total Interactions], FactInteractions[sentiment_score] >= 0.6),
    [Total Interactions], 0
)
```

---

## PHASE 1E — DAX Measures (Batch 3: Quality & Compliance)

```
Add these measures to _Measures:

Avg Script Adherence = AVERAGE(FactInteractions[script_adherence_pct])

Compliance Pass Rate = DIVIDE(
    CALCULATE([Total Interactions], FactInteractions[compliance_status] = "Pass"),
    [Total Interactions], 0
)

Compliance Reviews = CALCULATE([Total Interactions], FactInteractions[compliance_status] = "Review")

Adverse Events Flagged = CALCULATE([Total Interactions], FactInteractions[adverse_event_flagged] = "Yes")

Adverse Event Rate = DIVIDE([Adverse Events Flagged], [Total Interactions], 0)
```

---

## PHASE 1F — DAX Measures (Batch 4: Time Intelligence)

```
Add these measures to _Measures:

Interactions PY = CALCULATE([Total Interactions], SAMEPERIODLASTYEAR(Calendar[Date]))

Interactions YoY Growth = DIVIDE([Total Interactions] - [Interactions PY], [Interactions PY], 0)

Interactions MTD = TOTALMTD([Total Interactions], Calendar[Date])

Interactions YTD = TOTALYTD([Total Interactions], Calendar[Date])

Interactions L3M = CALCULATE(
    [Total Interactions],
    DATESINPERIOD(Calendar[Date], MAX(Calendar[Date]), -3, MONTH)
)

Connect Rate PY = CALCULATE([Connect Rate], SAMEPERIODLASTYEAR(Calendar[Date]))
```

---

## PHASE 1G — DAX Measures (Batch 5: Patient Support & Outcomes)

```
Add these measures to _Measures:

Support Records = COUNTROWS(FactPatientSupport)

Total Patients Enrolled = DISTINCTCOUNT(FactPatientSupport[patient_id])

Active Patients = CALCULATE([Support Records], FactPatientSupport[status] IN {"Active", "On Therapy"})

Active Patient Rate = DIVIDE([Active Patients], [Support Records], 0)

Discontinued Patients = CALCULATE([Support Records], FactPatientSupport[status] = "Discontinued")

Discontinuation Rate = DIVIDE([Discontinued Patients], [Support Records], 0)

Avg Time to Therapy = AVERAGE(FactPatientSupport[time_to_therapy_days])

Avg Adherence = AVERAGE(FactPatientSupport[adherence_pct])

Avg Persistence Days = AVERAGE(FactPatientSupport[persistence_days])

Barrier Resolution Rate = DIVIDE(
    CALCULATE([Support Records], FactPatientSupport[barrier_resolved] = "Yes"),
    CALCULATE([Support Records], FactPatientSupport[barrier_type] <> "None"),
    0
)

Payer Approval Rate = DIVIDE(
    CALCULATE([Support Records], FactPatientSupport[payer_status] IN {"Approved", "Appeal Won"}),
    [Support Records], 0
)

NPS Score =
VAR Promoters = CALCULATE([Support Records], FactPatientSupport[nps_score] >= 9)
VAR Detractors = CALCULATE([Support Records], FactPatientSupport[nps_score] <= 6)
RETURN DIVIDE(Promoters - Detractors, [Support Records], 0) * 100
```

---

## PHASE 1H — DAX Measures (Batch 6: Conditional Formatting RAG)

```
Add these measures to _Measures. They return hex colors for KPI-card and
table conditional formatting (green = good, amber = watch, red = act).

Connect Rate RAG Color = SWITCH(
    TRUE(),
    [Connect Rate] >= 0.70, "#27AE60",
    [Connect Rate] >= 0.55, "#F39C12",
    "#E74C3C"
)

Sentiment RAG Color = SWITCH(
    TRUE(),
    [Avg Sentiment Score] >= 0.65, "#27AE60",
    [Avg Sentiment Score] >= 0.50, "#F39C12",
    "#E74C3C"
)

Adherence RAG Color = SWITCH(
    TRUE(),
    [Avg Adherence] >= 0.80, "#27AE60",
    [Avg Adherence] >= 0.65, "#F39C12",
    "#E74C3C"
)

Compliance RAG Color = SWITCH(
    TRUE(),
    [Compliance Pass Rate] >= 0.97, "#27AE60",
    [Compliance Pass Rate] >= 0.93, "#F39C12",
    "#E74C3C"
)
```

---

## PHASE 1I — Save

> Do this manually:

1. In Power BI Desktop: **File > Save As > Power BI Project (.pbip)**
2. Save to `C:\YOUR_SAVE_PATH\EpikastDashboard` (name the report `epikast_dashb`)
3. **Close Power BI Desktop completely**

---

## PHASE 2 — Generate Visuals (PBIR)

> Run the Python script — no AI needed:

1. Edit `scripts/generate_pages.py` — update the `BASE` path on line ~12 to match your `.pbip` save location
2. Close Power BI Desktop
3. Run:

```bash
python scripts/generate_pages.py
```

The script generates 6 pages (~45 visuals): KPI cards, line/area trends, clustered bars
(incl. gradient), donuts, a scatter agent-quality plot, an HCP territory bubble map,
detail tables, and matrices — all as PBIR `visual.json` files.

### Visual Layout Reference

Canvas is 1280x720. Every page opens with a colored title bar.

**Page 1 — Engagement Overview** — "How is engagement performing overall?"
- Cards (y=60): Total Interactions, Connect Rate, Unique HCPs Reached, Avg Sentiment Score; Year slicer
- Bar gradient: client_name vs Total Interactions
- Line (dual): Year_Month vs Total Interactions + Interactions PY
- Donut: channel mix
- Area: Year_Month vs Total Engagement Minutes
- Bar: interaction_type vs Total Interactions

**Page 2 — Agent & Rep Performance** — "Who is delivering, and how well?"
- Cards: Total Interactions, Avg Interaction Duration, Connect Rate, Interactions per HCP; role slicer
- Bar: role vs Total Interactions
- Scatter: agents — X Connect Rate, Y Avg Sentiment Score, size Total Interactions
- Matrix: role x team vs core metrics

**Page 3 — HCP Engagement** — "Which physicians are we reaching?"
- Cards: Unique HCPs Reached, HCP Reach Pct, Interactions per HCP, Scientific Exchange Pct; specialty slicer
- Bar: specialty vs Total Interactions
- Donut: segment mix
- Bubble map: HCP territory by Total Interactions
- Table: HCP detail

**Page 4 — Patient Support & Outcomes** — "Are patients getting on and staying on therapy?"
- Cards: Total Patients Enrolled, Active Patient Rate, Avg Adherence, NPS Score; status slicer
- Bar: barrier_type vs Support Records
- Donut: payer_status mix
- Bar: client_name vs Avg Adherence
- Table: age_group x outcome metrics

**Page 5 — Quality & Compliance** — "Are we compliant and on-message?"
- Cards: Compliance Pass Rate, Avg Script Adherence, Adverse Event Rate, Positive Sentiment Pct; team slicer
- Bar: role vs Avg Script Adherence
- Line: Year_Month vs Avg Sentiment Score
- Donut: outcome mix
- Table: team x compliance metrics

**Page 6 — Client Campaign Health** — "How is each client's program performing?"
- Cards: Total Interactions, Active Patients, Connect Rate, Payer Approval Rate; client slicer
- Bar gradient: client_name vs Total Interactions
- Bar: therapeutic_area vs Connect Rate
- Matrix: client_name vs Total Interactions, Connect Rate, Unique HCPs Reached, Active Patients, Avg Adherence, NPS Score

---

## PHASE 3 — Open and Polish

1. Open `EpikastDashboard.pbip` in Power BI Desktop
2. All 6 pages should appear with data-bound visuals
3. Manual polish (~15-30 min):
   - Apply a color theme — a clinical teal/indigo palette suits a biopharma brand
   - Set conditional formatting on KPI cards using the RAG Color measures
   - Sync the Year slicer across pages (View > Sync Slicers)
   - Configure Page 6 (client) or Page 2 (agent) as a drill-through page
   - Add page navigation to the buttons (Format > Action > Page navigation)
   - Format percentage measures (Connect Rate, rates, Pcts) as 0.0%
   - Format sentiment/adherence as 0.00, duration with a " min" suffix, NPS as whole number

---

## Schema Reference

### Star Schema Diagram (two conformed-dimension fact tables)

```
                         Calendar
                       /          \
          interaction_date      enrollment_date
                 |                      |
   DimAgent --- FactInteractions      FactPatientSupport --- DimPatient
       \   \        |                   |        /   /
        \   DimHCP (hcp_id)             |        /  (patient_id)
         \                              |       /
          \------- DimClient (client_id, shared) ------/
```

DimAgent, DimClient, and Calendar are **conformed dimensions** — each filters both fact
tables through its own single-direction relationship, so all relationships stay active
without creating an ambiguous path. DimHCP is specific to FactInteractions; DimPatient is
specific to FactPatientSupport.

### All Relationships

| From | To | Cardinality | Active | Cross-Filter |
|------|----|-------------|--------|--------------|
| FactInteractions[agent_id] | DimAgent[agent_id] | Many:1 | Yes | Single |
| FactInteractions[hcp_id] | DimHCP[hcp_id] | Many:1 | Yes | Single |
| FactInteractions[client_id] | DimClient[client_id] | Many:1 | Yes | Single |
| FactInteractions[interaction_date] | Calendar[Date] | Many:1 | Yes | Single |
| FactPatientSupport[patient_id] | DimPatient[patient_id] | Many:1 | Yes | Single |
| FactPatientSupport[agent_id] | DimAgent[agent_id] | Many:1 | Yes | Single |
| FactPatientSupport[client_id] | DimClient[client_id] | Many:1 | Yes | Single |
| FactPatientSupport[enrollment_date] | Calendar[Date] | Many:1 | Yes | Single |

### Key DAX Skills Demonstrated

| Skill | Measure |
|-------|---------|
| COUNTROWS / DISTINCTCOUNT | Total Interactions, Unique HCPs Reached |
| CALCULATE filter context | channel/type/compliance breakdowns |
| DIVIDE (safe ratios) | every rate / Pct measure |
| IN operator | Active Patients, Payer Approval Rate |
| SAMEPERIODLASTYEAR | Interactions PY, Connect Rate PY |
| TOTALMTD / TOTALYTD | Interactions MTD, Interactions YTD |
| DATESINPERIOD | Interactions L3M (rolling 3 months) |
| VAR + RETURN | NPS Score (promoters − detractors) |
| SWITCH(TRUE()) RAG | Connect Rate / Sentiment / Adherence / Compliance colors |
| Conformed dimensions | DimAgent / DimClient / Calendar across two facts |
