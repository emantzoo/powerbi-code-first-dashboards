"""
Epikast CLIENT-FACING report — the value deliverable handed to the biopharma client.

5 pages: Engagement Overview, HCP Engagement, Patient Support & Outcomes,
AI-Driven Insights, ROI / Business Impact. Aggregated value story — NO rep
names, NO internal compliance detail. Apply RLS on DimDrug / TherapyArea if a
client should see only their own brand. Runs against the shared Epikast Pharma
Ops model (Epikast_Dashboard_Prompts.md).

Run with Power BI closed:  python scripts/generate_pages_client.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_card, make_slicer, make_clustered_bar, make_clustered_column_multi,
    make_combo_chart, make_line_chart, make_donut, make_filled_map, make_measure_column,
    make_table, write_page, write_pages_json,
)

pb.BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\epikast\epikast_client_dashb.Report\definition\pages"

TEAL = "#2E86AB"
M = "_Measures"

# ===== PAGE 1: Engagement Overview =====
p1 = uid("epi_cli_p1_overview")
P1 = [
    make_title_bar("c1_t", 0, 0, 1280, 50, "Epikast — Engagement Overview", TEAL),
    make_card("c1_calls",   20, 60, 220, 120, M, "Total Calls"),
    make_card("c1_connect", 255, 60, 220, 120, M, "Connect Rate"),
    make_card("c1_hcps",    490, 60, 220, 120, M, "HCPs Contacted"),
    make_card("c1_sent",    725, 60, 220, 120, M, "Avg HCP Sentiment"),
    make_slicer("c1_qtr",  960, 60, 300, 40, "DimCalendar", "Quarter"),
    make_slicer("c1_ta",   960, 104, 300, 38, "DimHCP", "TherapyArea"),
    make_slicer("c1_drug", 960, 144, 300, 38, "DimDrug", "DrugName"),
    make_combo_chart("c1_combo", 20, 200, 740, 290, "DimCalendar", "YearMonth",
                     M, "Total Calls", M, "Connect Rate"),
    make_donut("c1_chan", 780, 200, 480, 290, "FactHCPCalls", "Channel", M, "Total Calls"),
    make_clustered_bar("c1_itype", 20, 500, 620, 200, "FactHCPCalls", "InteractionType", M, "Total Calls"),
    make_clustered_bar("c1_ta_bar", 660, 500, 600, 200, "DimHCP", "TherapyArea", M, "Total Calls"),
]

# ===== PAGE 2: HCP Engagement =====
p2 = uid("epi_cli_p2_hcp")
P2 = [
    make_title_bar("c2_t", 0, 0, 1280, 50, "Epikast — HCP Engagement", TEAL),
    make_card("c2_hcps",  20, 60, 220, 120, M, "HCPs Contacted"),
    make_card("c2_reach", 255, 60, 220, 120, M, "HCP Reach"),
    make_card("c2_freq",  490, 60, 220, 120, M, "Avg Contact Frequency"),
    make_card("c2_sent",  725, 60, 220, 120, M, "Avg HCP Sentiment"),
    make_slicer("c2_spec", 960, 60, 300, 40, "DimHCP", "Specialty"),
    make_slicer("c2_tier", 960, 104, 300, 38, "DimHCP", "Tier"),
    make_slicer("c2_reg",  960, 144, 300, 38, "DimHCP", "Region"),
    make_clustered_bar("c2_spec_bar", 20, 200, 400, 290, "DimHCP", "Specialty", M, "Total Calls"),
    make_donut("c2_tier_donut", 440, 200, 360, 290, "DimHCP", "Tier", M, "Total Calls"),
    make_filled_map("c2_map", 820, 200, 440, 290, "DimHCP", "State", M, "Total Calls"),
    make_table("c2_tbl", 20, 500, 1240, 200, [
        ("DimHCP", "Specialty", False), ("DimHCP", "Region", False), ("DimHCP", "Tier", False),
        (M, "Total Calls", True), (M, "Connect Rate", True),
        (M, "Meaningful Interaction Rate", True), (M, "Avg HCP Sentiment", True),
    ]),
]

# ===== PAGE 3: Patient Support & Outcomes =====
p3 = uid("epi_cli_p3_patient")
P3 = [
    make_title_bar("c3_t", 0, 0, 1280, 50, "Epikast — Patient Support & Outcomes", TEAL),
    make_card("c3_cases", 20, 60, 220, 120, M, "Total Cases"),
    make_card("c3_aband", 255, 60, 220, 120, M, "Abandonment Rate"),
    make_card("c3_ttt",   490, 60, 220, 120, M, "Avg Time to Therapy"),
    make_card("c3_pa",    725, 60, 220, 120, M, "PA Approval Rate"),
    make_slicer("c3_ins",  960, 60, 300, 40, "FactPatientCases", "InsuranceType"),
    make_slicer("c3_drug", 960, 104, 300, 38, "DimDrug", "DrugName"),
    make_slicer("c3_ta",   960, 144, 300, 38, "DimPatient", "TherapyArea"),
    make_measure_column("c3_bottleneck", 20, 200, 400, 290,
                        [(M, "Avg Days Rx to Contact"), (M, "Avg Days Contact to PA Submit"),
                         (M, "Avg Days PA Submit to Decision"), (M, "Avg Days Decision to Fulfillment"),
                         (M, "Avg Days Fulfillment to First Dose")]),
    make_clustered_column_multi("c3_adherence", 440, 200, 400, 290, "DimPatient", "TherapyArea",
                                [(M, "Adherence 30 Day"), (M, "Adherence 60 Day"), (M, "Adherence 90 Day")]),
    make_donut("c3_pastatus", 860, 200, 400, 290, "FactPatientCases", "PAStatus", M, "Total Cases"),
    make_table("c3_tbl", 20, 500, 1240, 200, [
        ("FactPatientCases", "InsuranceType", False),
        (M, "Total Cases", True), (M, "PA Approval Rate", True),
        (M, "Avg Time to Therapy", True), (M, "Abandonment Rate", True),
        (M, "Adherence 90 Day", True),
    ]),
]

# ===== PAGE 4: AI-Driven Insights =====
p4 = uid("epi_cli_p4_ai")
P4 = [
    make_title_bar("c4_t", 0, 0, 1280, 50, "Epikast — AI-Driven Insights", TEAL),
    make_card("c4_liftc", 20, 60, 220, 120, M, "AI Lift on Connect Rate"),
    make_card("c4_liftm", 255, 60, 220, 120, M, "AI Lift on Meaningful Rate"),
    make_card("c4_saved", 490, 60, 220, 120, M, "Total Time Saved Hours"),
    make_card("c4_sent",  725, 60, 220, 120, M, "Avg HCP Sentiment"),
    make_slicer("c4_qtr", 960, 60, 300, 56, "DimCalendar", "Quarter"),
    make_slicer("c4_ta",  960, 122, 300, 58, "DimHCP", "TherapyArea"),
    make_measure_column("c4_vs", 20, 200, 400, 290,
                        [(M, "AI Connect Rate"), (M, "Non-AI Connect Rate"),
                         (M, "AI Meaningful Rate"), (M, "Non-AI Meaningful Rate")]),
    make_clustered_bar("c4_lift_ta", 440, 200, 400, 290, "DimHCP", "TherapyArea", M, "AI Lift on Connect Rate"),
    make_clustered_bar("c4_topics", 860, 200, 400, 290, "FactMSLPartnerUsage", "Topic", M, "Total MSL Queries"),
    make_table("c4_tbl", 20, 500, 1240, 200, [
        ("DimHCP", "TherapyArea", False),
        (M, "AI Connect Rate", True), (M, "Non-AI Connect Rate", True),
        (M, "AI Lift on Connect Rate", True), (M, "AI Meaningful Rate", True),
    ]),
]

# ===== PAGE 5: ROI / Business Impact =====
p5 = uid("epi_cli_p5_roi")
P5 = [
    make_title_bar("c5_t", 0, 0, 1280, 50, "Epikast — ROI / Business Impact", TEAL),
    make_card("c5_rev",   20, 60, 220, 120, M, "Total Revenue USD"),
    make_card("c5_margin", 255, 60, 220, 120, M, "Gross Margin Pct"),
    make_card("c5_cpc",   490, 60, 220, 120, M, "Avg Cost Per Call"),
    make_card("c5_cpcase", 725, 60, 220, 120, M, "Avg Cost Per Case"),
    make_slicer("c5_qtr",  960, 60, 300, 56, "DimCalendar", "Quarter"),
    make_slicer("c5_drug", 960, 122, 300, 58, "DimDrug", "DrugName"),
    make_measure_column("c5_rxinfluence", 20, 200, 400, 290,
                        [(M, "Rx from Engaged HCPs"), (M, "Rx from Non-Engaged HCPs"),
                         (M, "NBRx from Engaged HCPs")]),
    make_line_chart("c5_revcost", 440, 200, 400, 290, "FactFinancials", "YearMonth",
                    M, "Total Revenue USD", M, "Total Cost EUR"),
    make_clustered_bar("c5_nbrx_ta", 860, 200, 400, 290, "DimHCP", "TherapyArea", M, "NBRx Rate"),
    make_table("c5_tbl", 20, 500, 1240, 200, [
        ("FactFinancials", "YearMonth", False),
        (M, "Total Revenue USD", True), (M, "Total Cost EUR", True),
        (M, "Gross Margin Pct", True), (M, "Avg Cost Per Call", True),
        (M, "Avg Cost Per Case", True),
    ]),
]

write_page(p1, "Engagement Overview", P1)
write_page(p2, "HCP Engagement", P2)
write_page(p3, "Patient Support & Outcomes", P3)
write_page(p4, "AI-Driven Insights", P4)
write_page(p5, "ROI / Business Impact", P5)
write_pages_json([p1, p2, p3, p4, p5])

print("CLIENT-FACING report — 5 pages")
for n, pg in [("Engagement Overview", P1), ("HCP Engagement", P2), ("Patient Support & Outcomes", P3),
              ("AI-Driven Insights", P4), ("ROI / Business Impact", P5)]:
    print(f"  {n}: {len(pg)} visuals")
print(f"Total: {sum(len(p) for p in [P1,P2,P3,P4,P5])} visuals")
print("Done!")
