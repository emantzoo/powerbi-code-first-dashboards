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
    USERELATIONSHIP(FactInventorySnapshot[warehouse_id], DimWarehouse[warehouse_id]),
    USERELATIONSHIP(FactInventorySnapshot[product_id], DimProduct[product_id]),
    LASTDATE(FactInventorySnapshot[snapshot_date])
)

Latest Inventory Reserved = CALCULATE(
    SUM(FactInventorySnapshot[quantity_reserved]),
    USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date]),
    USERELATIONSHIP(FactInventorySnapshot[warehouse_id], DimWarehouse[warehouse_id]),
    USERELATIONSHIP(FactInventorySnapshot[product_id], DimProduct[product_id]),
    LASTDATE(FactInventorySnapshot[snapshot_date])
)

Available Inventory = [Latest Inventory On Hand] - [Latest Inventory Reserved]

Stockout Count = CALCULATE(
    COUNTROWS(FILTER(FactInventorySnapshot, FactInventorySnapshot[quantity_on_hand] = 0)),
    USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date]),
    USERELATIONSHIP(FactInventorySnapshot[warehouse_id], DimWarehouse[warehouse_id]),
    USERELATIONSHIP(FactInventorySnapshot[product_id], DimProduct[product_id])
)

Total Snapshot Records = CALCULATE(
    COUNTROWS(FactInventorySnapshot),
    USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date]),
    USERELATIONSHIP(FactInventorySnapshot[warehouse_id], DimWarehouse[warehouse_id]),
    USERELATIONSHIP(FactInventorySnapshot[product_id], DimProduct[product_id])
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
    USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date]),
    USERELATIONSHIP(FactInventorySnapshot[warehouse_id], DimWarehouse[warehouse_id]),
    USERELATIONSHIP(FactInventorySnapshot[product_id], DimProduct[product_id])
)

Inventory Turnover = DIVIDE(
    [Total Quantity Ordered],
    CALCULATE(
        AVERAGE(FactInventorySnapshot[quantity_on_hand]),
        USERELATIONSHIP(FactInventorySnapshot[snapshot_date], Calendar[Date]),
        USERELATIONSHIP(FactInventorySnapshot[warehouse_id], DimWarehouse[warehouse_id]),
        USERELATIONSHIP(FactInventorySnapshot[product_id], DimProduct[product_id])
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

> Run the Python script — no AI needed:

1. Edit `scripts/generate_pages.py` — update the `BASE` path on line 3 to match your `.pbip` save location
2. Close Power BI Desktop
3. Run:

```bash
python scripts/generate_pages.py
```

The script generates 5 pages with 43 visuals (cards, bar charts, line charts, donut charts, treemaps, filled maps, tables, matrices, slicers) as PBIR `visual.json` files.

### Visual Layout Reference

This is the layout specification that was used to generate `scripts/generate_pages.py`. Canvas is 1280x720.

**Page 1 — Supply Chain KPIs**

Row 1 (y=10, h=110):
- Card (x=20, w=190): Total Orders
- Card (x=225, w=190): Total Order Value
- Card (x=430, w=190): On Time Delivery Rate
- Card (x=635, w=190): Stockout Rate
- Card (x=840, w=190): Warehouse Utilization
- Slicer (x=1045, w=210): Calendar[Year]

Row 2 (y=140, h=280):
- Line chart (x=20, w=410): Calendar[Year_Month] vs Total Order Value + Order Value PY
- Clustered bar chart (x=450, w=400): DimProduct[category] vs Total Order Value
- Donut chart (x=870, w=370): DimWarehouse[warehouse_name] vs Total Quantity Ordered

Row 3 (y=440, h=260):
- Area chart (x=20, w=610): Calendar[Year_Month] vs On Time Delivery Rate
- Clustered bar chart (x=650, w=600): DimSupplier[supplier_name] vs Avg Lead Time Days

**Page 2 — Supplier Scorecard**

Row 1 (y=10, h=110):
- Card (x=20, w=235): Unique Suppliers Used
- Card (x=270, w=235): Supplier Avg Reliability
- Card (x=520, w=235): Avg Lead Time Variance
- Card (x=770, w=235): On Time Rate Change
- Slicer (x=1020, w=230): DimSupplier[country]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=610): DimSupplier[supplier_name] vs On Time Delivery Rate
- Clustered bar chart (x=650, w=600): DimSupplier[supplier_name] vs Total Order Value

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimSupplier[supplier_name], DimSupplier[country], DimSupplier[lead_time_days], DimSupplier[reliability_rating], Total Orders, On Time Delivery Rate, Avg Lead Time Days, Avg Lead Time Variance, Total Order Value

**Page 3 — Inventory Health**

Row 1 (y=10, h=110):
- Card (x=20, w=235): Latest Inventory On Hand
- Card (x=270, w=235): Available Inventory
- Card (x=520, w=235): Stockout Rate
- Card (x=770, w=235): Days of Supply
- Slicer (x=1020, w=230): DimProduct[category]

Row 2 (y=140, h=280):
- Line chart (x=20, w=610): Calendar[Year_Month] vs Latest Inventory On Hand
- Clustered bar chart (x=650, w=600): DimProduct[category] vs Stockout Count

Row 3 (y=440, h=260):
- Matrix (x=20, w=1230): Rows: DimWarehouse[warehouse_name], Values: Latest Inventory On Hand, Available Inventory, Warehouse Utilization, Stockout Count, Stockout Rate, Below Reorder Point, Inventory Turnover

**Page 4 — Global Logistics Map**

Row 1 (y=10, h=60):
- Card (x=20, w=295): Route Shipment Count
- Card (x=330, w=295): Route Avg Transit Days
- Card (x=640, w=295): Route On Time Pct
- Card (x=950, w=295): Route Total Cost

Row 2 (y=80, h=350):
- Treemap (x=20, w=420): DimSupplier[city] grouped by DimSupplier[country], sized by Total Orders
- Filled map / choropleth (x=460, w=790): DimWarehouse[country] vs Total Orders

Row 3 (y=440, h=260):
- Table (x=20, w=1230): FactShipmentRoutes[supplier_name], supplier_country, warehouse_name, warehouse_country, total_shipments, avg_transit_days, on_time_pct, total_cost

**Page 5 — Warehouse Comparison**

Row 1 (y=10, h=110):
- Card (x=20, w=235): Total Orders
- Card (x=270, w=235): Total Order Value
- Card (x=520, w=235): Warehouse Utilization
- Card (x=770, w=235): Stockout Rate
- Slicer (x=1020, w=230): DimWarehouse[warehouse_name]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): DimProduct[category] vs Total Quantity Ordered
- Donut chart (x=440, w=380): DimSupplier[supplier_name] vs Total Orders
- Line chart (x=840, w=410): Calendar[Year_Month] vs Latest Inventory On Hand

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimProduct[product_name], DimProduct[category], Total Quantity Ordered, Latest Inventory On Hand, Available Inventory, Stockout Count, Below Reorder Point

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
