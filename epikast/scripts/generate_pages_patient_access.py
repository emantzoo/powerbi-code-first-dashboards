"""
Epikast PATIENT ACCESS FUNNEL report — funnel throughput, PA/insurance barriers, adherence decay.

3 pages:
  1. Funnel Overview  — PA funnel, dropout bar, summary table
  2. PA and Insurance — approval/delay bars, PA trend line, insurance table
  3. Adherence        — 30/60/90-day KPIs, therapy-area matrix, trend line

Run with Power BI closed:  python scripts/generate_pages_patient_access.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar,
    make_clustered_bar, make_line_chart, make_funnel,
    make_table, make_matrix,
    card_row, slicer_row,
    CARD_H, SLICER_H, GAP,
    CARD1_Y, SL1_Y, BODY1_Y, BODY1_H,
    SL_Y, BODY_Y, BODY_H,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_patient_dashb")

PURPLE = "#5B21B6"
M      = "_Measures"


# ===== PAGE 1: Funnel Overview =====
p1 = uid("ep_patient_funnel_overview")

FUN_CHART_H = BODY1_H * 7 // 10      # ~330 funnel + dropout
FUN_TBL_H   = BODY1_H - FUN_CHART_H - GAP   # ~132

P1 = [
    make_title_bar("pa_title", 0, 0, 1280, 50, "Patient Access \u2014 Funnel Overview", PURPLE),

    *card_row("par1", CARD1_Y, CARD_H, [
        "Total Cases",
        "Abandonment Rate",
        "Avg Time to Therapy",
        "PA Approval Rate",
        "Contacted Within 48h Rate",
    ]),

    *slicer_row("pasl", SL1_Y, SLICER_H, [
        ("DimCalendar", "Quarter"),
        ("DimPatient",  "InsuranceType"),
        ("DimRep",      "TherapyArea"),
        ("DimDrug",     "DrugName"),
    ]),

    make_funnel("pa_funnel", 20, BODY1_Y, 740, FUN_CHART_H,
        "FactPatientCases", "PAStatus", M, "Total Cases"),
    make_clustered_bar("pa_dropout_bar", 775, BODY1_Y, 485, FUN_CHART_H,
        "FactPatientCases", "AbandonmentStage", M, "Abandoned Cases"),

    make_table("pa_summary", 20, BODY1_Y + FUN_CHART_H + GAP, 1240, FUN_TBL_H, [
        ("FactPatientCases", "PAStatus",           False),
        (M,                  "Total Cases",         True),
        (M,                  "Abandonment Rate",    True),
        (M,                  "Avg Time to Therapy", True),
        (M,                  "PA Approval Rate",    True),
    ]),
]


# ===== PAGE 2: PA and Insurance =====
p2 = uid("ep_patient_pa_insurance")

# Slicers at bottom, charts fill the body above
TOP2_H   = BODY_H * 3 // 5       # ~361 charts
MID2_Y   = BODY_Y + TOP2_H + GAP
MID2_H   = BODY_H - TOP2_H - GAP # ~231 line + table

P2 = [
    make_title_bar("pb_title", 0, 0, 1280, 50, "Patient Access \u2014 PA & Insurance", PURPLE),

    *slicer_row("pbsl", SL_Y, SLICER_H, [
        ("DimCalendar", "Quarter"),
        ("DimDrug",     "DrugName"),
    ]),

    make_clustered_bar("pb_pa_outcome", 20, BODY_Y, 610, TOP2_H,
        "FactPatientCases", "InsuranceType", M, "PA Approval Rate"),
    make_clustered_bar("pb_pa_delay", 650, BODY_Y, 610, TOP2_H,
        "FactPatientCases", "InsuranceType", M, "Avg PA Decision Delay"),

    make_line_chart("pb_approval_trend", 20, MID2_Y, 610, MID2_H,
        "DimCalendar", "YearMonth", M, "PA Approval Rate", M, "PA Denial Rate"),
    make_table("pb_ins_table", 650, MID2_Y, 610, MID2_H, [
        ("FactPatientCases", "InsuranceType",        False),
        (M,                  "Total Cases",           True),
        (M,                  "PA Approval Rate",      True),
        (M,                  "PA Denial Rate",        True),
        (M,                  "Avg PA Decision Delay", True),
        (M,                  "Abandonment Rate",      True),
        (M,                  "Avg Time to Therapy",   True),
    ]),
]


# ===== PAGE 3: Adherence =====
p3 = uid("ep_patient_adherence")

ADH_MID_H = (BODY1_H - GAP) // 2    # ~231

P3 = [
    make_title_bar("pc_title", 0, 0, 1280, 50, "Patient Access \u2014 Adherence", PURPLE),

    *card_row("pcr1", CARD1_Y, CARD_H, [
        "Adherence 30 Day",
        "Adherence 60 Day",
        "Adherence 90 Day",
    ]),

    *slicer_row("pcsl", SL1_Y, SLICER_H, [
        ("FactPatientCases", "InsuranceType"),
        ("DimDrug",          "DrugName"),
    ]),

    make_matrix("pc_adh_matrix", 20, BODY1_Y, 1240, ADH_MID_H,
        [("DimPatient", "TherapyArea")],
        [],
        [(M, "Adherence 30 Day"), (M, "Adherence 60 Day"), (M, "Adherence 90 Day")]),

    make_line_chart("pc_adh_trend", 20, BODY1_Y + ADH_MID_H + GAP, 1240, BODY1_H - ADH_MID_H - GAP,
        "DimCalendar", "YearMonth", M, "Adherence 30 Day", M, "Adherence 90 Day"),
]


write_page(p1, "Funnel Overview",  P1)
write_page(p2, "PA and Insurance", P2)
write_page(p3, "Adherence",        P3)
write_pages_json([p1, p2, p3])

print("Patient Access Funnel: 3 pages generated.")
