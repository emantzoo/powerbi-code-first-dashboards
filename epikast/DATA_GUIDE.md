# Epikast Pharma Ops — Data Guide

A full reference for the dataset behind the Epikast dashboards: every file, where it
comes from in a real Epikast-style stack, every column, and which dashboard pages use it —
plus how the star schema fits together.

- **11 source tables** (6 dimensions + 5 facts) + **3 model-output tables** (from
  `scripts/train_uplift.py`) = 14 CSVs in `data/`.
- All sample data is synthetic, generated deterministically by
  `data/generate_epikast_data.py` (`random.seed(42)`). Period **2025-07-01 → 2026-04-30**.
- To run for real Epikast, replace each CSV with the same-named columns from the source
  system noted below — measures and visuals keep working unchanged.

**Provenance tiers** (how likely the data exists / how it's produced):
🟢 System-of-record · 🔵 Purchased data · 🟣 AI-derived (Epikast's AI layer) · 🟠 Internal finance · ⚙️ Model output

---

## 1. Source systems at a glance

| Table | Tier | Real-world source | Grain (1 row = ) | Rows |
|-------|------|-------------------|------------------|------|
| DimCalendar | 🟢 | Generated date table | one calendar day | 304 |
| DimRep | 🟢 | HR / Veeva user list | one delivery staff member | 25 |
| DimHCP | 🟢 | Veeva account + alignment | one targeted physician | 500 |
| DimPatient | 🟢 | Patient hub (de-identified) | one enrolled patient | 2,000 |
| DimDrug | 🟢 | Client / product master | one brand | 5 |
| DimExperiment | 🟣 | Experimentation tracker | one A/B experiment | 8 |
| FactHCPCalls | 🟢🟣 | Veeva CRM call activity + AI/telephony | one HCP interaction | 15,000 |
| FactPatientCases | 🟢 | Patient hub / case management | one patient access journey | 3,000 |
| FactRx | 🔵 | IQVIA / Symphony Rx data | one prescription | 7,683 |
| FactMSLPartnerUsage | 🟣 | AI medical-info assistant logs | one MSL AI query | 8,281 |
| FactFinancials | 🟠 | Internal finance | one month of program P&L | 10 |
| FactUplift | ⚙️ | `train_uplift.py` | one tactic×outcome×segment estimate | 132 |
| DimNBA | ⚙️ | `train_uplift.py` | one segment×outcome recommendation | 33 |
| FeatureImportance | ⚙️ | `train_uplift.py` | one tactic×outcome importance | 12 |

---

## 2. Dimensions

### DimCalendar 🟢 — used by **all reports** (time axes & Quarter/YearMonth slicers)
| Column | Type | Description |
|--------|------|-------------|
| Date | Date | Primary key; marked as the model's Date Table |
| Year | Whole | Calendar year |
| Quarter | Text | "Q1"–"Q4" |
| Month / MonthNum | Text / Whole | Month name / 1–12 |
| YearMonth | Text | "YYYY-MM" — main trend axis |
| WeekNum | Whole | ISO week |
| DayOfWeek / DayOfWeekNum | Text / Whole | Weekday name / 1–7 (heatmap rows) |
| IsWeekend | Flag | 1 if Sat/Sun |

### DimRep 🟢 — Internal (all pages), AI (MSL pages), Insights (drivers)
| Column | Type | Description |
|--------|------|-------------|
| RepID | Text | Primary key |
| RepName | Text | Staff name (**internal-only** — hidden from client report) |
| Role | Text | MSL · Patient Support Specialist · HCP Engagement Rep |
| Team | Text | Team Alpha / Beta / Gamma |
| TherapyArea | Text | Rep's focus area |
| HireDate | Date | Used to derive tenure |
| TenureMonths | Whole | Months since hire |
| IsActive | Flag | Active roster flag |
| *Performance Tier* | calc col | "Top 20%" vs "Rest" by meaningful interactions |
| *Tenure Bucket* | calc col | 0-6mo / 6-12mo / 12-18mo / 18+mo |

### DimHCP 🟢 — Internal (Call Outcomes), AI (targeting), Client (HCP Engagement), Insights
| Column | Type | Description |
|--------|------|-------------|
| HCPID | Text | Primary key |
| HCPName | Text | Physician name |
| Specialty | Text | Oncologist, Cardiologist, … |
| TherapyArea | Text | Therapeutic area |
| State / Region | Text | US state / region (filled-map + territory) |
| Tier | Text | Tier 1 High / Tier 2 Medium / Tier 3 Low value |
| PrePeriodRxVolume | Whole | Baseline Rx volume (targeting input) |
| IsTarget | Flag | On the call plan; drives **HCP Reach** denominator |

### DimPatient 🟢 — Client (Patient Outcomes), Insights (abandonment drivers)
| Column | Type | Description |
|--------|------|-------------|
| PatientID | Text | Primary key |
| AgeGroup | Text | 18-34 / 35-49 / 50-64 / 65+ |
| Gender | Text | Male / Female |
| State / Region | Text | Geography |
| InsuranceType | Text | Commercial / Medicare / Medicaid / VA / Self-Pay |
| TherapyArea / Drug | Text | Therapy / brand |
| EnrollmentDate | Date | Hub enrollment date |

### DimDrug 🟢 — Client/AI/Insights DrugName slicers
| Column | Type | Description |
|--------|------|-------------|
| DrugID | Text | Primary key |
| DrugName | Text | Brand — **related to each fact's `Drug` column** |
| TherapyArea | Text | Therapy area |
| LaunchDate | Date | Launch (launch-phase analysis) |
| IsSpecialty | Flag | Specialty vs primary-care drug |

### DimExperiment 🟣 — AI Effectiveness (Experiment Registry)
| Column | Type | Description |
|--------|------|-------------|
| ExperimentID | Text | Primary key |
| ExperimentName | Text | e.g. "Script Tone Test" |
| Hypothesis | Text | What's being tested |
| PrimaryKPI / GuardrailKPI | Text | Success metric / guardrail |
| StartDate / EndDate | Date | Run window (EndDate blank if running) |
| Status | Text | Concluded - Winner / Concluded - No Significant Difference / Running / Planned |
| Winner | Text | Winning variant (blank if none) |
| SampleSizeTarget / Actual | Whole | Planned vs achieved n |
| ConfidenceLevel | Decimal | e.g. 0.95 |
| ObservedLift | Decimal | Measured lift (drives **Experiment Lift** bar) |
| TherapyArea / TargetPopulation | Text | Scope |

---

## 3. Facts

### FactHCPCalls 🟢🟣 — the core engagement event (15,000 rows)
Powers **Internal Ops** (all pages), **AI Effectiveness** (targeting, script), **Client**
(engagement), **Insights Engine** (drivers, sentiment).

| Column | Type | Tier | Description |
|--------|------|------|-------------|
| CallID | Text | 🟢 | Primary key |
| CallDate | Date | 🟢 | **Active** relationship to DimCalendar |
| CallTime | Text | 🟢 | "HH:MM" (Athens evening) → `CallTimeBucket` for the heatmap |
| RepID / HCPID | Text | 🟢 | FKs to DimRep / DimHCP |
| CallOutcome | Text | 🟢 | Connected / Voicemail / No Answer / Gatekeeper Block / Wrong Number |
| IsConnected | Flag | 🟢 | Drives **Connect Rate** |
| DurationMinutes | Decimal | 🟢 | Talk time (connected) → **selling time** |
| AfterCallWorkMinutes | Decimal | 🟢 | Admin after the call → **admin time** |
| AHT_Minutes | Decimal | 🟢 | Duration + ACW (avg handling time) |
| IsMeaningfulInteraction | Flag | 🟣 | AI-labelled "real dialogue" → **Meaningful Rate** (uplift outcome) |
| InteractionType | Text | 🟢 | Scientific Discussion, Product Info, … |
| Script | Text | 🟢 | "Script A - Empathetic" / "Script B - Direct" (A/B test) |
| AIRecommended / AIFollowed | Flag | 🟣 | NBA suggested / rep followed → **AI lift**, acceptance |
| ScheduledTime / IsScheduleAdherent | Text / Flag | 🟢 | Planned time / kept it → **Schedule Adherence** |
| Drug / TherapyArea | Text | 🟢 | Brand / therapy area |
| NotesTaken | Flag | 🟢 | CRM notes logged → **Notes Compliance** |
| FollowUpScheduled | Flag | 🟢 | Next step booked → **Follow Up Rate** |
| HCPSentimentScore | Decimal | 🟣 | AI sentiment 1–5 → **sentiment analysis**, `SentimentBand` |
| Channel | Text | 🟢 | Phone / Email / Video → **channel mix** |
| ScriptDeviation | Flag | 🟣 | Off-script → **Script Deviation Rate** |
| CallQualityScore | Decimal | 🟣 | QA score 1–10 → **quality** measures |
| AdverseEventFlagged | Flag | 🟢 | Pharmacovigilance flag → **AE Flag Rate** |
| *CallTimeBucket* | calc col | | 16-18 / 18-20 / 20-22 / 22-00 (heatmap) |
| *SentimentBand* | calc col | | Positive / Neutral / Negative |

### FactPatientCases 🟢 — the patient access journey (3,000 rows)
Powers **Client** (Patient Support & Outcomes) and **Insights** (abandonment).

| Column | Type | Description |
|--------|------|-------------|
| CaseID | Text | Primary key |
| PatientID / RepID | Text | FKs (RepID = assigned navigator) |
| Drug / TherapyArea / InsuranceType | Text | Case attributes |
| RxDate | Date | Prescription date → **inactive** Calendar link (USERELATIONSHIP) |
| FirstContactDate / FirstContactDelayDays | Date / Whole | First outreach → **Contacted Within 48h** |
| PASubmitDate / PADecisionDate | Date | Prior-auth submit / decision dates (bottleneck) |
| PAStatus | Text | Approved / Denied / Pending / Appeal → **PA Approval Rate** |
| PADecisionDelayDays | Whole | PA turnaround |
| FulfillmentDate / FirstDoseDate | Date | Pharmacy fill / therapy start |
| TimeToTherapyDays | Whole | Rx → first dose → **Avg Time to Therapy** |
| CaseStatus | Text | Open / In Progress / Resolved / Abandoned |
| IsAbandoned | Flag | Dropped off → **Abandonment Rate** (Insights outcome) |
| AbandonmentReason / AbandonmentStage | Text | Why / where (Pre-PA … Post-Fulfillment) |
| NumberOfTouches | Whole | Contacts to resolve |
| FirstCallResolved | Flag | Resolved on first contact → **FCR** |
| Adherent30 / 60 / 90 | Flag | On-therapy at 30/60/90 days → **adherence curve** |
| CaseResolutionDays | Whole | Days to resolve |

### FactRx 🔵 — prescriptions (7,683 rows) — **Client** (ROI, Rx influence)
| Column | Type | Description |
|--------|------|-------------|
| RxID | Text | Primary key |
| HCPID | Text | FK to DimHCP (links Rx to engagement) |
| RxDate | Date | Inactive Calendar link (USERELATIONSHIP) |
| Drug / TherapyArea | Text | Brand / therapy |
| IsNewToBrand | Flag | New-to-brand → **NBRx Rate** |
| Quantity | Whole | Units (30/60/90) |
| State / Region | Text | Geography |

### FactMSLPartnerUsage 🟣 — AI medical-info assistant queries (8,281 rows)
Powers **AI Effectiveness** (MSL pages) and **Client** (AI-Driven Insights topics).

| Column | Type | Description |
|--------|------|-------------|
| UsageID | Text | Primary key |
| UsageDate | Date | Inactive Calendar link (USERELATIONSHIP) |
| RepID | Text | FK (the MSL) |
| Drug / TherapyArea | Text | Subject |
| Topic | Text | Mechanism of Action, Clinical Trial Data, … (top-topics bar) |
| QueryType | Text | Pre-Meeting Prep / Live During HCP Call / Post-Call / Self-Study |
| AnswerQuality | Text | Fully / Partially Answered / No Answer / Redirected → **Fully Answered Rate** |
| TimeToAnswerSec | Decimal | Response speed |
| TimeSavedMinutes | Decimal | Est. vs manual lit search → **Total Time Saved Hours** |
| UsedInHCPInteraction | Flag | Answer used in a call → **Used in Interaction Rate** |
| UserSatisfaction | Whole | 1–5 → **Avg MSL Satisfaction** |
| HCPID | Text | Linked HCP (when used in an interaction; often blank) |

### FactFinancials 🟠 — monthly program P&L (10 rows) — **Client** (ROI)
| Column | Type | Description |
|--------|------|-------------|
| FinancialID | Text | Primary key |
| YearMonth / MonthDate | Text / Date | Month (MonthDate = inactive Calendar link) |
| RepHeadcount | Whole | Active reps |
| RepCost_EUR / TechCost_EUR / MgmtCost_EUR | Decimal | Cost components |
| TotalCost_EUR | Decimal | Total program cost |
| BaseRevenue_USD / EngagementRevenue_USD / CaseRevenue_USD | Decimal | Revenue components |
| TotalRevenue_USD | Decimal | Total revenue |
| TotalCalls / TotalCases | Whole | Volume (for unit economics) |
| CostPerCall_EUR / CostPerCase_EUR | Decimal | Unit cost |
| GrossMargin_USD / GrossMarginPct | Decimal | Margin |

---

## 4. Model-output tables ⚙️ (from `scripts/train_uplift.py`)

Standalone / disconnected — **no relationships**; each is read directly by its visuals on
the Insights Engine report. Regenerate by re-running the script after a data refresh.

### FactUplift (132 rows) — Insights → Winning Plays
`outcome` (Meaningful Interaction / Connect / HCP Sentiment) · `tactic` (AI-Followed vs Not,
Script A vs B, Video vs Phone, Email vs Phone) · `segment_type` (Overall / Specialty / Tier) ·
`segment_value` · `treated_value` · `control_value` · `uplift` · `ci_low` · `ci_high` ·
`n_treated` · `n_control` · `significant` (1/0).

### DimNBA (33 rows) — Insights → Next-Best-Action
`segment_type` · `segment_value` · `outcome` · `recommended_tactic` · `est_uplift`.

### FeatureImportance (12 rows) — Insights → NBA page
`outcome` · `feature` (tactic) · `importance` (|uplift|) · `uplift` · `direction` (Helps/Hurts).

---

## 5. The schema explained

### Star schema with conformed dimensions
Facts sit in the middle; dimensions describe them. Three dimensions are **conformed** —
shared across several facts so one slicer filters them all:

```
                                   DimCalendar
   (ACTIVE: FactHCPCalls.CallDate · INACTIVE+USERELATIONSHIP: RxDate, RxDate, UsageDate, MonthDate)
                                        |
     DimRep ──┬─────── FactHCPCalls ────┼──────── FactRx ─────── DimHCP
              │            │            │            │
       FactMSLPartnerUsage │       FactPatientCases ─┴─── DimPatient
              │            │
            (RepID)     DimDrug  (DrugName → each fact's Drug)

   DimExperiment   ·   FactFinancials        (reference / standalone)
   FactUplift · DimNBA · FeatureImportance   (disconnected model output)
```

### Three design rules to know
1. **One active date relationship.** Only `FactHCPCalls[CallDate] → DimCalendar` is active.
   Every other fact's date link is **inactive** and switched on inside its measures with
   `USERELATIONSHIP`. This is the repo's signature pattern and keeps date logic explicit.
2. **Conformed dimensions are all active.** `DimRep`, `DimDrug`, and `DimCalendar` each
   filter multiple facts via single-direction (Dim→Fact) relationships — no ambiguous path,
   so they coexist without conflict.
3. **Model-output + reference tables are disconnected.** `FactUplift`, `DimNBA`,
   `FeatureImportance` (and largely `DimExperiment`, `FactFinancials`) are pre-aggregated or
   standalone; their visuals read their own columns directly.

### Relationship list
| From | To | Active |
|------|----|--------|
| FactHCPCalls[CallDate] | DimCalendar[Date] | ✅ |
| FactPatientCases[RxDate] · FactRx[RxDate] · FactMSLPartnerUsage[UsageDate] · FactFinancials[MonthDate] | DimCalendar[Date] | ❌ (USERELATIONSHIP) |
| FactHCPCalls[RepID] · FactPatientCases[RepID] · FactMSLPartnerUsage[RepID] | DimRep[RepID] | ✅ |
| FactHCPCalls[HCPID] · FactRx[HCPID] | DimHCP[HCPID] | ✅ |
| FactPatientCases[PatientID] | DimPatient[PatientID] | ✅ |
| DimDrug[DrugName] → FactHCPCalls / FactPatientCases / FactRx / FactMSLPartnerUsage [Drug] | | ✅ |

Full DAX and load instructions are in `Epikast_Dashboard_Prompts.md`.

---

## 6. Which data feeds which dashboard

Four reports run off this one model. ✅ = the table materially drives that report.

| Table | Internal Ops | AI Effectiveness | Client-facing | Insights Engine |
|-------|:---:|:---:|:---:|:---:|
| DimCalendar | ✅ | ✅ | ✅ | ✅ |
| DimRep | ✅ | ✅ | | ✅ |
| DimHCP | ✅ | ✅ | ✅ | ✅ |
| DimPatient | | | ✅ | ✅ |
| DimDrug | | ✅ | ✅ | ✅ |
| DimExperiment | | ✅ | | |
| FactHCPCalls | ✅ | ✅ | ✅ | ✅ |
| FactPatientCases | | | ✅ | ✅ |
| FactRx | | | ✅ | |
| FactMSLPartnerUsage | | ✅ | ✅ | |
| FactFinancials | | | ✅ | |
| FactUplift / DimNBA / FeatureImportance | | | | ✅ |

### Page-level usage
**Internal Ops** — Exec Summary, Call Outcomes, Rep Productivity, Trends, Compliance,
Channel/Workforce → almost entirely `FactHCPCalls` × `DimRep`/`DimHCP`/`DimCalendar`.

**AI Effectiveness** — AI Call Targeting (`FactHCPCalls` AI fields × `DimHCP`); MSL Partner
Performance/ROI (`FactMSLPartnerUsage` × `DimRep`); Experiment Registry (`DimExperiment`);
Script A/B (`FactHCPCalls` Script field × `DimHCP`).

**Client-facing** — Engagement Overview & HCP Engagement (`FactHCPCalls` × `DimHCP`/`DimDrug`);
Patient Support & Outcomes (`FactPatientCases` × `DimPatient`); AI-Driven Insights
(`FactHCPCalls` AI fields + `FactMSLPartnerUsage`); ROI (`FactFinancials` + `FactRx`).

**Insights Engine** — What Drives Engagement/Abandonment (`FactHCPCalls` / `FactPatientCases`
via native AI visuals); Winning Plays & NBA (`FactUplift` / `DimNBA` / `FeatureImportance`);
HCP Sentiment Analysis (`FactHCPCalls.HCPSentimentScore` × `DimHCP`/`DimCalendar`).

---

## 7. Going from sample to live

1. Replace each CSV in `data/` with the real extract — **same file name, same column
   names/types** as above.
2. For the model-output tables, point `scripts/train_uplift.py` at the real
   `FactHCPCalls`, re-run it, and reload the three output CSVs.
3. Everything else (relationships, 127 measures, 21 dashboard pages) is unchanged.

> Reminder: 🟣 AI-derived fields (sentiment, meaningful, quality, NBA flags) come from
> Epikast's AI/conversation layer — in this sample they're modeled; in production they're the
> real model outputs. True conversation-text mining (objections, phrases, talk/listen ratio)
> would need transcript data, which is not part of this dataset.
