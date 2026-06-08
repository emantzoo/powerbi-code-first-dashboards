# Market Orders — Order Activity & Surveillance — Power BI Build Prompts

Use these prompts in order. Each one is a copy-paste block for Claude Desktop (Cowork or Code tab) or a manual checklist for Power BI Desktop.

> **About the data:** `data/order_events.csv` is a fully synthetic, single-day sample with one row per order lifecycle event (new / modify / cancel / partial-fill / fill). It uses the same 52-column header as the target order record-keeping schema, but every direct identifier (firm LEI, client ID, instrument ISIN, order ID, venue transaction ID) is fictitious, and the optional/sparse fields are left mostly empty to mirror a real extract. It is representative demo data only; no real or proprietary dataset is included or referenced. When you have the real file, drop it in place of this CSV — the model and visuals are wired to the column names, so nothing else changes.

The data CSV is in: `C:\Users\emant\Documents\powerbi-code-first-dashboards\market_orders\data`

---

## PHASE 0 — Load Data

> Open a blank Power BI Desktop first. Then paste this into Claude Desktop:

```
Connect to my open Power BI Desktop file.

Load this CSV from C:\Users\emant\Documents\powerbi-code-first-dashboards\market_orders\data:
- order_events.csv (~1,800 rows, 52 columns — one row per order event)

Rename the table to: OrderEvents

Read the header and set data types (the schema follows an order record-keeping layout):

Identifiers / categorical (Text):
  investment_firm_lei, client_ID, invest_dec, within_firm, non_exec,
  trading_capacity, validity_period, order_restriction, MIC, order_book_code,
  fin_instr_ID, order_ID, order_event_type, order_type, order_type_class,
  currency, leg2_currency, price_notation, buy_sell, order_status,
  quantity_notation, quantity_currency, passive_aggressive, self_exec_prevention,
  sl_order_ID, routing_strategy, trading_venue_trans_ID, trading_phases,
  "reserved fields"

Boolean (True/False):
  DEA, liq_prov_activity, MES_first, passive_only

DateTime (UTC, with microseconds + trailing Z):
  date_time, validity_period_ts, priority_time, receipt_date

Whole Number:
  priority_size, sequence_no, initial_quantity, remaining_quantity,
  displayed_quantity, traded_quantity, MAQ, MES, auction_volume

Decimal Number:
  limit_price, additional_limit_price, stop_price, pegged_limit_price,
  transaction_price, auction_price

Notes:
- Many optional fields are intentionally sparse/empty (e.g. traded_quantity is only
  populated on FILL/PARF rows; passive_aggressive, trading_phases, MAQ/MES, auction_*
  are mostly empty). Keep them — they are part of the schema.
- "reserved fields" can be left as-is or dropped; it carries no data.

Refresh and confirm the row count.
```

---

## PHASE 1 — Derived Columns (Calculated Columns on OrderEvents)

> These build the intraday axis, event-type flags, the instrument reference price,
> and the two surveillance signals (off-market price, rapid cancel). Add each as a
> **calculated column** on the OrderEvents table.

```
EventHour = HOUR(OrderEvents[date_time])

IsNew    = IF(OrderEvents[order_event_type] = "NEWO", 1, 0)
IsModify = IF(OrderEvents[order_event_type] = "REME", 1, 0)
IsCancel = IF(OrderEvents[order_event_type] = "CAME", 1, 0)
IsTrade  = IF(OrderEvents[order_event_type] IN {"FILL", "PARF"}, 1, 0)

TradedNotional =
IF(OrderEvents[IsTrade] = 1,
   OrderEvents[traded_quantity] * OrderEvents[transaction_price],
   BLANK())

-- Prevailing level for each instrument = average NEWO limit price for that ISIN
RefPrice =
CALCULATE(
    AVERAGE(OrderEvents[limit_price]),
    ALLEXCEPT(OrderEvents, OrderEvents[fin_instr_ID]),
    OrderEvents[order_event_type] = "NEWO",
    OrderEvents[limit_price] > 0
)

EffectivePrice =
IF(OrderEvents[limit_price] > 0, OrderEvents[limit_price], OrderEvents[transaction_price])

PriceDevBps =
IF(OrderEvents[RefPrice] > 0 && OrderEvents[EffectivePrice] > 0,
   DIVIDE(OrderEvents[EffectivePrice] - OrderEvents[RefPrice], OrderEvents[RefPrice]) * 10000,
   BLANK())

AbsPriceDevBps =
IF(NOT ISBLANK(OrderEvents[PriceDevBps]), ABS(OrderEvents[PriceDevBps]), BLANK())

-- Off-market: priced 150+ bps away from the instrument's prevailing level
OffMarket = IF(OrderEvents[AbsPriceDevBps] >= 150, 1, 0)

-- Entry time of each order (its NEWO timestamp)
NewoTime =
CALCULATE(
    MIN(OrderEvents[date_time]),
    ALLEXCEPT(OrderEvents, OrderEvents[order_ID]),
    OrderEvents[order_event_type] = "NEWO"
)

-- Latency from entry to cancellation, in milliseconds (CAME rows only)
CancelLatencyMs =
IF(OrderEvents[order_event_type] = "CAME" && NOT ISBLANK(OrderEvents[NewoTime]),
   (OrderEvents[date_time] - OrderEvents[NewoTime]) * 86400000.0,
   BLANK())

-- Rapid cancel: cancelled within 1 second of entry
RapidCancel =
IF(OrderEvents[order_event_type] = "CAME"
   && OrderEvents[CancelLatencyMs] >= 0
   && OrderEvents[CancelLatencyMs] <= 1000, 1, 0)

AnomalyFlag = IF(OrderEvents[OffMarket] = 1 || OrderEvents[RapidCancel] = 1, 1, 0)

AnomalyType =
SWITCH(TRUE(),
    OrderEvents[OffMarket] = 1 && OrderEvents[RapidCancel] = 1, "Off-market + Rapid cancel",
    OrderEvents[OffMarket] = 1, "Off-market price",
    OrderEvents[RapidCancel] = 1, "Rapid cancel",
    "None")
```

---

## PHASE 2A — DAX Measures (Batch 1: Activity)

```
Create a _Measures table with this DAX expression:
_Measures = {1}

Then add these measures to _Measures:

Total Events = COUNTROWS(OrderEvents)

New Orders     = CALCULATE(COUNTROWS(OrderEvents), OrderEvents[order_event_type] = "NEWO")
Modifications  = CALCULATE(COUNTROWS(OrderEvents), OrderEvents[order_event_type] = "REME")
Cancellations  = CALCULATE(COUNTROWS(OrderEvents), OrderEvents[order_event_type] = "CAME")
Trades         = CALCULATE(COUNTROWS(OrderEvents), OrderEvents[order_event_type] IN {"FILL", "PARF"})

Traded Quantity = SUM(OrderEvents[traded_quantity])
Traded Notional = SUM(OrderEvents[TradedNotional])

Distinct Orders      = DISTINCTCOUNT(OrderEvents[order_ID])
Distinct Instruments = DISTINCTCOUNT(OrderEvents[fin_instr_ID])
Distinct Firms       = DISTINCTCOUNT(OrderEvents[investment_firm_lei])

Avg Order Size =
AVERAGEX(FILTER(OrderEvents, OrderEvents[order_event_type] = "NEWO"), OrderEvents[initial_quantity])
```

Set `Traded Notional` to a currency format and `Avg Order Size` to whole number.

---

## PHASE 2B — DAX Measures (Batch 2: Surveillance Ratios)

```
Add these measures to _Measures:

Order to Trade Ratio =
DIVIDE([New Orders] + [Modifications] + [Cancellations], [Trades])

Cancel Rate = DIVIDE([Cancellations], [New Orders])
Fill Rate   = DIVIDE([Trades], [New Orders])
```

Set `Cancel Rate` and `Fill Rate` to Percentage; `Order to Trade Ratio` to 2-decimal number.

---

## PHASE 2C — DAX Measures (Batch 3: Anomaly Flags)

```
Add these measures to _Measures:

Anomaly Events     = SUM(OrderEvents[AnomalyFlag])
Off-Market Events  = SUM(OrderEvents[OffMarket])
Rapid Cancel Events = SUM(OrderEvents[RapidCancel])

Anomaly Rate = DIVIDE([Anomaly Events], [Total Events])

Avg Abs Price Dev bps = AVERAGE(OrderEvents[AbsPriceDevBps])
Max Abs Price Dev bps = MAX(OrderEvents[AbsPriceDevBps])
Min Cancel Latency ms = MIN(OrderEvents[CancelLatencyMs])

Surveillance Status =
SWITCH(TRUE(),
    [Anomaly Rate] > 0.15, "ELEVATED",
    [Anomaly Rate] > 0.07, "WATCH",
    "NORMAL")
```

Set `Anomaly Rate` to Percentage.

> The measure names `Avg Abs Price Dev bps` and `Min Cancel Latency ms` are referenced
> verbatim by `generate_pages.py`. Keep them exactly as written.

---

## PHASE 3 — Save

```
Save the file as a Power BI Project (.pbip) named "market_orders_dash" in:
C:\Users\emant\Documents\powerbi-code-first-dashboards\market_orders\

Then close Power BI Desktop completely (the Python script needs exclusive file access).
```

---

## After Coworker completes all phases:

1. Close Power BI Desktop
2. Update the `BASE` path at the top of `scripts/generate_pages.py` to your saved `.pbip` location
3. Run: `python market_orders/scripts/generate_pages.py`
4. Reopen `market_orders_dash.pbip` — 4 pages with all visuals + auto-generated backgrounds appear
5. Apply theme: View > Themes > Browse > `themes/code-first-dashboard.json`
6. Configure button navigation: select each button > Format > Action > Page navigation

No R is required — every visual binds to DAX measures / derived columns.

---

## Pages

| Page | Purpose | Key visuals |
|------|---------|-------------|
| **Order Activity Overview** | "How busy was the book, and how does activity convert to trades?" | KPI cards (Events, New Orders, Trades, Order-to-Trade Ratio), intraday event-volume line, event-type donut, instrument table |
| **Order Lifecycle & Flow** | New / modify / cancel / fill dynamics through the session | Lifecycle cards, events-by-hour stacked by event type, traded-quantity by side, order-type-class bar, capacity-by-instrument 100% bar |
| **Surveillance & Anomalies** | The two seeded patterns, surfaced | Anomaly KPI cards, **Order-to-Trade Ratio by firm** (gradient), **off-market events by instrument**, **rapid cancels by firm**, flagged-events table |
| **Firm & Instrument Insights** | Who and what drives volume and exceptions | Top instruments by traded notional, firms by event volume, per-firm OTR-vs-anomaly-rate scatter, firm scorecard |

---

## Surveillance Logic (what's flagged, and why)

- **Off-market price** — a NEWO/REME limit price (or an execution price) **≥ 150 bps** away from
  the instrument's prevailing level (`RefPrice`, the average NEWO limit price per ISIN). Surfaces
  potential mismarking / price manipulation.
- **Rapid cancel** — a cancellation (`CAME`) occurring **within 1 second** of the order's entry
  (`NewoTime`). Surfaces quote-stuffing / fleeting-order behaviour.
- **Order-to-Trade Ratio** — `(New + Modify + Cancel) / Trades`, per firm and per instrument. A
  classic surveillance metric; the gradient bar on the Surveillance page makes outlier firms pop.
- All three are computed in **pure DAX** from the schema columns, so they recompute automatically
  when you swap in your real CSV. The thresholds (150 bps, 1,000 ms) are single constants in the
  `OffMarket` / `RapidCancel` calculated columns — tune them to your venue.
- The synthetic generator seeds a handful of firms with high-OTR, rapid-cancel and off-market
  behaviour so the visuals have realistic structure to reveal.
