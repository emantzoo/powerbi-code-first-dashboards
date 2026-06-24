"""
Epikast INTERNAL OPS report — for Epikast's own delivery / operations teams.

7 pages: Exec Summary, Call Outcomes, Rep Productivity (+ selling-time &
top-performer analyses), Trends, Compliance & Quality, Channel Mix & Workforce,
Patient Ops & Drill-Down.
Rep-level detail — NOT for clients. Runs against the shared Epikast Pharma Ops
model (Epikast_Dashboard_Prompts.md). Requires the Performance Tier / Tenure
Bucket / CallTimeBucket calculated columns from that file.

Run with Power BI closed:  python scripts/generate_pages_internal.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_clustered_bar,
    make_clustered_bar_gradient, make_clustered_column, make_clustered_column_multi,
    make_combo_chart, make_line_chart, make_donut, make_scatter, make_matrix_heatmap,
    make_decomposition_tree, make_measure_column,
    make_table, card_row, slicer_row,
    CARD_H, SLICER_H, GAP, TITLE_BOT,
    CARD1_Y, SL1_Y, BODY1_Y, BODY1_H,
    SL_Y, BODY_Y, BODY_H,
    make_r_visual,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_internal_dashb")

NAVY = "#1B3A5C"
M    = "_Measures"

# Standard internal slicers: Client / Team / Quarter / TherapyArea
def int_slicers(prefix, y):
    return slicer_row(prefix, y, SLICER_H, [
        ("DimRep",      "Client"),
        ("DimRep",      "Team"),
        ("DimCalendar", "Quarter"),
        ("DimHCP",      "TherapyArea"),
    ])


# ===== PAGE 1: Exec Summary =====
p1 = uid("epi_int_p1_exec")

EXEC_MID_H = (BODY1_H - GAP) // 2   # ~231

P1 = [
    make_title_bar("i1_t", 0, 0, 1280, 50, "Epikast Ops — Executive Summary", NAVY),

    *card_row("i1r1", CARD1_Y, CARD_H, [
        "Total Calls",
        "Connect Rate",
        "Meaningful Interaction Rate",
        "Avg AHT",
        "Schedule Adherence Rate",
    ]),

    *int_slicers("i1", SL1_Y),

    make_combo_chart("i1_combo", 20, BODY1_Y, 740, EXEC_MID_H,
        "DimCalendar", "YearMonth", M, "Total Calls", M, "Connect Rate"),
    make_clustered_column_multi("i1_team_bar", 775, BODY1_Y, 485, EXEC_MID_H,
        "DimRep", "Team",
        [(M, "Total Calls"), (M, "Connected Calls"), (M, "Meaningful Interactions")]),

    make_table("i1_tbl", 20, BODY1_Y + EXEC_MID_H + GAP, 1240, BODY1_H - EXEC_MID_H - GAP, [
        ("DimCalendar", "YearMonth", False),
        (M, "Total Calls", True), (M, "Connect Rate", True),
        (M, "Meaningful Interaction Rate", True), (M, "Avg AHT", True),
        (M, "Schedule Adherence Rate", True),
    ]),
]


# ===== PAGE 2: Call Outcomes =====
p2 = uid("epi_int_p2_outcomes")

# Layout: title | slicers | donut+bar | heatmap
OUT_SL_Y    = TITLE_BOT
OUT_BODY_Y  = OUT_SL_Y + SLICER_H + GAP     # 108
OUT_DONUT_H = (720 - OUT_BODY_Y - 10) * 2 // 3   # ~2/3 of remaining
OUT_HEAT_Y  = OUT_BODY_Y + OUT_DONUT_H + GAP
OUT_HEAT_H  = 720 - OUT_HEAT_Y - 10

P2 = [
    make_title_bar("i2_t", 0, 0, 1280, 50, "Epikast Ops — Call Outcomes", NAVY),

    *slicer_row("i2sl", OUT_SL_Y, SLICER_H, [
        ("DimRep",      "Client"),
        ("DimRep",      "Team"),
        ("DimCalendar", "YearMonth"),
        ("DimHCP",      "TherapyArea"),
    ]),

    make_donut("i2_donut", 20, OUT_BODY_Y, 400, OUT_DONUT_H,
        "FactHCPCalls", "CallOutcome", M, "Total Calls"),
    make_clustered_bar("i2_spec", 440, OUT_BODY_Y, 820, OUT_DONUT_H,
        "DimHCP", "Specialty", M, "Connect Rate"),

    make_matrix_heatmap("i2_heat", 20, OUT_HEAT_Y, 1240, OUT_HEAT_H,
        [("DimCalendar", "DayOfWeek")], [("FactHCPCalls", "CallTimeBucket")],
        M, "Connect Rate"),
]


# ===== PAGE 3: Rep Productivity =====
p3 = uid("epi_int_p3_reps")

REP_MID_H = (BODY1_H - GAP) // 2

P3 = [
    make_title_bar("i3_t", 0, 0, 1280, 50, "Epikast Ops — Rep Productivity", NAVY),

    *card_row("i3r1", CARD1_Y, CARD_H, [
        "Calls Per Rep Per Day",
        "Connected Calls Per Rep Per Day",
        "Notes Compliance Rate",
        "Selling Time Pct",
    ]),

    *slicer_row("i3sl", SL1_Y, SLICER_H, [
        ("DimRep",      "Client"),
        ("DimRep",      "Team"),
        ("DimCalendar", "YearMonth"),
        ("DimRep",      "Role"),
    ]),

    make_scatter("i3_scatter", 20, BODY1_Y, 620, REP_MID_H,
        "DimRep", "RepName",
        M, "Total Calls", M, "Connect Rate",
        size_table=M, size_measure="Meaningful Interactions",
        series_table="DimRep", series_col="Team"),
    make_clustered_column_multi("i3_top", 660, BODY1_Y, 600, REP_MID_H,
        "DimRep", "Performance Tier",
        [(M, "AI Acceptance Rate"), (M, "Follow Up Rate"),
         (M, "Notes Compliance Rate"), (M, "Meaningful Interaction Rate")]),

    make_table("i3_tbl", 20, BODY1_Y + REP_MID_H + GAP, 1240, BODY1_H - REP_MID_H - GAP, [
        ("DimRep", "Client",             False),
        ("DimRep", "RepName",            False),
        ("DimRep", "Performance Tier",   False),
        (M, "Total Calls", True), (M, "Connect Rate", True),
        (M, "Meaningful Interaction Rate", True), (M, "Avg AHT", True),
        (M, "Schedule Adherence Rate", True), (M, "Notes Compliance Rate", True),
    ]),
]


# ===== PAGE 4: Trends =====
p4 = uid("epi_int_p4_trends")

# 3 stacked trend lines + compact slicer bar at top
TR_SL_Y   = TITLE_BOT
TR_BODY_Y = TR_SL_Y + SLICER_H + GAP    # 108
TR_BODY_H = 720 - TR_BODY_Y - 10        # 602
TR_LINE_H = (TR_BODY_H - 2 * GAP) // 3  # ~194 each

P4 = [
    make_title_bar("i4_t", 0, 0, 1280, 50, "Epikast Ops — Trends", NAVY),

    *slicer_row("i4sl", TR_SL_Y, SLICER_H, [
        ("DimRep",      "Client"),
        ("DimRep",      "Team"),
        ("DimHCP",      "TherapyArea"),
    ]),

    make_line_chart("i4_connect", 20, TR_BODY_Y, 1240, TR_LINE_H,
        "DimCalendar", "YearMonth", M, "Connect Rate", M, "Connect Rate L4W"),
    make_line_chart("i4_aht", 20, TR_BODY_Y + TR_LINE_H + GAP, 1240, TR_LINE_H,
        "DimCalendar", "YearMonth", M, "Avg AHT",
        ref_value=10, ref_label="Target 10 min"),
    make_line_chart("i4_sched", 20, TR_BODY_Y + 2 * (TR_LINE_H + GAP), 1240, TR_LINE_H,
        "DimCalendar", "YearMonth", M, "Schedule Adherence Rate",
        ref_value=0.85, ref_label="Target 85%"),
]


# ===== PAGE 5: Compliance & Quality =====
p5 = uid("epi_int_p5_compliance")

COMP_MID_H = (BODY1_H - GAP) // 2

P5 = [
    make_title_bar("i5_t", 0, 0, 1280, 50, "Epikast Ops — Compliance & Quality", NAVY),

    *card_row("i5r1", CARD1_Y, CARD_H, [
        "Script Deviation Rate",
        "Avg Call Quality Score",
        "AE Flag Rate",
        "High Quality Calls Pct",
        "Notes Compliance Rate",
    ]),

    *slicer_row("i5sl", SL1_Y, SLICER_H, [
        ("DimRep",      "Client"),
        ("DimRep",      "Team"),
        ("DimCalendar", "YearMonth"),
        ("DimHCP",      "TherapyArea"),
    ]),

    make_clustered_bar_gradient("i5_dev_bar", 20, BODY1_Y, 610, COMP_MID_H,
        "DimRep", "RepName", M, "Script Deviation Rate"),
    make_clustered_bar("i5_qual_bar", 650, BODY1_Y, 610, COMP_MID_H,
        "DimRep", "RepName", M, "Avg Call Quality Score"),

    make_line_chart("i5_trend", 20, BODY1_Y + COMP_MID_H + GAP, 620, BODY1_H - COMP_MID_H - GAP,
        "DimCalendar", "YearMonth", M, "Script Deviation Rate", M, "AE Flag Rate"),
    make_table("i5_tbl", 660, BODY1_Y + COMP_MID_H + GAP, 600, BODY1_H - COMP_MID_H - GAP, [
        ("DimRep", "Client",   False),
        ("DimRep", "RepName",  False),
        (M, "Script Deviation Rate", True), (M, "Avg Call Quality Score", True),
        (M, "AE Flag Rate", True), (M, "Notes Compliance Rate", True),
    ]),
]


# ===== PAGE 6: Channel Mix & Workforce =====
p6 = uid("epi_int_p6_workforce")

WF_MID_H = (BODY1_H - GAP) // 2

P6 = [
    make_title_bar("i6_t", 0, 0, 1280, 50, "Epikast Ops — Channel Mix & Workforce", NAVY),

    *card_row("i6r1", CARD1_Y, CARD_H, [
        "Phone Calls Pct",
        "Email Pct",
        "Video Pct",
        "Utilization Rate",
    ]),

    *slicer_row("i6sl", SL1_Y, SLICER_H, [
        ("DimRep",      "Client"),
        ("DimRep",      "Team"),
        ("DimCalendar", "YearMonth"),
        ("DimRep",      "Role"),
    ]),

    make_donut("i6_chan", 20, BODY1_Y, 360, WF_MID_H,
        "FactHCPCalls", "Channel", M, "Total Calls"),
    make_clustered_column_multi("i6_chan_perf", 400, BODY1_Y, 440, WF_MID_H,
        "FactHCPCalls", "Channel",
        [(M, "Connect Rate"), (M, "Meaningful Interaction Rate")]),
    make_clustered_column("i6_ramp", 860, BODY1_Y, 400, WF_MID_H,
        "DimRep", "Tenure Bucket", M, "Connect Rate"),

    make_table("i6_tbl", 20, BODY1_Y + WF_MID_H + GAP, 1240, BODY1_H - WF_MID_H - GAP, [
        ("DimRep", "Tenure Bucket", False),
        (M, "Connect Rate", True), (M, "Avg Call Quality Score", True),
        (M, "Script Deviation Rate", True), (M, "Utilization Rate", True),
        (M, "Calls Per Rep Per Day", True),
    ]),
]


# ===== PAGE 7: Patient Ops & Drill-Down =====
p7 = uid("epi_int_p7_patientops")

PAT_SL_Y   = TITLE_BOT
PAT_BODY_Y = PAT_SL_Y + SLICER_H + GAP     # 108
PAT_BODY_H = 720 - PAT_BODY_Y - 10          # 602
PAT_TOP_H  = 110
PAT_MID_Y  = PAT_BODY_Y + PAT_TOP_H + GAP
PAT_MID_H  = (PAT_BODY_H - PAT_TOP_H - GAP - GAP) // 2   # ~231
PAT_BOT_Y  = PAT_MID_Y + PAT_MID_H + GAP
PAT_BOT_H  = 720 - PAT_BOT_Y - 10

P7 = [
    make_title_bar("i7_t", 0, 0, 1280, 50, "Epikast Ops — Patient Ops & Drill-Down", NAVY),

    *slicer_row("i7sl", PAT_SL_Y, SLICER_H, [
        ("DimRep",      "Client"),
        ("DimRep",      "Team"),
    ]),

    *card_row("i7r1", PAT_BODY_Y, PAT_TOP_H, [
        "Calls Last 7 Days",
        "Calls WoW Change",
        "Active Cases",
        "Open High Risk Cases",
        "Avg Time to Therapy",
    ]),

    make_decomposition_tree("i7_decomp", 20, PAT_MID_Y, 620, PAT_MID_H,
        (M, "Meaningful Interaction Rate"),
        [("FactHCPCalls", "AIFollowed"), ("FactHCPCalls", "Channel"),
         ("DimRep", "Role"), ("DimHCP", "Specialty")]),

    make_measure_column("i7_funnel", 660, PAT_MID_Y, 600, PAT_MID_H // 2 - GAP,
        [(M, "Total Cases"), (M, "Cases First Contacted"), (M, "Cases PA Approved"),
         (M, "Cases Fulfilled"), (M, "Cases On Therapy")]),
    make_clustered_bar("i7_aging", 660, PAT_MID_Y + PAT_MID_H // 2, 600, PAT_MID_H // 2,
        "FactPatientCases", "Open Case Age Bucket", M, "Active Cases"),

    make_r_visual("i7_box", 20, PAT_BOT_Y, 1240, PAT_BOT_H,
        [("FactHCPCalls", "CallID", False), ("DimRep", "Team", False),
         ("FactHCPCalls", "AHT_Minutes", False)],
        "library(ggplot2)\n"
        "ggplot(dataset, aes(x=Team, y=AHT_Minutes, fill=Team)) +\n"
        "  geom_boxplot(outlier.alpha=0.25) +\n"
        "  labs(title='AHT distribution by team', x=NULL, y='AHT (min)') +\n"
        "  theme_minimal(base_size=12) + theme(legend.position='none')"),
]


write_page(p1, "Executive Summary",       P1)
write_page(p2, "Call Outcomes",           P2)
write_page(p3, "Rep Productivity",        P3)
write_page(p4, "Trends",                  P4)
write_page(p5, "Compliance & Quality",    P5)
write_page(p6, "Channel Mix & Workforce", P6)
write_page(p7, "Patient Ops & Drill-Down", P7)
write_pages_json([p1, p2, p3, p4, p5, p6, p7])

print("INTERNAL OPS report — 7 pages")
for n, pg in [("Executive Summary", P1), ("Call Outcomes", P2), ("Rep Productivity", P3),
              ("Trends", P4), ("Compliance & Quality", P5), ("Channel Mix & Workforce", P6),
              ("Patient Ops & Drill-Down", P7)]:
    print(f"  {n}: {len(pg)} visuals")
print(f"Total: {sum(len(p) for p in [P1,P2,P3,P4,P5,P6,P7])} visuals")
print("Done!")
