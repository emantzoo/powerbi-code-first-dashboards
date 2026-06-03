"""
Epikast CLIENT report — the client-safe deliverable handed to biopharma clients.

Shows the value Epikast delivers (engagement reach, HCP coverage, patient
outcomes, per-client campaign health) WITHOUT exposing rep-level performance or
internal quality/compliance review data. Runs against the same shared semantic
model (see Epikast_Dashboard_Prompts.md); apply RLS on DimClient so each client
sees only their own data.

Run with Power BI closed:  python scripts/generate_pages_client.py
"""

import os
import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_card, make_slicer, make_clustered_bar,
    make_clustered_bar_gradient, make_line_chart, make_area_chart, make_donut,
    make_map, make_matrix, make_table, make_button, write_page, write_pages_json,
)

# Point at the CLIENT report's pages folder.
pb.BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\epikast\epikast_client_dashb.Report\definition\pages"

TEAL = "#0F766E"   # client report accent

# ===== PAGE 1: Engagement Overview =====
p1_id = uid("epi_cli_p1_overview")
p1 = [
    make_title_bar("c1_title", 0, 0, 1280, 50, "Epikast — Engagement Overview", TEAL),
    make_card("c1_interactions", 20, 60, 235, 140, "_Measures", "Total Interactions"),
    make_card("c1_connect", 270, 60, 235, 140, "_Measures", "Connect Rate"),
    make_card("c1_hcps", 520, 60, 235, 140, "_Measures", "Unique HCPs Reached"),
    make_card("c1_sentiment", 770, 60, 235, 140, "_Measures", "Avg Sentiment Score"),
    make_slicer("c1_year", 1020, 60, 230, 140, "Calendar", "Year"),
    make_clustered_bar_gradient("c1_client_bar", 20, 220, 400, 280, "DimClient", "client_name", "_Measures", "Total Interactions"),
    make_line_chart("c1_trend", 440, 220, 400, 280, "Calendar", "Year_Month", "_Measures", "Total Interactions", "_Measures", "Interactions PY"),
    make_donut("c1_channel", 860, 220, 380, 280, "FactInteractions", "channel", "_Measures", "Total Interactions"),
    make_area_chart("c1_minutes", 20, 520, 600, 160, "Calendar", "Year_Month", "_Measures", "Total Engagement Minutes"),
    make_clustered_bar("c1_type_bar", 640, 520, 600, 160, "FactInteractions", "interaction_type", "_Measures", "Total Interactions"),
    make_button("c1_btn_hcp", 1100, 670, 150, 40, "HCPs"),
]

# ===== PAGE 2: HCP Engagement =====
p2_id = uid("epi_cli_p2_hcp")
p2 = [
    make_title_bar("c2_title", 0, 0, 1280, 50, "Epikast — HCP Engagement", TEAL),
    make_card("c2_hcps", 20, 60, 235, 140, "_Measures", "Unique HCPs Reached"),
    make_card("c2_reach", 270, 60, 235, 140, "_Measures", "HCP Reach Pct"),
    make_card("c2_per_hcp", 520, 60, 235, 140, "_Measures", "Interactions per HCP"),
    make_card("c2_sci", 770, 60, 235, 140, "_Measures", "Scientific Exchange Pct"),
    make_slicer("c2_specialty", 1020, 60, 230, 140, "DimHCP", "specialty"),
    make_clustered_bar("c2_spec_bar", 20, 220, 400, 280, "DimHCP", "specialty", "_Measures", "Total Interactions"),
    make_donut("c2_segment", 440, 220, 380, 280, "DimHCP", "segment", "_Measures", "Total Interactions"),
    make_map("c2_map", 840, 220, 410, 280, "DimHCP", "territory",
             "DimHCP", "latitude", "DimHCP", "longitude", "_Measures", "Total Interactions"),
    make_table("c2_table", 20, 520, 1230, 160, [
        ("DimHCP", "hcp_name", False),
        ("DimHCP", "specialty", False),
        ("DimHCP", "segment", False),
        ("DimHCP", "region", False),
        ("_Measures", "Total Interactions", True),
        ("_Measures", "Avg Sentiment Score", True),
        ("_Measures", "Scientific Exchange Pct", True),
    ]),
    make_button("c2_btn_back", 20, 670, 100, 40, "Back"),
    make_button("c2_btn_patient", 1100, 670, 150, 40, "Patients"),
]

# ===== PAGE 3: Patient Support & Outcomes =====
p3_id = uid("epi_cli_p3_patient")
p3 = [
    make_title_bar("c3_title", 0, 0, 1280, 50, "Epikast — Patient Support & Outcomes", TEAL),
    make_card("c3_enrolled", 20, 60, 235, 140, "_Measures", "Total Patients Enrolled"),
    make_card("c3_active", 270, 60, 235, 140, "_Measures", "Active Patient Rate"),
    make_card("c3_adherence", 520, 60, 235, 140, "_Measures", "Avg Adherence"),
    make_card("c3_nps", 770, 60, 235, 140, "_Measures", "NPS Score"),
    make_slicer("c3_status", 1020, 60, 230, 140, "FactPatientSupport", "status"),
    make_clustered_bar("c3_barrier_bar", 20, 220, 400, 280, "FactPatientSupport", "barrier_type", "_Measures", "Support Records"),
    make_donut("c3_payer", 440, 220, 380, 280, "FactPatientSupport", "payer_status", "_Measures", "Support Records"),
    make_clustered_bar("c3_client_adh", 840, 220, 410, 280, "DimClient", "client_name", "_Measures", "Avg Adherence"),
    make_table("c3_table", 20, 520, 1230, 160, [
        ("DimPatient", "age_group", False),
        ("FactPatientSupport", "status", False),
        ("_Measures", "Support Records", True),
        ("_Measures", "Avg Adherence", True),
        ("_Measures", "Avg Time to Therapy", True),
        ("_Measures", "Avg Persistence Days", True),
        ("_Measures", "Barrier Resolution Rate", True),
    ]),
    make_button("c3_btn_back", 20, 670, 100, 40, "Back"),
    make_button("c3_btn_campaign", 1100, 670, 150, 40, "Campaign"),
]

# ===== PAGE 4: Client Campaign Health =====
p4_id = uid("epi_cli_p4_campaign")
p4 = [
    make_title_bar("c4_title", 0, 0, 1280, 50, "Epikast — Client Campaign Health", TEAL),
    make_card("c4_interactions", 20, 60, 235, 140, "_Measures", "Total Interactions"),
    make_card("c4_active", 270, 60, 235, 140, "_Measures", "Active Patients"),
    make_card("c4_connect", 520, 60, 235, 140, "_Measures", "Connect Rate"),
    make_card("c4_payer", 770, 60, 235, 140, "_Measures", "Payer Approval Rate"),
    make_slicer("c4_client", 1020, 60, 230, 140, "DimClient", "client_name"),
    make_clustered_bar_gradient("c4_client_bar", 20, 220, 610, 280, "DimClient", "client_name", "_Measures", "Total Interactions"),
    make_clustered_bar("c4_ta_bar", 650, 220, 600, 280, "DimClient", "therapeutic_area", "_Measures", "Connect Rate"),
    make_matrix("c4_matrix", 20, 520, 1230, 180,
        [("DimClient", "client_name")],
        None,
        [("_Measures", "Total Interactions"), ("_Measures", "Connect Rate"),
         ("_Measures", "Unique HCPs Reached"), ("_Measures", "Active Patients"),
         ("_Measures", "Avg Adherence"), ("_Measures", "NPS Score")]),
    make_button("c4_btn_back", 20, 670, 100, 40, "Back"),
]

write_page(p1_id, "Engagement Overview", p1)
write_page(p2_id, "HCP Engagement", p2)
write_page(p3_id, "Patient Support & Outcomes", p3)
write_page(p4_id, "Client Campaign Health", p4)
write_pages_json([p1_id, p2_id, p3_id, p4_id])

print(f"CLIENT report — 4 pages, {len(p1)+len(p2)+len(p3)+len(p4)} visuals")
print(f"  P1 Engagement Overview:        {p1_id} ({len(p1)})")
print(f"  P2 HCP Engagement:             {p2_id} ({len(p2)})")
print(f"  P3 Patient Support & Outcomes: {p3_id} ({len(p3)})")
print(f"  P4 Client Campaign Health:     {p4_id} ({len(p4)})")
print("Done!")
