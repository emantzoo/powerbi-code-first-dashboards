# Epikast Pharma Ops — Power BI Build Prompts (Data Model)

Tech-enabled biopharma services: HCP engagement (inside reps + MSLs), patient access &
adherence, MSL Partner (AI medical-information assistant), A/B experimentation, and program
financials — delivered from an Athens hub for US biopharma clients.

This file builds the **shared semantic model**. It feeds **6 dashboards / 16 pages**
(specs at the bottom). Visuals are generated separately by the Python scripts in `scripts/`
(built in the next step — this checkpoint is the data model only).

Use the phases in order. Each grey block is copy-paste ready for Claude Desktop (Cowork /
Code) driving the Power BI Modeling MCP, or follow them by hand in Power BI Desktop.

> **Sample data**: `data/generate_epikast_data.py` (stdlib, `random.seed(42)`) writes all
> 11 CSVs into `data/`. Period 2025-07-01 → 2026-04-30.

---

## ⚠️ Changes from the source spec (applied fixes)

Three corrections were applied so the model and its slicers behave correctly. Each is
flagged inline below with **[FIX]**.

1. **Rx from / NBRx from Engaged HCPs** — original `FILTER(VALUES(FactRx[HCPID]), …)`
   can't see `FactHCPCalls` (filters flow Dim→Fact, not Fact→Fact). Rewritten with
   `TREATAS` of the connected-HCP set onto `FactRx[HCPID]`.
2. **Patient-case time response** — `FactPatientCases[RxDate] → DimCalendar` is inactive,
   so without help the Quarter / YearMonth slicers on the Patient Access pages would be
   ignored. Every `FactPatientCases` measure activates the relationship with
   `USERELATIONSHIP`.
3. **Secondary `RepID` relationships set ACTIVE** — the source marked
   `FactPatientCases[RepID]→DimRep` and `FactMSLPartnerUsage[RepID]→DimRep` inactive, which
   would break the MSL-by-rep and case-by-rep breakdowns. They're conformed dimensions
   (single-direction, no ambiguous path), so they're active. `DimDrug[DrugName]→…[Drug]`
   relationships were also added so the DrugName slicers work.

---

## PHASE 0 — Load Data

```
Connect to my open Power BI Desktop file.

Load all CSV files from C:\YOUR_DATA_PATH into my Power BI model. The folder has 11 files:

Dimensions:
- DimCalendar.csv      (304 rows — one row per day, 2025-07-01 to 2026-04-30)
- DimRep.csv           (25 rows — delivery talent: MSL / Patient Support / HCP Engagement)
- DimHCP.csv           (500 rows — physicians: specialty, therapy area, tier, geo)
- DimPatient.csv       (2000 rows — patient demographics + insurance)
- DimDrug.csv          (5 rows — brands with therapy area, launch date, specialty flag)
- DimExperiment.csv    (8 rows — A/B experiment registry)

Facts:
- FactHCPCalls.csv          (15000 rows — HCP engagement events)
- FactPatientCases.csv      (3000 rows — patient access journey Rx → first dose)
- FactRx.csv                (~7700 rows — prescriptions)
- FactMSLPartnerUsage.csv   (~8300 rows — AI medical-info assistant queries)
- FactFinancials.csv        (10 rows — monthly program P&L)

Model-output tables (Approach B — generate them first with `python scripts/train_uplift.py`):
- FactUplift.csv         (~132 rows — uplift per tactic × outcome × segment, with 95% CIs)
- DimNBA.csv             (~33 rows — next-best-action: top tactic per segment/outcome)
- FeatureImportance.csv  (~12 rows — overall |uplift| per tactic, per outcome)
Load these three as STANDALONE tables — no relationships (they are pre-aggregated model
output; each visual reads its own columns). uplift / ci_low / ci_high / treated_value /
control_value / importance / est_uplift = Decimal; n_treated / n_control / significant =
Whole Number; everything else Text.

Read each CSV header and create tables with correct names/types.
- Dates (Date, CallDate, RxDate, FirstContactDate, PASubmitDate, PADecisionDate,
  FulfillmentDate, FirstDoseDate, UsageDate, MonthDate, HireDate, EnrollmentDate,
  StartDate, EndDate, LaunchDate): Date type.
- IDs (all *ID columns): Text.
- Flags (IsConnected, IsMeaningfulInteraction, AIRecommended, AIFollowed,
  IsScheduleAdherent, NotesTaken, FollowUpScheduled, ScriptDeviation, AdverseEventFlagged,
  IsAbandoned, FirstCallResolved, Adherent30/60/90, IsTarget, IsSpecialty, IsNewToBrand,
  IsWeekend, IsActive, UsedInHCPInteraction): Whole Number (0/1, blanks allowed where noted).
- Counts/days/minutes/scores (DurationMinutes, AHT_Minutes, *Days, *Sec, *Minutes,
  Quantity, TenureMonths, *Score, UserSatisfaction, *Headcount, *Cost*, *Revenue*): Decimal
  or Whole Number as appropriate.
- Everything else (names, Role, Team, Specialty, Tier, Region, Status, Channel, Script,
  PAStatus, AnswerQuality, etc.): Text.

Refresh and confirm row counts.
```

> Mark **DimCalendar** as a Date Table on `[Date]` (Table tools → Mark as date table). The
> time-intelligence measures (DATESINPERIOD, DATEADD, etc.) require it.

---

## PHASE 1A — Relationships

```
Delete all auto-detected relationships first. Then create:

# Date — only Calls is ACTIVE; the rest are INACTIVE and activated per-measure via USERELATIONSHIP
1.  FactHCPCalls[CallDate]          -> DimCalendar[Date]   (Many:1, ACTIVE,   single)
2.  FactPatientCases[RxDate]        -> DimCalendar[Date]   (Many:1, INACTIVE, single)
3.  FactRx[RxDate]                  -> DimCalendar[Date]   (Many:1, INACTIVE, single)
4.  FactMSLPartnerUsage[UsageDate]  -> DimCalendar[Date]   (Many:1, INACTIVE, single)
5.  FactFinancials[MonthDate]       -> DimCalendar[Date]   (Many:1, INACTIVE, single)

# Rep / HCP / Patient — conformed dims, all ACTIVE  [FIX #3: RepID links are active]
6.  FactHCPCalls[RepID]             -> DimRep[RepID]       (Many:1, ACTIVE, single)
7.  FactHCPCalls[HCPID]             -> DimHCP[HCPID]       (Many:1, ACTIVE, single)
8.  FactPatientCases[PatientID]     -> DimPatient[PatientID] (Many:1, ACTIVE, single)
9.  FactPatientCases[RepID]         -> DimRep[RepID]       (Many:1, ACTIVE, single)
10. FactRx[HCPID]                   -> DimHCP[HCPID]       (Many:1, ACTIVE, single)
11. FactMSLPartnerUsage[RepID]      -> DimRep[RepID]       (Many:1, ACTIVE, single)

# Drug — conformed, all ACTIVE  [FIX #4: enables DrugName slicers]
12. DimDrug[DrugName]               -> FactHCPCalls[Drug]
13. DimDrug[DrugName]               -> FactPatientCases[Drug]
14. DimDrug[DrugName]               -> FactRx[Drug]
15. DimDrug[DrugName]               -> FactMSLPartnerUsage[Drug]

All single-direction (dimension filters fact). Multiple facts sharing DimCalendar / DimRep /
DimDrug is the conformed-dimension pattern — no ambiguous path is created.
```

---

## PHASE 1 — DAX Measures

Create a `_Measures` table and add the measures below, grouped by theme. Names are exact
(case-sensitive) and must match what the visual scripts reference.

### 1. HCP Engagement (13)

```
Total Calls = COUNTROWS(FactHCPCalls)
Connected Calls = CALCULATE([Total Calls], FactHCPCalls[IsConnected] = 1)
Connect Rate = DIVIDE([Connected Calls], [Total Calls], 0)
Meaningful Interactions = CALCULATE([Total Calls], FactHCPCalls[IsMeaningfulInteraction] = 1)
Meaningful Interaction Rate = DIVIDE([Meaningful Interactions], [Connected Calls], 0)
HCPs Contacted = DISTINCTCOUNT(FactHCPCalls[HCPID])
Target HCPs = CALCULATE(DISTINCTCOUNT(DimHCP[HCPID]), DimHCP[IsTarget] = 1)
HCP Reach = DIVIDE(CALCULATE(DISTINCTCOUNT(FactHCPCalls[HCPID]), FactHCPCalls[IsConnected] = 1), [Target HCPs], 0)
Avg Contact Frequency = DIVIDE([Connected Calls], [HCPs Contacted], 0)
Avg Call Duration = CALCULATE(AVERAGE(FactHCPCalls[DurationMinutes]), FactHCPCalls[IsConnected] = 1)
Avg Meaningful Duration = CALCULATE(AVERAGE(FactHCPCalls[DurationMinutes]), FactHCPCalls[IsMeaningfulInteraction] = 1)
Follow Up Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[FollowUpScheduled] = 1), [Connected Calls], 0)
Avg HCP Sentiment = CALCULATE(AVERAGE(FactHCPCalls[HCPSentimentScore]), NOT(ISBLANK(FactHCPCalls[HCPSentimentScore])))
```

### 2. AI / Next-Best-Action (9)

```
AI Recommended Calls = CALCULATE([Total Calls], FactHCPCalls[AIRecommended] = 1)
AI Followed Calls = CALCULATE([Total Calls], FactHCPCalls[AIFollowed] = 1)
AI Acceptance Rate = DIVIDE([AI Followed Calls], [AI Recommended Calls], 0)
AI Connect Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[AIFollowed] = 1, FactHCPCalls[IsConnected] = 1), [AI Followed Calls], 0)
Non-AI Connect Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[AIRecommended] = 0, FactHCPCalls[IsConnected] = 1), CALCULATE([Total Calls], FactHCPCalls[AIRecommended] = 0), 0)
AI Lift on Connect Rate = [AI Connect Rate] - [Non-AI Connect Rate]
AI Meaningful Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[AIFollowed] = 1, FactHCPCalls[IsMeaningfulInteraction] = 1), CALCULATE([Total Calls], FactHCPCalls[AIFollowed] = 1, FactHCPCalls[IsConnected] = 1), 0)
Non-AI Meaningful Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[AIRecommended] = 0, FactHCPCalls[IsMeaningfulInteraction] = 1), CALCULATE([Total Calls], FactHCPCalls[AIRecommended] = 0, FactHCPCalls[IsConnected] = 1), 0)
AI Lift on Meaningful Rate = [AI Meaningful Rate] - [Non-AI Meaningful Rate]
```

### 3. Script A/B Testing (8)

```
Script A Calls = CALCULATE([Total Calls], FactHCPCalls[Script] = "Script A - Empathetic")
Script B Calls = CALCULATE([Total Calls], FactHCPCalls[Script] = "Script B - Direct")
Script A Connect Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[Script] = "Script A - Empathetic", FactHCPCalls[IsConnected] = 1), [Script A Calls], 0)
Script B Connect Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[Script] = "Script B - Direct", FactHCPCalls[IsConnected] = 1), [Script B Calls], 0)
Script A Meaningful Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[Script] = "Script A - Empathetic", FactHCPCalls[IsMeaningfulInteraction] = 1), CALCULATE([Total Calls], FactHCPCalls[Script] = "Script A - Empathetic", FactHCPCalls[IsConnected] = 1), 0)
Script B Meaningful Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[Script] = "Script B - Direct", FactHCPCalls[IsMeaningfulInteraction] = 1), CALCULATE([Total Calls], FactHCPCalls[Script] = "Script B - Direct", FactHCPCalls[IsConnected] = 1), 0)
Script A Avg Duration = CALCULATE(AVERAGE(FactHCPCalls[DurationMinutes]), FactHCPCalls[Script] = "Script A - Empathetic", FactHCPCalls[IsConnected] = 1)
Script B Avg Duration = CALCULATE(AVERAGE(FactHCPCalls[DurationMinutes]), FactHCPCalls[Script] = "Script B - Direct", FactHCPCalls[IsConnected] = 1)
```

### 4. Patient Support (21)

> **[FIX #2]** Every measure here wraps `USERELATIONSHIP(FactPatientCases[RxDate],
> DimCalendar[Date])` so Quarter / YearMonth slicers and trend axes filter patient data.
> Ratio measures that only reference other measures inherit it automatically.

```
Total Cases = CALCULATE(COUNTROWS(FactPatientCases), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Active Cases = CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[CaseStatus] IN {"Open", "In Progress"}, USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Resolved Cases = CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[CaseStatus] = "Resolved", USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Abandoned Cases = CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[IsAbandoned] = 1, USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Abandonment Rate = DIVIDE([Abandoned Cases], [Total Cases], 0)
Avg Time to Therapy = CALCULATE(AVERAGE(FactPatientCases[TimeToTherapyDays]), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Median Time to Therapy = CALCULATE(MEDIAN(FactPatientCases[TimeToTherapyDays]), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
PA Approval Rate = DIVIDE(
    CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[PAStatus] = "Approved", USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])),
    CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[PAStatus] IN {"Approved", "Denied", "Appeal"}, USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])), 0)
PA Denial Rate = DIVIDE(
    CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[PAStatus] = "Denied", USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])),
    CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[PAStatus] IN {"Approved", "Denied", "Appeal"}, USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])), 0)
Avg PA Decision Delay = CALCULATE(AVERAGE(FactPatientCases[PADecisionDelayDays]), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
First Call Resolution Rate = DIVIDE(
    CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[FirstCallResolved] = 1, USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])),
    [Resolved Cases], 0)
Avg Case Resolution Days = CALCULATE(AVERAGE(FactPatientCases[CaseResolutionDays]), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Avg First Contact Delay = CALCULATE(AVERAGE(FactPatientCases[FirstContactDelayDays]), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Contacted Within 48h Rate = DIVIDE(
    CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[FirstContactDelayDays] <= 2, USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])),
    [Total Cases], 0)
Adherence 30 Day = DIVIDE(
    CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[Adherent30] = 1, USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])),
    CALCULATE(COUNTROWS(FactPatientCases), NOT(ISBLANK(FactPatientCases[Adherent30])), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])), 0)
Adherence 60 Day = DIVIDE(
    CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[Adherent60] = 1, USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])),
    CALCULATE(COUNTROWS(FactPatientCases), NOT(ISBLANK(FactPatientCases[Adherent60])), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])), 0)
Adherence 90 Day = DIVIDE(
    CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[Adherent90] = 1, USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])),
    CALCULATE(COUNTROWS(FactPatientCases), NOT(ISBLANK(FactPatientCases[Adherent90])), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])), 0)
Abandoned Pre PA = CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[IsAbandoned] = 1, FactPatientCases[AbandonmentStage] = "Pre-PA", USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Abandoned During PA = CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[IsAbandoned] = 1, FactPatientCases[AbandonmentStage] = "During PA", USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Abandoned Post PA = CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[IsAbandoned] = 1, FactPatientCases[AbandonmentStage] = "Post-PA", USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Abandoned Post Fulfillment = CALCULATE(COUNTROWS(FactPatientCases), FactPatientCases[IsAbandoned] = 1, FactPatientCases[AbandonmentStage] = "Post-Fulfillment", USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
```

### 5. Ops Efficiency (7)

```
Avg AHT = AVERAGE(FactHCPCalls[AHT_Minutes])
Avg After Call Work = AVERAGE(FactHCPCalls[AfterCallWorkMinutes])
Schedule Adherence Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[IsScheduleAdherent] = 1), [Total Calls], 0)
Calls Per Rep Per Day = DIVIDE([Total Calls], DISTINCTCOUNT(FactHCPCalls[RepID]) * DISTINCTCOUNT(FactHCPCalls[CallDate]), 0)
Connected Calls Per Rep Per Day = DIVIDE([Connected Calls], DISTINCTCOUNT(FactHCPCalls[RepID]) * DISTINCTCOUNT(FactHCPCalls[CallDate]), 0)
Meaningful Per Rep Per Day = DIVIDE([Meaningful Interactions], DISTINCTCOUNT(FactHCPCalls[RepID]) * DISTINCTCOUNT(FactHCPCalls[CallDate]), 0)
Notes Compliance Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[NotesTaken] = 1), [Connected Calls], 0)
```

### 6. Prescriptions (7)

> **[FIX #1]** "Rx from / NBRx from Engaged HCPs" use `TREATAS` to push the connected-HCP
> set onto `FactRx[HCPID]` (the original `FILTER(VALUES(FactRx[HCPID]) …)` could not see
> `FactHCPCalls`).

```
Total Rx = CALCULATE(COUNTROWS(FactRx), USERELATIONSHIP(FactRx[RxDate], DimCalendar[Date]))
New to Brand Rx = CALCULATE(COUNTROWS(FactRx), FactRx[IsNewToBrand] = 1, USERELATIONSHIP(FactRx[RxDate], DimCalendar[Date]))
NBRx Rate = DIVIDE([New to Brand Rx], [Total Rx], 0)
Rx Per HCP = DIVIDE([Total Rx], DISTINCTCOUNT(FactRx[HCPID]), 0)
Rx from Engaged HCPs =
VAR EngagedHCPs = CALCULATETABLE(VALUES(FactHCPCalls[HCPID]), FactHCPCalls[IsConnected] = 1)
RETURN CALCULATE(COUNTROWS(FactRx), USERELATIONSHIP(FactRx[RxDate], DimCalendar[Date]), TREATAS(EngagedHCPs, FactRx[HCPID]))
Rx from Non-Engaged HCPs = [Total Rx] - [Rx from Engaged HCPs]
NBRx from Engaged HCPs =
VAR EngagedHCPs = CALCULATETABLE(VALUES(FactHCPCalls[HCPID]), FactHCPCalls[IsConnected] = 1)
RETURN CALCULATE(COUNTROWS(FactRx), FactRx[IsNewToBrand] = 1, USERELATIONSHIP(FactRx[RxDate], DimCalendar[Date]), TREATAS(EngagedHCPs, FactRx[HCPID]))
```

### 7. MSL Partner Usage (11)

```
Total MSL Queries = CALCULATE(COUNTROWS(FactMSLPartnerUsage), USERELATIONSHIP(FactMSLPartnerUsage[UsageDate], DimCalendar[Date]))
MSL Queries Per Day = DIVIDE([Total MSL Queries], DISTINCTCOUNT(FactMSLPartnerUsage[UsageDate]), 0)
MSL Queries Per MSL Per Day = DIVIDE([Total MSL Queries], DISTINCTCOUNT(FactMSLPartnerUsage[RepID]) * DISTINCTCOUNT(FactMSLPartnerUsage[UsageDate]), 0)
Fully Answered Rate = DIVIDE(CALCULATE(COUNTROWS(FactMSLPartnerUsage), FactMSLPartnerUsage[AnswerQuality] = "Fully Answered"), [Total MSL Queries], 0)
Partially Answered Rate = DIVIDE(CALCULATE(COUNTROWS(FactMSLPartnerUsage), FactMSLPartnerUsage[AnswerQuality] = "Partially Answered"), [Total MSL Queries], 0)
No Answer Rate = DIVIDE(CALCULATE(COUNTROWS(FactMSLPartnerUsage), FactMSLPartnerUsage[AnswerQuality] = "No Answer Found"), [Total MSL Queries], 0)
Avg Time to Answer Sec = AVERAGE(FactMSLPartnerUsage[TimeToAnswerSec])
Total Time Saved Hours = DIVIDE(SUM(FactMSLPartnerUsage[TimeSavedMinutes]), 60, 0)
Avg Time Saved Per Query Min = AVERAGE(FactMSLPartnerUsage[TimeSavedMinutes])
Used in HCP Interaction Rate = DIVIDE(CALCULATE(COUNTROWS(FactMSLPartnerUsage), FactMSLPartnerUsage[UsedInHCPInteraction] = 1), [Total MSL Queries], 0)
Avg MSL Satisfaction = AVERAGE(FactMSLPartnerUsage[UserSatisfaction])
```

### 8. Experiment Tracking (5)

```
Total Experiments = COUNTROWS(DimExperiment)
Concluded Experiments = CALCULATE(COUNTROWS(DimExperiment), LEFT(DimExperiment[Status], 9) = "Concluded")
Running Experiments = CALCULATE(COUNTROWS(DimExperiment), DimExperiment[Status] = "Running")
Win Rate = DIVIDE(CALCULATE(COUNTROWS(DimExperiment), DimExperiment[Status] = "Concluded - Winner"), [Concluded Experiments], 0)
Avg Observed Lift = CALCULATE(AVERAGE(DimExperiment[ObservedLift]), DimExperiment[Status] = "Concluded - Winner")
Experiment Lift = AVERAGE(DimExperiment[ObservedLift])
```

### 9. Financials (7)

```
Total Revenue USD = SUM(FactFinancials[TotalRevenue_USD])
Total Cost EUR = SUM(FactFinancials[TotalCost_EUR])
Gross Margin USD = SUM(FactFinancials[GrossMargin_USD])
Gross Margin Pct = DIVIDE([Gross Margin USD], [Total Revenue USD], 0)
Avg Cost Per Call = AVERAGE(FactFinancials[CostPerCall_EUR])
Avg Cost Per Case = AVERAGE(FactFinancials[CostPerCase_EUR])
Cost Breakdown Rep Pct = DIVIDE(SUM(FactFinancials[RepCost_EUR]), [Total Cost EUR], 0)
```

### 10. Time Intelligence (5)

```
Calls L4W = CALCULATE([Total Calls], DATESINPERIOD(DimCalendar[Date], MAX(DimCalendar[Date]), -28, DAY))
Connect Rate L4W = CALCULATE([Connect Rate], DATESINPERIOD(DimCalendar[Date], MAX(DimCalendar[Date]), -28, DAY))
Calls MoM Change = VAR Current = [Total Calls] VAR Prior = CALCULATE([Total Calls], DATEADD(DimCalendar[Date], -1, MONTH)) RETURN DIVIDE(Current - Prior, Prior, 0)
Connect Rate MoM Change = [Connect Rate] - CALCULATE([Connect Rate], DATEADD(DimCalendar[Date], -1, MONTH))
Abandonment Rate MoM Change = [Abandonment Rate] - CALCULATE([Abandonment Rate], DATEADD(DimCalendar[Date], -1, MONTH))
```

### 11. Compliance & Quality (5)

```
Script Deviation Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[ScriptDeviation] = 1), [Connected Calls], 0)
Avg Call Quality Score = CALCULATE(AVERAGE(FactHCPCalls[CallQualityScore]), NOT(ISBLANK(FactHCPCalls[CallQualityScore])))
AE Flag Rate = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[AdverseEventFlagged] = 1), [Connected Calls], 0)
High Quality Calls Pct = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[CallQualityScore] >= 7), CALCULATE([Total Calls], NOT(ISBLANK(FactHCPCalls[CallQualityScore]))), 0)
Low Quality Calls Pct = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[CallQualityScore] <= 4), CALCULATE([Total Calls], NOT(ISBLANK(FactHCPCalls[CallQualityScore]))), 0)
```

### 12. Workforce Efficiency (4)

```
Quality Adjusted Productivity = [Meaningful Per Rep Per Day] * [Avg Call Quality Score] / 10
Utilization Rate = DIVIDE([Total Calls] * [Avg AHT], DISTINCTCOUNT(FactHCPCalls[RepID]) * DISTINCTCOUNT(FactHCPCalls[CallDate]) * 480, 0)
Calls Per Productive Hour = DIVIDE([Total Calls], [Total Calls] * [Avg AHT] / 60, 0)
Deviation Rate by Tenure = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[ScriptDeviation] = 1), [Total Calls], 0)
```

### 13. Channel Mix (4)

```
Phone Calls Pct = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[Channel] = "Phone"), [Total Calls], 0)
Email Pct = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[Channel] = "Email"), [Total Calls], 0)
Video Pct = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[Channel] = "Video"), [Total Calls], 0)
Connect Rate by Channel Phone = DIVIDE(CALCULATE([Total Calls], FactHCPCalls[Channel] = "Phone", FactHCPCalls[IsConnected] = 1), CALCULATE([Total Calls], FactHCPCalls[Channel] = "Phone"), 0)
```

### 14. RAG Indicators (7)

```
Connect Rate RAG = SWITCH(TRUE(), [Connect Rate] >= 0.35, "Green", [Connect Rate] >= 0.25, "Amber", "Red")
Abandonment Rate RAG = SWITCH(TRUE(), [Abandonment Rate] <= 0.15, "Green", [Abandonment Rate] <= 0.25, "Amber", "Red")
Time to Therapy RAG = SWITCH(TRUE(), [Avg Time to Therapy] <= 20, "Green", [Avg Time to Therapy] <= 35, "Amber", "Red")
PA Approval Rate RAG = SWITCH(TRUE(), [PA Approval Rate] >= 0.70, "Green", [PA Approval Rate] >= 0.55, "Amber", "Red")
Schedule Adherence RAG = SWITCH(TRUE(), [Schedule Adherence Rate] >= 0.85, "Green", [Schedule Adherence Rate] >= 0.75, "Amber", "Red")
MSL Answer Quality RAG = SWITCH(TRUE(), [Fully Answered Rate] >= 0.70, "Green", [Fully Answered Rate] >= 0.55, "Amber", "Red")
Script Deviation RAG = SWITCH(TRUE(), [Script Deviation Rate] <= 0.05, "Green", [Script Deviation Rate] <= 0.15, "Amber", "Red")
```

### 15. Patient Access Bottleneck (5)  ⭐ added

> Process-mining "where do the days go?" — avg days per funnel stage. Each wraps
> `USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date])` (fix #2) and filters out
> rows whose end-date is blank so `DATEDIFF` never sees a missing date. Stacked together
> they reconstruct Avg Time to Therapy and expose the slow stage (PA decision).

```
Avg Days Rx to Contact = CALCULATE(AVERAGEX(FactPatientCases, DATEDIFF(FactPatientCases[RxDate], FactPatientCases[FirstContactDate], DAY)), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Avg Days Contact to PA Submit = CALCULATE(AVERAGEX(FactPatientCases, DATEDIFF(FactPatientCases[FirstContactDate], FactPatientCases[PASubmitDate], DAY)), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Avg Days PA Submit to Decision = CALCULATE(AVERAGEX(FILTER(FactPatientCases, NOT(ISBLANK(FactPatientCases[PADecisionDate]))), DATEDIFF(FactPatientCases[PASubmitDate], FactPatientCases[PADecisionDate], DAY)), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Avg Days Decision to Fulfillment = CALCULATE(AVERAGEX(FILTER(FactPatientCases, NOT(ISBLANK(FactPatientCases[FulfillmentDate]))), DATEDIFF(FactPatientCases[PADecisionDate], FactPatientCases[FulfillmentDate], DAY)), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
Avg Days Fulfillment to First Dose = CALCULATE(AVERAGEX(FILTER(FactPatientCases, NOT(ISBLANK(FactPatientCases[FirstDoseDate]))), DATEDIFF(FactPatientCases[FulfillmentDate], FactPatientCases[FirstDoseDate], DAY)), USERELATIONSHIP(FactPatientCases[RxDate], DimCalendar[Date]))
```

### 16. Selling Time vs Admin (4)  ⭐ added

> Epikast's #1 productivity lever — how much rep time is live engagement vs after-call work.
> `AHT_Minutes = DurationMinutes + AfterCallWorkMinutes`, so these split total handling time.

```
Total Handling Minutes = SUM(FactHCPCalls[AHT_Minutes])
Selling Minutes = CALCULATE(SUM(FactHCPCalls[DurationMinutes]), FactHCPCalls[IsConnected] = 1)
Selling Time Pct = DIVIDE([Selling Minutes], [Total Handling Minutes], 0)
Admin Time Pct = DIVIDE(SUM(FactHCPCalls[AfterCallWorkMinutes]), [Total Handling Minutes], 0)
```

### 17. Sentiment & Insight Engine (4)  ⭐ added

> Sentiment analysis on the AI `HCPSentimentScore` (uses the `SentimentBand` column
> below), plus two helper measures over the offline uplift output tables.

```
Positive Sentiment Pct = DIVIDE(
    CALCULATE([Total Calls], FactHCPCalls[SentimentBand] = "Positive"),
    CALCULATE([Total Calls], NOT(ISBLANK(FactHCPCalls[HCPSentimentScore]))), 0)
Negative Sentiment Pct = DIVIDE(
    CALCULATE([Total Calls], FactHCPCalls[SentimentBand] = "Negative"),
    CALCULATE([Total Calls], NOT(ISBLANK(FactHCPCalls[HCPSentimentScore]))), 0)
Avg Uplift = AVERAGE(FactUplift[uplift])
Avg Importance = AVERAGE(FeatureImportance[importance])
```

**Total: 127 measures** across 17 groups.

### Calculated Columns

```
# DimRep — splits reps into Top 20% vs Rest by lifetime meaningful interactions, so the
# "what do top performers do differently?" comparison works as a slicer / axis.  ⭐ added
Performance Tier =
VAR Total = COUNTROWS(ALL(DimRep))
VAR Rnk = RANKX(ALL(DimRep), CALCULATE([Meaningful Interactions]), , DESC)
RETURN IF(Rnk <= ROUNDUP(Total * 0.2, 0), "Top 20%", "Rest")

# DimRep — tenure band for the workforce ramp-up analysis (Internal report)
Tenure Bucket = SWITCH(TRUE(),
    DimRep[TenureMonths] < 6, "0-6mo",
    DimRep[TenureMonths] < 12, "6-12mo",
    DimRep[TenureMonths] < 18, "12-18mo",
    "18+mo")

# FactHCPCalls — 2-hour evening call-time band for the connect-rate heatmap (Internal report)
CallTimeBucket = VAR h = VALUE(LEFT(FactHCPCalls[CallTime], 2))
RETURN SWITCH(TRUE(), h < 18, "16-18", h < 20, "18-20", h < 22, "20-22", "22-00")

# FactHCPCalls — sentiment band for the Sentiment Analysis page (Insights Engine report)
SentimentBand = SWITCH(TRUE(),
    ISBLANK(FactHCPCalls[HCPSentimentScore]), BLANK(),
    FactHCPCalls[HCPSentimentScore] >= 4, "Positive",
    FactHCPCalls[HCPSentimentScore] >= 2.5, "Neutral",
    "Negative")
```

---

## PHASE 2 — Generate Visuals (next step)

The 6 dashboards / 16 pages below are built by Python scripts in `scripts/` (PBIR JSON,
one `make_*` call per visual). **Not built yet** — this checkpoint delivers the data model
only. The dashboard specs are recorded here so the visual layer can be generated against
them next.

Palette: Navy `#1B3A5C`, Teal `#2E86AB`, Magenta `#A23B72`, Green `#2E8B57`,
Amber `#DAA520`, Red `#CD3333`, Background `#F8F9FA`, Cards `#FFFFFF`, Text `#333333`.
Canvas 1280×720.

| # | Dashboard | Pages | Audience |
|---|-----------|-------|----------|
| 1 | Ops Overview | 4 (Exec Summary, Call Outcomes, Rep Productivity, Trends) | VP Operations |
| 2 | Patient Access Funnel | 3 (Funnel, PA & Insurance, Adherence) | Patient services lead |
| 3 | AI Impact | 3 (AI Call Targeting, MSL Partner Performance, MSL Partner ROI) | Exec / client |
| 4 | A/B Test Tracker | 2 (Experiment Registry, Script A/B Deep Dive) | Optimization team |
| 5 | Compliance & Quality | 1 | Compliance officer |
| 6 | Channel Mix & Workforce | 1 | Ops / workforce planning |

**Added analyses woven into the above:** a **patient-access bottleneck** stage-duration
waterfall (group 15) on Dashboard 2 — surfacing the slow PA-decision stage (~15 of the ~26
day time-to-therapy); a **selling-time vs admin** split (group 16) on Dashboards 1/6; and a
**top-performer vs rest** comparison (via `DimRep[Performance Tier]`) on Dashboard 1's Rep
Productivity page — contrasting AI adoption, Script-A use, follow-up and notes compliance
between the top 20% and the rest.

> A few visuals in these specs need small new helper functions beyond the existing
> framework: **combo chart** (bars + line on a secondary axis), **heatmap matrix** with a
> color scale, **reference lines**, and **A-vs-B comparison cards**. These will be added to
> the shared `pbir_lib.py` when the visual scripts are generated.

---

## Schema Reference

```
                                  DimCalendar
            (active: CallDate · inactive+USERELATIONSHIP: RxDate, RxDate, UsageDate, MonthDate)
                                       |
   DimRep ────┬──── FactHCPCalls ──────┼────── FactRx ──── DimHCP
              │          │             │          │
         FactMSLPartnerUsage      FactPatientCases ──── DimPatient
                                       │
                                  DimDrug (DrugName → each fact's Drug)

   DimExperiment  ·  FactFinancials   (reference / standalone)
```

### Key DAX skills demonstrated

| Skill | Example |
|-------|---------|
| USERELATIONSHIP | all Rx / MSL / Patient-case measures (inactive date links) |
| TREATAS (virtual relationship) | Rx from / NBRx from Engaged HCPs |
| IN operator | Active Cases, PA Approval/Denial Rate |
| DIVIDE (safe ratios) | every rate / Pct |
| DATESINPERIOD / DATEADD | Calls L4W, MoM change measures |
| VAR + RETURN | Calls MoM Change, engaged-HCP measures |
| LEFT / text logic | Concluded Experiments |
| SWITCH(TRUE()) RAG | 7 status-color measures |
| Conformed dimensions | DimRep / DimDrug / DimCalendar across multiple facts |
