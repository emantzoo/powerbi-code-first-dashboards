"""
workflow/pbip_builder.py — PBIP project scaffolder.

Creates all the boilerplate files needed for an openable .pbip project under a
given root directory.  Works with Power BI Desktop June 2026+ (report.json schema
3.2.0, version.json 2.0.0, CY26SU02 base theme).

Usage from an orchestrator script (e.g. generate_pbip.py):
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "workflow"))
    import pbip_builder as pb

    pages_dir = pb.scaffold_report(root, "my_report_name", model_name="MyModel.SemanticModel")
    # → writes <root>/my_report_name.Report/{.platform, definition.pbir,
    #           definition/report.json, definition/version.json}
    # → writes <root>/my_report_name.pbip
    # → returns path to <root>/my_report_name.Report/definition/pages  (not created yet)

Functions:
    scaffold_report(root, report, model_name=DEFAULT_MODEL) → pages_dir
    write_json(path, obj)           — utility: makedirs + json.dump
    _guid(seed)                     — deterministic GUID from an MD5 seed

Pure stdlib. No external dependencies.
"""

import hashlib
import json
import os

DEFAULT_MODEL = "SemanticModel"

REPORT_JSON_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/"
    "item/report/definition/report/3.2.0/schema.json"
)
VERSION_JSON_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/"
    "item/report/definition/versionMetadata/1.0.0/schema.json"
)
PLATFORM_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/"
    "gitIntegration/platformProperties/2.0.0/schema.json"
)


def _guid(seed):
    """Return a deterministic GUID string (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
    derived from the MD5 of *seed*.  Identical to the helper used inside
    generate_semantic_model.py so that lineageTags stay stable across regenerations.
    """
    h = hashlib.md5(seed.encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def write_json(path, obj):
    """Write *obj* as indented JSON to *path*, creating parent directories."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def scaffold_report(root, report, model_name=None):
    """Create all scaffold files for one report inside *root*.

    Parameters
    ----------
    root : str
        Directory that will contain the .Report folder and the .pbip file.
    report : str
        Report name, e.g. "my_dashboard".  Must not contain path separators.
    model_name : str, optional
        Folder name of the shared semantic model, e.g. "MyProject.SemanticModel".
        Defaults to DEFAULT_MODEL ("SemanticModel").

    Returns
    -------
    str
        Absolute path to <root>/<report>.Report/definition/pages  (not yet created).
        Pass this to pbir_lib.BASE or the --pages argument of a page-generator script.
    """
    if model_name is None:
        model_name = DEFAULT_MODEL

    rdir = os.path.join(root, f"{report}.Report")

    # .platform
    write_json(os.path.join(rdir, ".platform"), {
        "$schema": PLATFORM_SCHEMA,
        "metadata": {"type": "Report", "displayName": report},
        "config": {"version": "2.0", "logicalId": _guid(f"{report}.Report")},
    })

    # definition.pbir  — points the report at the shared model by relative path
    write_json(os.path.join(rdir, "definition.pbir"), {
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{model_name}"}},
    })

    # definition/report.json  — June 2026 schema with CY26SU02 base theme
    write_json(os.path.join(rdir, "definition", "report.json"), {
        "$schema": REPORT_JSON_SCHEMA,
        "themeCollection": {
            "baseTheme": {
                "name": "CY26SU02",
                "reportVersionAtImport": {
                    "visual": "2.6.0",
                    "report": "3.1.0",
                    "page": "2.3.0",
                },
                "type": "SharedResources",
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
                        "type": "BaseTheme",
                    }
                ],
            }
        ],
        "settings": {
            "useStylableVisualContainerHeader": True,
            "exportDataMode": "AllowSummarized",
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True,
            "useDefaultAggregateDisplayName": True,
        },
    })

    # definition/version.json  — required by Power BI Desktop June 2026+
    write_json(os.path.join(rdir, "definition", "version.json"), {
        "$schema": VERSION_JSON_SCHEMA,
        "version": "2.0.0",
    })

    # <report>.pbip wrapper
    write_json(os.path.join(root, f"{report}.pbip"), {
        "version": "1.0",
        "artifacts": [{"report": {"path": f"{report}.Report"}}],
        "settings": {"enableAutoRecovery": True},
    })

    return os.path.join(rdir, "definition", "pages")
