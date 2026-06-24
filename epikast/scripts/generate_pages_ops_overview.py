"""
Epikast SMART OPS OVERVIEW report — command center, call outcomes, rep performance, trends.

4 pages:
  1. Command Center      — anomaly alerts, cross-dashboard signals, top/bottom movers
  2. Call Outcomes       — outcome donut, specialty bar, day-of-week matrix
  3. Rep Performance     — schedule insight, scatter, scorecard table
  4. Trends & Optimization — trend lines, MoM cards, monthly summary

Run with Power BI closed:  python scripts/generate_pages_ops_overview.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_card, make_slicer,
    make_clustered_bar, make_line_chart, make_donut,
    make_matrix, make_scatter, make_table,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_ops_dashb")

NAVY = "#1B3A5C"
M = "_Measures"



# ===== PAGE 1: Command Center =====
p1 = uid("ep_smart_command_center")
P1 = [
    make_title_bar("s1_title", 0, 0, 1280, 50, "Command Center", NAVY),

    # Row 1: Core KPIs
    make_card("s1_total_calls",  20,  60, 190, 100, M, "Total Calls"),
    make_card("s1_connect_rate", 220, 60, 190, 100, M, "Connect Rate"),
    make_card("s1_meaningful",   420, 60, 190, 100, M, "Meaningful Interaction Rate"),
    make_card("s1_aht",          620, 60, 190, 100, M, "Avg AHT"),
    make_card("s1_sched_adh",    820, 60, 190, 100, M, "Schedule Adherence Rate"),
    make_slicer("s1_sl_quarter", 1025, 60, 115, 30, "DimCalendar", "Quarter"),
    make_slicer("s1_sl_team",    1025, 95, 115, 30, "DimRep",      "Team"),
    make_slicer("s1_sl_therapy", 1145, 60, 115, 65, "DimRep",      "TherapyArea"),

    # Row 2: WoW + experiment signals (7 equal cards across full width)
    make_card("s1_calls_wow",    20,  175, 170, 90, M, "Calls WoW Change"),
    make_card("s1_cr_wow",       200, 175, 170, 90, M, "Connect Rate L4W"),
    make_card("s1_cr_mom",       380, 175, 170, 90, M, "Connect Rate MoM Change"),
    make_card("s1_calls_mom",    560, 175, 170, 90, M, "Calls MoM Change"),
    make_card("s1_ai_lift",      740, 175, 170, 90, M, "AI Lift on Connect Rate"),
    make_card("s1_exp_running",  920, 175, 170, 90, M, "Running Experiments"),
    make_card("s1_exp_winrate", 1100, 175, 160, 90, M, "Win Rate"),

    # Trend + team bar
    make_line_chart("s1_trend", 20, 280, 850, 415,
        "DimCalendar", "YearMonth", M, "Total Calls", M, "Connect Rate"),
    make_clustered_bar("s1_team_bar", 885, 280, 375, 415,
        "DimRep", "Team", M, "Total Calls"),
]

# ===== PAGE 2: Call Outcomes =====
p2 = uid("ep_ops_call_outcomes_v2")
P2 = [
    make_title_bar("o2_title", 0, 0, 1280, 50, "Call Outcomes", NAVY),
    make_donut("o2_outcome_donut", 20, 60, 600, 300,
        "FactHCPCalls", "CallOutcome", M, "Total Calls"),
    make_clustered_bar("o2_specialty_bar", 635, 60, 625, 300,
        "DimHCP", "Specialty", M, "Connect Rate"),
    make_matrix("o2_heatmap", 20, 375, 1240, 255,
        [("DimCalendar", "DayOfWeek")],
        [],
        [(M, "Total Calls"), (M, "Connect Rate"), (M, "Meaningful Interaction Rate")]),
    make_slicer("o2_sl_month", 20,  640, 200, 35, "DimCalendar", "YearMonth"),
    make_slicer("o2_sl_team",  230, 640, 200, 35, "DimRep",      "Team"),
]

# ===== PAGE 3: Rep Performance =====
p3 = uid("ep_smart_rep_performance")
P3 = [
    make_title_bar("o3_title", 0, 0, 1280, 50, "Rep Performance", NAVY),
    # Row 1: KPI cards
    make_card("o3_calls_per_rep",  20,  60, 230, 100, M, "Calls Per Rep Per Day"),
    make_card("o3_notes_comply",  260,  60, 230, 100, M, "Notes Compliance Rate"),
    make_card("o3_connect_rate",  500,  60, 230, 100, M, "Connect Rate"),
    make_card("o3_sched_adh",     740,  60, 230, 100, M, "Schedule Adherence Rate"),
    make_slicer("o3_sl_month",    985,  60, 135, 45, "DimCalendar", "YearMonth"),
    make_slicer("o3_sl_team",    1130,  60, 130, 45, "DimRep",      "Team"),
    # Scatter: Calls vs Connect Rate, sized by Meaningful Interactions
    make_scatter("o3_scatter", 20, 175, 1240, 255,
        "DimRep", "RepName",
        M, "Total Calls",
        M, "Connect Rate",
        M, "Meaningful Interactions"),
    # Scorecard table
    make_table("o3_table", 20, 445, 1240, 260, [
        ("DimRep", "RepName",                    False),
        ("DimRep", "Team",                       False),
        (M,        "Total Calls",                True),
        (M,        "Connected Calls",            True),
        (M,        "Connect Rate",               True),
        (M,        "Meaningful Interaction Rate", True),
        (M,        "Avg AHT",                    True),
        (M,        "Schedule Adherence Rate",    True),
        (M,        "Notes Compliance Rate",      True),
    ]),
]

# ===== PAGE 4: Trends & Optimization =====
p4 = uid("ep_smart_trends")
P4 = [
    make_title_bar("o4_title", 0, 0, 1280, 50, "Trends & Optimization", NAVY),
    make_line_chart("o4_connect_trend", 20, 60, 1010, 195,
        "DimCalendar", "YearMonth", M, "Connect Rate", M, "Connect Rate L4W"),
    make_line_chart("o4_aht_trend", 20, 265, 1010, 195,
        "DimCalendar", "YearMonth", M, "Avg AHT"),
    make_line_chart("o4_sched_trend", 20, 470, 1010, 195,
        "DimCalendar", "YearMonth", M, "Schedule Adherence Rate"),
    make_slicer("o4_sl_team",    1045, 60,  215, 45, "DimRep", "Team"),
    make_slicer("o4_sl_therapy", 1045, 115, 215, 45, "DimRep", "TherapyArea"),
    make_card("o4_calls_mom", 1045, 175, 215, 80, M, "Calls MoM Change"),
    make_card("o4_cr_mom",    1045, 265, 215, 80, M, "Connect Rate MoM Change"),
    make_table("o4_summary", 1045, 360, 215, 305, [
        ("DimCalendar", "YearMonth",  False),
        (M,             "Total Calls", True),
        (M,             "Connect Rate", True),
    ]),
]

write_page(p1, "Command Center",        P1)
write_page(p2, "Call Outcomes",         P2)
write_page(p3, "Rep Performance",       P3)
write_page(p4, "Trends & Optimization", P4)
write_pages_json([p1, p2, p3, p4])

print("Smart Ops Overview: 4 pages generated.")
