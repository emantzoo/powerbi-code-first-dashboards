# Order Data — Privacy & Disclosure-Risk Assessment — Power BI Build Prompts

Use these prompts in order. Each is a copy-paste block for Claude Desktop (Cowork or Code tab) or a manual checklist for Power BI Desktop.

> **About the data:** this dashboard uses **schema-level metadata only** — no real records, identifiers, or values. `DimField.csv` is a per-field risk register (disclosure-control class, re-identification risk level, recommended statistical-disclosure-control method, information-loss metric, sparsity). `DimScenario.csv` is an SDC scenario ladder (successive anonymisation configurations) with indicative re-identification-risk and information-loss (utility-loss) indices, for visualising the privacy-vs-utility trade-off.

The data CSVs are in: `C:\Users\emant\Documents\powerbi-code-first-dashboards\disclosure_risk\data`

---

## PHASE 0 — Load Data

```
Connect to my open Power BI Desktop file.

Load these CSVs from C:\Users\emant\Documents\powerbi-code-first-dashboards\disclosure_risk\data:
- DimField.csv     (52 rows — field risk register)
- DimScenario.csv  (15 rows — SDC scenario ladder)

Types for DimField:
- field, schema_category, sdc_class, risk_level, sdc_method, info_loss_metric,
  research_interest, needs_sdc: Text
- risk_weight, risk_rank, pct_empty: Whole Number

Types for DimScenario:
- scenario_id, level, time_generalization, price_rounding, quantity_topcoding,
  description: Text
- risk_index, utility_loss, protection_gain: Whole Number

No relationship is needed between the two tables — they are independent reference tables.

In the model view, set DimField[risk_level] → Sort by column → risk_rank
(so Low / Medium / High / Very High sort in severity order).

Refresh and confirm row counts.
```

---

## PHASE 1 — DAX Measures (Field Register)

```
Create a _Measures table:
_Measures = {1}

Add these measures:

Field Count = COUNTROWS(DimField)

Direct Identifiers = CALCULATE(COUNTROWS(DimField), DimField[sdc_class] = "Direct identifier")
Quasi Identifiers  = CALCULATE(COUNTROWS(DimField), DimField[sdc_class] = "Quasi-identifier")
Sensitive Fields   = CALCULATE(COUNTROWS(DimField), DimField[sdc_class] = "Sensitive")

High Risk Fields   = CALCULATE(COUNTROWS(DimField), DimField[risk_rank] >= 3)
Fields Needing SDC = CALCULATE(COUNTROWS(DimField), DimField[needs_sdc] = "Yes")
Sparse Fields      = CALCULATE(COUNTROWS(DimField), DimField[pct_empty] >= 90)

Avg Risk Weight = AVERAGE(DimField[risk_weight])
```

---

## PHASE 2 — DAX Measures (Scenario Ladder)

```
Add these measures to _Measures:

Scenario Count = COUNTROWS(DimScenario)

Risk Index      = AVERAGE(DimScenario[risk_index])
Utility Loss    = AVERAGE(DimScenario[utility_loss])
Protection Gain = AVERAGE(DimScenario[protection_gain])

Lowest Risk Index    = MIN(DimScenario[risk_index])
Highest Utility Loss = MAX(DimScenario[utility_loss])
Avg Protection Gain  = AVERAGE(DimScenario[protection_gain])
```

> `Risk Index`, `Utility Loss`, `Protection Gain` are referenced verbatim by `generate_pages.py`.
> Used on the privacy-utility scatter (X = Utility Loss, Y = Risk Index, size = Protection Gain),
> the trade-off line, and the scenario table.

---

## PHASE 3 — Save

```
Save the file as a Power BI Project (.pbip) named "disclosure_risk_dash" in:
C:\Users\emant\Documents\powerbi-code-first-dashboards\disclosure_risk\

Then close Power BI Desktop completely.
```

---

## After Coworker completes all phases:

1. Close Power BI Desktop
2. Update the `BASE` path at the top of `scripts/generate_pages.py`
3. Run: `python disclosure_risk/scripts/generate_pages.py`
4. Reopen `disclosure_risk_dash.pbip` — 3 pages with all visuals + backgrounds appear
5. Apply theme: View > Themes > Browse > `themes/code-first-dashboard.json`
6. Configure button navigation (Format > Action > Page navigation)

No R required — pure DAX.

---

## Pages

| Page | Purpose | Key visuals |
|------|---------|-------------|
| **Field Risk Register** | Which fields carry disclosure risk, and how to treat them | Cards (fields, direct identifiers, high-risk, needing SDC), fields-by-risk-level bar, disclosure-class donut, SDC-method treemap, register table |
| **SDC Scenario Ladder** | The privacy-vs-utility trade-off across anonymisation configurations | Trade-off scatter (risk vs utility per scenario), risk/utility trade-off line, utility-loss bar, scenario detail table |
| **Risk Heatmap & Deep-dive** | Where risk concentrates by class and severity | Disclosure-class × risk-level heatmap matrix, fields-by-SDC-method bar, avg-risk-weight by schema category, high-risk field table |

---

## Notes

- The re-identification-risk and utility-loss indices on the scenario ladder are **indicative /
  illustrative** values that demonstrate the expected privacy-utility trade-off shape (more
  aggressive SDC → lower risk, higher information loss). Replace them with measured values from a
  real risk-assessment run when available — the visuals will reflect them automatically.
- Risk levels, disclosure-control classes, SDC methods and information-loss metrics in `DimField`
  follow standard statistical-disclosure-control practice applied to the order-data schema.
- This dashboard pairs with **Market Orders** (the operational surveillance dashboard) to tell a
  complete story: what the data shows, and how to share it safely.
