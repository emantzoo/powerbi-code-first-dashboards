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
    uid, make_title_bar,
    make_clustered_bar, make_line_chart, make_donut,
    make_stacked_bar, make_table,
    card_row, slicer_row,
    TITLE_H, CARD_H, SLICER_H, GAP, TITLE_BOT, std_layout,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_ai_dashb")

MAGENTA = "#A23B72"
M       = "_Measures"

# Derived positions
_L      = std_layout(n_card_rows=1, n_slicer_rows=1)
CARD1_Y = _L["card_y"]    # 60
SL1_Y   = _L["slicer_y"]  # 190
BODY1_Y = _L["body_y"]    # 238
BODY1_H = _L["body_h"]    # 472

_LS    = std_layout(n_card_rows=0, n_slicer_rows=1)
SL_Y   = _LS["slicer_y"]  # 60
BODY_Y = _LS["body_y"]    # 108
BODY_H = _LS["body_h"]    # 602


# ===== PAGE 1: AI Call Targeting =====
p1 = uid("ep_ai_targeting")

AI_BARS_H = BODY1_H * 2 // 3       # ~315 bars
AI_TREND_H = BODY1_H - AI_BARS_H - GAP  # ~147

P1 = [
    make_title_bar("a1_title", 0, 0, 1280, 50, "AI Impact \u2014 Call Targeting", MAGENTA),

    *card_row("a1r1", CARD1_Y, CARD_H, [
        "AI Connect Rate",
        "Non-AI Connect Rate",
        "AI Acceptance Rate",
        "AI Lift on Connect Rate",
    ]),

    *slicer_row("a1sl", SL1_Y, SLICER_H, [
        ("DimCalendar", "Quarter"),
        ("DimHCP",      "Tier"),
        ("DimRep",      "TherapyArea"),
    ]),

    make_clustered_bar("a1_rates_bar", 20, BODY1_Y, 610, AI_BARS_H,
        "DimRep", "TherapyArea", M, "AI Connect Rate"),
    make_clustered_bar("a1_lift_bar", 650, BODY1_Y, 610, AI_BARS_H,
        "DimRep", "TherapyArea", M, "AI Lift on Connect Rate"),

    make_line_chart("a1_accept_trend", 20, BODY1_Y + AI_BARS_H + GAP, 1240, AI_TREND_H,
        "DimCalendar", "YearMonth", M, "AI Acceptance Rate"),
]


# ===== PAGE 2: MSL Partner Performance =====
p2 = uid("ep_ai_msl_performance")

MSL_BARS_H  = BODY1_H * 2 // 3
MSL_TREND_H = BODY1_H - MSL_BARS_H - GAP

P2 = [
    make_title_bar("a2_title", 0, 0, 1280, 50, "AI Impact \u2014 MSL Partner Performance", MAGENTA),

    *card_row("a2r1", CARD1_Y, CARD_H, [
        "Total MSL Queries",
        "Fully Answered Rate",
        "Avg Time to Answer Sec",
        "Total Time Saved Hours",
    ]),

    *slicer_row("a2sl", SL1_Y, SLICER_H, [
        ("DimRep",      "RepName"),
        ("DimCalendar", "Quarter"),
        ("DimRep",      "TherapyArea"),
    ]),

    make_clustered_bar("a2_topic_bar", 20, BODY1_Y, 610, MSL_BARS_H,
        "FactMSLPartnerUsage", "Topic", M, "Total MSL Queries"),
    make_donut("a2_query_donut", 650, BODY1_Y, 610, MSL_BARS_H,
        "FactMSLPartnerUsage", "QueryType", M, "Total MSL Queries"),

    make_line_chart("a2_adoption_trend", 20, BODY1_Y + MSL_BARS_H + GAP, 1240, MSL_TREND_H,
        "DimCalendar", "YearMonth",
        M, "MSL Queries Per MSL Per Day", M, "Fully Answered Rate"),
]


# ===== PAGE 3: MSL Partner ROI =====
p3 = uid("ep_ai_msl_roi")

ROI_SL_Y    = TITLE_BOT
ROI_BODY_Y  = ROI_SL_Y + SLICER_H + GAP    # 108
ROI_BODY_H  = 720 - ROI_BODY_Y - 10        # 602
ROI_BAR_H   = ROI_BODY_H * 2 // 5          # ~240 stacked bar
ROI_TBL_H   = ROI_BODY_H - ROI_BAR_H - GAP # ~352

P3 = [
    make_title_bar("a3_title", 0, 0, 1280, 50, "AI Impact \u2014 MSL Partner ROI", MAGENTA),

    *slicer_row("a3sl", ROI_SL_Y, SLICER_H, [
        ("DimCalendar", "Quarter"),
    ]),

    *card_row("a3r1", ROI_BODY_Y, CARD_H, [
        "MSL Queries Per MSL Per Day",
        "Used in HCP Interaction Rate",
        "Avg MSL Satisfaction",
    ]),

    make_stacked_bar("a3_quality_bar", 20, ROI_BODY_Y + CARD_H + GAP, 1240, ROI_BAR_H,
        "DimRep", "RepName",
        "FactMSLPartnerUsage", "AnswerQuality",
        M, "Total MSL Queries"),

    make_table("a3_scorecard", 20, ROI_BODY_Y + CARD_H + GAP + ROI_BAR_H + GAP, 1240, ROI_TBL_H - CARD_H - GAP, [
        ("DimRep", "RepName",                     False),
        (M,        "Total MSL Queries",            True),
        (M,        "Fully Answered Rate",          True),
        (M,        "Avg Time to Answer Sec",       True),
        (M,        "Total Time Saved Hours",       True),
        (M,        "Used in HCP Interaction Rate", True),
        (M,        "Avg MSL Satisfaction",         True),
    ]),
]


write_page(p1, "AI Call Targeting",       P1)
write_page(p2, "MSL Partner Performance", P2)
write_page(p3, "MSL Partner ROI",         P3)
write_pages_json([p1, p2, p3])

print("AI Impact (condensed): 3 pages generated.")
