# PortPulse Demo Guide

## What This Is

A Power BI dashboard that monitors vessel congestion at Piraeus port using AIS data. Combines native Power BI visuals with embedded R analytics (Isolation Forest anomaly detection, K-means clustering, ARIMA forecasting).

## Quick Setup (Synthetic Data — No API Key Needed)

1. **Generate data**
   ```bash
   cd portpulse/data
   python generate_piraeus_data.py
   ```
   Creates `piraeus_ais.csv` (4031 rows, 31 vessels, 3 days) and `piraeus_zones.csv`.

2. **Open Power BI Desktop** and import the `.pbip`:
   ```
   portpulse/portpulse_dash.pbip
   ```

3. **Build the data model** — open `PortPulse_Dashboard_Prompts.md` and paste each phase into Claude Coworker (with Power BI MCP) or follow manually:
   - Phase 0: Load CSVs
   - Phase 0B: Add Status and Zone columns in Power Query
   - Phase 1A: Create relationship (PiraeusZones → AIS_Positions)
   - Phase 1B–1E: Create DAX measures (15 total)

4. **Generate dashboard pages**
   ```bash
   # Close Power BI Desktop first!
   python portpulse/scripts/generate_pages.py
   ```
   Creates 4 pages with 45 visuals.

5. **Reopen** `portpulse_dash.pbip` in Power BI Desktop.

## Live Data Setup (Real AIS — Requires Free API Key)

1. **Get an API key** — register at [aisstream.io](https://aisstream.io) (free, GitHub login)

2. **Install websockets**
   ```bash
   pip install websockets
   ```

3. **Start the collector**
   ```bash
   cd portpulse/data
   export AISSTREAM_API_KEY="your_key_here"
   python piraeus_collector.py
   ```
   Saves to `piraeus_ais_live.csv`. Let it run for 2–4 hours for a demo dataset.

4. **Switch Power BI to live data** — in Power Query Editor, change the CSV source path from `piraeus_ais.csv` to `piraeus_ais_live.csv`. The live file has extra columns (course, heading, nav_status, destination) which Power BI will ignore if not mapped.

5. **Refresh** — click Refresh in Power BI to load latest positions. The collector keeps writing while Power BI reads.

## R Packages Required

Install these in R before opening the dashboard:

```r
install.packages(c(
  "ggplot2",      # all R visuals
  "dplyr",        # data manipulation
  "forecast",     # ARIMA (Trends page)
  "solitude",     # Isolation Forest (Vessel Detail page)
  "scales"        # formatting
))
```

Verify Power BI R path: File → Options → R scripting → set R home directory.

## Dashboard Pages

### Page 1: Port Overview
- 4 KPI cards: Waiting Vessels, Avg Wait Hours, Congestion Index, Total Waiting Cost
- Azure Map: vessel positions by location, bubble size = position count
- Bar chart: wait hours by vessel type
- Slicers: vessel type, flag, status

### Page 2: Trends & Patterns
- Line chart: Daily Waiting Count + 7-day moving average
- Bar chart: Avg Wait Hours by day of week
- Column chart: Waiting Vessels by hour
- **R Visual**: ARIMA 3-day congestion forecast with confidence interval

### Page 3: Vessel Detail
- Detail table: all vessels with speed, wait hours, zone
- **R Visual**: Isolation Forest anomaly detection — flags top 10% anomalous positions (red dots on map)
- **R Visual**: K-means clustering (k=4) — groups vessels by behaviour (waiting, berthed, transit, mixed)

### Page 4: Cost Impact
- 3 KPI cards: Total Cost, Waiting Vessels, Avg Wait Hours
- Donut chart: cost breakdown by vessel type
- Gradient bar chart: cost per vessel (top waiters)
- Cost detail table

## Demo Script (5 minutes)

1. **Open Page 1** — "This monitors Piraeus port congestion in real-time. Right now we have X vessels waiting, costing an estimated $Y per day."

2. **Point to the map** — "Each bubble is a vessel. The cluster south of the port entrance is the anchorage — those are the waiting vessels."

3. **Use a slicer** — filter by Tanker. "Tankers have the highest daily cost rate at $35K/day."

4. **Switch to Page 2** — "The line chart shows congestion over time. The R visual at bottom right uses ARIMA to forecast the next 3 days."

5. **Switch to Page 3** — "The left R visual runs Isolation Forest in real-time — red dots are anomalous positions. The right visual clusters vessels by behaviour using K-means."

6. **Switch to Page 4** — "Total estimated cost impact. The gradient bar shows which specific vessels are most expensive to have waiting."

7. **If using live data** — show the terminal running the collector, then hit Refresh in Power BI. "The data updates from a WebSocket stream connected to aisstream.io."

## Technical Talking Points

- **Code-first approach**: Dashboard pages generated from Python, not drag-and-drop. Version-controlled, reproducible, auditable.
- **Three languages**: Python (data pipeline + page generation), DAX (business logic), R (ML analytics) — all integrated in one .pbip.
- **R embedded in Power BI**: Isolation Forest, K-means, and ARIMA run directly inside the dashboard visuals. No external server needed.
- **Real AIS data**: aisstream.io provides free global vessel tracking. The collector filters to Piraeus bounding box.
- **Domain knowledge**: Status classification uses speed + geographic zones matching real Piraeus port layout (PCT container terminal, passenger terminal, anchorage areas).

## Files

```
portpulse/
  data/
    generate_piraeus_data.py    # Synthetic data generator
    piraeus_collector.py        # Live AIS WebSocket collector
    piraeus_ais.csv             # Synthetic dataset (4031 rows)
    piraeus_zones.csv           # Port zone reference (5 zones)
  scripts/
    generate_pages.py           # Generates all 4 dashboard pages (45 visuals)
  PortPulse_Dashboard_Prompts.md  # Coworker prompts for data model
  portpulse_dash.pbip           # Power BI project file
```
