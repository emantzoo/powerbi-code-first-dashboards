"""
Epikast A/B TEST TRACKER report — experiment registry + script A/B deep dive.

2 pages:
  1. Experiment Overview  — registry table, lift bar, status KPIs
  2. Script A/B Deep Dive — rate comparison bars, specialty matrix

Run with Power BI closed:  python scripts/generate_pages_ab_tracker.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar,
    make_clustered_bar, make_table,
    card_row, slicer_row,
    TITLE_H, CARD_H, SLICER_H, GAP, TITLE_BOT, std_layout,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_ab_dashb")

NAVY = "#1B3A5C"
M    = "_Measures"

# Derived positions
_L      = std_layout(n_card_rows=1, n_slicer_rows=1)
CARD1_Y = _L["card_y"]    # 60
SL1_Y   = _L["slicer_y"]  # 190
BODY1_Y = _L["body_y"]    # 238
BODY1_H = _L["body_h"]    # 472


# ===== PAGE 1: Experiment Overview =====
p1 = uid("ep_ab_experiment_overview")

REG_H  = BODY1_H * 3 // 5   # ~283 for registry
LIFT_H = BODY1_H - REG_H - GAP   # ~179 for lift bar

P1 = [
    make_title_bar("t1_title", 0, 0, 1280, 50, "A/B Test Tracker \u2014 Experiment Overview", NAVY),

    *card_row("t1r1", CARD1_Y, CARD_H, [
        "Total Experiments",
        "Concluded Experiments",
        "Win Rate",
        "Running Experiments",
    ]),

    *slicer_row("t1sl", SL1_Y, SLICER_H, [
        ("DimExperiment", "Status"),
        ("DimExperiment", "TherapyArea"),
    ]),

    make_table("t1_registry", 20, BODY1_Y, 1240, REG_H, [
        ("DimExperiment", "ExperimentName",   False),
        ("DimExperiment", "Status",           False),
        ("DimExperiment", "PrimaryKPI",       False),
        ("DimExperiment", "StartDate",        False),
        ("DimExperiment", "EndDate",          False),
        ("DimExperiment", "SampleSizeActual", False),
        ("DimExperiment", "SampleSizeTarget", False),
        ("DimExperiment", "ObservedLift",     False),
        ("DimExperiment", "Winner",           False),
    ]),

    make_clustered_bar("t1_lift_bar", 20, BODY1_Y + REG_H + GAP, 1240, LIFT_H,
        "DimExperiment", "ExperimentName", M, "Avg Observed Lift"),
]


# ===== PAGE 2: Script A/B Deep Dive =====
p2 = uid("ep_ab_script_deep_dive")

SL_ONLY_Y = TITLE_BOT
BODY2_Y   = SL_ONLY_Y + SLICER_H + GAP    # 108
BODY2_H   = 720 - BODY2_Y - 10            # 602
TOP2_H    = (BODY2_H - GAP) * 2 // 5      # ~238 top bars
BOT2_H    = BODY2_H - TOP2_H - GAP        # ~354 table

P2 = [
    make_title_bar("t2_title", 0, 0, 1280, 50, "A/B Test Tracker \u2014 Script A/B Deep Dive", NAVY),

    *slicer_row("t2sl", SL_ONLY_Y, SLICER_H, [
        ("DimCalendar",  "YearMonth"),
        ("DimRep",       "TherapyArea"),
        ("DimHCP",       "Region"),
    ]),

    *card_row("t2r1", BODY2_Y, CARD_H, [
        "Script A Connect Rate",
        "Script B Connect Rate",
    ]),

    make_clustered_bar("t2_script_rates", 20, BODY2_Y + CARD_H + GAP, 610, TOP2_H - CARD_H - GAP,
        "FactHCPCalls", "Script", M, "Connect Rate"),
    make_clustered_bar("t2_script_duration", 650, BODY2_Y + CARD_H + GAP, 610, TOP2_H - CARD_H - GAP,
        "FactHCPCalls", "Script", M, "Avg Call Duration"),

    make_table("t2_specialty_tbl", 20, BODY2_Y + TOP2_H + GAP, 1240, BOT2_H - CARD_H, [
        ("DimHCP", "Specialty",               False),
        (M,        "Script A Connect Rate",    True),
        (M,        "Script B Connect Rate",    True),
        (M,        "Script A Meaningful Rate", True),
        (M,        "Script B Meaningful Rate", True),
        (M,        "Script A Avg Duration",    True),
        (M,        "Script B Avg Duration",    True),
    ]),
]


write_page(p1, "Experiment Overview",  P1)
write_page(p2, "Script A/B Deep Dive", P2)
write_pages_json([p1, p2])

print("A/B Test Tracker: 2 pages generated.")
