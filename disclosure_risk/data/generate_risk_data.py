"""
Generate the reference data for the Privacy & Disclosure-Risk dashboard.

This describes the *order dataset's schema* from a data-protection angle: for each
of the 52 fields, its schema category, disclosure-control class (direct identifier,
quasi-identifier, behavioural, sensitive, technical), re-identification risk level,
the recommended statistical-disclosure-control (SDC) method, the information-loss
metric used to measure distortion, and how sparse the field is.

It also encodes an SDC *scenario ladder* — successive anonymisation configurations
(time generalisation, price rounding, quantity top-coding) — each with an indicative
re-identification risk index and an information-loss (utility-loss) index, so the
classic privacy-vs-utility trade-off can be visualised.

No real data, identifiers, or values are included — only schema-level metadata and
illustrative risk/utility indices.

Output (written next to this script):
- DimField.csv     (52 fields — risk register)
- DimScenario.csv  (16 SDC scenarios — privacy/utility ladder)

Run once:  python data/generate_risk_data.py
"""

import csv
import os

# risk_level -> numeric weight for averaging / heatmaps
RISK_WEIGHT = {"Very High": 4, "High": 3, "Medium": 2, "Low": 1}
RISK_RANK = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}

# field, schema_category, sdc_class, risk_level, sdc_method, info_loss_metric, pct_empty, research_interest
FIELDS = [
    ("investment_firm_lei", "Core", "Direct identifier", "High", "Pseudonymization", "Not applicable", 0, "No"),
    ("DEA", "Optional", "Behavioural", "Low", "None", "Not applicable", 0, "No"),
    ("client_ID", "Optional", "Direct identifier", "Very High", "Pseudonymization", "Not applicable", 0, "No"),
    ("invest_dec", "Core", "Quasi-identifier", "Medium", "Generalization", "Category change %", 0, "No"),
    ("within_firm", "Optional", "Behavioural", "Low", "None", "Not applicable", 0, "No"),
    ("non_exec", "Core", "Behavioural", "Low", "None", "Not applicable", 0, "No"),
    ("trading_capacity", "Core", "Behavioural", "Medium", "Generalization", "Category change %", 0, "No"),
    ("liq_prov_activity", "Core", "Behavioural", "Medium", "Generalization", "Category change %", 0, "No"),
    ("date_time", "Optional", "Quasi-identifier", "High", "Time generalization", "Temporal deviation", 0, "Yes"),
    ("validity_period", "Core", "Behavioural", "Medium", "Generalization", "Not applicable", 0, "No"),
    ("order_restriction", "Core", "Behavioural", "Medium", "Generalization", "Category change %", 0, "No"),
    ("validity_period_ts", "Core", "Quasi-identifier", "High", "Time generalization", "Temporal deviation", 0, "Yes"),
    ("priority_time", "Core", "Quasi-identifier", "High", "Time generalization", "Temporal deviation", 0, "Yes"),
    ("priority_size", "Optional", "Behavioural", "Medium", "Binning", "Bin change %", 30, "No"),
    ("sequence_no", "Optional", "Technical", "Low", "None", "Not applicable", 0, "Yes"),
    ("MIC", "Core", "Quasi-identifier", "Medium", "Generalization", "Category change %", 0, "No"),
    ("order_book_code", "Core", "Behavioural", "Medium", "Generalization", "Category change %", 0, "No"),
    ("fin_instr_ID", "Core", "Quasi-identifier", "High", "Pseudonymization", "Generalization level", 0, "No"),
    ("receipt_date", "Core", "Quasi-identifier", "High", "Time generalization", "Temporal deviation", 0, "Yes"),
    ("order_ID", "Core", "Direct identifier", "High", "Pseudonymization", "Not applicable", 0, "No"),
    ("order_event_type", "Core", "Behavioural", "Low", "None", "Not applicable", 0, "No"),
    ("order_type", "Core", "Behavioural", "Low", "None", "Not applicable", 0, "No"),
    ("order_type_class", "Core", "Behavioural", "Medium", "Generalization", "Category change %", 0, "No"),
    ("limit_price", "Core", "Sensitive", "High", "Noise addition / Rounding", "NMAE", 0, "Yes"),
    ("additional_limit_price", "Core", "Sensitive", "Low", "None", "Not applicable", 60, "No"),
    ("stop_price", "Core", "Sensitive", "Medium", "Noise addition / Rounding", "NMAE", 40, "Yes"),
    ("pegged_limit_price", "Core", "Sensitive", "High", "Noise addition / Rounding", "NMAE", 80, "Yes"),
    ("transaction_price", "Optional", "Sensitive", "High", "Noise addition / Rounding", "NMAE", 60, "Yes"),
    ("currency", "Core", "Non-sensitive", "Low", "None", "Not applicable", 0, "No"),
    ("leg2_currency", "Optional", "Non-sensitive", "Low", "None", "Category change %", 95, "No"),
    ("price_notation", "Core", "Non-sensitive", "Low", "None", "Not applicable", 0, "No"),
    ("buy_sell", "Optional", "Behavioural", "Low", "None", "Not applicable", 0, "No"),
    ("order_status", "Optional", "Behavioural", "Low", "None", "Not applicable", 0, "No"),
    ("quantity_notation", "Core", "Non-sensitive", "Low", "None", "Category change %", 0, "No"),
    ("quantity_currency", "Core", "Non-sensitive", "Low", "None", "Category change %", 0, "No"),
    ("initial_quantity", "Core", "Sensitive", "High", "Noise / Binning / Top-coding", "NMAE / Bin change %", 0, "Yes"),
    ("remaining_quantity", "Optional", "Sensitive", "High", "Noise / Binning / Top-coding", "NMAE / Bin change %", 40, "Yes"),
    ("displayed_quantity", "Optional", "Sensitive", "High", "Noise / Binning / Top-coding", "NMAE / Bin change %", 30, "Yes"),
    ("traded_quantity", "Optional", "Sensitive", "High", "Noise / Binning / Top-coding", "NMAE / Bin change %", 86, "Yes"),
    ("MAQ", "Optional", "Behavioural", "Low", "None", "Not applicable", 100, "No"),
    ("MES", "Optional", "Behavioural", "Low", "None", "Not applicable", 100, "No"),
    ("MES_first", "Optional", "Behavioural", "Low", "None", "Not applicable", 100, "No"),
    ("passive_only", "Optional", "Behavioural", "Low", "None", "Not applicable", 100, "No"),
    ("passive_aggressive", "Optional", "Behavioural", "Low", "None", "Not applicable", 97, "No"),
    ("self_exec_prevention", "Optional", "Behavioural", "Medium", "Generalization", "Category change %", 100, "No"),
    ("sl_order_ID", "Optional", "Direct identifier", "High", "Pseudonymization", "Not applicable", 100, "No"),
    ("routing_strategy", "Optional", "Behavioural", "Medium", "Generalization", "Category change %", 100, "No"),
    ("trading_venue_trans_ID", "Optional", "Direct identifier", "High", "Pseudonymization", "Not applicable", 0, "No"),
    ("trading_phases", "Optional", "Behavioural", "Medium", "Generalization", "Category change %", 98, "No"),
    ("auction_price", "Optional", "Sensitive", "Low", "None", "Not applicable", 99, "No"),
    ("auction_volume", "Extra", "Technical", "Low", "None", "Suppression %", 99, "No"),
    ("reserved fields", "Optional", "Technical", "Low", "Drop", "Not applicable", 100, "No"),
]

# scenario_id, level, time_generalization, price_rounding, quantity_topcoding, risk_index, utility_loss, description
SCENARIOS = [
    ("0",     "0", "None",   "None",   "No",  78, 6,  "Pseudonymization (hash) of direct identifiers only"),
    ("1",     "1", "Hour",   "None",   "No",  55, 22, "+ Time generalization of timestamps to the hour"),
    ("2",     "2", "Minute", "None",   "No",  64, 14, "+ Time generalization of timestamps to the minute"),
    ("1.1",   "1", "Hour",   "Low",    "No",  50, 30, "Scenario 1 + low-level price rounding"),
    ("1.2",   "1", "Hour",   "Medium", "No",  44, 42, "Scenario 1 + medium-level price rounding"),
    ("1.3",   "1", "Hour",   "High",   "No",  38, 55, "Scenario 1 + high-level price rounding"),
    ("2.1",   "2", "Minute", "Low",    "No",  58, 24, "Scenario 2 + low-level price rounding"),
    ("2.2",   "2", "Minute", "Medium", "No",  52, 35, "Scenario 2 + medium-level price rounding"),
    ("2.3",   "2", "Minute", "High",   "No",  46, 47, "Scenario 2 + high-level price rounding"),
    ("1.1.1", "1", "Hour",   "Low",    "Yes", 44, 41, "Scenario 1.1 + top-coding of order quantity"),
    ("1.2.1", "1", "Hour",   "Medium", "Yes", 38, 53, "Scenario 1.2 + top-coding of order quantity"),
    ("1.3.1", "1", "Hour",   "High",   "Yes", 32, 66, "Scenario 1.3 + top-coding of order quantity"),
    ("2.1.1", "2", "Minute", "Low",    "Yes", 52, 35, "Scenario 2.1 + top-coding of order quantity"),
    ("2.2.1", "2", "Minute", "Medium", "Yes", 46, 46, "Scenario 2.2 + top-coding of order quantity"),
    ("2.3.1", "2", "Minute", "High",   "Yes", 40, 58, "Scenario 2.3 + top-coding of order quantity"),
]


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(out_dir, "DimField.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field", "schema_category", "sdc_class", "risk_level", "risk_weight",
                    "risk_rank", "sdc_method", "info_loss_metric", "pct_empty",
                    "research_interest", "needs_sdc"])
        for (field, schema_cat, sdc_class, risk, method, metric, pct, research) in FIELDS:
            needs = "Yes" if method not in ("None", "Drop") else "No"
            w.writerow([field, schema_cat, sdc_class, risk, RISK_WEIGHT[risk],
                        RISK_RANK[risk], method, metric, pct, research, needs])

    with open(os.path.join(out_dir, "DimScenario.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scenario_id", "level", "time_generalization", "price_rounding",
                    "quantity_topcoding", "risk_index", "utility_loss", "protection_gain",
                    "description"])
        base_risk = 78  # base-case risk index, for protection-gain reference
        for (sid, level, timegen, rounding, topcode, risk, util, desc) in SCENARIOS:
            w.writerow([sid, level, timegen, rounding, topcode, risk, util,
                        base_risk - risk, desc])

    n_di = sum(1 for r in FIELDS if r[2] == "Direct identifier")
    n_high = sum(1 for r in FIELDS if r[3] in ("High", "Very High"))
    print(f"Generated risk register: {len(FIELDS)} fields "
          f"({n_di} direct identifiers, {n_high} high/very-high risk)")
    print(f"Generated SDC scenario ladder: {len(SCENARIOS)} scenarios")
    print(f"  Output dir: {out_dir}")


if __name__ == "__main__":
    main()
