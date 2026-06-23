# Advanced Analytics Report — Storyboard & Measure Spec

Wireframes, the business question each page answers, and the **exact** field/measure binding
for every visual in `scripts/generate_pages_advanced.py`. Canvas is 1280×720.

**Build order:** `python scripts/train_uplift.py` → `python scripts/train_shap.py` →
`python scripts/generate_pages_advanced.py`. R pages need R + ggplot2/GGally/ggalluvial/
survival/survminer; the SHAP beeswarm needs Python + matplotlib in Power BI Desktop.

Legend: 🟩 native visual · 🟦 embedded R · 🟪 embedded Python.

---

## Page 1 — What Works Best (Multivariate) 🟩
**Q: Which tactic × context combinations move the needle most?**

```
┌───────────────────────────────────────────────[title]───────────────────────────┐
│                                              [slicer outcome] [slicer segment_type]│
├──────────────────────────────────┬───────────────────────────────────────────────┤
│ Interaction heatmap              │ Uplift heatmap                                 │
│ Channel × InteractionType        │ Specialty × Tactic                             │
│   → Meaningful Interaction Rate  │   → Avg Uplift                                 │
├──────────────────────────────────┼───────────────────────────────────────────────┤
│ AI-adoption lift (Low/Med/High)  │ Significant winners table                      │
│   Connect Rate + Meaningful Rate │   tactic, segment_value, uplift, CI, sig       │
└──────────────────────────────────┴───────────────────────────────────────────────┘
```
| Visual | Type | Rows / Category | Columns / Series | Value |
|--------|------|-----------------|------------------|-------|
| Interaction heatmap | matrix heatmap | `FactHCPCalls[Channel]` | `FactHCPCalls[InteractionType]` | `[Meaningful Interaction Rate]` |
| Uplift heatmap | matrix heatmap | `FactUplift[segment_value]` | `FactUplift[tactic]` | `[Avg Uplift]` |
| AI-adoption lift | clustered column | `DimRep[AI Adoption Band]` | — | `[Connect Rate]`, `[Meaningful Interaction Rate]` |
| Winners table | table | `FactUplift[tactic]`, `[segment_value]` | — | cols: `uplift`, `ci_low`, `ci_high`, `significant` |
| Slicers | — | `FactUplift[outcome]`, `FactUplift[segment_type]` | | |

---

## Page 2 — Progress & Cohorts 🟩
**Q: Are we improving over time, and do newer cohorts ramp?**

```
┌───────────────────────────────────────────────[title]───────────────────────────┐
│ Cohort ramp heatmap                                  │ Slope: Meaningful + Connect │
│ Tenure Bucket × YearMonth → Meaningful Rate          │   over YearMonth             │
├──────────────────────────────────────────────────────┴──────────────────────────┤
│ Experiment power table                          │ Winner tracker table             │
│ name, KPI, target n, actual n, conf, status     │ name, winner, end, lift, status  │
└─────────────────────────────────────────────────┴──────────────────────────────┘
```
| Visual | Type | Binding |
|--------|------|---------|
| Cohort ramp heatmap | matrix heatmap | rows `DimRep[Tenure Bucket]` × cols `DimCalendar[YearMonth]` → `[Meaningful Interaction Rate]` |
| Slope | line (dual) | axis `DimCalendar[YearMonth]`; `[Meaningful Interaction Rate]` + `[Connect Rate]` |
| Power table | table | `DimExperiment`: ExperimentName, PrimaryKPI, SampleSizeTarget, SampleSizeActual, ConfidenceLevel, Status |
| Winner tracker | table | `DimExperiment`: ExperimentName, Winner, EndDate, ObservedLift, Status |

---

## Page 3 — Forest Plot & Parallel Coordinates 🟦
**Q: Which tactics are statistically real, and what does a winning call look like?**

```
┌───────────────────────────────────────────────[title]──────[slicer out][slicer seg]┐
│ R: Uplift forest plot (95% CI)        │ R: Parallel coordinates of winning calls    │
│   point + error bar per tactic,       │   Duration · CallQuality · Sentiment ·       │
│   green = significant                 │   AIFollowed · ScriptDeviation, colored by   │
│                                       │   Meaningful vs Not                          │
└───────────────────────────────────────┴──────────────────────────────────────────┘
```
| Visual | Engine | Bound fields (→ R `dataset`) | Script |
|--------|--------|------------------------------|--------|
| Forest plot | R / ggplot2 | `FactUplift`: outcome, segment_type, segment_value, tactic, uplift, ci_low, ci_high, significant | `geom_pointrange` sorted by uplift |
| Parallel coords | R / GGally | `FactHCPCalls`: CallID, DurationMinutes, CallQualityScore, HCPSentimentScore, AIFollowed, ScriptDeviation, IsMeaningfulInteraction | `ggparcoord(groupColumn=Meaningful)` (samples 600 rows) |

> CallID is bound to stop Power BI de-duplicating rows. Use the slicers to focus the forest
> plot on one outcome × segment_type.

---

## Page 4 — Patient Journey & Survival 🟦
**Q: Where do patients flow, and how fast do segments reach therapy?**

```
┌───────────────────────────────────────────────[title]──────────────[slicer DrugName]┐
│ R: Alluvial — PA Status → Case Outcome  │ R: Survival curves — time-to-therapy        │
│   ribbon widths = patient counts        │   by InsuranceType, with CI bands           │
└─────────────────────────────────────────┴──────────────────────────────────────────┘
```
| Visual | Engine | Bound fields | Notes |
|--------|--------|--------------|-------|
| Alluvial journey | R / ggalluvial | `FactPatientCases`: CaseID, PAStatus, CaseStatus | counts flows PA decision → outcome |
| Survival curve | R / survminer | `FactPatientCases`: CaseID, TimeToTherapyDays, IsAbandoned, InsuranceType | event = started therapy; abandoned = censored at 60d |

---

## Page 5 — SHAP Explainability 🟩🟪
**Q: Which call features drive a meaningful interaction, and in which direction?**

```
┌───────────────────────────────────────────────[title]───────────────────────────┐
│ Native: mean|SHAP| by feature  │ Python: SHAP beeswarm                           │
│   bar, descending              │   per-call SHAP dots, colored by feature value  │
└────────────────────────────────┴──────────────────────────────────────────────┘
```
| Visual | Engine | Binding |
|--------|--------|---------|
| Mean \|SHAP\| bar | native | `ShapImportance[feature]` → `[Avg Shap Importance]` |
| Beeswarm | Python / matplotlib | `ShapBeeswarm`: feature, shap_value, feature_value_norm |

> Both tables come from `scripts/train_shap.py` (LightGBM on `IsMeaningfulInteraction`,
> features: AIFollowed, ScriptDeviation, DurationMinutes, CallQualityScore,
> HCPSentimentScore, ScriptIsA, ChannelVideo, ChannelEmail). It also saves a static
> `images/epikast_shap_beeswarm.png` if you prefer an image over the live Python visual.

---

## Measures / columns this report relies on
Existing measures: `Meaningful Interaction Rate`, `Connect Rate`, `Avg Uplift`,
`Avg Shap Importance`. Added for this report:
- `DimRep[AI Adoption Band]` (calc column) — Low/Med/High by a rep's AIFollowed share.
- `Avg Shap Importance` (measure) — `AVERAGE(ShapImportance[mean_abs_shap])`.

Model-output tables (disconnected): `FactUplift`, `ShapImportance`, `ShapBeeswarm`
(plus `DimNBA`, `FeatureImportance` from the Insights Engine report).

## Visual-by-visual feasibility recap
| Plot | Path | Caveat |
|------|------|--------|
| Interaction / uplift / cohort heatmaps | native matrix | color scale may need a manual tweak |
| AI-adoption lift, slope, tables | native | none |
| Forest plot, parallel coords, alluvial, survival | embedded R | needs R + packages in PBI Desktop; static image |
| SHAP beeswarm | embedded Python | needs Python + matplotlib; run `train_shap.py` first |
