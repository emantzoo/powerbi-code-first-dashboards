# Epikast Build Flow

How one command (`generate_pbip.py`) produces five openable Power BI reports.

```mermaid
flowchart TD
    MD([Epikast_Dashboard_Prompts.md])

    subgraph MODEL["① Semantic Model"]
        TSP[generate_tabular_script.py]
        GSM[generate_semantic_model.py]
        BIM([Epikast.SemanticModel / model.bim])
        MD --> TSP --> GSM --> BIM
    end

    subgraph ORCH["② Orchestrator"]
        GPBIP[generate_pbip.py]
    end

    MODEL --> ORCH

    subgraph SCAFFOLD["③ Report Scaffold x5"]
        PBB[workflow/pbip_builder.py]
        FILES([".platform · definition.pbir\nreport.json · version.json · .pbip"])
        PBB --> FILES
    end

    subgraph PAGES["④ Page Generation x5"]
        GP1[generate_pages_client.py]
        GP2[generate_pages_internal.py]
        GP3[generate_pages_ai.py]
        GP4[generate_pages_insights.py]
        GP5[generate_pages_advanced.py]
        SHIM[epikast/scripts/pbir_lib.py - shim]
        LIB[workflow/pbir_lib.py\n40+ make_* visual builders]
        JSON([pages JSON files])

        GP1 & GP2 & GP3 & GP4 & GP5 --> SHIM --> LIB --> JSON
    end

    ORCH --> SCAFFOLD
    ORCH --> PAGES

    BIM & FILES & JSON --> PBIP

    PBIP(["epikast/pbip/ — 5 x .pbip\nOpen in Power BI Desktop"])
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
