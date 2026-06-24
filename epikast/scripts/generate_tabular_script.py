#!/usr/bin/env python3
"""
Generate a Tabular Editor 2 C# script (build_model.csx) that builds the Epikast
semantic model in one run: all measures (parsed live from Epikast_Dashboard_Prompts.md),
the calculated columns, and the Phase-1A relationships.

Usage:
    python epikast/scripts/generate_tabular_script.py
    -> writes epikast/build_model.csx

Then in Tabular Editor 2 (free), connected to the model: Advanced Scripting tab,
paste/open build_model.csx, Run (F5), Save. See BUILD.md.
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PROMPTS = os.path.normpath(os.path.join(HERE, "..", "Epikast_Dashboard_Prompts.md"))
OUT = os.path.normpath(os.path.join(HERE, "..", "build_model.csx"))

# Calc-column → owning table (only 6; the md comments name the table but parsing the
# prose is brittle, so map explicitly here).
CALC_COL_TABLE = {
    "Performance Tier": "DimRep",
    "Tenure Bucket": "DimRep",
    "CallTimeBucket": "FactHCPCalls",
    "SentimentBand": "FactHCPCalls",
    "AI Adoption Band": "DimRep",
    "Open Case Age Bucket": "FactPatientCases",
}

# Phase-1A relationships: (fromTable, fromCol, toTable, toCol, isActive). The "many" side
# is the from-column. DimDrug links are written dim-first in the md but the fact holds the
# many side, so they're normalised here.
RELATIONSHIPS = [
    ("FactHCPCalls", "CallDate", "DimCalendar", "Date", True),
    ("FactPatientCases", "RxDate", "DimCalendar", "Date", False),
    ("FactRx", "RxDate", "DimCalendar", "Date", False),
    ("FactMSLPartnerUsage", "UsageDate", "DimCalendar", "Date", False),
    ("FactFinancials", "MonthDate", "DimCalendar", "Date", False),
    ("FactHCPCalls", "RepID", "DimRep", "RepID", True),
    ("FactHCPCalls", "HCPID", "DimHCP", "HCPID", True),
    ("FactPatientCases", "PatientID", "DimPatient", "PatientID", True),
    ("FactPatientCases", "RepID", "DimRep", "RepID", True),
    ("FactRx", "HCPID", "DimHCP", "HCPID", True),
    ("FactMSLPartnerUsage", "RepID", "DimRep", "RepID", True),
    ("FactHCPCalls", "Drug", "DimDrug", "DrugName", True),
    ("FactPatientCases", "Drug", "DimDrug", "DrugName", True),
    ("FactRx", "Drug", "DimDrug", "DrugName", True),
    ("FactMSLPartnerUsage", "Drug", "DimDrug", "DrugName", True),
]

NAME_START = re.compile(r"^[A-Za-z][A-Za-z0-9 _%/+\-]*? = ")


def _parse_definitions(lines):
    """Yield (name, dax) from a code-block body. A definition starts at column 0 on a
    'Name = ...' line; indented / non-matching lines continue the previous definition."""
    name, buf = None, []
    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace() and NAME_START.match(line):
            if name:
                yield name, "\n".join(buf).strip()
            n, _, rest = line.partition(" = ")
            name, buf = n.strip(), [rest]
        else:
            buf.append(line)
    if name:
        yield name, "\n".join(buf).strip()


def parse_measures(md):
    """Measures live in code fences between '## PHASE 1 — DAX Measures' and
    '### Calculated Columns', grouped under '### N. Group (count)' headers."""
    region = md.split("## PHASE 1 — DAX Measures", 1)[1].split("### Calculated Columns", 1)[0]
    out = []
    current_group = "General"
    pos = 0
    for m in re.finditer(r"### .*?\n|```.*?```", region, re.DOTALL):
        chunk = m.group(0)
        if chunk.startswith("### "):
            # "### 1. HCP Engagement (13)" -> "HCP Engagement"
            current_group = re.sub(r"^### \d+\.\s*", "", chunk).split("(")[0].strip()
        else:
            body = chunk.strip("`").split("\n", 1)[-1].rsplit("```", 1)[0]
            for name, dax in _parse_definitions(body.splitlines()):
                out.append((current_group, name, dax))
    return out


def parse_calc_columns(md):
    """Calc columns use column-0 VAR/RETURN lines, so the indentation rule doesn't apply.
    They're blank-line-separated records instead; first non-comment line carries the name."""
    block = md.split("### Calculated Columns", 1)[1]
    body = re.search(r"```(.*?)```", block, re.DOTALL).group(1)
    out = []
    for record in re.split(r"\n\s*\n", body):
        lines = [l for l in record.splitlines() if l.strip() and not l.lstrip().startswith("#")]
        if not lines:
            continue
        first = lines[0].rstrip()
        if first.endswith("="):
            name, dax = first[:-1].strip(), "\n".join(lines[1:]).strip()
        else:
            n, _, rest = first.partition(" = ")
            name, dax = n.strip(), "\n".join([rest] + lines[1:]).strip()
        out.append((name, dax))
    return out


def cs_string(s):
    """C# verbatim string literal: wrap in @"" and double the quotes."""
    return '@"' + s.replace('"', '""') + '"'


def main():
    md = open(PROMPTS, encoding="utf-8").read()
    measures = parse_measures(md)
    calc_cols = parse_calc_columns(md)

    L = []
    L.append("// AUTO-GENERATED by scripts/generate_tabular_script.py — do not edit by hand.")
    L.append("// Tabular Editor 2 (free): connect to the Epikast model, Advanced Scripting, Run (F5), Save.")
    L.append(f"// Creates {len(measures)} measures, {len(calc_cols)} calculated columns, "
             f"{len(RELATIONSHIPS)} relationships.")
    L.append("")
    L.append("int mAdded = 0, cAdded = 0, rAdded = 0;")
    L.append("")
    L.append('// ---- _Measures host table ----')
    L.append('var mt = Model.Tables.Contains("_Measures") ? Model.Tables["_Measures"]')
    L.append('    : Model.AddCalculatedTable("_Measures", "{BLANK()}");')
    L.append("")
    L.append("// ---- Measures ----")
    for group, name, dax in measures:
        L.append("try {")
        L.append(f'    var m = mt.Measures.Contains({cs_string(name)}) ? mt.Measures[{cs_string(name)}] : mt.AddMeasure({cs_string(name)});')
        L.append(f"    m.Expression = {cs_string(dax)};")
        L.append(f"    m.DisplayFolder = {cs_string(group)};")
        L.append("    mAdded++;")
        L.append(f'}} catch (Exception ex) {{ Info("Measure failed: {name} -> " + ex.Message); }}')
    L.append("")
    L.append("// ---- Calculated columns ----")
    for name, dax in calc_cols:
        tbl = CALC_COL_TABLE.get(name)
        if not tbl:
            L.append(f'Info("No table mapping for calc column: {name} — skipped");')
            continue
        L.append("try {")
        L.append(f'    var t = Model.Tables["{tbl}"];')
        L.append(f'    if (!t.Columns.Contains({cs_string(name)})) t.AddCalculatedColumn({cs_string(name)}, {cs_string(dax)});')
        L.append(f'    else ((CalculatedColumn)t.Columns[{cs_string(name)}]).Expression = {cs_string(dax)};')
        L.append("    cAdded++;")
        L.append(f'}} catch (Exception ex) {{ Info("Calc column failed: {name} -> " + ex.Message); }}')
    L.append("")
    L.append("// ---- Relationships (Phase 1A) ----")
    for ft, fc, tt, tc, active in RELATIONSHIPS:
        L.append("try {")
        L.append("    var r = Model.AddRelationship();")
        L.append(f'    r.FromColumn = Model.Tables["{ft}"].Columns["{fc}"];')
        L.append(f'    r.ToColumn = Model.Tables["{tt}"].Columns["{tc}"];')
        L.append(f'    r.IsActive = {"true" if active else "false"};')
        L.append("    rAdded++;")
        L.append(f'}} catch (Exception ex) {{ Info("Relationship failed: {ft}[{fc}]->{tt}[{tc}] -> " + ex.Message); }}')
    L.append("")
    L.append('Info($"Done: {mAdded} measures, {cAdded} calc columns, {rAdded} relationships.");')

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    print(f"Wrote {OUT}")
    print(f"  measures:      {len(measures)}")
    print(f"  calc columns:  {len(calc_cols)}")
    print(f"  relationships: {len(RELATIONSHIPS)}")


if __name__ == "__main__":
    main()
