#!/usr/bin/env python3
"""
Generate the shared Epikast semantic model as TMSL (model.bim) + the PBIP wrapper,
so the model is built from files — no manual measure entry, no Tabular Editor.

It emits, under <root>/Epikast.SemanticModel/:
    model.bim            all tables (columns + typed CSV partitions), 139 measures,
                         6 calc columns, 15 relationships, a SourceFolder parameter
    definition.pbism     project metadata
    .platform            Fabric/git metadata

Measures/relationships/calc-columns are parsed from Epikast_Dashboard_Prompts.md
(via generate_tabular_script), so this stays in sync with the spec.

Usage:
    python epikast/scripts/generate_semantic_model.py                 # -> epikast/pbip/
    python epikast/scripts/generate_semantic_model.py --root="C:/path"
    python epikast/scripts/generate_semantic_model.py --data="C:/.../epikast/data"
"""

import csv
import glob
import hashlib
import json
import os
import re
import sys

from generate_tabular_script import (
    parse_measures, parse_calc_columns, RELATIONSHIPS, CALC_COL_TABLE, PROMPTS,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data"))

# CSV type → (TMSL dataType, M type cast, format string or None)
TYPE_MAP = {
    "string":   ("string",   "type text",   None),
    "int64":    ("int64",    "Int64.Type",  "0"),
    "double":   ("double",   "type number", None),
    "dateTime": ("dateTime", "type datetime", "General Date"),
    "boolean":  ("boolean",  "type logical", None),
}


def _guid(seed):
    h = hashlib.md5(seed.encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def infer_types(path):
    """Robust per-column type: scan the whole file, treat ''/blank as null, and pick the
    narrowest type that fits every non-blank value (int64 < double < dateTime < string)."""
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}")
    with open(path, newline="", encoding="utf-8-sig") as fh:
        r = csv.reader(fh)
        hdr = next(r)
        state = {c: {"int": True, "float": True, "date": True, "any": False} for c in hdr}
        for row in r:
            for i, c in enumerate(hdr):
                if i >= len(row):
                    continue
                v = row[i].strip()
                if v == "":
                    continue
                st = state[c]
                st["any"] = True
                if st["int"]:
                    try:
                        int(v)
                    except ValueError:
                        st["int"] = False
                if st["float"]:
                    try:
                        float(v)
                    except ValueError:
                        st["float"] = False
                if st["date"] and not date_re.match(v):
                    st["date"] = False
    out = []
    for c in hdr:
        st = state[c]
        if not st["any"]:
            t = "string"
        elif st["int"]:
            t = "int64"
        elif st["float"]:
            t = "double"
        elif st["date"]:
            t = "dateTime"
        else:
            t = "string"
        out.append((c, t))
    return out


def m_partition(table, cols):
    casts = ", ".join(f'{{"{c}", {TYPE_MAP[t][1]}}}' for c, t in cols)
    return [
        "let",
        f'    Source = Csv.Document(File.Contents(SourceFolder & "{table}.csv"), '
        "[Delimiter=\",\", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),",
        "    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
        f"    Typed = Table.TransformColumnTypes(Promoted, {{{casts}}})",
        "in",
        "    Typed",
    ]


def build_model_bim():
    md = open(PROMPTS, encoding="utf-8").read()
    measures = parse_measures(md)
    calc_cols = parse_calc_columns(md)
    calc_by_table = {}
    for name, dax in calc_cols:
        calc_by_table.setdefault(CALC_COL_TABLE.get(name, "?"), []).append((name, dax))

    tables = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.csv"))):
        tname = os.path.basename(path)[:-4]
        cols = infer_types(path)
        columns = []
        for c, t in cols:
            dt, _, fmt = TYPE_MAP[t]
            col = {"name": c, "dataType": dt, "sourceColumn": c,
                   "summarizeBy": "none", "lineageTag": _guid(f"{tname}.{c}")}
            if fmt:
                col["formatString"] = fmt
            columns.append(col)
        # calculated columns on this table
        for name, dax in calc_by_table.get(tname, []):
            columns.append({"name": name, "dataType": "string", "type": "calculated",
                            "expression": dax, "summarizeBy": "none",
                            "lineageTag": _guid(f"{tname}.{name}")})
        tables.append({
            "name": tname,
            "lineageTag": _guid(tname),
            "columns": columns,
            "partitions": [{
                "name": tname, "mode": "import",
                "source": {"type": "m", "expression": m_partition(tname, cols)},
            }],
        })

    # _Measures host table (calculated, hidden)
    measure_objs = []
    for group, name, dax in measures:
        measure_objs.append({
            "name": name, "expression": dax, "displayFolder": group,
            "lineageTag": _guid(f"_Measures.{name}"),
        })
    tables.append({
        "name": "_Measures", "isHidden": True, "lineageTag": _guid("_Measures"),
        "columns": [{"name": "Value", "dataType": "int64", "type": "calculatedTableColumn",
                     "sourceColumn": "[Value]", "isHidden": True,
                     "lineageTag": _guid("_Measures.Value")}],
        "partitions": [{"name": "_Measures", "mode": "import",
                        "source": {"type": "calculated", "expression": "{BLANK()}"}}],
        "measures": measure_objs,
    })

    relationships = []
    for ft, fc, tt, tc, active in RELATIONSHIPS:
        relationships.append({
            "name": _guid(f"{ft}.{fc}->{tt}.{tc}"),
            "fromTable": ft, "fromColumn": fc, "toTable": tt, "toColumn": tc,
            "isActive": active, "crossFilteringBehavior": "oneDirection",
        })

    data_default = DATA_DIR.replace("\\", "\\\\") + "\\\\"
    expressions = [{
        "name": "SourceFolder", "kind": "m",
        "expression": f'"{data_default}" meta [IsParameterQuery=true, Type="Text", '
                      "IsParameterQueryRequired=true]",
    }]

    return {
        "name": "Epikast",
        "compatibilityLevel": 1600,
        "model": {
            "culture": "en-US",
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "discourageImplicitMeasures": True,
            "sourceQueryCulture": "en-US",
            "tables": tables,
            "relationships": relationships,
            "expressions": expressions,
            "annotations": [{"name": "PBI_QueryOrder",
                             "value": json.dumps([t["name"] for t in tables])}],
        },
    }, len(measures), len(calc_cols), len(relationships), len(tables)


def main():
    root = None
    data = None
    for a in sys.argv[1:]:
        if a.startswith("--root="):
            root = a.split("=", 1)[1]
        elif a.startswith("--data="):
            data = a.split("=", 1)[1]
    global DATA_DIR
    if data:
        DATA_DIR = data
    if not root:
        root = os.path.normpath(os.path.join(HERE, "..", "pbip"))

    sm_dir = os.path.join(root, "Epikast.SemanticModel")
    os.makedirs(sm_dir, exist_ok=True)

    bim, nm, nc, nr, nt = build_model_bim()
    with open(os.path.join(sm_dir, "model.bim"), "w", encoding="utf-8") as f:
        json.dump(bim, f, indent=2)
    with open(os.path.join(sm_dir, "definition.pbism"), "w", encoding="utf-8") as f:
        json.dump({"version": "4.0", "settings": {}}, f, indent=2)
    with open(os.path.join(sm_dir, ".platform"), "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {"type": "SemanticModel", "displayName": "Epikast"},
            "config": {"version": "2.0", "logicalId": _guid("Epikast.SemanticModel")},
        }, f, indent=2)

    print(f"Wrote {sm_dir}")
    print(f"  tables: {nt}  measures: {nm}  calc cols: {nc}  relationships: {nr}")
    print("  NOTE: set the SourceFolder parameter to your epikast/data path on first open.")


if __name__ == "__main__":
    main()
