"""
Epikast uplift / "what works best" model — OFFLINE scoring step (Approach B).

Estimates the INCREMENTAL lift of each engagement tactic on three outcomes
(meaningful interaction, connect, HCP sentiment), overall and per HCP segment,
with analytic 95% confidence intervals. Writes three result tables that the
Power BI "Insights Engine" report imports:

    data/FactUplift.csv         uplift per tactic x outcome x segment (+ CIs)
    data/DimNBA.csv             next-best-action: top tactic per segment/outcome
    data/FeatureImportance.csv  overall |uplift| per tactic, per outcome

This is the train-offline -> visualise-results pattern: re-run when the data
refreshes. Kept pure-stdlib with analytic (normal-approx) CIs so it runs
anywhere. For production swap in CausalML / econml X-learner with a LightGBM
base + SHAP for record-level explanations; the output table schema stays the same.

Run:  python scripts/train_uplift.py
"""

import csv, os, math, statistics

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
Z = 1.96  # 95% CI
MIN_N = 30


def load():
    hcp = {r["HCPID"]: r for r in csv.DictReader(open(os.path.join(DATA, "DimHCP.csv")))}
    recs = []
    for c in csv.DictReader(open(os.path.join(DATA, "FactHCPCalls.csv"))):
        h = hcp.get(c["HCPID"], {})
        recs.append({
            "ai_followed": c["AIFollowed"] == "1",
            "script": c["Script"],
            "channel": c["Channel"],
            "meaningful": 1 if c["IsMeaningfulInteraction"] == "1" else 0,
            "connected": 1 if c["IsConnected"] == "1" else 0,
            "sentiment": float(c["HCPSentimentScore"]) if c["HCPSentimentScore"] else None,
            "specialty": h.get("Specialty", "?"),
            "tier": h.get("Tier", "?"),
        })
    return recs


# tactic = (name, treat predicate, control predicate)
TACTICS = [
    ("AI-Followed vs Not", lambda r: r["ai_followed"], lambda r: not r["ai_followed"]),
    ("Script A vs B", lambda r: "Empathetic" in r["script"], lambda r: "Direct" in r["script"]),
    ("Video vs Phone", lambda r: r["channel"] == "Video", lambda r: r["channel"] == "Phone"),
    ("Email vs Phone", lambda r: r["channel"] == "Email", lambda r: r["channel"] == "Phone"),
]

# outcome = (name, value fn, kind, record filter)
OUTCOMES = [
    ("Meaningful Interaction", lambda r: r["meaningful"], "binary", lambda r: True),
    ("Connect", lambda r: r["connected"], "binary", lambda r: True),
    ("HCP Sentiment", lambda r: r["sentiment"], "continuous", lambda r: r["connected"] == 1 and r["sentiment"] is not None),
]


def estimate(treated, control, kind):
    nt, nc = len(treated), len(control)
    if nt < MIN_N or nc < MIN_N:
        return None
    if kind == "binary":
        pt, pc = statistics.mean(treated), statistics.mean(control)
        se = math.sqrt(pt * (1 - pt) / nt + pc * (1 - pc) / nc)
        uplift = pt - pc
    else:
        pt, pc = statistics.mean(treated), statistics.mean(control)
        vt = statistics.variance(treated) if nt > 1 else 0
        vc = statistics.variance(control) if nc > 1 else 0
        se = math.sqrt(vt / nt + vc / nc)
        uplift = pt - pc
    lo, hi = uplift - Z * se, uplift + Z * se
    sig = 1 if (lo > 0 or hi < 0) else 0
    return pt, pc, uplift, lo, hi, nt, nc, sig


def segments(recs):
    yield ("Overall", "All", recs)
    for s in sorted(set(r["specialty"] for r in recs)):
        yield ("Specialty", s, [r for r in recs if r["specialty"] == s])
    for t in sorted(set(r["tier"] for r in recs)):
        yield ("Tier", t, [r for r in recs if r["tier"] == t])


def main():
    recs = load()
    print(f"Loaded {len(recs)} calls")
    uplift_rows, nba, feat = [], [], []
    for oname, vfn, kind, ofilter in OUTCOMES:
        for stype, sval, srecs in segments(recs):
            pool = [r for r in srecs if ofilter(r)]
            best = None
            for tname, tfn, cfn in TACTICS:
                treated = [vfn(r) for r in pool if tfn(r)]
                control = [vfn(r) for r in pool if cfn(r)]
                res = estimate(treated, control, kind)
                if res is None:
                    continue
                pt, pc, up, lo, hi, nt, nc, sig = res
                uplift_rows.append({
                    "outcome": oname, "tactic": tname, "segment_type": stype, "segment_value": sval,
                    "treated_value": round(pt, 4), "control_value": round(pc, 4),
                    "uplift": round(up, 4), "ci_low": round(lo, 4), "ci_high": round(hi, 4),
                    "n_treated": nt, "n_control": nc, "significant": sig,
                })
                if stype == "Overall":
                    feat.append({"outcome": oname, "feature": tname,
                                 "importance": round(abs(up), 4), "uplift": round(up, 4),
                                 "direction": "Helps" if up > 0 else "Hurts"})
                if sig and (best is None or up > best[1]):
                    best = (tname, up)
            nba.append({"segment_type": stype, "segment_value": sval, "outcome": oname,
                        "recommended_tactic": best[0] if best else "No clear winner",
                        "est_uplift": round(best[1], 4) if best else 0})

    def dump(name, rows, fields):
        with open(os.path.join(DATA, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
        print(f"  {name}: {len(rows)} rows")

    dump("FactUplift.csv", uplift_rows,
         ["outcome", "tactic", "segment_type", "segment_value", "treated_value", "control_value",
          "uplift", "ci_low", "ci_high", "n_treated", "n_control", "significant"])
    dump("DimNBA.csv", nba, ["segment_type", "segment_value", "outcome", "recommended_tactic", "est_uplift"])
    dump("FeatureImportance.csv", feat, ["outcome", "feature", "importance", "uplift", "direction"])
    print("Done!")


if __name__ == "__main__":
    main()
