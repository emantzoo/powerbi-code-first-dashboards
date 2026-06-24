"""
Epikast AI IMPACT report — condensed AI/MSL view (alternative to generate_pages_ai.py).

3 pages (AI targeting + MSL performance + MSL ROI only — no experiment registry):
  1. AI Call Targeting       — connect rate comparison, lift by TA, acceptance trend
  2. MSL Partner Performance — query volume, type donut, adoption trend
  3. MSL Partner ROI         — quality stacked bar, scorecard table

Write to epikast_ai_dashb to replace the first 3 pages of generate_pages_ai.py,
or use as a standalone lightweight AI dashboard.

Run with Power BI closed:  python scripts/generate_pages_ai_impact.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_card, make_slicer,
    make_clustered_bar, make_line_chart, make_donut,
    make_stacked_bar, make_table,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_ai_dashb")

MAGENTA = "#A23B72"
M = "_Measures"

# ===== PAGE 1: AI Call Targeting =====
p1 = uid("ep_ai_targeting")
P1 = [
    make_title_bar("a1_title", 0, 0, 1280, 50, "AI Impact \u2014 Call Targeting", MAGENTA),
    make_card("a1_ai_connect",    20,  60, 230, 120, M, "AI Connect Rate"),
    make_card("a1_nonai_connect", 265, 60, 230, 120, M, "Non-AI Connect Rate"),
    make_card("a1_accept",        510, 60, 230, 120, M, "AI Acceptance Rate"),
    make_card("a1_lift",          755, 60, 230, 120, M, "AI Lift on Connect Rate"),
    make_slicer("a1_sl_qtr",     1000, 60,  260, 35, "DimCalendar", "Quarter"),
    make_slicer("a1_sl_tier",    1000, 100, 260, 35, "DimHCP",      "Tier"),
    make_slicer("a1_sl_therapy", 1000, 140, 260, 35, "DimRep",      "TherapyArea"),
    make_clustered_bar("a1_rates_bar", 20, 195, 610, 270,
        "DimRep", "TherapyArea", M, "AI Connect Rate"),
    make_clustered_bar("a1_lift_bar", 645, 195, 615, 270,
        "DimRep", "TherapyArea", M, "AI Lift on Connect Rate"),
    make_line_chart("a1_accept_trend", 20, 480, 1240, 210,
        "DimCalendar", "YearMonth", M, "AI Acceptance Rate"),
]

# ===== PAGE 2: MSL Partner Performance =====
p2 = uid("ep_ai_msl_performance")
P2 = [
    make_title_bar("a2_title", 0, 0, 1280, 50, "AI Impact \u2014 MSL Partner Performance", MAGENTA),
    make_card("a2_queries",    20,  60, 230, 120, M, "Total MSL Queries"),
    make_card("a2_full_rate",  265, 60, 230, 120, M, "Fully Answered Rate"),
    make_card("a2_resp_time",  510, 60, 230, 120, M, "Avg Time to Answer Sec"),
    make_card("a2_time_saved", 755, 60, 230, 120, M, "Total Time Saved Hours"),
    make_slicer("a2_sl_rep",     1000, 60,  260, 35, "DimRep",      "RepName"),
    make_slicer("a2_sl_qtr",     1000, 100, 260, 35, "DimCalendar", "Quarter"),
    make_slicer("a2_sl_therapy", 1000, 140, 260, 35, "DimRep",      "TherapyArea"),
    make_clustered_bar("a2_topic_bar", 20, 195, 610, 270,
        "FactMSLPartnerUsage", "Topic", M, "Total MSL Queries"),
    make_donut("a2_query_donut", 645, 195, 615, 270,
        "FactMSLPartnerUsage", "QueryType", M, "Total MSL Queries"),
    make_line_chart("a2_adoption_trend", 20, 480, 1240, 210,
        "DimCalendar", "YearMonth",
        M, "MSL Queries Per MSL Per Day", M, "Fully Answered Rate"),
]

# ===== PAGE 3: MSL Partner ROI =====
p3 = uid("ep_ai_msl_roi")
P3 = [
    make_title_bar("a3_title", 0, 0, 1280, 50, "AI Impact \u2014 MSL Partner ROI", MAGENTA),
    make_card("a3_per_day",      20,  60, 300, 120, M, "MSL Queries Per MSL Per Day"),
    make_card("a3_interaction",  335, 60, 300, 120, M, "Used in HCP Interaction Rate"),
    make_card("a3_satisfaction", 650, 60, 300, 120, M, "Avg MSL Satisfaction"),
    make_slicer("a3_sl_qtr", 965, 60, 295, 120, "DimCalendar", "Quarter"),
    make_stacked_bar("a3_quality_bar", 20, 195, 1240, 270,
        "DimRep", "RepName",
        "FactMSLPartnerUsage", "AnswerQuality",
        M, "Total MSL Queries"),
    make_table("a3_scorecard", 20, 480, 1240, 220, [
        ("DimRep", "RepName",                    False),
        (M,        "Total MSL Queries",           True),
        (M,        "Fully Answered Rate",         True),
        (M,        "Avg Time to Answer Sec",      True),
        (M,        "Total Time Saved Hours",      True),
        (M,        "Used in HCP Interaction Rate", True),
        (M,        "Avg MSL Satisfaction",        True),
    ]),
]

write_page(p1, "AI Call Targeting",       P1)
write_page(p2, "MSL Partner Performance", P2)
write_page(p3, "MSL Partner ROI",         P3)
write_pages_json([p1, p2, p3])

print("AI Impact (condensed): 3 pages generated.")
