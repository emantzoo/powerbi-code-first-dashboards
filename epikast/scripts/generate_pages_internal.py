"""
Epikast INTERNAL report — for Epikast's own delivery & operations teams.

Includes rep-level performance, quality/compliance, and workforce capacity —
content you would NOT expose to a biopharma client. Runs against the shared
Epikast semantic model (see Epikast_Dashboard_Prompts.md) and writes into the
internal report definition only.

Run with Power BI closed:  python scripts/generate_pages_internal.py
"""

import os
import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_card, make_slicer, make_clustered_bar,
    make_clustered_bar_gradient, make_line_chart, make_area_chart, make_donut,
    make_scatter, make_matrix, make_table, make_button, write_page, write_pages_json,
)

# Point at the INTERNAL report's pages folder.
pb.BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\epikast\epikast_internal_dashb.Report\definition\pages"

INDIGO = "#3730A3"   # internal report accent

# ===== PAGE 1: Operations Overview =====
p1_id = uid("epi_int_p1_ops")
p1 = [
    make_title_bar("i1_title", 0, 0, 1280, 50, "Epikast Internal — Operations Overview", INDIGO),
    make_card("i1_interactions", 20, 60, 235, 140, "_Measures", "Total Interactions"),
    make_card("i1_connect", 270, 60, 235, 140, "_Measures", "Connect Rate"),
    make_card("i1_agents", 520, 60, 235, 140, "_Measures", "Active Agents"),
    make_card("i1_minutes", 770, 60, 235, 140, "_Measures", "Total Engagement Minutes"),
    make_slicer("i1_year", 1020, 60, 230, 140, "Calendar", "Year"),
    make_clustered_bar_gradient("i1_team_bar", 20, 220, 400, 280, "DimAgent", "team", "_Measures", "Total Interactions"),
    make_line_chart("i1_trend", 440, 220, 400, 280, "Calendar", "Year_Month", "_Measures", "Total Interactions", "_Measures", "Interactions PY"),
    make_donut("i1_channel", 860, 220, 380, 280, "FactInteractions", "channel", "_Measures", "Total Interactions"),
    make_area_chart("i1_minutes_area", 20, 520, 600, 160, "Calendar", "Year_Month", "_Measures", "Total Engagement Minutes"),
    make_clustered_bar("i1_type_bar", 640, 520, 600, 160, "FactInteractions", "interaction_type", "_Measures", "Total Interactions"),
    make_button("i1_btn_agents", 1100, 670, 150, 40, "Agents"),
]

# ===== PAGE 2: Agent & Rep Performance =====
p2_id = uid("epi_int_p2_agents")
p2 = [
    make_title_bar("i2_title", 0, 0, 1280, 50, "Epikast Internal — Agent & Rep Performance", INDIGO),
    make_card("i2_agents", 20, 60, 235, 140, "_Measures", "Active Agents"),
    make_card("i2_per_agent", 270, 60, 235, 140, "_Measures", "Interactions per Agent"),
    make_card("i2_connect", 520, 60, 235, 140, "_Measures", "Connect Rate"),
    make_card("i2_duration", 770, 60, 235, 140, "_Measures", "Avg Interaction Duration"),
    make_slicer("i2_role", 1020, 60, 230, 140, "DimAgent", "role"),
    make_clustered_bar("i2_role_bar", 20, 220, 400, 280, "DimAgent", "role", "_Measures", "Total Interactions"),
    make_scatter("i2_scatter", 440, 220, 800, 280, "DimAgent", "agent_name",
                 "_Measures", "Connect Rate", "_Measures", "Avg Sentiment Score",
                 "_Measures", "Total Interactions"),
    make_matrix("i2_matrix", 20, 520, 1230, 180,
        [("DimAgent", "role")],
        [("DimAgent", "team")],
        [("_Measures", "Total Interactions"), ("_Measures", "Connect Rate"),
         ("_Measures", "Avg Interaction Duration"), ("_Measures", "Avg Sentiment Score"),
         ("_Measures", "Avg Script Adherence")]),
    make_button("i2_btn_back", 20, 670, 100, 40, "Back"),
    make_button("i2_btn_quality", 1100, 670, 150, 40, "Quality"),
]

# ===== PAGE 3: Quality & Compliance =====
p3_id = uid("epi_int_p3_quality")
p3 = [
    make_title_bar("i3_title", 0, 0, 1280, 50, "Epikast Internal — Quality & Compliance", INDIGO),
    make_card("i3_compliance", 20, 60, 235, 140, "_Measures", "Compliance Pass Rate"),
    make_card("i3_adherence", 270, 60, 235, 140, "_Measures", "Avg Script Adherence"),
    make_card("i3_ae", 520, 60, 235, 140, "_Measures", "Adverse Event Rate"),
    make_card("i3_pos", 770, 60, 235, 140, "_Measures", "Positive Sentiment Pct"),
    make_slicer("i3_team", 1020, 60, 230, 140, "DimAgent", "team"),
    make_clustered_bar("i3_role_adh", 20, 220, 400, 280, "DimAgent", "role", "_Measures", "Avg Script Adherence"),
    make_line_chart("i3_sentiment_trend", 440, 220, 400, 280, "Calendar", "Year_Month", "_Measures", "Avg Sentiment Score"),
    make_donut("i3_outcome", 860, 220, 380, 280, "FactInteractions", "outcome", "_Measures", "Total Interactions"),
    make_table("i3_table", 20, 520, 1230, 160, [
        ("DimAgent", "team", False),
        ("_Measures", "Compliance Pass Rate", True),
        ("_Measures", "Compliance Reviews", True),
        ("_Measures", "Adverse Events Flagged", True),
        ("_Measures", "Avg Script Adherence", True),
        ("_Measures", "Avg Sentiment Score", True),
    ]),
    make_button("i3_btn_back", 20, 670, 100, 40, "Back"),
    make_button("i3_btn_workforce", 1100, 670, 150, 40, "Workforce"),
]

# ===== PAGE 4: Workforce & Capacity =====
p4_id = uid("epi_int_p4_workforce")
p4 = [
    make_title_bar("i4_title", 0, 0, 1280, 50, "Epikast Internal — Workforce & Capacity", INDIGO),
    make_card("i4_roster", 20, 60, 235, 140, "_Measures", "Roster Size"),
    make_card("i4_active", 270, 60, 235, 140, "_Measures", "Active Agents"),
    make_card("i4_util", 520, 60, 235, 140, "_Measures", "Agent Utilization"),
    make_card("i4_tenure", 770, 60, 235, 140, "_Measures", "Avg Tenure Months"),
    make_slicer("i4_hub", 1020, 60, 230, 140, "DimAgent", "hub_location"),
    make_clustered_bar("i4_hub_bar", 20, 220, 400, 280, "DimAgent", "hub_location", "_Measures", "Total Interactions"),
    make_scatter("i4_scatter", 440, 220, 800, 280, "DimAgent", "agent_name",
                 "_Measures", "Avg Tenure Months", "_Measures", "Interactions per Agent",
                 "_Measures", "Total Interactions"),
    make_table("i4_table", 20, 520, 1230, 160, [
        ("DimAgent", "hub_location", False),
        ("DimAgent", "team", False),
        ("_Measures", "Roster Size", True),
        ("_Measures", "Active Agents", True),
        ("_Measures", "Total Interactions", True),
        ("_Measures", "Interactions per Agent", True),
        ("_Measures", "Connect Rate", True),
    ]),
    make_button("i4_btn_back", 20, 670, 100, 40, "Back"),
]

write_page(p1_id, "Operations Overview", p1)
write_page(p2_id, "Agent & Rep Performance", p2)
write_page(p3_id, "Quality & Compliance", p3)
write_page(p4_id, "Workforce & Capacity", p4)
write_pages_json([p1_id, p2_id, p3_id, p4_id])

print(f"INTERNAL report — 4 pages, {len(p1)+len(p2)+len(p3)+len(p4)} visuals")
print(f"  P1 Operations Overview:     {p1_id} ({len(p1)})")
print(f"  P2 Agent & Rep Performance: {p2_id} ({len(p2)})")
print(f"  P3 Quality & Compliance:    {p3_id} ({len(p3)})")
print(f"  P4 Workforce & Capacity:    {p4_id} ({len(p4)})")
print("Done!")
