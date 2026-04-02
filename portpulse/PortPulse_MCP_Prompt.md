# PortPulse — MCP Agent Prompt for Power BI Data Model

Paste this into Claude Desktop (with Power BI Modeling MCP server active) to build the PortPulse data model step by step.

**Before starting:**
1. Open Power BI Desktop
2. Get Data > CSV > import `piraeus_ais.csv` from `portpulse/data/`
3. Get Data > CSV > import `piraeus_zones.csv` from `portpulse/data/`
4. In Power Query Editor:
   - Set column types for AIS_Positions (mmsi=Text, timestamp=DateTime, lat/lon=Decimal, speed_knots=Decimal, vessel_type/vessel_name/flag/day_of_week=Text, hour=Whole Number, date=Date)
   - Add custom column "Status":
     ```
     = if [speed_knots] < 0.5 and [lat] >= 37.935 and [lat] <= 37.960 and [lon] >= 23.595 and [lon] <= 23.650 then "Berthed" else if [speed_knots] < 1.0 and [lat] >= 37.845 and [lat] <= 37.935 and [lon] >= 23.505 and [lon] <= 23.575 then "Waiting" else if [speed_knots] >= 5.0 then "In Transit" else "Maneuvering"
     ```
   - Add custom column "Zone":
     ```
     = if [lat] >= 37.935 then "Port" else if [lat] >= 37.845 then "Anchorage" else "Approach"
     ```
   - (Optional) Run R script transforms for anomaly_score/is_anomaly and VesselClusters — see PortPulse_Dashboard_Prompts.md Steps 2-3
5. Close & Apply
6. Save as .pbip (e.g. `portpulse_dash.pbip`)

**Then paste the prompt below into Claude Desktop:**

---

## Prompt to paste:

I have a Power BI model open with two tables already imported: `AIS_Positions` and `PiraeusZones`. Please execute the following phases using the Power BI Modeling MCP tools.

### Phase 1: Create _Measures table

Create an empty calculated table called `_Measures` with this DAX expression:
```
_Measures = {1}
```

### Phase 2: Core KPI Measures

Create these measures in the `_Measures` table:

**Measure 1: Waiting Vessels**
```dax
Waiting Vessels =
CALCULATE(
    DISTINCTCOUNT(AIS_Positions[mmsi]),
    AIS_Positions[Status] = "Waiting"
)
```

**Measure 2: Avg Wait Hours**
```dax
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
```

**Measure 3: Congestion Index**
```dax
Congestion Index =
[Waiting Vessels] * [Avg Wait Hours] / 10
```

**Measure 4: Severity**
```dax
Severity =
SWITCH(TRUE(),
    [Congestion Index] > 25, "HIGH",
    [Congestion Index] > 12, "MEDIUM",
    "LOW"
)
```

**Measure 5: Total Vessels**
```dax
Total Vessels = DISTINCTCOUNT(AIS_Positions[mmsi])
```

**Measure 6: Berthed Vessels**
```dax
Berthed Vessels =
CALCULATE(
    DISTINCTCOUNT(AIS_Positions[mmsi]),
    AIS_Positions[Status] = "Berthed"
)
```

**Measure 7: Transit Vessels**
```dax
Transit Vessels =
CALCULATE(
    DISTINCTCOUNT(AIS_Positions[mmsi]),
    AIS_Positions[Status] = "In Transit"
)
```

**Measure 8: Avg Speed**
```dax
Avg Speed = AVERAGE(AIS_Positions[speed_knots])
```

**Measure 9: Total Positions**
```dax
Total Positions = COUNT(AIS_Positions[mmsi])
```

### Phase 3: Cost Estimation Measures

**Measure 10: Daily Cost Rate**
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
```

**Measure 11: Total Waiting Cost USD**
```dax
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
```

**Measure 12: Waiting Cost Display**
```dax
Waiting Cost Display =
FORMAT([Total Waiting Cost USD], "$#,##0")
```

### Phase 4: Trend Measures

**Measure 13: Daily Waiting Count**
```dax
Daily Waiting Count =
CALCULATE(
    DISTINCTCOUNT(AIS_Positions[mmsi]),
    AIS_Positions[Status] = "Waiting"
)
```

**Measure 14: Waiting 7D Avg**
```dax
Waiting 7D Avg =
AVERAGEX(
    DATESINPERIOD(AIS_Positions[date], LASTDATE(AIS_Positions[date]), -7, DAY),
    [Daily Waiting Count]
)
```

**Measure 15: Anomaly Count**
```dax
Anomaly Count =
CALCULATE(
    DISTINCTCOUNT(AIS_Positions[mmsi]),
    AIS_Positions[is_anomaly] = TRUE()
)
```

### Phase 5: Verify

After creating all measures, please list all measures in the `_Measures` table to confirm all 15 were created successfully.

---

## After MCP completes:

1. Save the .pbip and **close Power BI Desktop**
2. Run: `python portpulse/scripts/generate_pages.py`
3. Reopen the .pbip — 4 pages with all visuals will appear
4. Apply theme: View > Themes > Browse > `themes/code-first-dashboard.json`
5. Configure button navigation manually (Format > Action > Page navigation)
6. (Optional) Add R script visuals for anomaly scatter, cluster plot, ARIMA forecast
