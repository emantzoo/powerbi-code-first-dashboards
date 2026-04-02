# PortPulse — Piraeus Port Congestion & Waiting Time Analyzer — Power BI Build Prompts

Use these prompts in order. Each one is a copy-paste block for Claude Desktop (Cowork or Code tab).

The data CSVs are in: `C:\Users\emant\Documents\powerbi-code-first-dashboards\portpulse\data`

---

## PHASE 0 — Load Data

> Open a blank Power BI Desktop first. Then paste this into Claude Desktop:

```
Connect to my open Power BI Desktop file.

Load these CSV files from C:\Users\emant\Documents\powerbi-code-first-dashboards\portpulse\data into my Power BI model:
- piraeus_ais.csv (~4000 rows — AIS vessel positions with timestamps, coordinates, speed)
- piraeus_zones.csv (5 rows — port zone reference with coordinates)

Read the headers from each CSV and create tables with the correct column names and data types.

For piraeus_ais (rename table to AIS_Positions):
- mmsi: Text (not number — no arithmetic on vessel IDs)
- timestamp: DateTime
- lat, lon: Decimal Number
- speed_knots: Decimal Number
- vessel_type, vessel_name, flag, day_of_week: Text
- hour: Whole Number
- date: Date

For piraeus_zones (rename table to PiraeusZones):
- zone: Text
- lat, lon: Decimal Number
- type: Text

Refresh the model after loading. Confirm row counts for each table.
```

---

## PHASE 0B — Power Query Computed Columns

> Paste this after Phase 0 completes:

```
Open Power Query Editor for the AIS_Positions table.

Add a custom column called "Status" with this formula:
= if [speed_knots] < 0.5 and [lat] >= 37.935 and [lat] <= 37.960 and [lon] >= 23.595 and [lon] <= 23.650 then "Berthed" else if [speed_knots] < 1.0 and [lat] >= 37.845 and [lat] <= 37.935 and [lon] >= 23.505 and [lon] <= 23.575 then "Waiting" else if [speed_knots] >= 5.0 then "In Transit" else "Maneuvering"

Add another custom column called "Zone" with this formula:
= if [lat] >= 37.935 then "Port" else if [lat] >= 37.845 then "Anchorage" else "Approach"

Set both new columns to Text type.

Close & Apply.
```

---

## PHASE 0C — R Script Transform: Anomaly Detection (Optional)

> This step requires R installed and configured in Power BI. Skip if R is not set up.

```
Open Power Query Editor for the AIS_Positions table.

Go to Transform > Run R Script. Paste this R code:

library(dplyr)
library(solitude)

features <- dataset %>%
  select(speed_knots, lat, lon, hour) %>%
  mutate(across(everything(), as.numeric))

iso <- isolationForest$new(
  sample_size = min(256, nrow(features)),
  num_trees = 100
)
iso$fit(features)

scores <- iso$predict(features)

threshold <- quantile(scores$anomaly_score, 0.90)
dataset$anomaly_score <- scores$anomaly_score
dataset$is_anomaly <- scores$anomaly_score >= threshold

output <- dataset

Click OK. This adds anomaly_score (Decimal) and is_anomaly (True/False) columns.
Set anomaly_score to Decimal Number type and is_anomaly to True/False type.

Close & Apply.
```

---

## PHASE 0D — R Script Transform: Vessel Clustering (Optional)

> This creates a separate VesselClusters table. Skip if R is not set up.

```
In Power Query Editor, go to the AIS_Positions table.
Right-click the table > Reference (this creates a new query based on AIS_Positions).
Rename the new query to "VesselClusters".

On the VesselClusters query, go to Transform > Run R Script. Paste this R code:

library(dplyr)

vessel_summary <- dataset %>%
  group_by(mmsi, vessel_type, flag) %>%
  summarise(
    avg_speed = mean(speed_knots, na.rm = TRUE),
    max_speed = max(speed_knots, na.rm = TRUE),
    pct_slow = mean(speed_knots < 1.0, na.rm = TRUE),
    avg_lat = mean(lat, na.rm = TRUE),
    avg_lon = mean(lon, na.rm = TRUE),
    n_positions = n(),
    .groups = "drop"
  )

set.seed(42)
cluster_features <- vessel_summary %>%
  select(avg_speed, pct_slow, avg_lat) %>%
  scale()

km <- kmeans(cluster_features, centers = 4, nstart = 25)
vessel_summary$cluster <- km$cluster

cluster_labels <- vessel_summary %>%
  group_by(cluster) %>%
  summarise(avg_spd = mean(avg_speed), avg_pct_slow = mean(pct_slow)) %>%
  mutate(cluster_label = case_when(
    avg_pct_slow > 0.8 & avg_spd < 1 ~ "Long-term Waiting",
    avg_pct_slow > 0.5 ~ "Berthed/Short Wait",
    avg_spd > 8 ~ "In Transit",
    TRUE ~ "Mixed Behaviour"
  ))

vessel_summary <- vessel_summary %>%
  left_join(cluster_labels %>% select(cluster, cluster_label), by = "cluster")

output <- vessel_summary

Click OK. Set column types:
- mmsi: Text
- vessel_type, flag, cluster_label: Text
- avg_speed, max_speed, pct_slow, avg_lat, avg_lon: Decimal Number
- n_positions, cluster: Whole Number

Close & Apply.
```

---

## PHASE 1A — Relationships

> Paste this after all data is loaded:

```
Delete all auto-detected relationships in the model first.

Then create this relationship:
1. AIS_Positions[mmsi] -> VesselClusters[mmsi] (Many:1, ACTIVE, both directions cross-filter)

If VesselClusters table was not created (R steps were skipped), skip this phase.
```

---

## PHASE 1B — DAX Measures (Batch 1: Core KPIs)

```
Create a _Measures table with this DAX expression:
_Measures = {1}

Then add these measures to _Measures:

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

## PHASE 1C — DAX Measures (Batch 2: Cost Estimation)

```
Add these measures to _Measures:

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

## PHASE 1D — DAX Measures (Batch 3: Trends & Anomalies)

```
Add these measures to _Measures:

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

## PHASE 1E — DAX Measures (Batch 4: Cost Insight)

```
Add this measure to _Measures:

Cost Insight =
VAR MostExpensiveType =
    TOPN(1, SUMMARIZE(AIS_Positions, AIS_Positions[vessel_type],
         "TypeCost", [Total Waiting Cost USD]), [TypeCost], DESC)
RETURN
"Highest cost impact: " & MAXX(MostExpensiveType, [vessel_type]) &
" vessels — " & FORMAT(MAXX(MostExpensiveType, [TypeCost]), "$#,##0")
```

---

## PHASE 2 — Save

```
Save the file as a Power BI Project (.pbip) with the name "portpulse_dash" in:
C:\Users\emant\Documents\powerbi-code-first-dashboards\portpulse\

Then close Power BI Desktop completely (the Python script needs exclusive file access).
```

---

## After Coworker completes all phases:

1. Close Power BI Desktop
2. Run: `python portpulse/scripts/generate_pages.py`
3. Reopen `portpulse_dash.pbip` — 4 pages with all visuals will appear
4. Apply theme: View > Themes > Browse > `themes/code-first-dashboard.json`
5. Configure button navigation: select each button > Format > Action > Page navigation
6. R script visuals (ARIMA forecast, anomaly scatter, cluster plot) are embedded via `make_r_visual` — they will render if R is configured

---

## Notes

- If R is not installed, skip Phases 0C and 0D. The dashboard will work without anomaly detection and clustering — the Anomaly Count measure and VesselClusters table references will show blank/error, which is fine
- Navigation buttons render but page navigation must be configured manually in Power BI Desktop (Format > Action > Page navigation)
- Data is ~4,000 rows / 31 vessels / 3 days of AIS positions for Piraeus port
