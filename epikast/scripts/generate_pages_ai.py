"""
Epikast AI EFFECTIVENESS report — the human+AI value-proof (board / client-share).

5 pages: AI Call Targeting, MSL Partner Performance, MSL Partner ROI, A/B
Experiment Registry, Script A/B Deep Dive. Runs against the shared Epikast
Pharma Ops model (Epikast_Dashboard_Prompts.md).

Run with Power BI closed:  python scripts/generate_pages_ai.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_card, make_multi_card, make_slicer, make_clustered_bar,
    make_clustered_bar_gradient, make_donut, make_line_chart, make_measure_column,
    make_stacked_bar, make_matrix, make_table, write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_ai_dashb")  # portable: --pages=, --root=, $EPIKAST_PBI_ROOT, or epikast/build/

MAGENTA = "#A23B72"
M = "_Measures"

# ===== PAGE 1: AI Call Targeting =====
p1 = uid("epi_ai_p1_targeting")
P1 = [
    make_title_bar("a1_t", 0, 0, 1280, 50, "Epikast AI — Call Targeting Lift", MAGENTA),
    make_card("a1_accept", 20, 60, 220, 120, M, "AI Acceptance Rate"),
    make_card("a1_aiconn", 255, 60, 220, 120, M, "AI Connect Rate"),
    make_card("a1_noaiconn", 490, 60, 220, 120, M, "Non-AI Connect Rate"),
    make_card("a1_lift", 725, 60, 220, 120, M, "AI Lift on Connect Rate"),
    make_slicer("a1_qtr",  960, 60, 300, 40, "DimCalendar", "Quarter"),
    make_slicer("a1_tier", 960, 104, 300, 38, "DimHCP", "Tier"),
    make_slicer("a1_ta",   960, 144, 300, 38, "DimHCP", "TherapyArea"),
    make_measure_column("a1_vs", 20, 200, 400, 290,
                        [(M, "AI Connect Rate"), (M, "Non-AI Connect Rate"),
                         (M, "AI Meaningful Rate"), (M, "Non-AI Meaningful Rate")]),
    make_clustered_bar("a1_lift_ta", 440, 200, 400, 290, "DimHCP", "TherapyArea", M, "AI Lift on Connect Rate"),
    make_line_chart("a1_accept_trend", 860, 200, 400, 290, "DimCalendar", "YearMonth",
                    M, "AI Acceptance Rate", ref_value=0.70, ref_label="Target 70%"),
    make_table("a1_tbl", 20, 500, 1240, 200, [
        ("DimHCP", "TherapyArea", False),
        (M, "AI Connect Rate", True), (M, "Non-AI Connect Rate", True),
        (M, "AI Lift on Connect Rate", True), (M, "AI Meaningful Rate", True),
        (M, "AI Acceptance Rate", True),
    ]),
]

# ===== PAGE 2: MSL Partner Performance =====
p2 = uid("epi_ai_p2_mslperf")
P2 = [
    make_title_bar("a2_t", 0, 0, 1280, 50, "Epikast AI — MSL Partner Performance", MAGENTA),
    make_card("a2_q",    20, 60, 220, 120, M, "Total MSL Queries"),
    make_card("a2_fa",   255, 60, 220, 120, M, "Fully Answered Rate"),
    make_card("a2_tta",  490, 60, 220, 120, M, "Avg Time to Answer Sec"),
    make_card("a2_saved", 725, 60, 220, 120, M, "Total Time Saved Hours"),
    make_slicer("a2_rep", 960, 60, 300, 40, "DimRep", "RepName"),
    make_slicer("a2_qtr", 960, 104, 300, 38, "DimCalendar", "Quarter"),
    make_slicer("a2_ta",  960, 144, 300, 38, "DimRep", "TherapyArea"),
    make_clustered_bar("a2_topics", 20, 200, 500, 290, "FactMSLPartnerUsage", "Topic", M, "Total MSL Queries"),
    make_donut("a2_qtype", 540, 200, 340, 290, "FactMSLPartnerUsage", "QueryType", M, "Total MSL Queries"),
    make_line_chart("a2_adopt", 900, 200, 360, 290, "DimCalendar", "YearMonth",
                    M, "MSL Queries Per MSL Per Day", M, "Fully Answered Rate"),
    make_table("a2_tbl", 20, 500, 1240, 200, [
        ("FactMSLPartnerUsage", "Topic", False),
        (M, "Total MSL Queries", True), (M, "Fully Answered Rate", True),
        (M, "Avg Time to Answer Sec", True), (M, "Avg Time Saved Per Query Min", True),
    ]),
]

# ===== PAGE 3: MSL Partner ROI =====
p3 = uid("epi_ai_p3_mslroi")
P3 = [
    make_title_bar("a3_t", 0, 0, 1280, 50, "Epikast AI — MSL Partner ROI", MAGENTA),
    make_card("a3_perday", 20, 60, 300, 120, M, "MSL Queries Per MSL Per Day"),
    make_card("a3_used",   335, 60, 300, 120, M, "Used in HCP Interaction Rate"),
    make_card("a3_sat",    650, 60, 300, 120, M, "Avg MSL Satisfaction"),
    make_slicer("a3_qtr",  965, 60, 295, 120, "DimCalendar", "Quarter"),
    make_stacked_bar("a3_quality", 20, 200, 620, 290, "DimRep", "RepName",
                     "FactMSLPartnerUsage", "AnswerQuality", M, "Total MSL Queries"),
    make_clustered_bar_gradient("a3_saved_rep", 660, 200, 600, 290, "DimRep", "RepName", M, "Total Time Saved Hours"),
    make_table("a3_tbl", 20, 500, 1240, 200, [
        ("DimRep", "RepName", False),
        (M, "Total MSL Queries", True), (M, "Fully Answered Rate", True),
        (M, "Avg Time to Answer Sec", True), (M, "Total Time Saved Hours", True),
        (M, "Used in HCP Interaction Rate", True), (M, "Avg MSL Satisfaction", True),
    ]),
]

# ===== PAGE 4: A/B Experiment Registry =====
p4 = uid("epi_ai_p4_experiments")
P4 = [
    make_title_bar("a4_t", 0, 0, 1280, 50, "Epikast AI — Experiment Registry", MAGENTA),
    make_card("a4_total", 20, 60, 220, 120, M, "Total Experiments"),
    make_card("a4_concl", 255, 60, 220, 120, M, "Concluded Experiments"),
    make_card("a4_win",   490, 60, 220, 120, M, "Win Rate"),
    make_card("a4_run",   725, 60, 220, 120, M, "Running Experiments"),
    make_slicer("a4_status", 960, 60, 300, 56, "DimExperiment", "Status"),
    make_slicer("a4_ta",     960, 122, 300, 58, "DimExperiment", "TherapyArea"),
    make_table("a4_tbl", 20, 200, 1240, 270, [
        ("DimExperiment", "ExperimentName", False), ("DimExperiment", "Status", False),
        ("DimExperiment", "PrimaryKPI", False), ("DimExperiment", "StartDate", False),
        ("DimExperiment", "EndDate", False), ("DimExperiment", "SampleSizeActual", False),
        ("DimExperiment", "SampleSizeTarget", False), ("DimExperiment", "ObservedLift", False),
        ("DimExperiment", "Winner", False),
    ]),
    make_clustered_bar_gradient("a4_lift", 20, 485, 1240, 215, "DimExperiment", "ExperimentName", M, "Experiment Lift"),
]

# ===== PAGE 5: Script A/B Deep Dive =====
p5 = uid("epi_ai_p5_scriptab")
P5 = [
    make_title_bar("a5_t", 0, 0, 1280, 50, "Epikast AI — Script A/B Deep Dive", MAGENTA),
    make_multi_card("a5_conn", 20, 60, 300, 160, [(M, "Script A Connect Rate"), (M, "Script B Connect Rate")]),
    make_multi_card("a5_mean", 335, 60, 300, 160, [(M, "Script A Meaningful Rate"), (M, "Script B Meaningful Rate")]),
    make_slicer("a5_ym",  960, 60, 300, 40, "DimCalendar", "YearMonth"),
    make_slicer("a5_ta",  960, 104, 300, 38, "DimHCP", "TherapyArea"),
    make_slicer("a5_reg", 960, 144, 300, 38, "DimHCP", "Region"),
    make_measure_column("a5_rates", 20, 235, 600, 255,
                        [(M, "Script A Connect Rate"), (M, "Script B Connect Rate"),
                         (M, "Script A Meaningful Rate"), (M, "Script B Meaningful Rate")]),
    make_measure_column("a5_dur", 640, 235, 620, 255,
                        [(M, "Script A Avg Duration"), (M, "Script B Avg Duration")]),
    make_matrix("a5_matrix", 20, 500, 1240, 200,
        [("DimHCP", "Specialty")], None,
        [(M, "Script A Connect Rate"), (M, "Script B Connect Rate"),
         (M, "Script A Meaningful Rate"), (M, "Script B Meaningful Rate")]),
]

write_page(p1, "AI Call Targeting", P1)
write_page(p2, "MSL Partner Performance", P2)
write_page(p3, "MSL Partner ROI", P3)
write_page(p4, "Experiment Registry", P4)
write_page(p5, "Script A/B Deep Dive", P5)
write_pages_json([p1, p2, p3, p4, p5])

print("AI EFFECTIVENESS report — 5 pages")
for n, pg in [("AI Call Targeting", P1), ("MSL Partner Performance", P2), ("MSL Partner ROI", P3),
              ("Experiment Registry", P4), ("Script A/B Deep Dive", P5)]:
    print(f"  {n}: {len(pg)} visuals")
print(f"Total: {sum(len(p) for p in [P1,P2,P3,P4,P5])} visuals")
print("Done!")
