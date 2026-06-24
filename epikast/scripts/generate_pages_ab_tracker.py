"""
Epikast A/B TEST TRACKER report — experiment registry + script A/B deep dive.

2 pages:
  1. Experiment Overview  — registry table, lift bar, status KPIs
  2. Script A/B Deep Dive — rate comparison bars, specialty matrix

Run with Power BI closed:  python scripts/generate_pages_ab_tracker.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_card, make_slicer,
    make_clustered_bar, make_table,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_ab_dashb")

NAVY = "#1B3A5C"
M = "_Measures"

# ===== PAGE 1: Experiment Overview =====
p1 = uid("ep_ab_experiment_overview")
P1 = [
    make_title_bar("t1_title", 0, 0, 1280, 50, "A/B Test Tracker \u2014 Experiment Overview", NAVY),
    make_card("t1_total_exp",  20,  60, 230, 120, M, "Total Experiments"),
    make_card("t1_concluded",  265, 60, 230, 120, M, "Concluded Experiments"),
    make_card("t1_win_rate",   510, 60, 230, 120, M, "Win Rate"),
    make_card("t1_running",    755, 60, 230, 120, M, "Running Experiments"),
    make_slicer("t1_sl_status",  1000, 60,  260, 55, "DimExperiment", "Status"),
    make_slicer("t1_sl_therapy", 1000, 120, 260, 55, "DimExperiment", "TherapyArea"),
    make_table("t1_registry", 20, 195, 1240, 280, [
        ("DimExperiment", "ExperimentName",    False),
        ("DimExperiment", "Status",            False),
        ("DimExperiment", "PrimaryKPI",        False),
        ("DimExperiment", "StartDate",         False),
        ("DimExperiment", "EndDate",           False),
        ("DimExperiment", "SampleSizeActual",  False),
        ("DimExperiment", "SampleSizeTarget",  False),
        ("DimExperiment", "ObservedLift",      False),
        ("DimExperiment", "Winner",            False),
    ]),
    make_clustered_bar("t1_lift_bar", 20, 490, 1240, 200,
        "DimExperiment", "ExperimentName", M, "Avg Observed Lift"),
]

# ===== PAGE 2: Script A/B Deep Dive =====
p2 = uid("ep_ab_script_deep_dive")
P2 = [
    make_title_bar("t2_title", 0, 0, 1280, 50, "A/B Test Tracker \u2014 Script A/B Deep Dive", NAVY),
    make_card("t2_a_connect", 20,  60, 300, 120, M, "Script A Connect Rate"),
    make_card("t2_b_connect", 335, 60, 300, 120, M, "Script B Connect Rate"),
    make_slicer("t2_sl_month",   650,  60, 200, 55, "DimCalendar", "YearMonth"),
    make_slicer("t2_sl_therapy", 860,  60, 200, 55, "DimRep",      "TherapyArea"),
    make_slicer("t2_sl_region",  1070, 60, 190, 55, "DimHCP",      "Region"),
    make_clustered_bar("t2_script_rates", 20, 195, 610, 270,
        "FactHCPCalls", "Script", M, "Connect Rate"),
    make_clustered_bar("t2_script_duration", 645, 195, 615, 270,
        "FactHCPCalls", "Script", M, "Avg Call Duration"),
    make_table("t2_specialty_tbl", 20, 480, 1240, 220, [
        ("DimHCP",    "Specialty",               False),
        (M,           "Script A Connect Rate",    True),
        (M,           "Script B Connect Rate",    True),
        (M,           "Script A Meaningful Rate", True),
        (M,           "Script B Meaningful Rate", True),
        (M,           "Script A Avg Duration",    True),
        (M,           "Script B Avg Duration",    True),
    ]),
]

write_page(p1, "Experiment Overview",  P1)
write_page(p2, "Script A/B Deep Dive", P2)
write_pages_json([p1, p2])

print("A/B Test Tracker: 2 pages generated.")
