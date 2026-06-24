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
    uid, make_title_bar, make_clustered_bar, make_clustered_column_multi,
    make_combo_chart, make_line_chart, make_donut, make_filled_map, make_measure_column,
    make_table, card_row, slicer_row,
    TITLE_H, CARD_H, SLICER_H, GAP, CANVAS_H, TITLE_BOT, std_layout,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_client_dashb")

TEAL = "#2E86AB"
M    = "_Measures"

# Derived positions — 1 card row + 1 slicer row
_L      = std_layout(n_card_rows=1, n_slicer_rows=1)
CARD1_Y = _L["card_y"]    # 60
SL1_Y   = _L["slicer_y"]  # 190
BODY1_Y = _L["body_y"]    # 238
BODY1_H = _L["body_h"]    # 472

# Slicers-only pages
_LS  = std_layout(n_card_rows=0, n_slicer_rows=1)
SL_Y = _LS["slicer_y"]   # 60
BODY_Y = _LS["body_y"]   # 108
BODY_H = _LS["body_h"]   # 602


# Standard 3-slicer row: Quarter / TherapyArea / DrugName
def cli_slicers(prefix, y):
    return slicer_row(prefix, y, SLICER_H, [
        ("DimCalendar", "Quarter"),
        ("DimHCP",      "TherapyArea"),
        ("DimDrug",     "DrugName"),
    ])


# ===== PAGE 1: Engagement Overview =====
p1 = uid("epi_cli_p1_overview")

# Split the body into top section (combo + donut) and bottom (two bars)
CHART_H1 = (BODY1_H - GAP) // 2    # ~231 each half

P1 = [
    make_title_bar("c1_t", 0, 0, 1280, 50, "Epikast — Engagement Overview", TEAL),

    *card_row("c1r1", CARD1_Y, CARD_H, [
        "Total Calls",
        "Connect Rate",
        "HCPs Contacted",
        "Avg HCP Sentiment",
    ]),

    *cli_slicers("c1", SL1_Y),

    make_combo_chart("c1_combo",    20, BODY1_Y, 740, CHART_H1,
        "DimCalendar", "YearMonth", M, "Total Calls", M, "Connect Rate"),
    make_donut("c1_chan",           775, BODY1_Y, 485, CHART_H1,
        "FactHCPCalls", "Channel", M, "Total Calls"),

    make_clustered_bar("c1_itype", 20, BODY1_Y + CHART_H1 + GAP, 620, CHART_H1,
        "FactHCPCalls", "InteractionType", M, "Total Calls"),
    make_clustered_bar("c1_ta_bar", 655, BODY1_Y + CHART_H1 + GAP, 605, CHART_H1,
        "DimHCP", "TherapyArea", M, "Total Calls"),
]


# ===== PAGE 2: HCP Engagement =====
p2 = uid("epi_cli_p2_hcp")

HCP_SLICER_Y = TITLE_BOT        # 60  (4 slicers: Specialty / Tier / Region / Quarter)
HCP_BODY_Y   = HCP_SLICER_Y + SLICER_H + GAP   # 108
HCP_BODY_H   = 720 - HCP_BODY_Y - 10            # 602
HCP_MID_H    = (HCP_BODY_H - GAP) // 2          # ~296

P2 = [
    make_title_bar("c2_t", 0, 0, 1280, 50, "Epikast — HCP Engagement", TEAL),

    *slicer_row("c2sl", HCP_SLICER_Y, SLICER_H, [
        ("DimHCP",      "Specialty"),
        ("DimHCP",      "Tier"),
        ("DimHCP",      "Region"),
        ("DimCalendar", "Quarter"),
    ]),

    *card_row("c2r1", HCP_BODY_Y, CARD_H, [
        "HCPs Contacted",
        "HCP Reach",
        "Avg Contact Frequency",
        "Avg HCP Sentiment",
    ]),

    make_clustered_bar("c2_spec_bar",  20, HCP_BODY_Y + CARD_H + GAP, 400, HCP_MID_H - CARD_H - GAP,
        "DimHCP", "Specialty", M, "Total Calls"),
    make_donut("c2_tier_donut",       440, HCP_BODY_Y + CARD_H + GAP, 360, HCP_MID_H - CARD_H - GAP,
        "DimHCP", "Tier", M, "Total Calls"),
    make_filled_map("c2_map",         820, HCP_BODY_Y + CARD_H + GAP, 440, HCP_MID_H - CARD_H - GAP,
        "DimHCP", "State", M, "Total Calls"),

    make_table("c2_tbl", 20, HCP_BODY_Y + HCP_MID_H + GAP, 1240, HCP_BODY_H - HCP_MID_H - GAP, [
        ("DimHCP", "Specialty", False), ("DimHCP", "Region", False), ("DimHCP", "Tier", False),
        (M, "Total Calls", True), (M, "Connect Rate", True),
        (M, "Meaningful Interaction Rate", True), (M, "Avg HCP Sentiment", True),
    ]),
]


# ===== PAGE 3: Patient Support & Outcomes =====
p3 = uid("epi_cli_p3_patient")

P3_SL_SLICERS = [
    ("FactPatientCases", "InsuranceType"),
    ("DimDrug",          "DrugName"),
    ("DimPatient",       "TherapyArea"),
    ("DimCalendar",      "Quarter"),
]
CHART_HALF = (BODY1_H - GAP) // 2   # ~231

P3 = [
    make_title_bar("c3_t", 0, 0, 1280, 50, "Epikast — Patient Support & Outcomes", TEAL),

    *card_row("c3r1", CARD1_Y, CARD_H, [
        "Total Cases",
        "Abandonment Rate",
        "Avg Time to Therapy",
        "PA Approval Rate",
    ]),

    *slicer_row("c3sl", SL1_Y, SLICER_H, P3_SL_SLICERS),

    make_measure_column("c3_bottleneck", 20, BODY1_Y, 400, CHART_HALF,
        [(M, "Avg Days Rx to Contact"), (M, "Avg Days Contact to PA Submit"),
         (M, "Avg Days PA Submit to Decision"), (M, "Avg Days Decision to Fulfillment"),
         (M, "Avg Days Fulfillment to First Dose")]),
    make_clustered_column_multi("c3_adherence", 440, BODY1_Y, 400, CHART_HALF,
        "DimPatient", "TherapyArea",
        [(M, "Adherence 30 Day"), (M, "Adherence 60 Day"), (M, "Adherence 90 Day")]),
    make_donut("c3_pastatus", 860, BODY1_Y, 400, CHART_HALF,
        "FactPatientCases", "PAStatus", M, "Total Cases"),

    make_table("c3_tbl", 20, BODY1_Y + CHART_HALF + GAP, 1240, BODY1_H - CHART_HALF - GAP, [
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

    *card_row("c4r1", CARD1_Y, CARD_H, [
        "AI Lift on Connect Rate",
        "AI Lift on Meaningful Rate",
        "Total Time Saved Hours",
        "Avg HCP Sentiment",
    ]),

    *slicer_row("c4sl", SL1_Y, SLICER_H, [
        ("DimCalendar", "Quarter"),
        ("DimHCP",      "TherapyArea"),
    ]),

    make_measure_column("c4_vs", 20, BODY1_Y, 400, CHART_HALF,
        [(M, "AI Connect Rate"), (M, "Non-AI Connect Rate"),
         (M, "AI Meaningful Rate"), (M, "Non-AI Meaningful Rate")]),
    make_clustered_bar("c4_lift_ta", 440, BODY1_Y, 400, CHART_HALF,
        "DimHCP", "TherapyArea", M, "AI Lift on Connect Rate"),
    make_clustered_bar("c4_topics", 860, BODY1_Y, 400, CHART_HALF,
        "FactMSLPartnerUsage", "Topic", M, "Total MSL Queries"),

    make_table("c4_tbl", 20, BODY1_Y + CHART_HALF + GAP, 1240, BODY1_H - CHART_HALF - GAP, [
        ("DimHCP", "TherapyArea", False),
        (M, "AI Connect Rate", True), (M, "Non-AI Connect Rate", True),
        (M, "AI Lift on Connect Rate", True), (M, "AI Meaningful Rate", True),
    ]),
]


# ===== PAGE 5: ROI / Business Impact =====
p5 = uid("epi_cli_p5_roi")

P5 = [
    make_title_bar("c5_t", 0, 0, 1280, 50, "Epikast — ROI / Business Impact", TEAL),

    *card_row("c5r1", CARD1_Y, CARD_H, [
        "Total Revenue USD",
        "Gross Margin Pct",
        "Avg Cost Per Call",
        "Avg Cost Per Case",
    ]),

    *slicer_row("c5sl", SL1_Y, SLICER_H, [
        ("DimCalendar", "Quarter"),
        ("DimDrug",     "DrugName"),
    ]),

    make_measure_column("c5_rxinfluence", 20, BODY1_Y, 400, CHART_HALF,
        [(M, "Rx from Engaged HCPs"), (M, "Rx from Non-Engaged HCPs"),
         (M, "NBRx from Engaged HCPs")]),
    make_line_chart("c5_revcost", 440, BODY1_Y, 400, CHART_HALF,
        "FactFinancials", "YearMonth", M, "Total Revenue USD", M, "Total Cost EUR"),
    make_clustered_bar("c5_nbrx_ta", 860, BODY1_Y, 400, CHART_HALF,
        "DimHCP", "TherapyArea", M, "NBRx Rate"),

    make_table("c5_tbl", 20, BODY1_Y + CHART_HALF + GAP, 1240, BODY1_H - CHART_HALF - GAP, [
        ("FactFinancials", "YearMonth", False),
        (M, "Total Revenue USD", True), (M, "Total Cost EUR", True),
        (M, "Gross Margin Pct", True), (M, "Avg Cost Per Call", True),
        (M, "Avg Cost Per Case", True),
    ]),
]


write_page(p1, "Engagement Overview",      P1)
write_page(p2, "HCP Engagement",           P2)
write_page(p3, "Patient Support & Outcomes", P3)
write_page(p4, "AI-Driven Insights",       P4)
write_page(p5, "ROI / Business Impact",    P5)
write_pages_json([p1, p2, p3, p4, p5])

print("CLIENT-FACING report — 5 pages")
for n, pg in [("Engagement Overview", P1), ("HCP Engagement", P2),
              ("Patient Support & Outcomes", P3), ("AI-Driven Insights", P4),
              ("ROI / Business Impact", P5)]:
    print(f"  {n}: {len(pg)} visuals")
print(f"Total: {sum(len(p) for p in [P1,P2,P3,P4,P5])} visuals")
print("Done!")
