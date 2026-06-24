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
TEAL = "#2E86AB"
M = "_Measures"


def _section_label(name, x, y, w, h, text, bg="#2E86AB"):
    """Thin coloured header band — reuses make_title_bar with smaller font via bg override."""
    return pb.make_title_bar(name, x, y, w, h, text, bg_color=bg)


def _card_accent(name, x, y, w, h, measure, hex_color):
    """Card with a coloured accent bar (uses standard make_card — accent colour set via theme)."""
    return make_card(name, x, y, w, h, M, measure)


# ===== PAGE 1: Command Center =====
p1 = uid("ep_smart_command_center")
P1 = [
    make_title_bar("s1_title", 0, 0, 1280, 50, "Command Center", NAVY),

    # Core KPIs
    make_card("s1_total_calls",  20,  55, 160, 100, M, "Total Calls"),
    make_card("s1_connect_rate", 190, 55, 160, 100, M, "Connect Rate"),
    make_card("s1_meaningful",   360, 55, 160, 100, M, "Meaningful Interaction Rate"),
    make_card("s1_aht",          530, 55, 160, 100, M, "Avg AHT"),
    make_card("s1_sched_adh",    700, 55, 160, 100, M, "Schedule Adherence Rate"),
    make_slicer("s1_sl_quarter", 880,  55, 190, 30, "DimCalendar", "Quarter"),
    make_slicer("s1_sl_team",    880,  90, 190, 30, "DimRep",      "Team"),
    make_slicer("s1_sl_therapy", 880, 125, 190, 30, "DimRep",      "TherapyArea"),

    # Anomaly Alerts panel
    _section_label("s1_anom_hdr",   20, 165, 400, 28, "\u26A0  Anomaly Alerts", "#CD3333"),
    _card_accent("s1_wow_flag",      20, 197, 195, 85, "Connect Rate WoW Flag",                    "#CD3333"),
    _card_accent("s1_worst_spec",   220, 197, 200, 85, "Worst Performing Specialty This Week",     "#DAA520"),
    make_card("s1_worst_spec_cr",    20, 287, 195, 75, M, "Worst Specialty Connect Rate"),
    make_card("s1_wow_change",      220, 287, 200, 75, M, "Connect Rate WoW Change"),

    # Cross-Dashboard Alerts panel
    _section_label("s1_xdash_hdr", 435, 165, 400, 28, "\u2194  Cross-Dashboard Alerts", "#A23B72"),
    _card_accent("s1_funnel_rate",  435, 197, 195, 85, "Funnel Alert Abandonment Rate",  "#A23B72"),
    _card_accent("s1_funnel_stage", 635, 197, 200, 85, "Funnel Alert Worst Stage",        "#A23B72"),
    make_card("s1_funnel_cases",    435, 287, 195, 75, M, "Funnel Alert Worst Stage Cases"),
    _card_accent("s1_ai_lift",      635, 287, 200, 75, "AI Lift on Connect Rate",         TEAL),

    # Top/Bottom Movers panel
    _section_label("s1_movers_hdr", 850, 165, 410, 28, "\u2195  Top/Bottom Movers", "#2E8B57"),
    _card_accent("s1_top_rep",      850, 197, 200, 85, "Top Rep Connect Rate Improvement", "#2E8B57"),
    _card_accent("s1_top_val",     1055, 197, 205, 85, "Top Rep Improvement Value",        "#2E8B57"),
    _card_accent("s1_bot_rep",      850, 287, 200, 75, "Bottom Rep Connect Rate Decline",  "#CD3333"),
    _card_accent("s1_bot_val",     1055, 287, 205, 75, "Bottom Rep Decline Value",         "#CD3333"),

    # Experiment status bar
    _section_label("s1_exp_hdr",  20, 372, 200, 28, "\U0001F9EA  Experiments", NAVY),
    make_card("s1_exp_progress",  225, 372, 770, 28, M, "Running Experiment Progress"),
    make_card("s1_exp_running",  1000, 372, 130, 28, M, "Running Experiments"),
    make_card("s1_exp_winrate",  1135, 372, 125, 28, M, "Win Rate"),

    # Trend + team bar
    make_line_chart("s1_trend", 20, 410, 850, 295,
        "DimCalendar", "YearMonth", M, "Total Calls", M, "Connect Rate"),
    make_clustered_bar("s1_team_bar", 885, 410, 375, 295,
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
    make_matrix("o2_heatmap", 20, 375, 1240, 290,
        [("DimCalendar", "DayOfWeek")],
        [],
        [(M, "Total Calls"), (M, "Connect Rate"), (M, "Meaningful Interaction Rate")]),
    make_slicer("o2_sl_month", 20,  675, 200, 35, "DimCalendar", "YearMonth"),
    make_slicer("o2_sl_team",  230, 675, 200, 35, "DimRep",      "Team"),
]

# ===== PAGE 3: Rep Performance =====
p3 = uid("ep_smart_rep_performance")
P3 = [
    make_title_bar("o3_title", 0, 0, 1280, 50, "Rep Performance", NAVY),
    make_card("o3_calls_per_rep", 20,  60, 190, 100, M, "Calls Per Rep Per Day"),
    make_card("o3_notes_comply",  220, 60, 190, 100, M, "Notes Compliance Rate"),
    _section_label("o3_sched_hdr", 425, 60, 410, 25, "\U0001F4C5  Schedule Insight", TEAL),
    _card_accent("o3_best_day",  425, 88, 200, 72, "Best Day",                  "#2E8B57"),
    _card_accent("o3_worst_day", 635, 88, 200, 72, "Worst Day",                 "#CD3333"),
    make_card("o3_best_cr",  425, 60, 100, 25, M, "Best Time Slot Connect Rate"),
    make_card("o3_worst_cr", 635, 60, 100, 25, M, "Worst Day Connect Rate"),
    make_slicer("o3_sl_month", 855,  60, 190, 50, "DimCalendar", "YearMonth"),
    make_slicer("o3_sl_team",  1055, 60, 205, 50, "DimRep",      "Team"),
    make_scatter("o3_scatter", 20, 170, 1240, 260,
        "DimRep", "RepName",
        M, "Total Calls",
        M, "Connect Rate",
        M, "Meaningful Interactions"),
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
