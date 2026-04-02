# PortPulse — Piraeus Port Congestion & Waiting Time Analyzer

## Power BI Data Model Specification

---

## Phase 0 — Data Loading

### Table: AIS_Positions (Fact)
Source: `piraeus_ais.csv` (~5,000 rows)

| Column | Type | Description |
|--------|------|-------------|
| mmsi | Text | Vessel identifier (treat as text, not number) |
| timestamp | DateTime | AIS position timestamp |
| lat | Decimal | Latitude |
| lon | Decimal | Longitude |
| speed_knots | Decimal | Speed in knots |
| vessel_type | Text | Container, Tanker, Bulk Carrier, Passenger, Ro-Ro |
| vessel_name | Text | Vessel name |
| flag | Text | Flag state |
| hour | Whole Number | Hour of day (0–23) |
| day_of_week | Text | Day name (Monday, Tuesday, …) |
| date | Date | Date only |

**Power Query computed columns (add in Power Query Editor):**

| Column | Type | Formula |
|--------|------|---------|
| Status | Text | `= if speed_knots < 0.5 and lat >= 37.935 and lat <= 37.960 and lon >= 23.595 and lon <= 23.650 then "Berthed" else if speed_knots < 1.0 and lat >= 37.845 and lat <= 37.935 and lon >= 23.505 and lon <= 23.575 then "Waiting" else if speed_knots >= 5.0 then "In Transit" else "Maneuvering"` |
| Zone | Text | `= if lat >= 37.935 then "Port" else if lat >= 37.845 then "Anchorage" else "Approach"` |
| anomaly_score | Decimal | Added by R script transform (Isolation Forest) |
| is_anomaly | Boolean | Added by R script transform (top 10% anomaly scores) |

### Table: PiraeusZones (Dim)
Source: `piraeus_zones.csv`

| Column | Type | Description |
|--------|------|-------------|
| zone | Text | Zone name (Container Terminal, Passenger Terminal, etc.) |
| lat | Decimal | Zone center latitude |
| lon | Decimal | Zone center longitude |
| type | Text | "berth" or "anchorage" |

### Table: VesselClusters (Dim)
Source: R script transform output (Power Query)

| Column | Type | Description |
|--------|------|-------------|
| mmsi | Text | Vessel identifier |
| vessel_type | Text | Vessel type |
| flag | Text | Flag state |
| avg_speed | Decimal | Average speed across all positions |
| max_speed | Decimal | Maximum speed recorded |
| pct_slow | Decimal | % of time speed < 1 knot |
| avg_lat | Decimal | Average latitude |
| avg_lon | Decimal | Average longitude |
| n_positions | Whole Number | Number of AIS positions |
| cluster | Whole Number | K-means cluster ID |
| cluster_label | Text | Cluster label (Long-term Waiting, Berthed/Short Wait, In Transit, Mixed Behaviour) |

---

## Phase 1A — Relationships

| From | To | Cardinality | Cross-filter |
|------|----|-------------|-------------|
| AIS_Positions[mmsi] | VesselClusters[mmsi] | Many-to-One | Both |

---

## Phase 1B — Calendar Table

Not required for this dataset (date column exists on AIS_Positions directly, 3-day window).

---

## Phase 1C — Core KPI Measures

Create these in a `_Measures` table:

```dax
Waiting Vessels =
CALCULATE(
    DISTINCTCOUNT(AIS_Positions[mmsi]),
    AIS_Positions[Status] = "Waiting"
)

Avg Wait Hours =
VAR WaitingPositions =
    CALCULATE(COUNT(AIS_Positions[mmsi]), AIS_Positions[Status] = "Waiting")
VAR WaitingVessels = [Waiting Vessels]
VAR AvgIntervalHours = 0.33
RETURN
IF(WaitingVessels > 0,
   DIVIDE(WaitingPositions * AvgIntervalHours, WaitingVessels),
   0
)

Congestion Index =
[Waiting Vessels] * [Avg Wait Hours] / 10

Severity =
SWITCH(TRUE(),
    [Congestion Index] > 25, "HIGH",
    [Congestion Index] > 12, "MEDIUM",
    "LOW"
)

Total Vessels = DISTINCTCOUNT(AIS_Positions[mmsi])

Berthed Vessels =
CALCULATE(
    DISTINCTCOUNT(AIS_Positions[mmsi]),
    AIS_Positions[Status] = "Berthed"
)

Transit Vessels =
CALCULATE(
    DISTINCTCOUNT(AIS_Positions[mmsi]),
    AIS_Positions[Status] = "In Transit"
)

Avg Speed = AVERAGE(AIS_Positions[speed_knots])

Total Positions = COUNT(AIS_Positions[mmsi])
```

---

## Phase 1D — Cost Estimation Measures

```dax
Daily Cost Rate =
SWITCH(
    SELECTEDVALUE(AIS_Positions[vessel_type]),
    "Container", 25000,
    "Tanker", 35000,
    "Bulk Carrier", 15000,
    "Passenger", 5000,
    "Ro-Ro", 12000,
    10000
)

Total Waiting Cost USD =
SUMX(
    FILTER(
        SUMMARIZE(
            AIS_Positions,
            AIS_Positions[mmsi],
            AIS_Positions[vessel_type],
            "WaitHours", [Avg Wait Hours]
        ),
        [WaitHours] > 0
    ),
    [WaitHours] / 24 *
    SWITCH([vessel_type],
        "Container", 25000,
        "Tanker", 35000,
        "Bulk Carrier", 15000,
        "Passenger", 5000,
        10000
    )
)

Waiting Cost Display =
FORMAT([Total Waiting Cost USD], "$#,##0")
```

---

## Phase 1E — Trend Measures

```dax
Daily Waiting Count =
CALCULATE(
    DISTINCTCOUNT(AIS_Positions[mmsi]),
    AIS_Positions[Status] = "Waiting"
)

Waiting 7D Avg =
AVERAGEX(
    DATESINPERIOD(AIS_Positions[date], LASTDATE(AIS_Positions[date]), -7, DAY),
    [Daily Waiting Count]
)

Anomaly Count =
CALCULATE(
    DISTINCTCOUNT(AIS_Positions[mmsi]),
    AIS_Positions[is_anomaly] = TRUE()
)
```

---

## Phase 1F — Cost Insight Measure

```dax
Cost Insight =
VAR MostExpensiveType =
    TOPN(1, SUMMARIZE(AIS_Positions, AIS_Positions[vessel_type],
         "TypeCost", [Total Waiting Cost USD]), [TypeCost], DESC)
RETURN
"Highest cost impact: " & MAXX(MostExpensiveType, [vessel_type]) &
" vessels — " & FORMAT(MAXX(MostExpensiveType, [TypeCost]), "$#,##0")
```

---

## Visual Layout Reference

### Page 1: Port Overview
- Title bar: "PortPulse — Piraeus Port Congestion Monitor"
- 4 KPI cards: Waiting Vessels, Avg Wait Hours, Congestion Index, Total Waiting Cost USD
- Map: vessel positions (lat/lon), color by Status, size by speed
- Slicers: vessel_type, flag, Status
- Bar chart: Avg Wait Hours by vessel_type
- Nav buttons: Trends, Vessels, Costs

### Page 2: Trends & Patterns
- 3 KPI cards: Daily Waiting Count, Waiting 7D Avg, Total Vessels
- Line chart: date × Daily Waiting Count + Waiting 7D Avg
- Bar chart: Avg Wait Hours by day_of_week
- Clustered column: Waiting Vessels by hour
- Nav buttons: Back, Vessels, Costs

### Page 3: Vessel Detail
- 2 KPI cards: Total Vessels, Anomaly Count
- Slicer: vessel_type
- Table: mmsi, vessel_name, flag, vessel_type, Status, cluster_label, avg_speed, Avg Wait Hours, anomaly_score, is_anomaly
- Scatter: detail=vessel_name, x=Avg Speed, y=Avg Wait Hours (from VesselClusters perspective)
- Nav buttons: Back, Trends, Costs

### Page 4: Cost Impact
- 3 KPI cards: Total Waiting Cost USD, Waiting Vessels, Avg Wait Hours
- Donut: Total Waiting Cost USD by vessel_type
- Gradient bar: Total Waiting Cost USD by vessel_name (top waiters)
- Table: mmsi, vessel_name, vessel_type, flag, Avg Wait Hours, Total Waiting Cost USD
- Nav buttons: Back, Trends, Vessels

---

## Notes

- R script visuals (anomaly scatter, cluster plot, ARIMA forecast) must be added manually in Power BI Desktop — PBIR JSON does not support R script visual types
- Navigation buttons render but must have page navigation configured manually in Power BI Desktop (Format > Action > Page navigation)
- Data is ~5,000 rows / 31 vessels / 3 days of AIS positions for Piraeus port
