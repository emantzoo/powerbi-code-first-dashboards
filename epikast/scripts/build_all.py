#!/usr/bin/env python3
"""
Build all 5 Epikast report page-sets in one go.

This injects the PBIR *pages* into report folders. It does NOT create the .pbip
project, report shell, or semantic model — build those once in Power BI Desktop
(see epikast/BUILD.md), then run this to (re)generate every report's pages.

Target folder resolution (same as each generator's pb.resolve_pages_base):
    --root=<dir>           or  env EPIKAST_PBI_ROOT=<dir>
        → writes <dir>/<report>.Report/definition/pages for each report
    (nothing set)          → epikast/build/  (dry-run sandbox; validates JSON,
                             not an openable .pbip on its own)

Examples:
    python scripts/build_all.py
    python scripts/build_all.py --root="C:/Users/me/Documents/powerbi-code-first-dashboards/epikast"
    EPIKAST_PBI_ROOT="/path/to/epikast" python scripts/build_all.py
"""

import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

GENERATORS = [
    ("Client / External",  "generate_pages_client.py"),
    ("Internal Ops",       "generate_pages_internal.py"),
    ("AI & Experiment",    "generate_pages_ai.py"),
    ("Insights Engine",    "generate_pages_insights.py"),
    ("Advanced Analytics", "generate_pages_advanced.py"),
]


def main():
    passthrough = sys.argv[1:]  # forward --root=/--pages= to each generator
    root = None
    for a in passthrough:
        if a.startswith("--root="):
            root = a.split("=", 1)[1]
    root = root or os.environ.get("EPIKAST_PBI_ROOT")
    where = root or os.path.normpath(os.path.join(HERE, "..", "build")) + "  (dry-run sandbox)"
    print(f"Building 5 Epikast reports into: {where}\n")

    failures = []
    for label, script in GENERATORS:
        path = os.path.join(HERE, script)
        print(f"── {label}  ({script})")
        result = subprocess.run([sys.executable, path, *passthrough], env=os.environ)
        if result.returncode != 0:
            failures.append(label)
            print(f"   !! FAILED ({result.returncode})\n")
        else:
            print()

    print("=" * 50)
    if failures:
        print(f"DONE with errors — failed: {', '.join(failures)}")
        sys.exit(1)
    print("DONE — all 5 reports built.")
    if not root:
        print("Note: dry-run only (epikast/build/). Set --root= or $EPIKAST_PBI_ROOT")
        print("to a Power-BI-created project folder to inject pages into real reports.")


if __name__ == "__main__":
    main()
