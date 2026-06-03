"""
Epikast INSIGHTS ENGINE report — "What Works Best" (native Power BI AI visuals).

Approach A: zero external ML. Uses Power BI's built-in Key Influencers and
Decomposition Tree visuals on the existing model to surface what drives
meaningful HCP engagement and what drives patient abandonment.

(Approach B — an offline uplift model writing a FactUplift table + ranked-tactic
"Insights Engine" page — can be added to THIS report later.)

Runs against the shared Epikast Pharma Ops model. Run with Power BI closed:
    python scripts/generate_pages_insights.py

NOTE: keyDriversVisual / decompositionTreeVisual are native AI visuals. The
field bindings below emit valid PBIR, but if your Power BI version doesn't pick
them up, just drag the fields into Analyze / Explain-by once (they persist).
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_slicer, make_key_influencers, make_decomposition_tree,
    make_clustered_bar, make_clustered_bar_gradient, make_clustered_column_multi,
    make_measure_column, make_card, make_line_chart, make_donut, make_table,
    write_page, write_pages_json,
)

pb.BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\epikast\epikast_insights_dashb.Report\definition\pages"

AMBER = "#B45309"
M = "_Measures"

# ===== PAGE 1: What Drives Meaningful Engagement =====
p1 = uid("epi_ins_p1_engagement")
P1 = [
    make_title_bar("n1_t", 0, 0, 1280, 50, "Epikast Insights — What Drives Meaningful Engagement", AMBER),
    make_slicer("n1_qtr", 900, 55, 170, 42, "DimCalendar", "Quarter"),
    make_slicer("n1_ta", 1080, 55, 180, 42, "DimHCP", "TherapyArea"),
    make_key_influencers("n1_ki", 20, 105, 760, 405,
        ("FactHCPCalls", "IsMeaningfulInteraction", False),
        [("FactHCPCalls", "Channel"), ("FactHCPCalls", "Script"), ("FactHCPCalls", "AIFollowed"),
         ("FactHCPCalls", "CallTimeBucket"), ("DimHCP", "Specialty"), ("DimHCP", "Tier"),
         ("DimRep", "Team"), ("DimRep", "Tenure Bucket")]),
    make_decomposition_tree("n1_dt", 800, 105, 460, 405,
        (M, "Meaningful Interaction Rate"),
        [("FactHCPCalls", "Channel"), ("FactHCPCalls", "Script"), ("FactHCPCalls", "AIFollowed"),
         ("DimHCP", "Specialty"), ("DimHCP", "Tier")]),
    make_clustered_column_multi("n1_chan", 20, 525, 620, 175, "FactHCPCalls", "Channel",
                                [(M, "Connect Rate"), (M, "Meaningful Interaction Rate")]),
    make_measure_column("n1_script", 660, 525, 600, 175,
                        [(M, "Script A Meaningful Rate"), (M, "Script B Meaningful Rate")]),
]

# ===== PAGE 2: What Drives Patient Abandonment =====
p2 = uid("epi_ins_p2_abandonment")
P2 = [
    make_title_bar("n2_t", 0, 0, 1280, 50, "Epikast Insights — What Drives Patient Abandonment", AMBER),
    make_slicer("n2_drug", 900, 55, 170, 42, "DimDrug", "DrugName"),
    make_slicer("n2_ta", 1080, 55, 180, 42, "DimPatient", "TherapyArea"),
    make_key_influencers("n2_ki", 20, 105, 760, 405,
        ("FactPatientCases", "IsAbandoned", False),
        [("FactPatientCases", "InsuranceType"), ("FactPatientCases", "PAStatus"),
         ("FactPatientCases", "FirstContactDelayDays"), ("DimPatient", "AgeGroup"),
         ("DimPatient", "TherapyArea"), ("FactPatientCases", "Drug")]),
    make_decomposition_tree("n2_dt", 800, 105, 460, 405,
        (M, "Abandonment Rate"),
        [("FactPatientCases", "PAStatus"), ("FactPatientCases", "InsuranceType"),
         ("DimPatient", "TherapyArea"), ("FactPatientCases", "Drug")]),
    make_clustered_bar("n2_ins", 20, 525, 620, 175, "FactPatientCases", "InsuranceType", M, "Abandonment Rate"),
    make_clustered_bar("n2_pa", 660, 525, 600, 175, "FactPatientCases", "PAStatus", M, "Abandonment Rate"),
]

# ===== PAGE 3: Winning Plays — Uplift by Tactic (Approach B) =====
p3 = uid("epi_ins_p3_uplift")
P3 = [
    make_title_bar("n3_t", 0, 0, 1280, 50, "Epikast Insights — Winning Plays (Uplift by Tactic)", AMBER),
    make_slicer("n3_out", 20, 60, 400, 48, "FactUplift", "outcome"),
    make_slicer("n3_seg", 440, 60, 400, 48, "FactUplift", "segment_type"),
    make_clustered_bar_gradient("n3_bar", 20, 125, 620, 575, "FactUplift", "tactic", M, "Avg Uplift"),
    make_table("n3_tbl", 660, 125, 600, 575, [
        ("FactUplift", "tactic", False), ("FactUplift", "segment_value", False),
        ("FactUplift", "uplift", False), ("FactUplift", "ci_low", False),
        ("FactUplift", "ci_high", False), ("FactUplift", "significant", False),
        ("FactUplift", "n_treated", False),
    ]),
]

# ===== PAGE 4: Next-Best-Action =====
p4 = uid("epi_ins_p4_nba")
P4 = [
    make_title_bar("n4_t", 0, 0, 1280, 50, "Epikast Insights — Next-Best-Action by Segment", AMBER),
    make_slicer("n4_out", 20, 60, 400, 48, "DimNBA", "outcome"),
    make_slicer("n4_seg", 440, 60, 400, 48, "DimNBA", "segment_type"),
    make_table("n4_tbl", 20, 125, 760, 575, [
        ("DimNBA", "segment_type", False), ("DimNBA", "segment_value", False),
        ("DimNBA", "outcome", False), ("DimNBA", "recommended_tactic", False),
        ("DimNBA", "est_uplift", False),
    ]),
    make_clustered_bar_gradient("n4_feat", 800, 125, 460, 575, "FeatureImportance", "feature", M, "Avg Importance"),
]

# ===== PAGE 5: HCP Sentiment Analysis =====
p5 = uid("epi_ins_p5_sentiment")
P5 = [
    make_title_bar("n5_t", 0, 0, 1280, 50, "Epikast Insights — HCP Sentiment Analysis", AMBER),
    make_card("n5_avg", 20, 60, 220, 120, M, "Avg HCP Sentiment"),
    make_card("n5_pos", 255, 60, 220, 120, M, "Positive Sentiment Pct"),
    make_card("n5_neg", 490, 60, 220, 120, M, "Negative Sentiment Pct"),
    make_slicer("n5_ta", 725, 60, 230, 120, "DimHCP", "TherapyArea"),
    make_slicer("n5_chan", 965, 60, 295, 120, "FactHCPCalls", "Channel"),
    make_donut("n5_band", 20, 200, 380, 290, "FactHCPCalls", "SentimentBand", M, "Total Calls"),
    make_line_chart("n5_trend", 420, 200, 400, 290, "DimCalendar", "YearMonth", M, "Avg HCP Sentiment"),
    make_clustered_bar("n5_spec", 840, 200, 420, 290, "DimHCP", "Specialty", M, "Avg HCP Sentiment"),
    make_clustered_bar("n5_chanbar", 20, 510, 620, 190, "FactHCPCalls", "Channel", M, "Avg HCP Sentiment"),
    make_clustered_bar("n5_script", 660, 510, 600, 190, "FactHCPCalls", "Script", M, "Avg HCP Sentiment"),
]

write_page(p1, "What Drives Engagement", P1)
write_page(p2, "What Drives Abandonment", P2)
write_page(p3, "Winning Plays", P3)
write_page(p4, "Next-Best-Action", P4)
write_page(p5, "HCP Sentiment Analysis", P5)
write_pages_json([p1, p2, p3, p4, p5])

print("INSIGHTS ENGINE report — 5 pages")
for n, pg in [("What Drives Engagement", P1), ("What Drives Abandonment", P2),
              ("Winning Plays", P3), ("Next-Best-Action", P4), ("HCP Sentiment Analysis", P5)]:
    print(f"  {n}: {len(pg)} visuals")
print(f"Total: {sum(len(p) for p in [P1,P2,P3,P4,P5])} visuals")
print("Done!")
