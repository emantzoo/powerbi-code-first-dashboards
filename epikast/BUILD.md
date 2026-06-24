# Building the Epikast Power BI Dashboards

This repo is **code-first**: it stores the *recipe* (data, measures, Python page
generators), not the baked `.pbix`. The `.Report/` and `.SemanticModel/` folders are
`.gitignore`d on purpose. You build the model + project shell once in Power BI Desktop,
then the Python generators inject the report pages.

```
CSVs + DAX (this repo)  ──Power BI Desktop──▶  semantic model + .pbip shell
                                                        │
                         scripts/*.py ──inject pages──▶ .Report/definition/pages/
                                                        │
                                          reopen .pbip ▶ finished dashboard
```

## ⚡ Quickstart — fully file-generated PBIP (no manual model build)
If you just want working `.pbip` files with the model already inside, skip Phases 4–5 and run:
```bash
python epikast/scripts/generate_pbip.py --root="C:/Users/me/Documents/epikast_pbip"
```
This writes a shared `Epikast.SemanticModel` (15 tables, 139 measures, 6 calc columns, 15
relationships, all from `Epikast_Dashboard_Prompts.md`) **plus** all 5 reports and their pages.
Then in Power BI Desktop:
1. Open any `<report>.pbip`.
2. **Transform data → Manage parameters → `SourceFolder`** → set it to your `epikast/data`
   folder (keep the trailing `\`), then **Close & Apply / Refresh**.
3. Done — the model loads from the CSVs and every page renders.

> Caveat: this generates the PBIP/TMSL project from scratch and hasn't been round-tripped
> through Power BI Desktop here, so the first open may need a small fix (a metadata version
> or theme name). If Desktop complains, paste me the error and I'll patch the generator. The
> rock-solid fallback is the manual Phases below (Tabular Editor for the model).

The rest of this doc is the **manual / step-by-step** path.

---

## 0. Prerequisites
- **Power BI Desktop (Windows).** `.pbip` / PBIR is Windows-only — there is no Mac build.
- **Python 3** for the generators (standard library only; no pip installs needed).
- **Advanced report only:** R with `ggplot2, GGally, ggalluvial, survival, survminer`,
  and Python with `matplotlib`, configured in Power BI Desktop (Options → R/Python scripting).
  Model training needs `pandas, scikit-learn, lightgbm, shap`.

## 1. Get the repo locally
```bash
git clone <your-repo-url>
cd powerbi-code-first-dashboards
git checkout claude/clever-clarke-YNu4h
```

## 2. (Optional) Generate the ML output tables
`FactUplift.csv` is already in `epikast/data/`. To (re)create it and the SHAP tables:
```bash
python epikast/scripts/train_uplift.py     # → FactUplift.csv
python epikast/scripts/train_shap.py       # → ShapImportance.csv, ShapBeeswarm.csv
```

## 3. One-time Power BI Desktop setup
**Options → Preview features** → enable:
- ✅ **Power BI Project (.pbip) save option**
- ✅ **Store reports using enhanced metadata format (PBIR)**

Restart Power BI Desktop.

## 4. Build the shared semantic model (once)
All 5 reports run on **one** model (`Epikast_Dashboard_Prompts.md`).
1. **Get Data → Text/CSV** → load all CSVs from `epikast/data/` (14 dims/facts +
   `FactUplift`, and `ShapImportance`/`ShapBeeswarm`/`DimNBA`/`FeatureImportance` for the
   Insights/Advanced reports).
2. **Model view → relationships** per *Phase 1A* in `Epikast_Dashboard_Prompts.md`
   (Date is **active** only on `FactHCPCalls`; the patient/Rx/financial date links are
   **inactive** and activated per-measure via `USERELATIONSHIP`).
3. Create a **`_Measures`** table and add the **139 measures** + the **6 calculated columns**.
   **Fast path (recommended):** don't hand-type them — use the auto-generated Tabular Editor
   script:
   ```bash
   python epikast/scripts/generate_tabular_script.py   # → epikast/build_model.csx
   ```
   Install **Tabular Editor 2** (free), open it *connected to your model* (Power BI Desktop →
   External Tools → Tabular Editor, or open the .pbip's model), go to the **Advanced Scripting**
   tab, open `build_model.csx`, press **Run (F5)**, then **Save**. This creates all 139 measures
   (foldered by theme), the 6 calc columns, and the 15 relationships in one shot. Reopen in
   Power BI Desktop. (`build_model.csx` is regenerated from `Epikast_Dashboard_Prompts.md`, so
   edit the measures there and re-run the generator — never hand-edit the .csx.)
   **Manual path:** paste the measures/columns from `Epikast_Dashboard_Prompts.md` by hand.
4. **Save As → Power BI project (.pbip)** for the first report, e.g. name it
   `epikast_internal_dashb`. This creates the folder structure the generators write into:
   ```
   epikast_internal_dashb.Report/definition/pages/
   ```
   For the other 4 reports, create thin report projects with a **live connection** to this
   same model (or duplicate the .pbip) so you don't rebuild the model 5×.

## 5. Generate the pages
Close Power BI Desktop first (the generators rewrite the `pages/` folder).

The generators no longer hard-code a path — they resolve the target folder in this order:
| Priority | How | Result |
|---|---|---|
| 1 | `--pages=<full pages path>` | exact folder, used as-is |
| 2 | `--root=<dir>` or `EPIKAST_PBI_ROOT=<dir>` | `<dir>/<report>.Report/definition/pages` |
| 3 | nothing set | `epikast/build/…` — **dry-run sandbox** (validates JSON; not an openable .pbip) |

**Build all 5 at once** (point `--root` at the folder that holds your `.Report` dirs):
```bash
python epikast/scripts/build_all.py --root="C:/Users/me/Documents/powerbi-code-first-dashboards/epikast"
```
**Or one report:**
```bash
python epikast/scripts/generate_pages_internal.py --root="C:/…/epikast"
# or target an exact folder:
python epikast/scripts/generate_pages_internal.py --pages="C:/…/epikast_internal_dashb.Report/definition/pages"
```
**Dry run** (no Power BI needed — just confirms the JSON generates) writes to `epikast/build/`:
```bash
python epikast/scripts/build_all.py
```

## 6. Open and finish
1. Reopen each `.pbip` in Power BI Desktop → all pages render (Internal Ops = 7, the rest = 5).
2. **AI visuals** (Key Influencers, Decomposition Tree): if a role binding didn't take on
   your PBI version, drag the listed fields into Analyze / Explain-by (≈30 sec each).
3. **R / Python visuals** (Advanced report + Ops box-plot): enable scripting and click
   "Run" / allow the script the first time.
4. Eyeball the four less-common visuals (combo, multi-card, heatmap, reference lines) and
   tweak formatting if anything renders oddly.

## Report → generator map
| Report folder | Generator | Pages |
|---|---|---|
| `epikast_client_dashb`   | `generate_pages_client.py`   | 5 |
| `epikast_internal_dashb` | `generate_pages_internal.py` | 7 |
| `epikast_ai_dashb`       | `generate_pages_ai.py`       | 5 |
| `epikast_insights_dashb` | `generate_pages_insights.py` | 5 |
| `epikast_advanced_dashb` | `generate_pages_advanced.py` | 5 |

See `DASHBOARD_INDEX.md` for every plot and how to read it, and `ADVANCED_STORYBOARD.md`
for the Advanced report's wireframes.
