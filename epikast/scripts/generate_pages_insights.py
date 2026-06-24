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
    uid, make_title_bar, make_key_influencers, make_decomposition_tree,
    make_clustered_bar, make_clustered_bar_gradient, make_clustered_column_multi,
    make_measure_column, make_card, make_line_chart, make_donut, make_table,
    card_row, slicer_row,
    CARD_H, SLICER_H, GAP,
    CARD1_Y, SL1_Y, BODY1_Y, BODY1_H,
    SL_Y, BODY_Y, BODY_H,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_insights_dashb")

AMBER = "#B45309"
M     = "_Measures"


# ===== PAGE 1: What Drives Meaningful Engagement =====
p1 = uid("epi_ins_p1_engagement")

# Layout: slicer row | KI (large) + decomp tree | bottom comparison charts
KI_H      = BODY_H * 3 // 5   # ~361 for KI + decomp
BOTTOM_Y  = BODY_Y + KI_H + GAP
BOTTOM_H  = 720 - BOTTOM_Y - 10   # ~221

P1 = [
    make_title_bar("n1_t", 0, 0, 1280, 50, "Epikast Insights — What Drives Meaningful Engagement", AMBER),

    *slicer_row("n1sl", SL_Y, SLICER_H, [
        ("DimCalendar", "Quarter"),
        ("DimHCP",      "TherapyArea"),
    ]),

    make_key_influencers("n1_ki", 20, BODY_Y, 760, KI_H,
        ("FactHCPCalls", "IsMeaningfulInteraction", False),
        [("FactHCPCalls", "Channel"), ("FactHCPCalls", "Script"), ("FactHCPCalls", "AIFollowed"),
         ("FactHCPCalls", "CallTimeBucket"), ("DimHCP", "Specialty"), ("DimHCP", "Tier"),
         ("DimRep", "Team"), ("DimRep", "Tenure Bucket")]),
    make_decomposition_tree("n1_dt", 800, BODY_Y, 460, KI_H,
        (M, "Meaningful Interaction Rate"),
        [("FactHCPCalls", "Channel"), ("FactHCPCalls", "Script"), ("FactHCPCalls", "AIFollowed"),
         ("DimHCP", "Specialty"), ("DimHCP", "Tier")]),

    make_clustered_column_multi("n1_chan", 20, BOTTOM_Y, 620, BOTTOM_H,
        "FactHCPCalls", "Channel",
        [(M, "Connect Rate"), (M, "Meaningful Interaction Rate")]),
    make_measure_column("n1_script", 660, BOTTOM_Y, 600, BOTTOM_H,
        [(M, "Script A Meaningful Rate"), (M, "Script B Meaningful Rate")]),
]


# ===== PAGE 2: What Drives Patient Abandonment =====
p2 = uid("epi_ins_p2_abandonment")

P2 = [
    make_title_bar("n2_t", 0, 0, 1280, 50, "Epikast Insights — What Drives Patient Abandonment", AMBER),

    *slicer_row("n2sl", SL_Y, SLICER_H, [
        ("DimDrug",    "DrugName"),
        ("DimPatient", "TherapyArea"),
    ]),

    make_key_influencers("n2_ki", 20, BODY_Y, 760, KI_H,
        ("FactPatientCases", "IsAbandoned", False),
        [("FactPatientCases", "InsuranceType"), ("FactPatientCases", "PAStatus"),
         ("FactPatientCases", "FirstContactDelayDays"), ("DimPatient", "AgeGroup"),
         ("DimPatient", "TherapyArea"), ("FactPatientCases", "Drug")]),
    make_decomposition_tree("n2_dt", 800, BODY_Y, 460, KI_H,
        (M, "Abandonment Rate"),
        [("FactPatientCases", "PAStatus"), ("FactPatientCases", "InsuranceType"),
         ("DimPatient", "TherapyArea"), ("FactPatientCases", "Drug")]),

    make_clustered_bar("n2_ins", 20, BOTTOM_Y, 620, BOTTOM_H,
        "FactPatientCases", "InsuranceType", M, "Abandonment Rate"),
    make_clustered_bar("n2_pa", 660, BOTTOM_Y, 600, BOTTOM_H,
        "FactPatientCases", "PAStatus", M, "Abandonment Rate"),
]


# ===== PAGE 3: Winning Plays — Uplift by Tactic (Approach B) =====
p3 = uid("epi_ins_p3_uplift")

P3 = [
    make_title_bar("n3_t", 0, 0, 1280, 50, "Epikast Insights — Winning Plays (Uplift by Tactic)", AMBER),

    *slicer_row("n3sl", SL_Y, SLICER_H, [
        ("FactUplift", "outcome"),
        ("FactUplift", "segment_type"),
    ]),

    make_clustered_bar_gradient("n3_bar", 20, BODY_Y, 620, BODY_H,
        "FactUplift", "tactic", M, "Avg Uplift"),
    make_table("n3_tbl", 660, BODY_Y, 600, BODY_H, [
        ("FactUplift", "tactic",         False),
        ("FactUplift", "segment_value",  False),
        ("FactUplift", "uplift",         False),
        ("FactUplift", "ci_low",         False),
        ("FactUplift", "ci_high",        False),
        ("FactUplift", "significant",    False),
        ("FactUplift", "n_treated",      False),
    ]),
]


# ===== PAGE 4: Next-Best-Action =====
p4 = uid("epi_ins_p4_nba")

P4 = [
    make_title_bar("n4_t", 0, 0, 1280, 50, "Epikast Insights — Next-Best-Action by Segment", AMBER),

    *slicer_row("n4sl", SL_Y, SLICER_H, [
        ("DimNBA", "outcome"),
        ("DimNBA", "segment_type"),
    ]),

    make_table("n4_tbl", 20, BODY_Y, 760, BODY_H, [
        ("DimNBA", "segment_type",        False),
        ("DimNBA", "segment_value",       False),
        ("DimNBA", "outcome",             False),
        ("DimNBA", "recommended_tactic",  False),
        ("DimNBA", "est_uplift",          False),
    ]),
    make_clustered_bar_gradient("n4_feat", 800, BODY_Y, 460, BODY_H,
        "FeatureImportance", "feature", M, "Avg Importance"),
]


# ===== PAGE 5: HCP Sentiment Analysis =====
p5 = uid("epi_ins_p5_sentiment")

SENT_TOP_H   = BODY1_H * 11 // 20   # ~260 donuts + trend + bar
SENT_BOT_H   = BODY1_H - SENT_TOP_H - GAP   # ~201

P5 = [
    make_title_bar("n5_t", 0, 0, 1280, 50, "Epikast Insights — HCP Sentiment Analysis", AMBER),

    *card_row("n5r1", CARD1_Y, CARD_H, [
        "Avg HCP Sentiment",
        "Positive Sentiment Pct",
        "Negative Sentiment Pct",
    ]),

    *slicer_row("n5sl", SL1_Y, SLICER_H, [
        ("DimHCP",       "TherapyArea"),
        ("FactHCPCalls", "Channel"),
    ]),

    make_donut("n5_band", 20, BODY1_Y, 380, SENT_TOP_H,
        "FactHCPCalls", "SentimentBand", M, "Total Calls"),
    make_line_chart("n5_trend", 420, BODY1_Y, 400, SENT_TOP_H,
        "DimCalendar", "YearMonth", M, "Avg HCP Sentiment"),
    make_clustered_bar("n5_spec", 840, BODY1_Y, 420, SENT_TOP_H,
        "DimHCP", "Specialty", M, "Avg HCP Sentiment"),

    make_clustered_bar("n5_chanbar", 20, BODY1_Y + SENT_TOP_H + GAP, 620, SENT_BOT_H,
        "FactHCPCalls", "Channel", M, "Avg HCP Sentiment"),
    make_clustered_bar("n5_script", 660, BODY1_Y + SENT_TOP_H + GAP, 600, SENT_BOT_H,
        "FactHCPCalls", "Script", M, "Avg HCP Sentiment"),
]


write_page(p1, "What Drives Engagement",  P1)
write_page(p2, "What Drives Abandonment", P2)
write_page(p3, "Winning Plays",           P3)
write_page(p4, "Next-Best-Action",        P4)
write_page(p5, "HCP Sentiment Analysis",  P5)
write_pages_json([p1, p2, p3, p4, p5])

print("INSIGHTS ENGINE report — 5 pages")
for n, pg in [("What Drives Engagement", P1), ("What Drives Abandonment", P2),
              ("Winning Plays", P3), ("Next-Best-Action", P4), ("HCP Sentiment Analysis", P5)]:
    print(f"  {n}: {len(pg)} visuals")
print(f"Total: {sum(len(p) for p in [P1,P2,P3,P4,P5])} visuals")
print("Done!")
