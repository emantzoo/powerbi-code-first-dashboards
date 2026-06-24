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
    uid, make_title_bar, make_card, make_slicer,
    make_clustered_bar, make_line_chart, make_funnel,
    make_table, make_matrix,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_patient_dashb")

PURPLE = "#5B21B6"
M = "_Measures"

# ===== PAGE 1: Funnel Overview =====
p1 = uid("ep_patient_funnel_overview")
P1 = [
    make_title_bar("pa_title", 0, 0, 1280, 50, "Patient Access \u2014 Funnel Overview", PURPLE),
    make_card("pa_total_cases",  20,  60, 186, 120, M, "Total Cases"),
    make_card("pa_abandon_rate", 218, 60, 186, 120, M, "Abandonment Rate"),
    make_card("pa_ttt",          416, 60, 186, 120, M, "Avg Time to Therapy"),
    make_card("pa_pa_rate",      614, 60, 186, 120, M, "PA Approval Rate"),
    make_card("pa_48h",          812, 60, 186, 120, M, "Contacted Within 48h Rate"),
    make_slicer("pa_sl_qtr",  1010, 60,  250, 28, "DimCalendar",      "Quarter"),
    make_slicer("pa_sl_ins",  1010, 93,  250, 28, "DimPatient",       "InsuranceType"),
    make_slicer("pa_sl_ther", 1010, 126, 250, 28, "DimRep",           "TherapyArea"),
    make_slicer("pa_sl_drug", 1010, 159, 250, 28, "DimDrug",          "DrugName"),
    make_funnel("pa_funnel", 20, 195, 740, 310,
        "FactPatientCases", "PAStatus", M, "Total Cases"),
    make_clustered_bar("pa_dropout_bar", 775, 195, 485, 310,
        "FactPatientCases", "AbandonmentStage", M, "Abandoned Cases"),
    make_table("pa_summary", 20, 520, 1240, 180, [
        ("FactPatientCases", "PAStatus",           False),
        (M,                  "Total Cases",         True),
        (M,                  "Abandonment Rate",    True),
        (M,                  "Avg Time to Therapy", True),
        (M,                  "PA Approval Rate",    True),
    ]),
]

# ===== PAGE 2: PA and Insurance =====
p2 = uid("ep_patient_pa_insurance")
P2 = [
    make_title_bar("pb_title", 0, 0, 1280, 50, "Patient Access \u2014 PA & Insurance", PURPLE),
    make_clustered_bar("pb_pa_outcome", 20, 60, 610, 270,
        "FactPatientCases", "InsuranceType", M, "PA Approval Rate"),
    make_clustered_bar("pb_pa_delay", 645, 60, 615, 270,
        "FactPatientCases", "InsuranceType", M, "Avg PA Decision Delay"),
    make_line_chart("pb_approval_trend", 20, 345, 610, 250,
        "DimCalendar", "YearMonth", M, "PA Approval Rate", M, "PA Denial Rate"),
    make_table("pb_ins_table", 645, 345, 615, 250, [
        ("FactPatientCases", "InsuranceType",        False),
        (M,                  "Total Cases",           True),
        (M,                  "PA Approval Rate",      True),
        (M,                  "PA Denial Rate",        True),
        (M,                  "Avg PA Decision Delay", True),
        (M,                  "Abandonment Rate",      True),
        (M,                  "Avg Time to Therapy",   True),
    ]),
    make_slicer("pb_sl_qtr",  20,  610, 200, 35, "DimCalendar", "Quarter"),
    make_slicer("pb_sl_drug", 230, 610, 200, 35, "DimDrug",     "DrugName"),
]

# ===== PAGE 3: Adherence =====
p3 = uid("ep_patient_adherence")
P3 = [
    make_title_bar("pc_title", 0, 0, 1280, 50, "Patient Access \u2014 Adherence", PURPLE),
    make_card("pc_adh30", 20,  60, 300, 120, M, "Adherence 30 Day"),
    make_card("pc_adh60", 335, 60, 300, 120, M, "Adherence 60 Day"),
    make_card("pc_adh90", 650, 60, 300, 120, M, "Adherence 90 Day"),
    make_slicer("pc_sl_ins",  965, 60,  295, 55, "FactPatientCases", "InsuranceType"),
    make_slicer("pc_sl_drug", 965, 120, 295, 55, "DimDrug",          "DrugName"),
    make_matrix("pc_adh_matrix", 20, 195, 1240, 260,
        [("DimPatient", "TherapyArea")],
        [],
        [(M, "Adherence 30 Day"), (M, "Adherence 60 Day"), (M, "Adherence 90 Day")]),
    make_line_chart("pc_adh_trend", 20, 470, 1240, 230,
        "DimCalendar", "YearMonth", M, "Adherence 30 Day", M, "Adherence 90 Day"),
]

write_page(p1, "Funnel Overview", P1)
write_page(p2, "PA and Insurance", P2)
write_page(p3, "Adherence",        P3)
write_pages_json([p1, p2, p3])

print("Patient Access Funnel: 3 pages generated.")
