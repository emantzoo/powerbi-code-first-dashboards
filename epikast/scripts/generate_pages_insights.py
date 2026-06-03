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
    make_clustered_bar, make_clustered_column_multi, make_measure_column,
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

write_page(p1, "What Drives Engagement", P1)
write_page(p2, "What Drives Abandonment", P2)
write_pages_json([p1, p2])

print("INSIGHTS ENGINE report (native AI visuals) — 2 pages")
for n, pg in [("What Drives Engagement", P1), ("What Drives Abandonment", P2)]:
    print(f"  {n}: {len(pg)} visuals")
print(f"Total: {sum(len(p) for p in [P1,P2])} visuals")
print("Done!")
