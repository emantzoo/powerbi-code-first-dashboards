# Retail Supply Chain & Inventory Dashboard — Power BI Build Prompts

Use these prompts in order. Each one is a copy-paste block for Claude Desktop (Cowork or Code tab).

Replace `C:\YOUR_DATA_PATH` with the actual folder where you saved the 6 CSVs.
Replace `C:\YOUR_SAVE_PATH` with where you want the .pbip project saved.

---

## PHASE 0 — Load Data

> Open a blank Power BI Desktop first. Then paste this into Claude Desktop:

```
Connect to my open Power BI Desktop file.

Load all CSV files from C:\YOUR_DATA_PATH into my Power BI model.
The folder contains these 6 files:
- FactOrders.csv (3000 rows — purchase orders with expected vs actual delivery dates)
- FactInventorySnapshot.csv (10500 rows — weekly inventory levels by product and warehouse)
- FactShipmentRoutes.csv (50 rows — pre-aggregated supplier-to-warehouse route metrics with lat/lng for map visuals)
- DimProduct.csv (100 rows — product catalog with categories and weight)
- DimSupplier.csv (10 rows — suppliers with country, lead time, reliability rating, and lat/lng coordinates)
- DimWarehouse.csv (5 rows — warehouses with city, country, capacity, and lat/lng coordinates)

Read the headers from each CSV and create tables with the correct column names and data types.
For date columns (order_date, expected_delivery_date, actual_delivery_date, snapshot_date), use Date type.
For ID columns (order_id, product_id, supplier_id, warehouse_id, route_id), use Text type.
For coordinate columns (latitude, longitude, supplier_lat, supplier_lng, warehouse_lat, warehouse_lng), use Decimal Number type.
For other numeric columns (quantity_ordered, unit_cost, capacity_units, lead_time_days, reliability_rating, quantity_on_hand, quantity_reserved, reorder_point, unit_weight_kg, total_shipments, avg_transit_days, on_time_pct, total_quantity, total_cost), use Decimal Number or Whole Number as appropriate.
For text columns, use Text type.

Refresh the model after loading. Confirm row counts for each table.
```

---

## PHASE 1A — Relationships

```
Delete all auto-detected relationships in the model first.

Then create these relationships:

1. FactOrders[supplier_id] -> DimSupplier[supplier_id] (Many:1, ACTIVE, single direction)
2. FactOrders[product_id] -> DimProduct[product_id] (Many:1, ACTIVE, single direction)
3. FactOrders[warehouse_id] -> DimWarehouse[warehouse_id] (Many:1, ACTIVE, single direction)
4. FactInventorySnapshot[product_id] -> DimProduct[product_id] (Many:1, INACTIVE, single direction)
5. FactInventorySnapshot[warehouse_id] -> DimWarehouse[warehouse_id] (Many:1, INACTIVE, single direction)
6. FactShipmentRoutes[supplier_id] -> DimSupplier[supplier_id] (Many:1, INACTIVE, single direction)
7. FactShipmentRoutes[warehouse_id] -> DimWarehouse[warehouse_id] (Many:1, INACTIVE, single direction)

Do NOT create date relationships yet — we'll do that after the Calendar table.
```

---

## PHASE 1B — Calendar Table

```
Create a DAX calculated table called Calendar:

Calendar = ADDCOLUMNS(
    CALENDAR(DATE(2023,1,1), DATE(2025,6,30)),
    "Year", YEAR([Date]),
    "Quarter", "Q" & CEILING(MONTH([Date])/3, 1),
    "Month_Num", MONTH([Date]),
    "Month_Name", FORMAT([Date], "MMMM"),
    "Year_Quarter", FORMAT([Date], "YYYY") & "-Q" & CEILING(MONTH([Date])/3, 1),
    "Year_Month", FORMAT([Date], "YYYY-MM"),
    "Week_Num", WEEKNUM([Date]),
    "Year_Week", FORMAT([Date], "YYYY") & "-W" & FORMAT(WEEKNUM([Date]), "00")
)

Mark it as a Date Table using the Date column.

Then create these date relationships:
8. FactOrders[order_date] -> Calendar[Date] (Many:1, ACTIVE, single direction)
9. FactOrders[expected_delivery_date] -> Calendar[Date] (Many:1, INACTIVE, single direction)
10. FactOrders[actual_delivery_date] -> Calendar[Date] (Many:1, INACTIVE, single direction)
11. FactInventorySnapshot[snapshot_date] -> Calendar[Date] (Many:1, INACTIVE, single direction)
```

---

## PHASE 1C — DAX Measures (Batch 1: Order KPIs)

```
Create a _Measures table (or add to it if it exists) with these DAX measures:

Total Orders = COUNTROWS(FactOrders)

Total Order Value = SUMX(FactOrders, FactOrders[quantity_ordered] * FactOrders[unit_cost])

Avg Order Value = DIVIDE([Total Order Value], [Total Orders], 0)

Total Quantity Ordered = SUM(FactOrders[quantity_ordered])

Unique Suppliers Used = DISTINCTCOUNT(FactOrders[supplier_id])

Unique Products Ordered = DISTINCTCOUNT(FactOrders[product_id])
```

---

## PHASE 1D — DAX Measures (Batch 2: Delivery Performance)

```
Add these measures to _Measures:

On Time Deliveries = COUNTROWS(
    FILTER(FactOrders, FactOrders[actual_delivery_date] <= FactOrders[expected_delivery_date])
)

Late Deliveries = COUNTROWS(
    FILTER(FactOrders, FactOrders[actual_delivery_date] > FactOrders[expected_delivery_date])
)

On Time Delivery Rate = DIVIDE([On Time Deliveries], [Total Orders], 0)

Avg Lead Time Days = AVERAGEX(
    FactOrders,
    DATEDIFF(FactOrders[order_date], FactOrders[actual_delivery_date], DAY)
)

Avg Lead Time Variance = AVERAGEX(
    FactOrders,
    DATEDIFF(FactOrders[expected_delivery_date], FactOrders[actual_delivery_date], DAY)
)

Max Delay Days = MAXX(
    FILTER(FactOrders, FactOrders[actual_delivery_date] > FactOrders[expected_delivery_date]),
    DATEDIFF(FactOrders[expected_delivery_date], FactOrders[actual_delivery_date], DAY)
)

Supplier Avg Reliability = AVERAGE(DimSupplier[reliability_rating])
```

---

## PHASE 1E — DAX Measures (Batch 3: Inventory)

```
Add these measures to _Measures:

Latest Inventory On Hand = CALCULATE(
    SUM(FactInventorySnapshot[quantity_on_hand]),
    USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date]),
    LASTDATE(Calendar[Date])
)

Latest Inventory Reserved = CALCULATE(
    SUM(FactInventorySnapshot[quantity_reserved]),
    USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date]),
    LASTDATE(Calendar[Date])
)

Available Inventory = [Latest Inventory On Hand] - [Latest Inventory Reserved]

Stockout Count = CALCULATE(
    COUNTROWS(FILTER(FactInventorySnapshot, FactInventorySnapshot[quantity_on_hand] = 0)),
    USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date])
)

Total Snapshot Records = CALCULATE(
    COUNTROWS(FactInventorySnapshot),
    USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date])
)

Stockout Rate = DIVIDE([Stockout Count], [Total Snapshot Records], 0)

Below Reorder Point = CALCULATE(
    COUNTROWS(
        FILTER(
            FactInventorySnapshot,
            FactInventorySnapshot[quantity_on_hand] <= FactInventorySnapshot[reorder_point]
            && FactInventorySnapshot[quantity_on_hand] > 0
        )
    ),
    USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date])
)

Inventory Turnover = DIVIDE(
    [Total Quantity Ordered],
    CALCULATE(
        AVERAGE(FactInventorySnapshot[quantity_on_hand]),
        USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date])
    ),
    0
)

Days of Supply = DIVIDE(
    [Latest Inventory On Hand],
    DIVIDE([Total Quantity Ordered], COUNTROWS(Calendar), 0),
    0
)
```

---

## PHASE 1F — DAX Measures (Batch 4: Time Intelligence)

```
Add these measures to _Measures:

Order Value MTD = TOTALMTD([Total Order Value], Calendar[Date])

Order Value YTD = TOTALYTD([Total Order Value], Calendar[Date])

Order Value PY = CALCULATE([Total Order Value], SAMEPERIODLASTYEAR(Calendar[Date]))

Order Value YoY Growth = DIVIDE([Total Order Value] - [Order Value PY], [Order Value PY], 0)

Orders PY = CALCULATE([Total Orders], SAMEPERIODLASTYEAR(Calendar[Date]))

On Time Rate PY = CALCULATE([On Time Delivery Rate], SAMEPERIODLASTYEAR(Calendar[Date]))

On Time Rate Change = [On Time Delivery Rate] - [On Time Rate PY]

Order Value L3M = CALCULATE(
    [Total Order Value],
    DATESINPERIOD(Calendar[Date], MAX(Calendar[Date]), -3, MONTH)
)
```

---

## PHASE 1G — DAX Measures (Batch 5: Warehouse Utilization & Map Helpers)

```
Add these measures to _Measures:

Warehouse Capacity = SUM(DimWarehouse[capacity_units])

Warehouse Utilization = DIVIDE([Latest Inventory On Hand], [Warehouse Capacity], 0)

Supplier Lead Time Avg = AVERAGE(DimSupplier[lead_time_days])

Route Shipment Count = SUM(FactShipmentRoutes[total_shipments])

Route On Time Pct = AVERAGE(FactShipmentRoutes[on_time_pct])

Route Avg Transit Days = AVERAGE(FactShipmentRoutes[avg_transit_days])

Route Total Cost = SUM(FactShipmentRoutes[total_cost])
```

---

## PHASE 1H — DAX Measures (Batch 6: Conditional Formatting)

```
Add these measures to _Measures:

OTD RAG Color = SWITCH(
    TRUE(),
    [On Time Delivery Rate] >= 0.85, "#27AE60",
    [On Time Delivery Rate] >= 0.65, "#F39C12",
    "#E74C3C"
)

Stockout RAG Color = SWITCH(
    TRUE(),
    [Stockout Rate] <= 0.05, "#27AE60",
    [Stockout Rate] <= 0.12, "#F39C12",
    "#E74C3C"
)

Utilization RAG Color = SWITCH(
    TRUE(),
    [Warehouse Utilization] >= 0.90, "#E74C3C",
    [Warehouse Utilization] >= 0.70, "#F39C12",
    "#27AE60"
)

Lead Time RAG Color = SWITCH(
    TRUE(),
    [Avg Lead Time Variance] <= 0, "#27AE60",
    [Avg Lead Time Variance] <= 3, "#F39C12",
    "#E74C3C"
)

Supplier Rating Color = SWITCH(
    TRUE(),
    [Supplier Avg Reliability] >= 4.5, "#27AE60",
    [Supplier Avg Reliability] >= 3.5, "#F39C12",
    "#E74C3C"
)
```

---

## PHASE 1I — Save

> Do this manually:

1. In Power BI Desktop: **File > Save As > Power BI Project (.pbip)**
2. Save to `C:\YOUR_SAVE_PATH\SupplyChainDashboard`
3. **Close Power BI Desktop completely**

---

## PHASE 2 — Generate Visuals (PBIR)

> Paste this into Claude Code:

```
I have a Power BI project saved as .pbip with PBIR format at:
C:\YOUR_SAVE_PATH\SupplyChainDashboard

The data model has these tables:
- FactOrders (order_id, order_date, supplier_id, product_id, warehouse_id, quantity_ordered, unit_cost, expected_delivery_date, actual_delivery_date)
- FactInventorySnapshot (snapshot_date, product_id, warehouse_id, quantity_on_hand, quantity_reserved, reorder_point)
- FactShipmentRoutes (route_id, supplier_id, supplier_name, supplier_city, supplier_country, supplier_lat, supplier_lng, warehouse_id, warehouse_name, warehouse_city, warehouse_country, warehouse_lat, warehouse_lng, total_shipments, avg_transit_days, on_time_pct, total_quantity, total_cost)
- DimProduct (product_id, product_name, category, subcategory, unit_weight_kg, is_perishable)
- DimSupplier (supplier_id, supplier_name, country, city, latitude, longitude, lead_time_days, reliability_rating)
- DimWarehouse (warehouse_id, warehouse_name, city, country, latitude, longitude, capacity_units)
- Calendar (Date, Year, Quarter, Month_Num, Month_Name, Year_Quarter, Year_Month, Week_Num, Year_Week)
- _Measures (all measures listed below)

Measures in _Measures:
Total Orders, Total Order Value, Avg Order Value, Total Quantity Ordered,
Unique Suppliers Used, Unique Products Ordered,
On Time Deliveries, Late Deliveries, On Time Delivery Rate,
Avg Lead Time Days, Avg Lead Time Variance, Max Delay Days, Supplier Avg Reliability,
Latest Inventory On Hand, Latest Inventory Reserved, Available Inventory,
Stockout Count, Total Snapshot Records, Stockout Rate,
Below Reorder Point, Inventory Turnover, Days of Supply,
Order Value MTD, Order Value YTD, Order Value PY, Order Value YoY Growth,
Orders PY, On Time Rate PY, On Time Rate Change, Order Value L3M,
Warehouse Capacity, Warehouse Utilization, Supplier Lead Time Avg,
Route Shipment Count, Route On Time Pct, Route Avg Transit Days, Route Total Cost,
OTD RAG Color, Stockout RAG Color, Utilization RAG Color, Lead Time RAG Color, Supplier Rating Color

Generate PBIR visual.json files for a 5-page dashboard. Use schema version 2.7.0. Canvas is 1280x720.

### Page 1 — Supply Chain KPIs
Layout: top KPIs, delivery and cost trend charts, category breakdown.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=190): Total Orders
- Card 2 (x=225, w=190): Total Order Value
- Card 3 (x=430, w=190): On Time Delivery Rate
- Card 4 (x=635, w=190): Stockout Rate
- Card 5 (x=840, w=190): Warehouse Utilization
- Slicer (x=1045, w=210): Calendar[Year]

Row 2 (y=140, h=280):
- Line chart (x=20, w=410): Calendar[Year_Month] vs Total Order Value — add Order Value PY as second Y value for comparison
- Clustered bar chart (x=450, w=400): DimProduct[category] vs Total Order Value
- Donut chart (x=870, w=370): DimWarehouse[warehouse_name] vs Total Quantity Ordered

Row 3 (y=440, h=260):
- Area chart (x=20, w=610): Calendar[Year_Month] vs On Time Delivery Rate
- Clustered bar chart (x=650, w=600): DimSupplier[supplier_name] vs Avg Lead Time Days

### Page 2 — Supplier Scorecard
Layout: supplier performance comparison with reliability and delivery metrics.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=235): Unique Suppliers Used
- Card 2 (x=270, w=235): Supplier Avg Reliability
- Card 3 (x=520, w=235): Avg Lead Time Variance
- Card 4 (x=770, w=235): On Time Rate Change
- Slicer (x=1020, w=230): DimSupplier[country]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=610): DimSupplier[supplier_name] vs On Time Delivery Rate
- Clustered bar chart (x=650, w=600): DimSupplier[supplier_name] vs Total Order Value

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimSupplier[supplier_name], DimSupplier[country], DimSupplier[lead_time_days], DimSupplier[reliability_rating], Total Orders, On Time Delivery Rate, Avg Lead Time Days, Avg Lead Time Variance, Total Order Value

### Page 3 — Inventory Health
Layout: inventory levels, stockout analysis, warehouse comparison. Semi-additive measures featured.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=235): Latest Inventory On Hand
- Card 2 (x=270, w=235): Available Inventory
- Card 3 (x=520, w=235): Stockout Rate
- Card 4 (x=770, w=235): Days of Supply
- Slicer (x=1020, w=230): DimProduct[category]

Row 2 (y=140, h=280):
- Line chart (x=20, w=610): Calendar[Year_Month] vs Latest Inventory On Hand
- Clustered bar chart (x=650, w=600): DimProduct[category] vs Stockout Count

Row 3 (y=440, h=260):
- Matrix / Pivot table (x=20, w=1230):
  Rows: DimWarehouse[warehouse_name]
  Columns: (none — flat matrix)
  Values: DimWarehouse[capacity_units], Latest Inventory On Hand, Available Inventory, Warehouse Utilization, Stockout Count, Stockout Rate, Below Reorder Point, Inventory Turnover

### Page 4 — Global Logistics Map
Layout: MAP VISUALS showing supplier locations, warehouse locations, and shipment routes.

This page uses Power BI's built-in map visuals. The data is in FactShipmentRoutes with lat/lng for both endpoints.

Row 1 (y=10, h=60):
- Card 1 (x=20, w=295): Route Shipment Count
- Card 2 (x=330, w=295): Route Avg Transit Days
- Card 3 (x=640, w=295): Route On Time Pct
- Card 4 (x=950, w=295): Route Total Cost

Row 2 (y=80, h=350):
- Map visual (x=20, w=740, visualType="map"):
  Latitude: DimSupplier[latitude]
  Longitude: DimSupplier[longitude]
  Size: Total Orders
  Legend/Color: DimSupplier[country]
  Tooltip: DimSupplier[supplier_name], Total Orders, On Time Delivery Rate
  
- Map visual (x=780, w=470, visualType="map"):
  Latitude: DimWarehouse[latitude]
  Longitude: DimWarehouse[longitude]
  Size: Warehouse Utilization
  Legend/Color: DimWarehouse[warehouse_name]
  Tooltip: DimWarehouse[warehouse_name], Latest Inventory On Hand, Warehouse Utilization

Row 3 (y=440, h=260):
- Table (x=20, w=1230): FactShipmentRoutes[supplier_name], FactShipmentRoutes[supplier_country], FactShipmentRoutes[warehouse_name], FactShipmentRoutes[warehouse_country], FactShipmentRoutes[total_shipments], FactShipmentRoutes[avg_transit_days], FactShipmentRoutes[on_time_pct], FactShipmentRoutes[total_cost]

IMPORTANT for map visuals: The visualType for Power BI's built-in map is "map".
The query state roles for map visuals are:
- Category: the location identifier (city or name)
- Latitude: latitude column
- Longitude: longitude column  
- Size: measure for bubble size
- Color saturation or Legend: column for color coding
Use the standard PBIR visual.json structure but with these role names in queryState.

### Page 5 — Warehouse Comparison (drill-through target)
Layout: per-warehouse deep-dive with product mix and inventory detail.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=235): Total Orders
- Card 2 (x=270, w=235): Total Order Value
- Card 3 (x=520, w=235): Warehouse Utilization
- Card 4 (x=770, w=235): Stockout Rate
- Slicer (x=1020, w=230): DimWarehouse[warehouse_name]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): DimProduct[category] vs Total Quantity Ordered
- Donut chart (x=440, w=380): DimSupplier[supplier_name] vs Total Orders
- Line chart (x=840, w=410): Calendar[Year_Month] vs Latest Inventory On Hand

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimProduct[product_name], DimProduct[category], Total Quantity Ordered, Latest Inventory On Hand, Available Inventory, Stockout Count, Below Reorder Point

Write all files directly into SupplyChainDashboard.Report/definition/pages/
Update pages.json with the 5 page folders in pageOrder.
```

---

## PHASE 3 — Open and Polish

1. Open `SupplyChainDashboard.pbip` in Power BI Desktop
2. All 5 pages should appear with data-bound visuals
3. Manual polish (~20-30 min):
   - Apply a color theme — consider an industrial blue/orange palette
   - Set conditional formatting on KPI cards using the RAG Color measures
   - Sync the Year slicer across Pages 1, 2, 3
   - Configure Page 5 as a drill-through page (add DimWarehouse[warehouse_name])
   - Format percentage measures as 0.0%
   - Format currency measures with $#,##0
   - Format Days of Supply as 0.0
   - **Map visuals**: After opening, verify the map renders correctly:
     - If bubbles don't appear, manually set the Latitude and Longitude field wells
     - Enable "Show labels" in map formatting for supplier/warehouse names
     - Adjust bubble size range if needed
     - Set map style to "Grayscale" or "Dark" for professional look
   - Add page navigation buttons
   - Consider adding a custom tooltip page for the supplier map showing supplier detail

---

## Schema Reference

### Star Schema Diagram (Multi-Fact)

```
                           Calendar
                             |
                     order_date (active)
                     expected_delivery (INACTIVE)
                     actual_delivery (INACTIVE)
                     snapshot_date (INACTIVE)
                             |
DimSupplier -----> FactOrders <---------> DimProduct
  supplier_id        |     |               product_id
  (lat/lng)          |     |               (also INACTIVE to
                     |     |                FactInventorySnapshot)
               warehouse_id |
                     |       |
               DimWarehouse  |
                (lat/lng)    |
                  |          |
          (INACTIVE links)   |
                  |          |
          FactInventorySnapshot
              (snapshot pattern)
                  
FactShipmentRoutes (pre-aggregated, INACTIVE links to DimSupplier & DimWarehouse)
  - Contains lat/lng for both supplier and warehouse endpoints
  - Used for map visuals and route analysis
```

### All Relationships

| From | To | Cardinality | Active | Cross-Filter |
|------|----|-------------|--------|--------------|
| FactOrders[supplier_id] | DimSupplier[supplier_id] | Many:1 | Yes | Single |
| FactOrders[product_id] | DimProduct[product_id] | Many:1 | Yes | Single |
| FactOrders[warehouse_id] | DimWarehouse[warehouse_id] | Many:1 | Yes | Single |
| FactOrders[order_date] | Calendar[Date] | Many:1 | Yes | Single |
| FactOrders[expected_delivery_date] | Calendar[Date] | Many:1 | No | Single |
| FactOrders[actual_delivery_date] | Calendar[Date] | Many:1 | No | Single |
| FactInventorySnapshot[product_id] | DimProduct[product_id] | Many:1 | No | Single |
| FactInventorySnapshot[warehouse_id] | DimWarehouse[warehouse_id] | Many:1 | No | Single |
| FactInventorySnapshot[snapshot_date] | Calendar[Date] | Many:1 | No | Single |
| FactShipmentRoutes[supplier_id] | DimSupplier[supplier_id] | Many:1 | No | Single |
| FactShipmentRoutes[warehouse_id] | DimWarehouse[warehouse_id] | Many:1 | No | Single |

### Key DAX Skills Demonstrated

| Skill | Measure |
|-------|---------|
| Semi-additive (LASTDATE) | Latest Inventory On Hand — point-in-time via LASTDATE |
| USERELATIONSHIP (x8) | All inventory measures + route measures use inactive links |
| Multi-fact model | 3 fact tables sharing dimensions — most complex schema in portfolio |
| DATEDIFF (3 date pairs) | Lead time, variance, delay — comparing order/expected/actual dates |
| FILTER + comparison | On Time Deliveries — row-level date comparison in FILTER |
| SAMEPERIODLASTYEAR | Order Value PY, On Time Rate PY — YoY delivery improvement |
| Derived measures | On Time Rate Change — difference between current and PY rates |
| DATESINPERIOD | Order Value L3M — rolling 3-month window |
| SWITCH (RAG x5) | OTD, Stockout, Utilization, Lead Time, Supplier Rating colors |
| Map visual bindings | Lat/lng columns for geospatial supplier and warehouse maps |
| Pre-aggregated fact | FactShipmentRoutes — demonstrating when to pre-compute for performance |
| Inventory Turnover | Classic supply chain ratio — ordered qty vs avg on-hand |
| Days of Supply | Forward-looking inventory metric |

### Map Visual Notes for Power BI

Power BI's built-in map visual ("map" visualType) uses these queryState roles:

```json
{
  "Category": { "projections": [{ "field": { "Column": { "Entity": "DimSupplier", "Property": "supplier_name" }}}] },
  "X": { "projections": [{ "field": { "Column": { "Entity": "DimSupplier", "Property": "longitude" }}}] },
  "Y": { "projections": [{ "field": { "Column": { "Entity": "DimSupplier", "Property": "latitude" }}}] },
  "Size": { "projections": [{ "field": { "Measure": { "Entity": "_Measures", "Property": "Total Orders" }}}] }
}
```

Role mapping:
- **Y** = Latitude
- **X** = Longitude  
- **Category** = Location label (supplier name, warehouse name)
- **Size** = Bubble size measure
- **Color saturation** = Optional measure for color intensity
- **Legend** = Optional column for color grouping

The map requires Bing Maps to be enabled in Power BI (File > Options > Security > Map and Filled Map visuals > check "Use Map and Filled Map visuals").
