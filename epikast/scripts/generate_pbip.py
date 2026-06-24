#!/usr/bin/env python3
"""
Assemble complete, openable PBIP projects from files: the shared Epikast semantic
model + all 5 reports + their pages. After running this you double-click a .pbip in
Power BI Desktop — no manual model build, no Tabular Editor.

Builds under <root> (default epikast/pbip/):
    Epikast.SemanticModel/          (model.bim, via generate_semantic_model)
    <report>.Report/                (.platform, definition.pbir, report.json, pages/)
    <report>.pbip                   (one per report; all share the one model)

Usage:
    python epikast/scripts/generate_pbip.py
    python epikast/scripts/generate_pbip.py --root="C:/Users/me/Documents/epikast_pbip"

First open: set the SourceFolder parameter to your epikast/data folder (Transform data →
Manage parameters), then Refresh. See BUILD.md.
"""

import json
import os
import subprocess
import sys

import generate_semantic_model as gsm

HERE = os.path.dirname(os.path.abspath(__file__))

REPORTS = [
    ("epikast_client_dashb",   "generate_pages_client.py"),
    ("epikast_internal_dashb", "generate_pages_internal.py"),
    ("epikast_ai_dashb",       "generate_pages_ai.py"),
    ("epikast_insights_dashb", "generate_pages_insights.py"),
    ("epikast_advanced_dashb", "generate_pages_advanced.py"),
]
MODEL = "Epikast.SemanticModel"


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def scaffold_report(root, report):
    rdir = os.path.join(root, f"{report}.Report")
    # .platform
    write_json(os.path.join(rdir, ".platform"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": report},
        "config": {"version": "2.0", "logicalId": gsm._guid(f"{report}.Report")},
    })
    # definition.pbir → points the report at the shared semantic model by relative path
    write_json(os.path.join(rdir, "definition.pbir"), {
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{MODEL}"}},
    })
    # report.json (PBIR report-level)
    write_json(os.path.join(rdir, "definition", "report.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.2.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "CY26SU02",
                "reportVersionAtImport": {
                    "visual": "2.6.0",
                    "report": "3.1.0",
                    "page": "2.3.0"
                },
                "type": "SharedResources"
            }
        },
        "resourcePackages": [
            {
                "name": "SharedResources",
                "type": "SharedResources",
                "items": [
                    {
                        "name": "CY26SU02",
                        "path": "BaseThemes/CY26SU02.json",
                        "type": "BaseTheme"
                    }
                ]
            }
        ],
        "settings": {
            "useStylableVisualContainerHeader": True,
            "exportDataMode": "AllowSummarized",
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True,
            "useDefaultAggregateDisplayName": True
        }
    })
    # version.json (required by Power BI Desktop June 2026+)
    write_json(os.path.join(rdir, "definition", "version.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "2.0.0",
    })
    # .pbip wrapper
    write_json(os.path.join(root, f"{report}.pbip"), {
        "version": "1.0",
        "artifacts": [{"report": {"path": f"{report}.Report"}}],
        "settings": {"enableAutoRecovery": True},
    })
    return os.path.join(rdir, "definition", "pages")


def main():
    root = None
    data = None
    for a in sys.argv[1:]:
        if a.startswith("--root="):
            root = a.split("=", 1)[1]
        elif a.startswith("--data="):
            data = a.split("=", 1)[1]
    if not root:
        root = os.path.normpath(os.path.join(HERE, "..", "pbip"))
    os.makedirs(root, exist_ok=True)

    # 1) shared semantic model
    print("== Semantic model ==")
    gsm_args = [sys.executable, os.path.join(HERE, "generate_semantic_model.py"), f"--root={root}"]
    if data:
        gsm_args.append(f"--data={data}")
    subprocess.run(gsm_args, check=True)

    # 2) each report: scaffold + generate pages into it
    print("\n== Reports ==")
    for report, gen in REPORTS:
        pages_dir = scaffold_report(root, report)
        r = subprocess.run(
            [sys.executable, os.path.join(HERE, gen), f"--pages={pages_dir}"],
            stdout=subprocess.DEVNULL,
        )
        status = "ok" if r.returncode == 0 else f"FAILED({r.returncode})"
        print(f"  {report:26} {status}  -> {report}.pbip")

    print(f"\nDONE. Open any <report>.pbip in Power BI Desktop (Windows).")
    print(f"Root: {root}")
    print("First open: set SourceFolder parameter to your epikast/data path, then Refresh.")


if __name__ == "__main__":
    main()
