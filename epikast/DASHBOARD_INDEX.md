# Epikast Dashboard Index — Plots & How to Read Them

A complete map of all **9 dashboards / 39 pages**, what every plot shows, and how to read it.
Two parts:

1. **[Plot glossary](#part-1--plot-glossary)** — each visual *type* once: what it is, how to read it, when it lies to you.
2. **[Per-dashboard pages](#part-2--dashboards-page-by-page)** — every page, every plot, its exact field binding, and the question it answers.

> All visuals are generated code-first by `scripts/generate_pages_*.py` (PBIR JSON). Measures
> live in `Epikast_Dashboard_Prompts.md` (139 measures / 20 groups). `M` = the `_Measures` table.
> R/Python plots need those engines configured in Power BI Desktop.

---

## Dashboard Summary

| # | Script | Report folder | Pages | Audience |
|---|--------|--------------|-------|----------|
| 1 | `generate_pages_client.py` | `epikast_client_dashb` | 5 | Pharma client — outcomes & ROI |
| 2 | `generate_pages_internal.py` | `epikast_internal_dashb` | 7 | Internal ops team — rep-level |
| 3 | `generate_pages_ai.py` | `epikast_ai_dashb` | 5 | AI effectiveness, MSL, A/B |
| 4 | `generate_pages_ai_impact.py` | `epikast_ai_dashb` (alt) | 3 | Condensed AI / MSL view |
| 5 | `generate_pages_insights.py` | `epikast_insights_dashb` | 5 | Driver analysis, NBA, sentiment |
| 6 | `generate_pages_advanced.py` | `epikast_advanced_dashb` | 5 | Heatmaps, R plots, SHAP |
| 7 | `generate_pages_ab_tracker.py` | `epikast_ab_dashb` | 2 | Experiment registry & A/B deep dive |
| 8 | `generate_pages_ops_overview.py` | `epikast_ops_dashb` | 4 | Smart ops command center |
| 9 | `generate_pages_patient_access.py` | `epikast_patient_dashb` | 3 | Patient funnel & adherence |

> **Note on scripts 3 & 4:** `generate_pages_ai.py` (5 pages) is the full AI dashboard
> including experiment registry and A/B deep dive. `generate_pages_ai_impact.py` (3 pages) is
> a condensed version covering only AI targeting and MSL partner — write it to the same
> `epikast_ai_dashb` folder to replace pages 1–3. Use one or the other, not both.

---

## Part 1 — Plot glossary

### KPI card / multi-card
A single big number (multi-card = a few stacked rows). **Read:** the headline value for the
current slicer context. A multi-card is for A-vs-B (e.g. Script A vs B). **Watch:** a card
respects every slicer on the page — a "low" number is often just a narrow filter.

### Slicer
The filter controls. **Read:** whatever is selected constrains *every* visual on the page.
Nothing selected = all data.

### Bar / column chart
Categories compared on one measure (bar = horizontal, good for long labels; column = vertical,
good for time/few categories). **Read:** longest bar wins. **Gradient** variant colours bars by
their own value (red→green) so the worst/best jump out. **Multi** variant puts 2–3 measures
side-by-side per category — compare the *cluster shape*, not just one bar.

### Measure-column (no category)
Several *measures* drawn as columns with no shared dimension — e.g. AI vs Non-AI, or the 5
funnel stages. **Read:** left-to-right is a deliberate sequence (a comparison or a funnel that
should step *down*). A stage taller than the one before it = leakage/data issue.

### Combo chart
Columns + a line on a shared axis (usually time), two different scales. **Read:** columns =
volume (e.g. Total Calls), line = a *rate* (e.g. Connect Rate). Look for volume up but rate
down — busy-but-ineffective.

### Line chart
A measure over time. May carry a **reference line** (dashed target) and/or a second comparison
line (e.g. a 4-week moving average). **Read:** trend direction first, then position vs the
target line. Crossing below/above the dashed line is the signal.

### Donut chart
Part-to-whole for one category. **Read:** share of the total (channel mix, outcome mix). Use
for ≤6 slices; it answers "what's the split", not "how much".

### Scatter plot
Two measures as X/Y, optional bubble **size** (3rd measure) and **colour** (category). **Read:**
position = the trade-off (e.g. high volume *and* high quality = top-right = star reps); bubble
size = a third lever; colour = which team/group. Outliers are the story.

### Table / matrix
Rows of detail (table) or a row×column grid with totals (matrix). **Read:** sortable detail;
the matrix cross-tabs two dimensions. This is the "show me the actual numbers" layer.

### Heatmap (conditional-formatted matrix)
A matrix whose **cells are shaded** red→amber→green on the value. **Read:** ignore the numbers
first — scan for colour. Green clusters = where the metric is strong (e.g. best day×time to call),
red = avoid. Rows × columns define the two dimensions.

### Filled map
Regions shaded by a measure. **Read:** geographic concentration — darker = more.

### Key Influencers (AI visual)
Ranks which factors most change a chosen outcome ("When *X*, likelihood of meaningful interaction
increases 1.8×"). **Read:** the left "Top influencers" list is ordered by effect size; click one
to see its supporting bar. It's **correlational**, not causal — a hypothesis generator.

### Decomposition Tree (AI visual)
An interactive drill: start at a metric, expand by any dimension, and it auto-sorts to the
**highest-contributing branch** (or you pick). **Read:** follow the widest/auto-selected path to
find *where* a number comes from (e.g. Meaningful Rate → AIFollowed=Yes → Channel=Video → …).

### R / Python script visual
A fully custom plot rendered by R (ggplot) or Python (matplotlib). Used here for statistical
charts Power BI can't do natively. Read each per its own type (below):
- **Forest plot** — point = effect (uplift) per tactic, horizontal whisker = 95% CI. **Read:**
  if the whisker crosses zero, the effect isn't significant; green = significant.
- **Parallel coordinates** — each line is one call crossing several axes (duration, quality,
  sentiment…), coloured by outcome. **Read:** look for the colour-banding pattern that a
  "meaningful" call traces vs a non-meaningful one.
- **Alluvial / Sankey** — ribbon flows between stages, width = volume. **Read:** follow the fat
  ribbons to see where patients move (PA decision → outcome) and where they leak.
- **Survival curve** — % not-yet-converted over time, one line per group. **Read:** the faster a
  line drops, the faster that segment reaches therapy; gap between lines = segment disparity.
- **Box-and-whisker** — distribution per group: box = middle 50%, line = median, whiskers =
  range, dots = outliers. **Read:** compare medians *and* spread — a team with a tight low box is
  consistently fast; a tall box is erratic.

---

## Part 2 — Dashboards page-by-page

Each row: **plot — binding — what it answers / how to read.**

---

### 1. Client / External  (`epikast_client_dashb`) — 5 pages
Audience: the pharma client. Outcomes & impact, no rep names.

**Engagement Overview**
- 4 KPI cards — Total Calls · Connect Rate · HCPs Contacted · Avg HCP Sentiment — top-line health.
- Combo — `YearMonth` × Total Calls (col) + Connect Rate (line) — volume vs effectiveness over time.
- Donut — Total Calls by `Channel` — phone/email/video mix.
- Bar — Total Calls by `InteractionType` — what kinds of touches.
- Bar — Total Calls by `TherapyArea` — where effort lands.
- Slicers: Quarter · TherapyArea · DrugName.

**HCP Engagement**
- 4 KPI — HCPs Contacted · HCP Reach · Avg Contact Frequency · Avg HCP Sentiment.
- Bar — Total Calls by `Specialty`; Donut — by `Tier`; **Filled map** — by `State` (geographic spread).
- Table — Specialty/Region/Tier × Calls, Connect, Meaningful, Sentiment.
- Slicers: Specialty · Tier · Region.

**Patient Support & Outcomes**
- 4 KPI — Total Cases · Abandonment Rate · Avg Time to Therapy · PA Approval Rate.
- **Measure-column (bottleneck)** — the 5 access stages in days (Rx→Contact→PA submit→decision→
  fulfillment→first dose). *Read the tallest column = the slow stage (usually PA decision).*
- Column(multi) — Adherence 30/60/90-day by `TherapyArea` — does adherence decay over time.
- Donut — Total Cases by `PAStatus`. Table — by InsuranceType.
- Slicers: InsuranceType · DrugName · TherapyArea.

**AI-Driven Insights**
- 4 KPI — AI Lift on Connect · AI Lift on Meaningful · Time Saved Hours · Sentiment.
- **Measure-column (vs)** — AI vs Non-AI, Connect & Meaningful rates side-by-side. *Read: AI bars
  should top their Non-AI pair.*
- Bar — AI Lift on Connect by `TherapyArea`; Bar — MSL Queries by `Topic`. Table — lift by TA.
- Slicers: Quarter · TherapyArea.

**ROI / Business Impact**
- 4 KPI — Total Revenue · Gross Margin % · Avg Cost per Call · Avg Cost per Case.
- Measure-column — Rx from Engaged vs Non-Engaged HCPs + NBRx from Engaged. *Read: engaged > non.*
- Line — Revenue vs Cost over `YearMonth`. Bar — NBRx Rate by `TherapyArea`. Table — monthly P&L.
- Slicers: Quarter · DrugName.

---

### 2. Internal Ops  (`epikast_internal_dashb`) — 7 pages
Audience: Epikast delivery teams. Rep-level, *not* client-facing.

**Executive Summary**
- 5 KPI — Total Calls · Connect · Meaningful · Avg AHT · Schedule Adherence.
- Combo — calls vs connect over time. Column(multi) — Calls/Connected/Meaningful by `Team`. Table by month.
- Slicers: Quarter · Team · TherapyArea.

**Call Outcomes**
- Donut — by `CallOutcome`. Bar — Connect Rate by `Specialty`.
- **Heatmap** — `DayOfWeek` × `CallTimeBucket` → Connect Rate. *Green cells = best time-to-call.*
- Slicers: YearMonth · Team.

**Rep Productivity**
- 4 KPI — Calls/Rep/Day · Connected/Rep/Day · Notes Compliance · Selling Time %.
- **Scatter** — reps: X=Total Calls, Y=Connect Rate, size=Meaningful Interactions, colour=Team.
  *Top-right big bubbles = star reps; bottom-right = busy-but-ineffective.*
- Column(multi) — AI Acceptance/Follow-Up/Notes/Meaningful by `Performance Tier`. Table per rep.
- Slicers: YearMonth · Team · Role.

**Trends**
- 3 Lines — Connect Rate vs its 4-wk avg · Avg AHT (target 10 min) · Schedule Adherence (target 85%).
  *Read each vs its dashed target line.*
- Slicers: Team · TherapyArea.

**Compliance & Quality**
- 5 KPI — Script Deviation · Avg Quality · AE Flag · High-Quality % · Notes Compliance.
- Bar(gradient) — Deviation by rep (*red = worst offenders*). Bar — Quality by rep.
- Line — Deviation vs AE Flag over time. Table per rep.
- Slicers: YearMonth · Team · TherapyArea.

**Channel Mix & Workforce**
- 4 KPI — Phone/Email/Video % · Utilization.
- Donut — Calls by `Channel`. Column(multi) — Connect+Meaningful by `Channel`. Column — Connect by `Tenure Bucket` (ramp). Table.
- Slicers: YearMonth · Team · Role.

**Patient Ops & Drill-Down**
- 5 KPI — Calls Last 7 Days · Calls WoW Change · Open (Active) Cases · Open High-Risk Cases · Avg Time to Therapy.
  *("Last 7 days" is anchored to the latest data date, not today.)*
- **Decomposition Tree** — Meaningful Rate → AIFollowed → Channel → Role → Specialty. *Drill the widest branch.*
- **Measure-column funnel** — Total Cases → First Contacted → PA Approved → Fulfilled → On Therapy.
  *Should step down; a big drop = the leak stage.*
- Bar — Active Cases by `Open Case Age Bucket` (<3d/3-7d/7-14d/14d+). *Long 14d+ bar = aging backlog.*
- **R box-and-whisker** — AHT distribution by `Team`. *Compare medians and spread.*

---

### 3. AI & Experimentation  (`epikast_ai_dashb`) — 5 pages
Audience: AI/MSL product team. Full A/B experiment tracking included.

**AI Call Targeting**
- 4 KPI — AI Acceptance · AI Connect · Non-AI Connect · AI Lift on Connect.
- Measure-column — AI vs Non-AI (Connect & Meaningful). Bar — Lift by `TherapyArea`.
- Line — AI Acceptance over time (target 70%). Table by TA.
- Slicers: Quarter · Tier · TherapyArea.

**MSL Partner Performance**
- 4 KPI — Total Queries · Fully Answered Rate · Avg Time to Answer · Time Saved Hours.
- Bar — Queries by `Topic`. Donut — by `QueryType`. Line — queries/day vs answered rate. Table by topic.
- Slicers: RepName · Quarter · TherapyArea.

**MSL Partner ROI**
- 3 KPI — Queries/MSL/Day · Used-in-Interaction Rate · Avg Satisfaction.
- **Stacked bar** — `RepName` × `AnswerQuality` (queries) — quality mix per rep.
- Bar(gradient) — Time Saved Hours by rep. Table per rep.
- Slicer: Quarter.

**Experiment Registry**
- 4 KPI — Total · Concluded · Win Rate · Running experiments.
- Table — full registry (name, status, KPI, dates, sample size actual/target, observed lift, winner).
- Bar(gradient) — Experiment Lift by experiment. *Read sample-actual vs -target before trusting a lift.*
- Slicers: Status · TherapyArea.

**Script A/B Deep Dive**
- 2 Multi-cards — Script A vs B: Connect, Meaningful.
- 2 Measure-columns — A/B Connect+Meaningful rates · A/B Avg Duration.
- **Matrix** — `Specialty` × the 4 A/B rate measures. *Find specialties where the winner flips.*
- Slicers: YearMonth · TherapyArea · Region.

---

### 4. AI Impact (condensed)  (`epikast_ai_dashb`) — 3 pages
Alternate, lighter version of dashboard 3 — AI targeting and MSL only (no experiment registry).
Write to the same folder as dashboard 3 to replace pages 1–3.

**AI Call Targeting**
- 4 KPI — AI Connect Rate · Non-AI Connect Rate · AI Acceptance Rate · AI Lift on Connect Rate.
- Bar (left) — AI Connect Rate by `TherapyArea`. Bar (right) — AI Lift by `TherapyArea`.
- Line — AI Acceptance Rate over `YearMonth`.
- Slicers: Quarter · Tier · TherapyArea.

**MSL Partner Performance**
- 4 KPI — Total MSL Queries · Fully Answered Rate · Avg Time to Answer Sec · Total Time Saved Hours.
- Bar — Queries by `Topic`. Donut — by `QueryType`. Line — Queries/MSL/Day + Fully Answered Rate.
- Slicers: RepName · Quarter · TherapyArea.

**MSL Partner ROI**
- 3 KPI — MSL Queries Per MSL Per Day · Used in HCP Interaction Rate · Avg MSL Satisfaction.
- **Stacked bar** — `RepName` × `AnswerQuality` — quality mix per MSL.
- Table — MSL scorecard (RepName × Queries, Answered Rate, Time, Time Saved, Interaction Rate, Satisfaction).
- Slicer: Quarter.

---

### 5. Insights Engine  (`epikast_insights_dashb`) — 5 pages
Driver analysis & recommendations. Leans on AI visuals + offline model outputs.

**What Drives Engagement**
- **Key Influencers** — outcome `IsMeaningfulInteraction`, explained by Channel/Script/AIFollowed/
  CallTimeBucket/Specialty/Tier/Team/Tenure. *Left list = strongest levers.*
- **Decomposition Tree** — Meaningful Rate by Channel/Script/AIFollowed/Specialty/Tier.
- Column(multi) — Connect+Meaningful by `Channel`. Measure-column — Script A vs B Meaningful.
- Slicers: Quarter · TherapyArea.

**What Drives Abandonment**
- **Key Influencers** — outcome `IsAbandoned`, explained by InsuranceType/PAStatus/contact delay/
  AgeGroup/TherapyArea/Drug. **Decomp Tree** — Abandonment Rate by PAStatus/Insurance/TA/Drug.
- Bars — Abandonment Rate by `InsuranceType` and by `PAStatus`.
- Slicers: DrugName · TherapyArea.

**Winning Plays (Uplift by Tactic)**
- Bar(gradient) — Avg Uplift by `tactic` (from offline uplift model).
- Table — tactic/segment × uplift, CI low/high, significant, n_treated. *Trust only `significant=TRUE`
  rows whose CI doesn't span 0.*
- Slicers: outcome · segment_type.

**Next-Best-Action**
- Table — segment × recommended_tactic × est_uplift (from `DimNBA`).
- Bar(gradient) — Avg Importance by `feature` (model feature ranking).
- Slicers: outcome · segment_type.

**HCP Sentiment Analysis**
- 3 KPI — Avg Sentiment · Positive % · Negative %.
- Donut — by `SentimentBand`. Line — sentiment over time. Bars — sentiment by Specialty, Channel, Script.
- Slicers: TherapyArea · Channel.

---

### 6. Advanced Analytics  (`epikast_advanced_dashb`) — 5 pages
Native + embedded R + Python. Full spec in `ADVANCED_STORYBOARD.md`.

**What Works Best** — 2 **heatmaps** (Channel×InteractionType → Meaningful Rate; Specialty×Tactic →
Uplift) · Column(multi) AI-adoption lift · winners table. Slicers: outcome · segment_type.

**Progress & Cohorts** — **heatmap** Tenure×Month → Meaningful Rate · slope line · experiment power +
winner tables.

**Forest Plot & Parallel Coords** — **R**: uplift forest plot (point+95% CI, green=significant) ·
parallel-coordinates of winning calls. Slicers: outcome · segment_type.

**Patient Journey & Survival** — **R**: alluvial PA-status→outcome · survival curve time-to-therapy
by insurance. Slicer: DrugName.

**SHAP Explainability** — native mean-|SHAP| bar · **Python** SHAP beeswarm (per-call dots coloured by
feature value). *Bar = which features matter; beeswarm = direction & spread of their effect.*

---

### 7. A/B Test Tracker  (`epikast_ab_dashb`) — 2 pages
Audience: experiment owners. Registry overview + script-level deep dive.

**Experiment Overview**
- 4 KPI — Total Experiments · Concluded Experiments · Win Rate · Running Experiments.
- Table — full experiment registry: ExperimentName, Status, PrimaryKPI, StartDate, EndDate,
  SampleSizeActual, SampleSizeTarget, ObservedLift, Winner.
  *Compare SampleSizeActual vs SampleSizeTarget — underpowered experiments are unreliable.*
- Bar — Avg Observed Lift by `ExperimentName`. *Do not act on lifts from experiments with SampleSizeActual << SampleSizeTarget.*
- Slicers: Status · TherapyArea.

**Script A/B Deep Dive**
- 2 KPI cards — Script A Connect Rate · Script B Connect Rate — headline winner at a glance.
- Bar (left) — Connect Rate by `Script` (A vs B). Bar (right) — Avg Call Duration by `Script`.
- Table — `Specialty` × Script A/B rates (Connect, Meaningful, Avg Duration). *Find specialties where the winner flips.*
- Slicers: YearMonth · TherapyArea · Region.

---

### 8. Smart Ops Overview  (`epikast_ops_dashb`) — 4 pages
Audience: ops managers. Surfaces anomalies and insights, not just numbers.

**Command Center**
- 5 KPI — Total Calls · Connect Rate · Meaningful Interaction Rate · Avg AHT · Schedule Adherence Rate.
- *Anomaly Alerts panel* — Connect Rate WoW Flag (accent red) · Worst Performing Specialty This Week
  (amber) · Connect Rate WoW Change · Worst Specialty Connect Rate.
- *Cross-Dashboard Alerts panel* — Funnel Alert Abandonment Rate · Funnel Alert Worst Stage (purple) ·
  Funnel Alert Worst Stage Cases · AI Lift on Connect Rate.
- *Top/Bottom Movers panel* — Top Rep Connect Rate Improvement (green) · Top Rep Improvement Value ·
  Bottom Rep Connect Rate Decline (red) · Bottom Rep Decline Value.
- *Experiments row* — Running Experiment Progress · Running Experiments count · Win Rate.
- Line — Total Calls + Connect Rate over `YearMonth`. Bar — Total Calls by `Team`.
- Slicers: Quarter · Team · TherapyArea.

**Call Outcomes**
- Donut — Call Outcome distribution by `CallOutcome`.
- Bar — Connect Rate by `Specialty`.
- **Matrix** — `DayOfWeek` × Total Calls, Connect Rate, Meaningful Interaction Rate.
  *Use to find best/worst day for each metric.*
- Slicers: YearMonth · Team.

**Rep Performance**
- 2 KPI — Calls Per Rep Per Day · Notes Compliance Rate.
- *Schedule Insight panel* — Best Day (green) · Worst Day (red) · Best Time Slot Connect Rate ·
  Worst Day Connect Rate.
- **Scatter** — reps: X=Total Calls, Y=Connect Rate, size=Meaningful Interactions.
  *Top-right = high-volume high-quality; bottom-right = busy-but-ineffective.*
- Table — rep scorecard: RepName, Team, Total Calls, Connected, Connect Rate, Meaningful Rate, AHT,
  Schedule Adherence, Notes Compliance.
- Slicers: YearMonth · Team.

**Trends & Optimization**
- Line — Connect Rate + Connect Rate L4W (4-week moving average) over `YearMonth`.
- Line — Avg AHT trend. Line — Schedule Adherence Rate trend.
- 2 KPI — Calls MoM Change · Connect Rate MoM Change.
- Table — monthly summary: YearMonth, Total Calls, Connect Rate.
- Slicers: Team · TherapyArea.

---

### 9. Patient Access Funnel  (`epikast_patient_dashb`) — 3 pages
Audience: patient services teams. Funnel throughput, PA/insurance barriers, adherence decay.

**Funnel Overview**
- 5 KPI — Total Cases · Abandonment Rate · Avg Time to Therapy · PA Approval Rate ·
  Contacted Within 48h Rate.
- **Funnel** — Cases by `PAStatus` (PA status stages). *Widest-to-narrowest = healthy; a flat section = stuck.*
- Bar — Abandoned Cases by `AbandonmentStage` — where patients drop off.
- Table — PAStatus × Total Cases, Abandonment Rate, Avg Time to Therapy, PA Approval Rate.
- Slicers: Quarter · InsuranceType · TherapyArea · DrugName.

**PA and Insurance**
- Bar (left) — PA Approval Rate by `InsuranceType`. *Which plans approve fastest.*
- Bar (right) — Avg PA Decision Delay by `InsuranceType`. *Which plans take longest.*
- Line — PA Approval Rate + PA Denial Rate over `YearMonth`. *Watch for policy-driven shifts.*
- Table — InsuranceType × Cases, PA Approval Rate, PA Denial Rate, Avg PA Decision Delay,
  Abandonment Rate, Avg Time to Therapy.
- Slicers: Quarter · DrugName.

**Adherence**
- 3 KPI — Adherence 30 Day · Adherence 60 Day · Adherence 90 Day. *Expect drop-off; 90-day < 60-day < 30-day.*
- **Matrix** — `TherapyArea` × Adherence 30/60/90 Day. *Find TAs with the steepest decay.*
- Line — Adherence 30 Day + Adherence 90 Day over `YearMonth`. *Trend convergence = worsening adherence.*
- Slicers: InsuranceType · DrugName.

---

### Plot-type tally (across all 9 dashboards)

| Type | Approx. placements |
|------|-------------------|
| KPI / multi-card | ~90 |
| Bar (incl. gradient/stacked) | ~55 |
| Slicer | ~70 |
| Table / matrix | ~30 |
| Column (incl. multi/measure) | ~20 |
| Line / combo | ~25 |
| Donut | ~10 |
| Heatmap / conditional matrix | ~6 |
| Scatter | ~3 |
| Funnel | ~3 |
| Decomposition Tree (AI) | 3 |
| Key Influencers (AI) | 2 |
| Filled map | 1 |
| R visual | 5 |
| Python visual | 1 |

> Counts are placements across pages; title bars, section labels and buttons (chrome) are excluded.
> Totals differ slightly from raw `make_*` calls for that reason.
