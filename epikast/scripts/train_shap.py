"""
Epikast SHAP explainability — OFFLINE step for the Advanced report's SHAP page.

Trains a LightGBM classifier to predict meaningful HCP interactions, computes
SHAP values, and writes the two tables the SHAP page imports plus a static
beeswarm PNG:

    data/ShapImportance.csv   feature, mean_abs_shap, direction
    data/ShapBeeswarm.csv     feature, shap_value, feature_value_norm  (sampled)
    images/epikast_shap_beeswarm.png

REQUIRES (not in the stdlib — install where you run this):
    pip install pandas numpy lightgbm shap matplotlib scikit-learn

Run:  python scripts/train_shap.py
This is the production-grade explainability path (vs. the rate-difference uplift
in train_uplift.py). Re-run when the data refreshes.
"""

import os, sys, csv

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
IMAGES = os.path.join(HERE, "..", "..", "images")

try:
    import numpy as np
    import pandas as pd
    import lightgbm as lgb
    import shap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as e:
    sys.exit(f"Missing dependency: {e}. Install with:\n"
             f"  pip install pandas numpy lightgbm shap matplotlib scikit-learn")

FEATURES = ["AIFollowed", "ScriptDeviation", "DurationMinutes", "CallQualityScore",
            "HCPSentimentScore", "ScriptIsA", "ChannelVideo", "ChannelEmail"]
SAMPLE_BEESWARM = 1500


def main():
    df = pd.read_csv(os.path.join(DATA, "FactHCPCalls.csv"))
    df = df[df["IsConnected"] == 1].copy()           # meaningful only defined for connected
    df["ScriptIsA"] = (df["Script"].str.contains("Empathetic")).astype(int)
    df["ChannelVideo"] = (df["Channel"] == "Video").astype(int)
    df["ChannelEmail"] = (df["Channel"] == "Email").astype(int)
    for c in ["DurationMinutes", "CallQualityScore", "HCPSentimentScore"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["CallQualityScore", "HCPSentimentScore"])

    X = df[FEATURES].astype(float)
    y = df["IsMeaningfulInteraction"].astype(int)

    model = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, verbose=-1)
    model.fit(X, y)
    print(f"Trained LightGBM on {len(X)} connected calls")

    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(X)
    if isinstance(sv, list):           # binary classifier → take positive class
        sv = sv[1]
    sv = np.asarray(sv)

    # ── ShapImportance.csv ──
    mean_abs = np.abs(sv).mean(axis=0)
    corr_sign = []
    for j, f in enumerate(FEATURES):
        c = np.corrcoef(X[f], sv[:, j])[0, 1] if X[f].std() > 0 else 0
        corr_sign.append("Helps" if c >= 0 else "Hurts")
    imp = sorted(zip(FEATURES, mean_abs, corr_sign), key=lambda t: -t[1])
    with open(os.path.join(DATA, "ShapImportance.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["feature", "mean_abs_shap", "direction"])
        for name, val, d in imp:
            w.writerow([name, round(float(val), 5), d])
    print(f"  ShapImportance.csv: {len(imp)} rows")

    # ── ShapBeeswarm.csv (sampled long form) ──
    idx = np.random.RandomState(42).choice(len(X), size=min(SAMPLE_BEESWARM, len(X)), replace=False)
    rows = []
    for j, fname in enumerate(FEATURES):
        col = X[fname].values
        lo, hi = col.min(), col.max()
        for i in idx:
            norm = (col[i] - lo) / (hi - lo) if hi > lo else 0.5
            rows.append([fname, round(float(sv[i, j]), 5), round(float(norm), 4)])
    with open(os.path.join(DATA, "ShapBeeswarm.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["feature", "shap_value", "feature_value_norm"]); w.writerows(rows)
    print(f"  ShapBeeswarm.csv: {len(rows)} rows")

    # ── static beeswarm PNG ──
    os.makedirs(IMAGES, exist_ok=True)
    shap.summary_plot(sv, X, show=False, max_display=len(FEATURES))
    plt.title("SHAP beeswarm — drivers of meaningful interaction")
    plt.tight_layout()
    out_png = os.path.join(IMAGES, "epikast_shap_beeswarm.png")
    plt.savefig(out_png, dpi=130, bbox_inches="tight"); plt.close()
    print(f"  {out_png}")
    print("Done!")


if __name__ == "__main__":
    main()
