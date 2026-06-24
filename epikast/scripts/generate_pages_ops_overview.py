"""
Epikast SMART OPS OVERVIEW report — 6 pages (CSO view).

  1. Command Center     — KPI cards + signal cards + trend line + team bar
  2. Call Outcomes      — outcome donut + specialty bar
  3. Day-of-Week        — heatmap matrix
  4. Rep Performance    — scatter plot
  5. Rep Scorecard      — full scorecard table
  6. Trends             — 3 trend lines + monthly summary table

Uses card_row() / slicer_row() from pbir_lib for autoscaling layouts.
Run with Power BI closed:  python scripts/generate_pages_ops_overview.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar,
    make_clustered_bar, make_line_chart, make_donut,
    make_matrix, make_scatter, make_table,
    card_row, slicer_row,
    CARD_H, SLICER_H, GAP, TITLE_BOT,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_ops_dashb")

NAVY = "#1B3A5C"
M = "_Measures"


# Standard 4-slicer row: Client / Team / Quarter / TherapyArea
def std_slicers(prefix, y):
    return slicer_row(prefix, y, SLICER_H, [
        ("DimRep",      "Client"),
        ("DimRep",      "Team"),
        ("DimCalendar", "Quarter"),
        ("DimRep",      "TherapyArea"),
    ])


# ── Helpers for common y positions ───────────────────────────────────────────
# Page with slicers only:
#   title(50) + gap(10) = 60 → slicers → gap(10) → content
SL_Y      = TITLE_BOT                              # 60
CONTENT_Y = SL_Y + SLICER_H + GAP                 # 108  content after 1 slicer row
CONTENT_H = 720 - CONTENT_Y - 10                  # 602  fill to bottom with 10px margin

# Page with 1 card row + slicers:
#   title → cards → slicers → content
CARD1_Y   = TITLE_BOT                             # 60
SL1_Y     = CARD1_Y + CARD_H + GAP               # 190
BODY1_Y   = SL1_Y + SLICER_H + GAP               # 238
BODY1_H   = 720 - BODY1_Y - 10                   # 472


# ===== PAGE 1: Command Center =====
p1 = uid("ep_smart_command_center")

# Layout:  title | cards(120) | cards(120) | slicers(38) | charts fill
R1_Y = TITLE_BOT                                   # 60
R2_Y = R1_Y + CARD_H + GAP                        # 190
SL_P1_Y = R2_Y + CARD_H + GAP                     # 320
CHART_Y = SL_P1_Y + SLICER_H + GAP                # 368
CHART_H = 720 - CHART_Y - 10                      # 342

P1 = [
    make_title_bar("s1_title", 0, 0, 1280, 50, "Command Center", NAVY),

    *card_row("s1r1", R1_Y, CARD_H, [
        "Total Calls",
        "Connect Rate",
        "Meaningful Interaction Rate",
        "Avg AHT",
        "Schedule Adherence Rate",
    ]),

    *card_row("s1r2", R2_Y, CARD_H, [
        "Calls WoW Change",
        "Connect Rate L4W",
        "Calls L4W",
        "AI Lift on Connect Rate",
        "Running Experiments",
        "Win Rate",
    ]),

    *std_slicers("s1", SL_P1_Y),

    make_line_chart("s1_trend", 20, CHART_Y, 840, CHART_H,
        "DimCalendar", "YearMonth", M, "Total Calls", M, "Connect Rate"),
    make_clustered_bar("s1_team_bar", 875, CHART_Y, 385, CHART_H,
        "DimRep", "Team", M, "Total Calls"),
]


# ===== PAGE 2: Call Outcomes =====
p2 = uid("ep_ops_call_outcomes_v2")
P2 = [
    make_title_bar("o2_title", 0, 0, 1280, 50, "Call Outcomes", NAVY),
    *std_slicers("o2", SL_Y),
    make_donut("o2_outcome_donut", 20, CONTENT_Y, 620, CONTENT_H,
        "FactHCPCalls", "CallOutcome", M, "Total Calls"),
    make_clustered_bar("o2_specialty_bar", 655, CONTENT_Y, 605, CONTENT_H,
        "DimHCP", "Specialty", M, "Connect Rate"),
]


# ===== PAGE 3: Day-of-Week Heatmap =====
p3 = uid("ep_ops_dow_heatmap")
P3 = [
    make_title_bar("o3_title", 0, 0, 1280, 50, "Day-of-Week Patterns", NAVY),
    *std_slicers("o3", SL_Y),
    make_matrix("o3_heatmap", 20, CONTENT_Y, 1240, CONTENT_H,
        [("DimCalendar", "DayOfWeek")],
        [],
        [(M, "Total Calls"), (M, "Connect Rate"), (M, "Meaningful Interaction Rate")]),
]


# ===== PAGE 4: Rep Performance Scatter =====
p4 = uid("ep_smart_rep_performance")
P4 = [
    make_title_bar("o4_title", 0, 0, 1280, 50, "Rep Performance", NAVY),

    *card_row("o4r1", CARD1_Y, CARD_H, [
        "Calls Per Rep Per Day",
        "Connect Rate",
        "Notes Compliance Rate",
        "Schedule Adherence Rate",
    ]),

    *std_slicers("o4", SL1_Y),

    make_scatter("o4_scatter", 20, BODY1_Y, 1240, BODY1_H,
        "DimRep", "RepName",
        M, "Total Calls",
        M, "Connect Rate",
        M, "Meaningful Interactions"),
]


# ===== PAGE 5: Rep Scorecard =====
p5 = uid("ep_smart_rep_scorecard")
P5 = [
    make_title_bar("o5_title", 0, 0, 1280, 50, "Rep Scorecard", NAVY),
    *std_slicers("o5", SL_Y),
    make_table("o5_table", 20, CONTENT_Y, 1240, CONTENT_H, [
        ("DimRep", "Client",                     False),
        ("DimRep", "RepName",                    False),
        ("DimRep", "Team",                       False),
        (M,        "Total Calls",                True),
        (M,        "Connected Calls",            True),
        (M,        "Connect Rate",               True),
        (M,        "Meaningful Interaction Rate", True),
        (M,        "Avg AHT",                    True),
        (M,        "Schedule Adherence Rate",    True),
        (M,        "Notes Compliance Rate",      True),
        (M,        "Calls Per Rep Per Day",      True),
    ]),
]


# ===== PAGE 6: Trends =====
p6 = uid("ep_smart_trends")

# 3 equal trend lines stacked + summary table on right
TREND_H = (CONTENT_H - 2 * GAP) // 3              # ~190 each

P6 = [
    make_title_bar("o6_title", 0, 0, 1280, 50, "Trends", NAVY),
    *std_slicers("o6", SL_Y),
    make_line_chart("o6_connect_trend", 20, CONTENT_Y, 960, TREND_H,
        "DimCalendar", "YearMonth", M, "Connect Rate", M, "Connect Rate L4W"),
    make_line_chart("o6_aht_trend", 20, CONTENT_Y + TREND_H + GAP, 960, TREND_H,
        "DimCalendar", "YearMonth", M, "Avg AHT"),
    make_line_chart("o6_sched_trend", 20, CONTENT_Y + 2 * (TREND_H + GAP), 960, TREND_H,
        "DimCalendar", "YearMonth", M, "Schedule Adherence Rate"),
    make_table("o6_summary", 995, CONTENT_Y, 265, CONTENT_H, [
        ("DimCalendar", "YearMonth",   False),
        (M,             "Total Calls",  True),
        (M,             "Connect Rate", True),
        (M,             "Avg AHT",      True),
    ]),
]


write_page(p1, "Command Center",   P1)
write_page(p2, "Call Outcomes",    P2)
write_page(p3, "Day of Week",      P3)
write_page(p4, "Rep Performance",  P4)
write_page(p5, "Rep Scorecard",    P5)
write_page(p6, "Trends",           P6)
write_pages_json([p1, p2, p3, p4, p5, p6])

print("Smart Ops Overview: 6 pages generated.")
