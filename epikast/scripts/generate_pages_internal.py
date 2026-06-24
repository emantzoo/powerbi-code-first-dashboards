"""
Epikast INTERNAL OPS report — for Epikast's own delivery / operations teams.

6 pages: Exec Summary, Call Outcomes, Rep Productivity (+ selling-time &
top-performer analyses), Trends, Compliance & Quality, Channel Mix & Workforce.
Rep-level detail — NOT for clients. Runs against the shared Epikast Pharma Ops
model (Epikast_Dashboard_Prompts.md). Requires the Performance Tier / Tenure
Bucket / CallTimeBucket calculated columns from that file.

Run with Power BI closed:  python scripts/generate_pages_internal.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_card, make_slicer, make_clustered_bar,
    make_clustered_bar_gradient, make_clustered_column, make_clustered_column_multi,
    make_combo_chart, make_line_chart, make_donut, make_scatter, make_matrix,
    make_matrix_heatmap, make_table, make_decomposition_tree, make_measure_column,
    make_r_visual, write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_internal_dashb")  # portable: --pages=, --root=, $EPIKAST_PBI_ROOT, or epikast/build/

NAVY = "#1B3A5C"
M = "_Measures"

# ===== PAGE 1: Exec Summary =====
p1 = uid("epi_int_p1_exec")
P1 = [
    make_title_bar("i1_t", 0, 0, 1280, 50, "Epikast Ops — Executive Summary", NAVY),
    make_card("i1_calls",   20, 60, 220, 120, M, "Total Calls"),
    make_card("i1_connect", 255, 60, 220, 120, M, "Connect Rate"),
    make_card("i1_meaning", 490, 60, 220, 120, M, "Meaningful Interaction Rate"),
    make_card("i1_aht",     725, 60, 220, 120, M, "Avg AHT"),
    make_card("i1_sched",   960, 60, 220, 120, M, "Schedule Adherence Rate"),
    make_slicer("i1_qtr",  20, 192, 300, 48, "DimCalendar", "Quarter"),
    make_slicer("i1_team", 335, 192, 300, 48, "DimRep", "Team"),
    make_slicer("i1_ta",   650, 192, 300, 48, "DimHCP", "TherapyArea"),
    make_combo_chart("i1_combo", 20, 255, 740, 245, "DimCalendar", "YearMonth",
                     M, "Total Calls", M, "Connect Rate"),
    make_clustered_column_multi("i1_team_bar", 780, 255, 480, 245, "DimRep", "Team",
                                [(M, "Total Calls"), (M, "Connected Calls"), (M, "Meaningful Interactions")]),
    make_table("i1_tbl", 20, 510, 1240, 190, [
        ("DimCalendar", "YearMonth", False),
        (M, "Total Calls", True), (M, "Connect Rate", True),
        (M, "Meaningful Interaction Rate", True), (M, "Avg AHT", True),
        (M, "Schedule Adherence Rate", True),
    ]),
]

# ===== PAGE 2: Call Outcomes =====
p2 = uid("epi_int_p2_outcomes")
P2 = [
    make_title_bar("i2_t", 0, 0, 1280, 50, "Epikast Ops — Call Outcomes", NAVY),
    make_slicer("i2_ym",   20, 60, 280, 48, "DimCalendar", "YearMonth"),
    make_slicer("i2_team", 320, 60, 280, 48, "DimRep", "Team"),
    make_donut("i2_donut", 20, 125, 380, 300, "FactHCPCalls", "CallOutcome", M, "Total Calls"),
    make_clustered_bar("i2_spec", 420, 125, 820, 300, "DimHCP", "Specialty", M, "Connect Rate"),
    make_matrix_heatmap("i2_heat", 20, 445, 1240, 255,
                        [("DimCalendar", "DayOfWeek")], [("FactHCPCalls", "CallTimeBucket")],
                        M, "Connect Rate"),
]

# ===== PAGE 3: Rep Productivity (+ selling-time & top-performer) =====
p3 = uid("epi_int_p3_reps")
P3 = [
    make_title_bar("i3_t", 0, 0, 1280, 50, "Epikast Ops — Rep Productivity", NAVY),
    make_card("i3_cprd",  20, 60, 220, 120, M, "Calls Per Rep Per Day"),
    make_card("i3_ccprd", 255, 60, 220, 120, M, "Connected Calls Per Rep Per Day"),
    make_card("i3_notes", 490, 60, 220, 120, M, "Notes Compliance Rate"),
    make_card("i3_sell",  725, 60, 220, 120, M, "Selling Time Pct"),
    make_slicer("i3_ym",   960, 60, 300, 40, "DimCalendar", "YearMonth"),
    make_slicer("i3_team", 960, 104, 300, 38, "DimRep", "Team"),
    make_slicer("i3_role", 960, 144, 300, 38, "DimRep", "Role"),
    make_scatter("i3_scatter", 20, 200, 620, 290, "DimRep", "RepName",
                 M, "Total Calls", M, "Connect Rate",
                 size_table=M, size_measure="Meaningful Interactions",
                 series_table="DimRep", series_col="Team"),
    make_clustered_column_multi("i3_top", 660, 200, 600, 290, "DimRep", "Performance Tier",
                                [(M, "AI Acceptance Rate"), (M, "Follow Up Rate"),
                                 (M, "Notes Compliance Rate"), (M, "Meaningful Interaction Rate")]),
    make_table("i3_tbl", 20, 500, 1240, 200, [
        ("DimRep", "RepName", False), ("DimRep", "Performance Tier", False),
        (M, "Total Calls", True), (M, "Connect Rate", True),
        (M, "Meaningful Interaction Rate", True), (M, "Avg AHT", True),
        (M, "Schedule Adherence Rate", True), (M, "Notes Compliance Rate", True),
    ]),
]

# ===== PAGE 4: Trends =====
p4 = uid("epi_int_p4_trends")
P4 = [
    make_title_bar("i4_t", 0, 0, 1280, 50, "Epikast Ops — Trends", NAVY),
    make_slicer("i4_team", 900, 55, 170, 42, "DimRep", "Team"),
    make_slicer("i4_ta",  1080, 55, 180, 42, "DimHCP", "TherapyArea"),
    make_line_chart("i4_connect", 20, 105, 1240, 185, "DimCalendar", "YearMonth",
                    M, "Connect Rate", M, "Connect Rate L4W"),
    make_line_chart("i4_aht", 20, 300, 1240, 185, "DimCalendar", "YearMonth",
                    M, "Avg AHT", ref_value=10, ref_label="Target 10 min"),
    make_line_chart("i4_sched", 20, 495, 1240, 185, "DimCalendar", "YearMonth",
                    M, "Schedule Adherence Rate", ref_value=0.85, ref_label="Target 85%"),
]

# ===== PAGE 5: Compliance & Quality =====
p5 = uid("epi_int_p5_compliance")
P5 = [
    make_title_bar("i5_t", 0, 0, 1280, 50, "Epikast Ops — Compliance & Quality", NAVY),
    make_card("i5_dev",   20, 60, 220, 120, M, "Script Deviation Rate"),
    make_card("i5_qual",  255, 60, 220, 120, M, "Avg Call Quality Score"),
    make_card("i5_ae",    490, 60, 220, 120, M, "AE Flag Rate"),
    make_card("i5_hq",    725, 60, 220, 120, M, "High Quality Calls Pct"),
    make_card("i5_notes", 960, 60, 220, 120, M, "Notes Compliance Rate"),
    make_slicer("i5_ym",   20, 192, 300, 48, "DimCalendar", "YearMonth"),
    make_slicer("i5_team", 335, 192, 300, 48, "DimRep", "Team"),
    make_slicer("i5_ta",   650, 192, 300, 48, "DimHCP", "TherapyArea"),
    make_clustered_bar_gradient("i5_dev_bar", 20, 255, 610, 230, "DimRep", "RepName", M, "Script Deviation Rate"),
    make_clustered_bar("i5_qual_bar", 650, 255, 610, 230, "DimRep", "RepName", M, "Avg Call Quality Score"),
    make_line_chart("i5_trend", 20, 495, 620, 200, "DimCalendar", "YearMonth",
                    M, "Script Deviation Rate", M, "AE Flag Rate"),
    make_table("i5_tbl", 660, 495, 600, 200, [
        ("DimRep", "RepName", False),
        (M, "Script Deviation Rate", True), (M, "Avg Call Quality Score", True),
        (M, "AE Flag Rate", True), (M, "Notes Compliance Rate", True),
    ]),
]

# ===== PAGE 6: Channel Mix & Workforce =====
p6 = uid("epi_int_p6_workforce")
P6 = [
    make_title_bar("i6_t", 0, 0, 1280, 50, "Epikast Ops — Channel Mix & Workforce", NAVY),
    make_card("i6_phone", 20, 60, 220, 120, M, "Phone Calls Pct"),
    make_card("i6_email", 255, 60, 220, 120, M, "Email Pct"),
    make_card("i6_video", 490, 60, 220, 120, M, "Video Pct"),
    make_card("i6_util",  725, 60, 220, 120, M, "Utilization Rate"),
    make_slicer("i6_ym",   960, 60, 300, 40, "DimCalendar", "YearMonth"),
    make_slicer("i6_team", 960, 104, 300, 38, "DimRep", "Team"),
    make_slicer("i6_role", 960, 144, 300, 38, "DimRep", "Role"),
    make_donut("i6_chan", 20, 200, 360, 290, "FactHCPCalls", "Channel", M, "Total Calls"),
    make_clustered_column_multi("i6_chan_perf", 400, 200, 420, 290, "FactHCPCalls", "Channel",
                                [(M, "Connect Rate"), (M, "Meaningful Interaction Rate")]),
    make_clustered_column("i6_ramp", 840, 200, 420, 290, "DimRep", "Tenure Bucket", M, "Connect Rate"),
    make_table("i6_tbl", 20, 500, 1240, 200, [
        ("DimRep", "Tenure Bucket", False),
        (M, "Connect Rate", True), (M, "Avg Call Quality Score", True),
        (M, "Script Deviation Rate", True), (M, "Utilization Rate", True),
        (M, "Calls Per Rep Per Day", True),
    ]),
]

# ===== PAGE 7: Patient Ops & Drill-Down (net-new) =====
# Daily-pulse KPIs (anchored to latest data date, not TODAY()), a Decomposition Tree to
# explain Meaningful Rate, the patient-access funnel, open-case aging, and an R box-and-
# whisker of AHT spread by team. Needs measures groups 18-20 + the Open Case Age Bucket
# column from Epikast_Dashboard_Prompts.md; the box-plot needs R set up in PBI Desktop.
p7 = uid("epi_int_p7_patientops")
P7 = [
    make_title_bar("i7_t", 0, 0, 1280, 50, "Epikast Ops — Patient Ops & Drill-Down", NAVY),
    make_card("i7_l7",   20, 60, 220, 110, M, "Calls Last 7 Days"),
    make_card("i7_wow",  255, 60, 220, 110, M, "Calls WoW Change"),
    make_card("i7_open", 490, 60, 220, 110, M, "Active Cases"),
    make_card("i7_risk", 725, 60, 220, 110, M, "Open High Risk Cases"),
    make_card("i7_ttt",  960, 60, 220, 110, M, "Avg Time to Therapy"),
    # Decomposition Tree — break down Meaningful Rate by the levers Ops can pull
    make_decomposition_tree("i7_decomp", 20, 185, 620, 290,
                            (M, "Meaningful Interaction Rate"),
                            [("FactHCPCalls", "AIFollowed"), ("FactHCPCalls", "Channel"),
                             ("DimRep", "Role"), ("DimHCP", "Specialty")]),
    # Patient-access funnel as descending stage columns (no stage dimension needed)
    make_measure_column("i7_funnel", 660, 185, 600, 140, [
        (M, "Total Cases"), (M, "Cases First Contacted"), (M, "Cases PA Approved"),
        (M, "Cases Fulfilled"), (M, "Cases On Therapy")]),
    # Open-case aging — counts of open cases by days-open band
    make_clustered_bar("i7_aging", 660, 335, 600, 140, "FactPatientCases",
                       "Open Case Age Bucket", M, "Active Cases"),
    # R box-and-whisker: AHT spread by team (CallID keeps rows un-deduplicated)
    make_r_visual("i7_box", 20, 490, 1240, 205,
                  [("FactHCPCalls", "CallID", False), ("DimRep", "Team", False),
                   ("FactHCPCalls", "AHT_Minutes", False)],
                  "library(ggplot2)\n"
                  "ggplot(dataset, aes(x=Team, y=AHT_Minutes, fill=Team)) +\n"
                  "  geom_boxplot(outlier.alpha=0.25) +\n"
                  "  labs(title='AHT distribution by team', x=NULL, y='AHT (min)') +\n"
                  "  theme_minimal(base_size=12) + theme(legend.position='none')"),
]

write_page(p1, "Executive Summary", P1)
write_page(p2, "Call Outcomes", P2)
write_page(p3, "Rep Productivity", P3)
write_page(p4, "Trends", P4)
write_page(p5, "Compliance & Quality", P5)
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
