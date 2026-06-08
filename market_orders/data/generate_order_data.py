"""
Generate a synthetic order-event dataset for a single trading date.

Fully synthetic, representative sample data created for the dashboard demo. It
reproduces the *shape* of an order record-keeping extract — one row per order
lifecycle event (new / modify / cancel / partial-fill / fill) — using the same
52-column header as the target schema. All direct identifiers (firm LEI,
client ID, instrument ISIN, order ID, venue transaction ID) are fictitious, and
the optional/sparse fields are left mostly empty to mirror the real extract.

Three surveillance patterns are deliberately seeded so the anomaly visuals have
something to surface:
  - high order-to-trade ratio firms (many new+cancel events, few executions)
  - rapid cancellations (orders cancelled within ~1s of entry)
  - off-market limit prices (well away from the instrument's prevailing level)

Output (written next to this script):
- order_events.csv   (~4,500 rows — one row per order event, 52 columns)

Run once:  python data/generate_order_data.py
"""

import csv
import random
import datetime
import os

random.seed(11)

TRADE_DATE = datetime.date(2025, 7, 11)
SESSION_OPEN = datetime.time(7, 0, 0)
SESSION_CLOSE = datetime.time(17, 25, 0)
N_ORDERS = 650

# ── Exact target header (52 columns) ───────────────────────────────────────
COLUMNS = [
    "investment_firm_lei", "DEA", "client_ID", "invest_dec", "within_firm",
    "non_exec", "trading_capacity", "liq_prov_activity", "date_time",
    "validity_period", "order_restriction", "validity_period_ts", "priority_time",
    "priority_size", "sequence_no", "MIC", "order_book_code", "fin_instr_ID",
    "receipt_date", "order_ID", "order_event_type", "order_type",
    "order_type_class", "limit_price", "additional_limit_price", "stop_price",
    "pegged_limit_price", "transaction_price", "currency", "leg2_currency",
    "price_notation", "buy_sell", "order_status", "quantity_notation",
    "quantity_currency", "initial_quantity", "remaining_quantity",
    "displayed_quantity", "traded_quantity", "MAQ", "MES", "MES_first",
    "passive_only", "passive_aggressive", "self_exec_prevention", "sl_order_ID",
    "routing_strategy", "trading_venue_trans_ID", "trading_phases",
    "auction_price", "auction_volume", "reserved fields",
]

# ── Synthetic reference data (all identifiers fictitious) ──────────────────
# (lei, behaviour)  behaviour drives the seeded surveillance patterns
FIRMS = [
    ("SYNTHLEI0000000A0001", "normal"),
    ("SYNTHLEI0000000B0002", "normal"),
    ("SYNTHLEI0000000C0003", "normal"),
    ("SYNTHLEI0000000D0004", "normal"),
    ("SYNTHLEI0000000E0005", "high_otr"),     # places many orders, cancels most
    ("SYNTHLEI0000000F0006", "rapid_cancel"), # cancels within ~1s of entry
    ("SYNTHLEI0000000G0007", "off_market"),   # posts off-market limit prices
    ("SYNTHLEI0000000H0008", "normal"),
]

# (order_book_code, fin_instr_ID, MIC, ref_price)  — all fictitious
INSTRUMENTS = [
    ("ABLE", "ZZ0000000101", "XMKT", 6.50),
    ("BRVO", "ZZ0000000102", "XMKT", 2.085),
    ("CHRL", "ZZ0000000103", "XMKT", 16.25),
    ("DLTA", "ZZ0000000104", "XMKT", 3.14),
    ("ECHO", "ZZ0000000105", "XMKT", 7.92),
    ("FXTR", "ZZ0000000106", "XMKT", 3.195),
    ("GOLF", "ZZ0000000107", "XMKT", 4.165),
    ("HOTL", "ZZ0000000108", "XMKT", 3.18),
    ("INDX", "ZZ0000000109", "XMKT", 0.464),
    ("JULT", "ZZ0000000110", "XMKT", 11.40),
    ("FTSE25T4900", "ZV0000000201", "XDRV", 108.0),
    ("OPT25G15.00", "ZV0000000202", "XDRV", 0.456),
]

CLIENTS = ["CL" + str(1000 + i) for i in range(40)]
CAPACITY = ["AOTC", "DEAL", "MTCH"]
VALIDITY = ["DAVY", "GTCV", "GTDV", "IOCV", "FOKV"]
RESTRICTION = ["VFAR", "VFCR", ""]

_seq = 0
_otid = 0


def next_seq():
    global _seq
    _seq += 1
    return _seq


def next_order_id():
    global _otid
    _otid += 1
    return str(100000 + _otid)


def iso(ts):
    return ts.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def session_dt():
    open_dt = datetime.datetime.combine(TRADE_DATE, SESSION_OPEN)
    total = int((datetime.datetime.combine(TRADE_DATE, SESSION_CLOSE) - open_dt).total_seconds())
    # U-shaped intraday profile
    r = random.random()
    if r < 0.30:
        frac = abs(random.gauss(0.06, 0.10))
    elif r > 0.74:
        frac = 1.0 - abs(random.gauss(0.06, 0.10))
    else:
        frac = random.betavariate(2.0, 2.0)
    frac = min(max(frac, 0.0), 1.0)
    micro = random.randint(0, 999999)
    return open_dt + datetime.timedelta(seconds=int(frac * total), microseconds=micro)


def blank_row():
    return {c: "" for c in COLUMNS}


def base_qty(mic):
    if mic == "XDRV":
        return random.choice([1, 2, 5, 10, 20, 50])
    return random.choice([5, 20, 40, 60, 100, 150, 200, 500, 1000, 1500, 3000])


def make_order(firm_lei, behaviour):
    """Return a list of event row-dicts for one order's lifecycle."""
    rows = []
    obc, isin, mic, ref = random.choice(INSTRUMENTS)
    side = random.choice(["BUYI", "SELL"])
    capacity = random.choices(CAPACITY, weights=[0.55, 0.25, 0.20])[0]
    dea = "TRUE" if random.random() < 0.12 else "FALSE"
    liq = "TRUE" if capacity == "DEAL" and random.random() < 0.5 else "FALSE"
    validity = random.choices(VALIDITY, weights=[0.45, 0.2, 0.2, 0.1, 0.05])[0]
    restriction = random.choices(RESTRICTION, weights=[0.5, 0.4, 0.1])[0]
    is_stop = random.random() < 0.06
    order_type = "S" if is_stop else ("M" if random.random() < 0.05 else "L")
    otype_class = "STOP" if is_stop else "LMTO"
    client = random.choice(CLIENTS) if random.random() < 0.75 else "NONE"
    invest_dec = "NONE" if client != "NONE" else random.choice(["ALGO1", "ALGOPT", "NONE"])

    qty = base_qty(mic)

    # Limit price — normal noise, or seeded off-market
    if behaviour == "off_market" and random.random() < 0.6:
        dev_bps = random.choice([-1, 1]) * random.uniform(180, 550)
        anomaly_seed = "off_market"
    else:
        dev_bps = random.gauss(0, 12)
        anomaly_seed = "none"
    limit_price = round(ref * (1 + dev_bps / 10000.0), 4)
    stop_price = round(ref * (1 + random.choice([-1, 1]) * random.uniform(0.01, 0.03)), 4) if is_stop else 0

    t_new = session_dt()
    order_id = next_order_id()
    tvtic = "T" + order_id + str(random.randint(10, 99))

    def fill_common(row):
        row["investment_firm_lei"] = firm_lei
        row["DEA"] = dea
        row["client_ID"] = client
        row["invest_dec"] = invest_dec
        row["non_exec"] = ""
        row["trading_capacity"] = capacity
        row["liq_prov_activity"] = liq
        row["validity_period"] = validity
        row["order_restriction"] = restriction
        row["validity_period_ts"] = iso(datetime.datetime.combine(TRADE_DATE, datetime.time(23, 59, 59, 999999))) \
            if validity in ("DAVY", "GTDV") else "9999-12-31T23:59:59.999999Z"
        row["sequence_no"] = next_seq()
        row["MIC"] = mic
        row["order_book_code"] = obc
        row["fin_instr_ID"] = isin
        row["order_ID"] = order_id
        row["order_type"] = order_type
        row["currency"] = "EUR"
        row["price_notation"] = "MONE"
        row["buy_sell"] = side
        row["trading_venue_trans_ID"] = tvtic

    # ── NEWO ──
    r = blank_row()
    fill_common(r)
    r["date_time"] = iso(t_new)
    r["receipt_date"] = iso(t_new)
    r["priority_time"] = iso(t_new)
    r["order_event_type"] = "NEWO"
    r["order_type_class"] = otype_class
    r["limit_price"] = limit_price if order_type != "M" else 0
    r["stop_price"] = stop_price if is_stop else 0
    r["additional_limit_price"] = 0
    r["pegged_limit_price"] = 0
    r["transaction_price"] = 0
    r["order_status"] = "ACTI"
    r["initial_quantity"] = qty
    r["remaining_quantity"] = qty
    r["displayed_quantity"] = qty
    rows.append(r)

    remaining = qty
    t_cur = t_new

    # ── Decide lifecycle path ──
    if behaviour == "rapid_cancel" and random.random() < 0.7:
        # Cancel within ~1s, no fill
        t_cur = t_new + datetime.timedelta(milliseconds=random.randint(40, 950))
        c = blank_row(); fill_common(c)
        c["date_time"] = iso(t_cur); c["receipt_date"] = iso(t_cur); c["priority_time"] = iso(t_new)
        c["order_event_type"] = "CAME"; c["order_type_class"] = otype_class
        c["initial_quantity"] = qty; c["remaining_quantity"] = 0; c["displayed_quantity"] = 0
        rows.append(c)
        return rows, anomaly_seed if anomaly_seed != "none" else "rapid_cancel"

    if behaviour == "high_otr" and random.random() < 0.75:
        # A couple of modifies then a cancel, rarely a fill
        for _ in range(random.randint(1, 3)):
            t_cur = t_cur + datetime.timedelta(milliseconds=random.randint(200, 4000))
            m = blank_row(); fill_common(m)
            m["date_time"] = iso(t_cur); m["receipt_date"] = iso(t_cur); m["priority_time"] = iso(t_cur)
            m["order_event_type"] = "REME"; m["order_type_class"] = otype_class
            m["limit_price"] = round(limit_price * (1 + random.gauss(0, 5) / 10000.0), 4)
            m["order_status"] = "ACTI"; m["initial_quantity"] = qty
            m["remaining_quantity"] = remaining; m["displayed_quantity"] = remaining
            rows.append(m)
        t_cur = t_cur + datetime.timedelta(milliseconds=random.randint(200, 5000))
        c = blank_row(); fill_common(c)
        c["date_time"] = iso(t_cur); c["receipt_date"] = iso(t_cur); c["priority_time"] = iso(t_cur)
        c["order_event_type"] = "CAME"; c["order_type_class"] = otype_class
        c["initial_quantity"] = qty; c["remaining_quantity"] = 0; c["displayed_quantity"] = 0
        rows.append(c)
        return rows, anomaly_seed if anomaly_seed != "none" else "high_otr"

    # ── Normal path: maybe modify, then fill / partial+cancel / cancel / expire ──
    if random.random() < 0.25:
        t_cur = t_cur + datetime.timedelta(seconds=random.randint(1, 600))
        m = blank_row(); fill_common(m)
        m["date_time"] = iso(t_cur); m["receipt_date"] = iso(t_cur); m["priority_time"] = iso(t_cur)
        m["order_event_type"] = "REME"; m["order_type_class"] = otype_class
        limit_price = round(limit_price * (1 + random.gauss(0, 6) / 10000.0), 4)
        m["limit_price"] = limit_price
        m["order_status"] = "ACTI"; m["initial_quantity"] = qty
        m["remaining_quantity"] = remaining; m["displayed_quantity"] = remaining
        rows.append(m)

    outcome = random.choices(["fill", "partial_cancel", "cancel", "expire"],
                             weights=[0.5, 0.18, 0.22, 0.10])[0]

    def add_trade(part_qty, t_exec, full):
        nonlocal remaining
        remaining = max(remaining - part_qty, 0)
        tr = blank_row(); fill_common(tr)
        tr["date_time"] = iso(t_exec); tr["receipt_date"] = iso(t_exec); tr["priority_time"] = iso(t_new)
        tr["order_event_type"] = "FILL" if full else "PARF"
        tr["order_type_class"] = ""
        tr["transaction_price"] = round(limit_price if order_type != "M" else ref * (1 + random.gauss(0, 8) / 10000.0), 4)
        tr["traded_quantity"] = part_qty
        tr["remaining_quantity"] = remaining
        tr["passive_aggressive"] = random.choice(["PASV", "AGRE"])
        rows.append(tr)

    if outcome == "fill":
        n_parts = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        parts = []
        rem = qty
        for i in range(n_parts):
            if i == n_parts - 1:
                parts.append(rem)
            else:
                p = max(1, int(rem * random.uniform(0.2, 0.6)))
                parts.append(p); rem -= p
        for i, p in enumerate(parts):
            t_cur = t_cur + datetime.timedelta(seconds=random.randint(1, 400))
            add_trade(p, t_cur, full=(i == len(parts) - 1))
    elif outcome == "partial_cancel":
        t_cur = t_cur + datetime.timedelta(seconds=random.randint(1, 300))
        add_trade(max(1, int(qty * random.uniform(0.1, 0.5))), t_cur, full=False)
        t_cur = t_cur + datetime.timedelta(seconds=random.randint(1, 600))
        c = blank_row(); fill_common(c)
        c["date_time"] = iso(t_cur); c["receipt_date"] = iso(t_cur); c["priority_time"] = iso(t_cur)
        c["order_event_type"] = "CAME"; c["initial_quantity"] = qty
        c["remaining_quantity"] = 0; c["displayed_quantity"] = 0
        rows.append(c)
    elif outcome == "cancel":
        t_cur = t_cur + datetime.timedelta(seconds=random.randint(2, 1800))
        c = blank_row(); fill_common(c)
        c["date_time"] = iso(t_cur); c["receipt_date"] = iso(t_cur); c["priority_time"] = iso(t_cur)
        c["order_event_type"] = "CAME"; c["initial_quantity"] = qty
        c["remaining_quantity"] = 0; c["displayed_quantity"] = 0
        rows.append(c)
    else:  # expire
        t_exp = datetime.datetime.combine(TRADE_DATE, SESSION_CLOSE)
        e = blank_row(); fill_common(e)
        e["date_time"] = iso(t_exp); e["receipt_date"] = iso(t_exp); e["priority_time"] = iso(t_new)
        e["order_event_type"] = "EXPI"; e["initial_quantity"] = qty
        e["remaining_quantity"] = remaining; e["displayed_quantity"] = 0
        rows.append(e)

    return rows, anomaly_seed


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    all_rows = []
    seed_counts = {}
    for _ in range(N_ORDERS):
        firm_lei, behaviour = random.choices(
            FIRMS, weights=[3, 3, 3, 3, 2, 2, 2, 3])[0]
        rows, seed = make_order(firm_lei, behaviour)
        all_rows.extend(rows)
        seed_counts[seed] = seed_counts.get(seed, 0) + 1

    # Sort by event time, then re-stamp sequence_no in chronological order
    all_rows.sort(key=lambda r: r["date_time"])
    for i, r in enumerate(all_rows, start=1):
        r["sequence_no"] = i

    out_path = os.path.join(out_dir, "order_events.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_rows)

    n_trades = sum(1 for r in all_rows if r["order_event_type"] in ("FILL", "PARF"))
    n_new = sum(1 for r in all_rows if r["order_event_type"] == "NEWO")
    n_cancel = sum(1 for r in all_rows if r["order_event_type"] == "CAME")
    print(f"Generated {len(all_rows)} order events from {N_ORDERS} orders for {TRADE_DATE}")
    print(f"  NEWO={n_new}  CAME={n_cancel}  trades(FILL/PARF)={n_trades}  "
          f"order-to-trade ratio={ (n_new+n_cancel)/max(n_trades,1):.2f}")
    print(f"  seeded order outcomes: {seed_counts}")
    print(f"  Output: {out_path}")


if __name__ == "__main__":
    main()
