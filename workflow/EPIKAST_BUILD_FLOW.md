# Epikast Build Flow

How one command (`generate_pbip.py`) produces five openable Power BI reports.

```mermaid
flowchart TD
    MD([Epikast_Dashboard_Prompts.md\nTables · DAX · Visual layout spec])

    subgraph MODEL["① Semantic Model"]
        TSP[generate_tabular_script.py\nParses DAX measures from .md]
        GSM[generate_semantic_model.py\nBuilds model.bim]
        BIM([Epikast.SemanticModel/model.bim\nTables · M partitions · Relationships\nDAX measures · SourceFolder param])
        MD --> TSP --> GSM --> BIM
    end

    subgraph ORCH["② Orchestrator"]
        GPBIP[generate_pbip.py\npython epikast/scripts/generate_pbip.py]
    end

    MODEL --> ORCH

    subgraph SCAFFOLD["③ Report Scaffold  ×5"]
        PBB[workflow/pbip_builder.py\nscaffold_report\(\)]
        FILES([".platform\ndefinition.pbir\ndefinition/report.json  ← schema 3.2.0 · CY26SU02\ndefinition/version.json\n&lt;report&gt;.pbip"])
        PBB --> FILES
    end

    subgraph PAGES["④ Page Generation  ×5"]
        GP1[generate_pages_client.py]
        GP2[generate_pages_internal.py]
        GP3[generate_pages_ai.py]
        GP4[generate_pages_insights.py]
        GP5[generate_pages_advanced.py]
        SHIM[epikast/scripts/pbir_lib.py\nthin shim]
        LIB[workflow/pbir_lib.py\nmake_card · make_clustered_bar\nmake_line_chart · make_matrix\nwrite_page · write_pages_json\n... 40+ make_* functions]
        JSON([pages/*/page.json\npages/*/visuals/*/visual.json\npages/pages.json])

        GP1 & GP2 & GP3 & GP4 & GP5 --> SHIM --> LIB --> JSON
    end

    ORCH --> SCAFFOLD
    ORCH --> PAGES

    BIM & FILES & JSON --> PBIP

    PBIP(["✅ epikast/pbip/\n  Epikast.SemanticModel/model.bim\n  epikast_client_dashb.pbip\n  epikast_internal_dashb.pbip\n  epikast_ai_dashb.pbip\n  epikast_insights_dashb.pbip\n  epikast_advanced_dashb.pbip\n\nDouble-click any .pbip in Power BI Desktop"])
```

## File roles

| File | Role |
|------|------|
| `Epikast_Dashboard_Prompts.md` | Source of truth — tables, DAX, visual layout |
| `generate_tabular_script.py` | Parses DAX measure blocks from the prompt file |
| `generate_semantic_model.py` | Writes `model.bim` (TMSL JSON) |
| `generate_pbip.py` | **Entry point** — run this to build everything |
| `workflow/pbip_builder.py` | Writes per-report scaffold files (June 2026 compatible) |
| `generate_pages_client.py` | Page layout — client-facing report |
| `generate_pages_internal.py` | Page layout — internal ops report |
| `generate_pages_ai.py` | Page layout — AI effectiveness report |
| `generate_pages_insights.py` | Page layout — insights report |
| `generate_pages_advanced.py` | Page layout — advanced analytics report |
| `epikast/scripts/pbir_lib.py` | Shim — forwards all calls to `workflow/pbir_lib.py` |
| `workflow/pbir_lib.py` | All `make_*` visual builders + `write_page` |

## To rebuild

```bash
# from repo root
python epikast/scripts/generate_pbip.py

# optional: point output at a specific folder
python epikast/scripts/generate_pbip.py --root="C:/Users/me/Documents/epikast_pbip"
```

Then open any `.pbip` in Power BI Desktop (Windows, June 2026+).
On first open: **Transform data → Manage parameters → SourceFolder** → set to your `epikast/data/` path → **Refresh**.
