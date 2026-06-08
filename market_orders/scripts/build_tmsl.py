"""
Generate a TMSL createOrReplace script for the Market Orders model.
Mirrors MarketOrders_Dashboard_Prompts.md Phase 0 -> 2F exactly.
Output: C:\\tmp\\model.tmsl.json
"""
import json

CSV = r"C:\Users\emantzouni\Documents\powerbi-code-first-dashboards\market_orders\data\order_events.csv"

# ---- Phase 0 column types -> (TOM dataType, M type) ----
TEXT = ("string", "type text")
BOOL = ("boolean", "type logical")
# DateTime cols are ISO-8601 with microseconds + trailing Z (e.g. 2025-07-11T07:00:14.064744Z).
# Power Query's plain `type datetime` cannot parse the Z -> conversion errors. So we keep these
# as text in the bulk transform and convert them in a dedicated step (see m_expr below).
DT   = ("dateTime", "type text")   # TOM dataType stays dateTime; M produces datetime via custom step
INT  = ("int64", "Int64.Type")
DEC  = ("double", "type number")

DT_COLS = ["date_time", "validity_period_ts", "priority_time", "receipt_date"]

cols = [
    ("investment_firm_lei", TEXT), ("DEA", BOOL), ("client_ID", TEXT), ("invest_dec", TEXT),
    ("within_firm", TEXT), ("non_exec", TEXT), ("trading_capacity", TEXT), ("liq_prov_activity", BOOL),
    ("date_time", DT), ("validity_period", TEXT), ("order_restriction", TEXT), ("validity_period_ts", DT),
    ("priority_time", DT), ("priority_size", INT), ("sequence_no", INT), ("MIC", TEXT),
    ("order_book_code", TEXT), ("fin_instr_ID", TEXT), ("receipt_date", DT), ("order_ID", TEXT),
    ("order_event_type", TEXT), ("order_type", TEXT), ("order_type_class", TEXT), ("limit_price", DEC),
    ("additional_limit_price", DEC), ("stop_price", DEC), ("pegged_limit_price", DEC), ("transaction_price", DEC),
    ("currency", TEXT), ("leg2_currency", TEXT), ("price_notation", TEXT), ("buy_sell", TEXT),
    ("order_status", TEXT), ("quantity_notation", TEXT), ("quantity_currency", TEXT), ("initial_quantity", INT),
    ("remaining_quantity", INT), ("displayed_quantity", INT), ("traded_quantity", INT), ("MAQ", INT),
    ("MES", INT), ("MES_first", BOOL), ("passive_only", BOOL), ("passive_aggressive", TEXT),
    ("self_exec_prevention", TEXT), ("sl_order_ID", TEXT), ("routing_strategy", TEXT),
    ("trading_venue_trans_ID", TEXT), ("trading_phases", TEXT), ("auction_price", DEC),
    ("auction_volume", INT), ("reserved fields", TEXT),
]

# ---- M expression (Power Query) ----
# Bulk type transform (datetime cols typed as text here), then a custom datetime parse step
# that strips the trailing Z and parses the ISO microsecond format, tolerating blanks/nulls.
transforms = ", ".join('{"%s", %s}' % (n, mtype) for n, (tom, mtype) in cols)
dt_transforms = ", ".join(
    '{"%s", each if _ = null or Text.Trim(_) = "" then null else '
    'DateTime.FromText(Text.TrimEnd(_, "Z"), [Format="yyyy-MM-ddTHH:mm:ss.FFFFFF", Culture="en-US"]), type datetime}' % c
    for c in DT_COLS
)
m_lines = [
    "let",
    '    Source = Csv.Document(File.Contents("%s"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),' % CSV.replace("\\", "\\\\"),
    "    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
    "    Typed = Table.TransformColumnTypes(Promoted, {%s})," % transforms,
    "    Dated = Table.TransformColumns(Typed, {%s})" % dt_transforms,
    "in",
    "    Dated",
]
m_expr = "\n".join(m_lines)

# ---- Source columns (data columns from the CSV) ----
source_columns = []
for n, (tom, mtype) in cols:
    source_columns.append({
        "name": n,
        "dataType": tom,
        "sourceColumn": n,
    })

# ---- Phase 1 calculated columns (order matters for readability; engine resolves deps) ----
calc_cols = [
    ("EventHour", "HOUR(OrderEvents[date_time])", "int64", None),
    ("IsNew", 'IF(OrderEvents[order_event_type] = "NEWO", 1, 0)', "int64", None),
    ("IsModify", 'IF(OrderEvents[order_event_type] = "REME", 1, 0)', "int64", None),
    ("IsCancel", 'IF(OrderEvents[order_event_type] = "CAME", 1, 0)', "int64", None),
    ("IsTrade", 'IF(OrderEvents[order_event_type] IN {"FILL", "PARF"}, 1, 0)', "int64", None),
    ("TradedNotional",
     'IF(OrderEvents[IsTrade] = 1, OrderEvents[traded_quantity] * OrderEvents[transaction_price], BLANK())',
     "double", None),
    ("RefPrice",
     'CALCULATE(AVERAGE(OrderEvents[limit_price]), ALLEXCEPT(OrderEvents, OrderEvents[fin_instr_ID]), '
     'OrderEvents[order_event_type] = "NEWO", OrderEvents[limit_price] > 0)', "double", None),
    ("EffectivePrice",
     'IF(OrderEvents[limit_price] > 0, OrderEvents[limit_price], OrderEvents[transaction_price])', "double", None),
    ("PriceDevBps",
     'IF(OrderEvents[RefPrice] > 0 && OrderEvents[EffectivePrice] > 0, '
     'DIVIDE(OrderEvents[EffectivePrice] - OrderEvents[RefPrice], OrderEvents[RefPrice]) * 10000, BLANK())',
     "double", None),
    ("AbsPriceDevBps",
     'IF(NOT ISBLANK(OrderEvents[PriceDevBps]), ABS(OrderEvents[PriceDevBps]), BLANK())', "double", None),
    ("OffMarket", 'IF(OrderEvents[AbsPriceDevBps] >= 150, 1, 0)', "int64", None),
    ("NewoTime",
     'CALCULATE(MIN(OrderEvents[date_time]), ALLEXCEPT(OrderEvents, OrderEvents[order_ID]), '
     'OrderEvents[order_event_type] = "NEWO")', "dateTime", None),
    ("CancelLatencyMs",
     'IF(OrderEvents[order_event_type] = "CAME" && NOT ISBLANK(OrderEvents[NewoTime]), '
     '(OrderEvents[date_time] - OrderEvents[NewoTime]) * 86400000.0, BLANK())', "double", None),
    ("RapidCancel",
     'IF(OrderEvents[order_event_type] = "CAME" && OrderEvents[CancelLatencyMs] >= 0 '
     '&& OrderEvents[CancelLatencyMs] <= 1000, 1, 0)', "int64", None),
    ("AnomalyFlag", 'IF(OrderEvents[OffMarket] = 1 || OrderEvents[RapidCancel] = 1, 1, 0)', "int64", None),
    ("AnomalyType",
     'SWITCH(TRUE(), OrderEvents[OffMarket] = 1 && OrderEvents[RapidCancel] = 1, "Off-market + Rapid cancel", '
     'OrderEvents[OffMarket] = 1, "Off-market price", OrderEvents[RapidCancel] = 1, "Rapid cancel", "None")',
     "string", None),
    ("IsAlgo", 'IF(LEFT(OrderEvents[invest_dec], 4) = "ALGO", 1, 0)', "int64", None),
    ("IsPassiveFill",
     'IF(OrderEvents[IsTrade] = 1 && OrderEvents[passive_aggressive] = "PASV", 1, 0)', "int64", None),
    ("FirstFillTime",
     'CALCULATE(MIN(OrderEvents[date_time]), ALLEXCEPT(OrderEvents, OrderEvents[order_ID]), '
     'OrderEvents[order_event_type] IN {"FILL", "PARF"})', "dateTime", None),
    ("TimeToFillSec",
     'IF(OrderEvents[order_event_type] = "NEWO" && NOT ISBLANK(OrderEvents[FirstFillTime]), '
     '(OrderEvents[FirstFillTime] - OrderEvents[date_time]) * 86400.0, BLANK())', "double", None),
    ("SizeBucket",
     'SWITCH(TRUE(), OrderEvents[initial_quantity] <= 50, "1-50", OrderEvents[initial_quantity] <= 200, "51-200", '
     'OrderEvents[initial_quantity] <= 1000, "201-1,000", OrderEvents[initial_quantity] <= 5000, "1,001-5,000", ">5,000")',
     "string", None),
    ("SizeBucketSort",
     'SWITCH(TRUE(), OrderEvents[initial_quantity] <= 50, 1, OrderEvents[initial_quantity] <= 200, 2, '
     'OrderEvents[initial_quantity] <= 1000, 3, OrderEvents[initial_quantity] <= 5000, 4, 5)', "int64", None),
    ("DistanceBucket",
     'IF(ISBLANK(OrderEvents[AbsPriceDevBps]), "n/a", SWITCH(TRUE(), OrderEvents[AbsPriceDevBps] <= 10, "0-10 bps", '
     'OrderEvents[AbsPriceDevBps] <= 25, "10-25 bps", OrderEvents[AbsPriceDevBps] <= 50, "25-50 bps", '
     'OrderEvents[AbsPriceDevBps] <= 100, "50-100 bps", OrderEvents[AbsPriceDevBps] <= 150, "100-150 bps", "150+ bps"))',
     "string", None),
    ("DistanceBucketSort",
     'IF(ISBLANK(OrderEvents[AbsPriceDevBps]), 0, SWITCH(TRUE(), OrderEvents[AbsPriceDevBps] <= 10, 1, '
     'OrderEvents[AbsPriceDevBps] <= 25, 2, OrderEvents[AbsPriceDevBps] <= 50, 3, OrderEvents[AbsPriceDevBps] <= 100, 4, '
     'OrderEvents[AbsPriceDevBps] <= 150, 5, 6))', "int64", None),
]

calc_col_objs = []
for name, expr, dtype, _ in calc_cols:
    obj = {"type": "calculated", "name": name, "dataType": dtype, "expression": expr}
    calc_col_objs.append(obj)

# sort-by settings
sortby = {"SizeBucket": "SizeBucketSort", "DistanceBucket": "DistanceBucketSort"}
for obj in calc_col_objs:
    if obj["name"] in sortby:
        obj["sortByColumn"] = sortby[obj["name"]]

all_oe_columns = source_columns + calc_col_objs

# ---- Measures (Phase 2A-2F) with format strings ----
PCT = "0.0%"
CUR = r"\$#,0;(\$#,0)"
NUM2 = "0.00"
NUM1 = "0.0"
WHOLE = "#,0"

measures = [
    ("Total Events", "COUNTROWS(OrderEvents)", None),
    ("New Orders", 'CALCULATE(COUNTROWS(OrderEvents), OrderEvents[order_event_type] = "NEWO")', None),
    ("Modifications", 'CALCULATE(COUNTROWS(OrderEvents), OrderEvents[order_event_type] = "REME")', None),
    ("Cancellations", 'CALCULATE(COUNTROWS(OrderEvents), OrderEvents[order_event_type] = "CAME")', None),
    ("Trades", 'CALCULATE(COUNTROWS(OrderEvents), OrderEvents[order_event_type] IN {"FILL", "PARF"})', None),
    ("Traded Quantity", "SUM(OrderEvents[traded_quantity])", None),
    ("Traded Notional", "SUM(OrderEvents[TradedNotional])", CUR),
    ("Distinct Orders", "DISTINCTCOUNT(OrderEvents[order_ID])", None),
    ("Distinct Instruments", "DISTINCTCOUNT(OrderEvents[fin_instr_ID])", None),
    ("Distinct Firms", "DISTINCTCOUNT(OrderEvents[investment_firm_lei])", None),
    ("Avg Order Size",
     'AVERAGEX(FILTER(OrderEvents, OrderEvents[order_event_type] = "NEWO"), OrderEvents[initial_quantity])', WHOLE),
    # 2B
    ("Order to Trade Ratio", "DIVIDE([New Orders] + [Modifications] + [Cancellations], [Trades])", NUM2),
    ("Cancel Rate", "DIVIDE([Cancellations], [New Orders])", PCT),
    ("Fill Rate", "DIVIDE([Trades], [New Orders])", PCT),
    # 2C
    ("Anomaly Events", "SUM(OrderEvents[AnomalyFlag])", None),
    ("Off-Market Events", "SUM(OrderEvents[OffMarket])", None),
    ("Rapid Cancel Events", "SUM(OrderEvents[RapidCancel])", None),
    ("Anomaly Rate", "DIVIDE([Anomaly Events], [Total Events])", PCT),
    ("Avg Abs Price Dev bps", "AVERAGE(OrderEvents[AbsPriceDevBps])", NUM1),
    ("Max Abs Price Dev bps", "MAX(OrderEvents[AbsPriceDevBps])", NUM1),
    ("Min Cancel Latency ms", "MIN(OrderEvents[CancelLatencyMs])", NUM1),
    ("Surveillance Status",
     'SWITCH(TRUE(), [Anomaly Rate] > 0.15, "ELEVATED", [Anomaly Rate] > 0.07, "WATCH", "NORMAL")', None),
    # 2D
    ("Initial Quantity",
     'CALCULATE(SUM(OrderEvents[initial_quantity]), OrderEvents[order_event_type] = "NEWO")', None),
    ("Filled Orders", "CALCULATE(DISTINCTCOUNT(OrderEvents[order_ID]), OrderEvents[IsTrade] = 1)", None),
    ("Order Fill Rate", "DIVIDE([Filled Orders], [Distinct Orders])", PCT),
    ("Quantity Fill Rate", "DIVIDE([Traded Quantity], [Initial Quantity])", PCT),
    ("Avg Modifies per Order", "DIVIDE([Modifications], [Distinct Orders])", NUM1),
    ("Avg Time to Fill s",
     'AVERAGEX(FILTER(OrderEvents, OrderEvents[order_event_type] = "NEWO" && NOT ISBLANK(OrderEvents[TimeToFillSec])), '
     'OrderEvents[TimeToFillSec])', NUM1),
    ("Passive Fills", "SUM(OrderEvents[IsPassiveFill])", None),
    ("Passive Fill Share", "DIVIDE([Passive Fills], [Trades])", PCT),
    # 2E
    ("Distinct Clients",
     'CALCULATE(DISTINCTCOUNT(OrderEvents[client_ID]), OrderEvents[client_ID] <> "NONE")', None),
    ("DEA Orders", "CALCULATE(DISTINCTCOUNT(OrderEvents[order_ID]), OrderEvents[DEA] = TRUE())", None),
    ("DEA Share", "DIVIDE([DEA Orders], [Distinct Orders])", PCT),
    ("Algo Orders", "CALCULATE(DISTINCTCOUNT(OrderEvents[order_ID]), OrderEvents[IsAlgo] = 1)", None),
    ("Algo Share", "DIVIDE([Algo Orders], [Distinct Orders])", PCT),
    ("LP Orders", "CALCULATE(DISTINCTCOUNT(OrderEvents[order_ID]), OrderEvents[liq_prov_activity] = TRUE())", None),
    ("Liquidity Provision Share", "DIVIDE([LP Orders], [Distinct Orders])", PCT),
    # 2F
    ("Buy Events", 'CALCULATE(COUNTROWS(OrderEvents), OrderEvents[buy_sell] = "BUYI")', None),
    ("Sell Events", 'CALCULATE(COUNTROWS(OrderEvents), OrderEvents[buy_sell] = "SELL")', None),
    ("Buy/Sell Imbalance", "DIVIDE([Buy Events] - [Sell Events], [Buy Events] + [Sell Events])", PCT),
    ("Cumulative Events",
     "VAR h = MAX(OrderEvents[EventHour]) RETURN CALCULATE([Total Events], "
     "FILTER(ALLSELECTED(OrderEvents[EventHour]), OrderEvents[EventHour] <= h))", None),
    ("Top 5 Client Share",
     'VAR TotalN = CALCULATE([Traded Notional], ALLSELECTED(OrderEvents[client_ID]), OrderEvents[client_ID] <> "NONE") '
     'VAR Top5 = TOPN(5, FILTER(VALUES(OrderEvents[client_ID]), OrderEvents[client_ID] <> "NONE"), [Traded Notional], DESC) '
     "RETURN DIVIDE(SUMX(Top5, [Traded Notional]), TotalN)", PCT),
    ("Client HHI",
     'VAR TotalN = CALCULATE([Traded Notional], ALLSELECTED(OrderEvents[client_ID]), OrderEvents[client_ID] <> "NONE") '
     'RETURN SUMX(FILTER(VALUES(OrderEvents[client_ID]), OrderEvents[client_ID] <> "NONE"), '
     "VAR s = DIVIDE([Traded Notional], TotalN) RETURN s * s) * 10000", WHOLE),
]

measure_objs = []
for name, expr, fmt in measures:
    m = {"name": name, "expression": expr}
    if fmt:
        m["formatString"] = fmt
    measure_objs.append(m)

# ---- Assemble model ----
order_events_table = {
    "name": "OrderEvents",
    "columns": all_oe_columns,
    "partitions": [{
        "name": "OrderEvents",
        "mode": "import",
        "source": {"type": "m", "expression": m_expr}
    }]
}

measures_table = {
    "name": "_Measures",
    "columns": [{"type": "calculatedTableColumn", "name": "Value", "isHidden": True,
                 "sourceColumn": "[Value]", "dataType": "int64"}],
    "partitions": [{
        "name": "_Measures",
        "mode": "import",
        "source": {"type": "calculated", "expression": "{1}"}
    }],
    "measures": measure_objs
}

# Two table-level createOrReplace scripts targeting the live DB (DB id substituted by the PS applier).
tmsl_oe = {"createOrReplace": {"object": {"database": "%DBNAME%", "table": "OrderEvents"}, "table": order_events_table}}
tmsl_meas = {"createOrReplace": {"object": {"database": "%DBNAME%", "table": "_Measures"}, "table": measures_table}}

with open(r"C:\tmp\table_orderevents.tmsl.json", "w", encoding="utf-8") as f:
    json.dump(tmsl_oe, f, indent=2, ensure_ascii=False)
with open(r"C:\tmp\table_measures.tmsl.json", "w", encoding="utf-8") as f:
    json.dump(tmsl_meas, f, indent=2, ensure_ascii=False)

print("Wrote table_orderevents.tmsl.json and table_measures.tmsl.json")
print("OrderEvents columns:", len(all_oe_columns), "(", len(source_columns), "source +", len(calc_col_objs), "calculated )")
print("Measures:", len(measure_objs))
