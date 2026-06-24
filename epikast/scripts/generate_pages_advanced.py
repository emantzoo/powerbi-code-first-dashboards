"""
Epikast ADVANCED ANALYTICS report — multivariate / causal "what works best".

5 pages mixing native visuals, embedded R visuals (PortPulse-style), and a
Python SHAP visual:
  1. What Works Best (Multivariate)  — interaction + uplift heatmaps, AI-adoption lift   [native]
  2. Progress & Cohorts              — cohort ramp heatmap, slope, experiment power/winner [native]
  3. Forest Plot & Parallel Coords   — uplift forest plot, winning-call parallel coords    [R]
  4. Patient Journey & Survival      — PA→outcome alluvial, time-to-therapy survival curves [R]
  5. SHAP Explainability             — mean|SHAP| bar + beeswarm                           [native + Python]

Prerequisites: run scripts/train_uplift.py (FactUplift etc.) and, for page 5,
scripts/train_shap.py (ShapImportance / ShapBeeswarm). R visuals need R + ggplot2,
GGally, ggalluvial, survival, survminer installed and configured in Power BI
Desktop; the Python visual needs Python + matplotlib. These render as static images.

Run with Power BI closed:  python scripts/generate_pages_advanced.py
"""

import pbir_lib as pb
from pbir_lib import (
    uid, make_title_bar, make_matrix_heatmap, make_clustered_bar,
    make_clustered_column_multi, make_line_chart, make_table, make_r_visual, make_py_visual,
    slicer_row,
    SLICER_H, GAP, TITLE_BOT,
    SL_Y, BODY_Y, BODY_H,
    write_page, write_pages_json,
)

pb.BASE = pb.resolve_pages_base("epikast_advanced_dashb")

PURPLE = "#5B21B6"
M      = "_Measures"


# ===== PAGE 1: What Works Best (Multivariate) — native =====
p1 = uid("epi_adv_p1_works")

TOP1_H   = (BODY_H - GAP) // 2   # ~296 top row
BOT1_H   = BODY_H - TOP1_H - GAP  # ~296 bottom row
BOT1_Y   = BODY_Y + TOP1_H + GAP

P1 = [
    make_title_bar("v1_t", 0, 0, 1280, 50, "Epikast Advanced — What Works Best (Multivariate)", PURPLE),

    *slicer_row("v1sl", SL_Y, SLICER_H, [
        ("FactUplift", "outcome"),
        ("FactUplift", "segment_type"),
    ]),

    make_matrix_heatmap("v1_inter", 20, BODY_Y, 610, TOP1_H,
        [("FactHCPCalls", "Channel")], [("FactHCPCalls", "InteractionType")],
        M, "Meaningful Interaction Rate"),
    make_matrix_heatmap("v1_uplift", 650, BODY_Y, 610, TOP1_H,
        [("FactUplift", "segment_value")], [("FactUplift", "tactic")],
        M, "Avg Uplift"),

    make_clustered_column_multi("v1_aiband", 20, BOT1_Y, 610, BOT1_H,
        "DimRep", "AI Adoption Band",
        [(M, "Connect Rate"), (M, "Meaningful Interaction Rate")]),
    make_table("v1_tbl", 650, BOT1_Y, 610, BOT1_H, [
        ("FactUplift", "tactic",        False),
        ("FactUplift", "segment_value", False),
        ("FactUplift", "uplift",        False),
        ("FactUplift", "ci_low",        False),
        ("FactUplift", "ci_high",       False),
        ("FactUplift", "significant",   False),
    ]),
]


# ===== PAGE 2: Progress & Cohorts — native =====
p2 = uid("epi_adv_p2_progress")

TOP2_H  = (BODY_H - GAP) // 2
BOT2_H  = BODY_H - TOP2_H - GAP
BOT2_Y  = BODY_Y + TOP2_H + GAP

P2 = [
    make_title_bar("v2_t", 0, 0, 1280, 50, "Epikast Advanced — Progress & Cohorts", PURPLE),

    make_matrix_heatmap("v2_cohort", 20, BODY_Y, 800, TOP2_H,
        [("DimRep", "Tenure Bucket")], [("DimCalendar", "YearMonth")],
        M, "Meaningful Interaction Rate"),
    make_line_chart("v2_slope", 840, BODY_Y, 420, TOP2_H,
        "DimCalendar", "YearMonth",
        M, "Meaningful Interaction Rate", M, "Connect Rate"),

    make_table("v2_power", 20, BOT2_Y, 620, BOT2_H, [
        ("DimExperiment", "ExperimentName",     False),
        ("DimExperiment", "PrimaryKPI",         False),
        ("DimExperiment", "SampleSizeTarget",   False),
        ("DimExperiment", "SampleSizeActual",   False),
        ("DimExperiment", "ConfidenceLevel",    False),
        ("DimExperiment", "Status",             False),
    ]),
    make_table("v2_winner", 660, BOT2_Y, 600, BOT2_H, [
        ("DimExperiment", "ExperimentName", False),
        ("DimExperiment", "Winner",         False),
        ("DimExperiment", "EndDate",        False),
        ("DimExperiment", "ObservedLift",   False),
        ("DimExperiment", "Status",         False),
    ]),
]


# ===== PAGE 3: Forest Plot & Parallel Coordinates — R =====
FOREST_R = """
library(ggplot2)
df <- dataset
df <- df[order(df$uplift),]
df$tactic <- factor(df$tactic, levels=unique(df$tactic))
df$Significant <- ifelse(df$significant==1,'Significant','Not significant')
ggplot(df, aes(x=uplift, y=tactic, color=Significant)) +
  geom_vline(xintercept=0, linetype='dashed', color='grey50') +
  geom_errorbarh(aes(xmin=ci_low, xmax=ci_high), height=0.25) +
  geom_point(size=3.5) +
  scale_color_manual(values=c('Significant'='#2E8B57','Not significant'='grey60')) +
  labs(title='Uplift by tactic (95% CI)', x='Uplift', y=NULL) +
  theme_minimal(base_size=13)
"""
PARCOORD_R = """
library(GGally); library(ggplot2)
df <- dataset
df <- df[!is.na(df$CallQualityScore) & !is.na(df$HCPSentimentScore),]
set.seed(1); if(nrow(df)>600) df <- df[sample(nrow(df),600),]
df$Meaningful <- factor(ifelse(df$IsMeaningfulInteraction==1,'Meaningful','Not'))
cols <- c('DurationMinutes','CallQualityScore','HCPSentimentScore','AIFollowed','ScriptDeviation')
ggparcoord(df, columns=which(names(df) %in% cols), groupColumn='Meaningful',
           scale='uniminmax', alphaLines=0.25) +
  scale_color_manual(values=c('Meaningful'='#2E8B57','Not'='#CD3333')) +
  labs(title='Anatomy of a winning call', x=NULL, y=NULL) + theme_minimal(base_size=12)
"""

p3 = uid("epi_adv_p3_forest")

P3 = [
    make_title_bar("v3_t", 0, 0, 1280, 50, "Epikast Advanced — Forest Plot & Parallel Coordinates", PURPLE),

    *slicer_row("v3sl", SL_Y, SLICER_H, [
        ("FactUplift", "outcome"),
        ("FactUplift", "segment_type"),
    ]),

    make_r_visual("v3_forest", 20, BODY_Y, 620, BODY_H, [
        ("FactUplift", "outcome",       False),
        ("FactUplift", "segment_type",  False),
        ("FactUplift", "segment_value", False),
        ("FactUplift", "tactic",        False),
        ("FactUplift", "uplift",        False),
        ("FactUplift", "ci_low",        False),
        ("FactUplift", "ci_high",       False),
        ("FactUplift", "significant",   False),
    ], FOREST_R),
    make_r_visual("v3_parcoord", 660, BODY_Y, 600, BODY_H, [
        ("FactHCPCalls", "CallID",                  False),
        ("FactHCPCalls", "DurationMinutes",          False),
        ("FactHCPCalls", "CallQualityScore",         False),
        ("FactHCPCalls", "HCPSentimentScore",        False),
        ("FactHCPCalls", "AIFollowed",               False),
        ("FactHCPCalls", "ScriptDeviation",          False),
        ("FactHCPCalls", "IsMeaningfulInteraction",  False),
    ], PARCOORD_R),
]


# ===== PAGE 4: Patient Journey & Survival — R =====
ALLUVIAL_R = """
library(ggalluvial); library(ggplot2); library(dplyr)
df <- dataset %>% count(PAStatus, CaseStatus)
ggplot(df, aes(axis1=PAStatus, axis2=CaseStatus, y=n)) +
  geom_alluvium(aes(fill=PAStatus), alpha=0.7) +
  geom_stratum(width=0.3) +
  geom_text(stat='stratum', aes(label=after_stat(stratum)), size=3) +
  scale_x_discrete(limits=c('PA Status','Case Outcome'), expand=c(.05,.05)) +
  labs(title='Patient access flow: PA decision -> outcome', y='Patients', x=NULL) +
  theme_minimal(base_size=12)
"""
SURVIVAL_R = """
library(survival); library(survminer)
df <- dataset
df$time <- ifelse(is.na(df$TimeToTherapyDays) | df$TimeToTherapyDays<=0, 60, df$TimeToTherapyDays)
df$event <- ifelse(df$IsAbandoned==1, 0, 1)
fit <- survfit(Surv(time, event) ~ InsuranceType, data=df)
ggsurvplot(fit, data=df, conf.int=TRUE, legend.title='Insurance',
           xlab='Days since Rx', ylab='Share not yet on therapy',
           title='Time to therapy by insurance')$plot
"""

p4 = uid("epi_adv_p4_journey")

P4 = [
    make_title_bar("v4_t", 0, 0, 1280, 50, "Epikast Advanced — Patient Journey & Survival", PURPLE),

    *slicer_row("v4sl", SL_Y, SLICER_H, [
        ("DimDrug", "DrugName"),
    ]),

    make_r_visual("v4_alluvial", 20, BODY_Y, 620, BODY_H, [
        ("FactPatientCases", "CaseID",    False),
        ("FactPatientCases", "PAStatus",  False),
        ("FactPatientCases", "CaseStatus", False),
    ], ALLUVIAL_R),
    make_r_visual("v4_survival", 660, BODY_Y, 600, BODY_H, [
        ("FactPatientCases", "CaseID",             False),
        ("FactPatientCases", "TimeToTherapyDays",  False),
        ("FactPatientCases", "IsAbandoned",        False),
        ("FactPatientCases", "InsuranceType",      False),
    ], SURVIVAL_R),
]


# ===== PAGE 5: SHAP Explainability — native + Python =====
BEESWARM_PY = """
import matplotlib.pyplot as plt
import numpy as np
df = dataset
feats = list(dict.fromkeys(df['feature']))
fig, ax = plt.subplots(figsize=(8,5))
sc = None
for i, f in enumerate(feats):
    sub = df[df['feature'] == f]
    y = i + (np.random.rand(len(sub)) - 0.5) * 0.6
    sc = ax.scatter(sub['shap_value'], y, c=sub['feature_value_norm'], cmap='coolwarm', s=10, alpha=0.6)
ax.set_yticks(range(len(feats))); ax.set_yticklabels(feats)
ax.axvline(0, color='grey', lw=0.8)
ax.set_xlabel('SHAP value (impact on meaningful interaction)')
if sc is not None: plt.colorbar(sc, label='feature value')
plt.title('SHAP beeswarm — drivers of meaningful interaction')
plt.tight_layout(); plt.show()
"""

p5 = uid("epi_adv_p5_shap")

# No slicer needed on SHAP page — full canvas for charts
SHAP_Y = TITLE_BOT
SHAP_H = 720 - SHAP_Y - 10

P5 = [
    make_title_bar("v5_t", 0, 0, 1280, 50, "Epikast Advanced — SHAP Explainability", PURPLE),
    make_clustered_bar("v5_imp", 20, SHAP_Y, 500, SHAP_H,
        "ShapImportance", "feature", M, "Avg Shap Importance"),
    make_py_visual("v5_beeswarm", 540, SHAP_Y, 720, SHAP_H, [
        ("ShapBeeswarm", "feature",            False),
        ("ShapBeeswarm", "shap_value",         False),
        ("ShapBeeswarm", "feature_value_norm", False),
    ], BEESWARM_PY),
]


write_page(p1, "What Works Best",                P1)
write_page(p2, "Progress & Cohorts",             P2)
write_page(p3, "Forest Plot & Parallel Coords",  P3)
write_page(p4, "Patient Journey & Survival",     P4)
write_page(p5, "SHAP Explainability",            P5)
write_pages_json([p1, p2, p3, p4, p5])

print("ADVANCED ANALYTICS report — 5 pages")
for n, pg in [("What Works Best", P1), ("Progress & Cohorts", P2), ("Forest/Parallel", P3),
              ("Journey/Survival", P4), ("SHAP", P5)]:
    print(f"  {n}: {len(pg)} visuals")
print(f"Total: {sum(len(p) for p in [P1,P2,P3,P4,P5])} visuals")
print("Done!")
