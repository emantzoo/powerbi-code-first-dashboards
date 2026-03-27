# E-Commerce Sales & Customer Analytics — Power BI Build Prompts

Use these prompts in order. Each one is a copy-paste block for Claude Desktop (Cowork or Code tab).

Replace `C:\YOUR_DATA_PATH` with the actual folder where you saved the 5 CSVs.
Replace `C:\YOUR_SAVE_PATH` with where you want the .pbip project saved.

---

## PHASE 0 — Load Data

> Open a blank Power BI Desktop first. Then paste this into Claude Desktop:

```
Connect to my open Power BI Desktop file.

Load all CSV files from C:\YOUR_DATA_PATH into my Power BI model.
The folder contains these 5 files:
- FactSales.csv (5000 rows — order transactions)
- FactReturns.csv (400 rows — product returns)
- DimProduct.csv (150 rows — product catalog)
- DimCustomer.csv (800 rows — customer details)
- DimStore.csv (8 rows — store/channel info)

Read the headers from each CSV and create tables with the correct column names and data types.
For date columns (order_date, return_date, registration_date), use Date type.
For ID columns (order_id, customer_id, product_id, store_id, return_id), use Text type.
For numeric columns (quantity, unit_price, discount_pct, shipping_cost, cost_price, refund_amount), use Decimal Number type.

Refresh the model after loading. Confirm row counts for each table.
```

---

## PHASE 1A — Relationships

> Paste this after Phase 0 completes:

```
Delete all auto-detected relationships in the model first.

Then create these relationships:

1. FactSales[product_id] -> DimProduct[product_id] (Many:1, ACTIVE, single direction cross-filter)
2. FactSales[customer_id] -> DimCustomer[customer_id] (Many:1, ACTIVE, single direction cross-filter)
3. FactSales[store_id] -> DimStore[store_id] (Many:1, ACTIVE, single direction cross-filter)
4. FactReturns[order_id] -> FactSales[order_id] (Many:1, ACTIVE, single direction cross-filter)

Do NOT create date relationships yet — we'll do that after the Calendar table.
```

---

## PHASE 1B — Calendar Table

> Paste this next:

```
Create a DAX calculated table called Calendar:

Calendar = ADDCOLUMNS(
    CALENDAR(DATE(2022,1,1), DATE(2025,6,30)),
    "Year", YEAR([Date]),
    "Quarter", "Q" & CEILING(MONTH([Date])/3, 1),
    "Month_Num", MONTH([Date]),
    "Month_Name", FORMAT([Date], "MMMM"),
    "Year_Quarter", FORMAT([Date], "YYYY") & "-Q" & CEILING(MONTH([Date])/3, 1),
    "Year_Month", FORMAT([Date], "YYYY-MM"),
    "Day_of_Week", FORMAT([Date], "dddd"),
    "Is_Weekend", IF(WEEKDAY([Date], 2) >= 6, "Weekend", "Weekday")
)

Mark it as a Date Table using the Date column.

Then create these date relationships:
5. FactSales[order_date] -> Calendar[Date] (Many:1, ACTIVE, single direction cross-filter)
6. FactReturns[return_date] -> Calendar[Date] (Many:1, INACTIVE, single direction cross-filter)
```

---

## PHASE 1C — DAX Measures (Batch 1: Core KPIs)

```
Create a _Measures table (or add to it if it exists) with these DAX measures:

Total Revenue = SUMX(FactSales, FactSales[quantity] * FactSales[unit_price] * (1 - FactSales[discount_pct]))

Total Cost = SUMX(FactSales, FactSales[quantity] * RELATED(DimProduct[cost_price]))

Total Profit = [Total Revenue] - [Total Cost]

Profit Margin = DIVIDE([Total Profit], [Total Revenue], 0)

Total Orders = DISTINCTCOUNT(FactSales[order_id])

Total Quantity = SUM(FactSales[quantity])

Avg Order Value = DIVIDE([Total Revenue], [Total Orders], 0)

Total Discount Given = SUMX(FactSales, FactSales[quantity] * FactSales[unit_price] * FactSales[discount_pct])

Total Shipping = SUM(FactSales[shipping_cost])

Total Customers = DISTINCTCOUNT(FactSales[customer_id])
```

---

## PHASE 1D — DAX Measures (Batch 2: Returns)

```
Add these measures to _Measures:

Total Returns = COUNTROWS(FactReturns)

Total Refunds = SUM(FactReturns[refund_amount])

Return Rate = DIVIDE([Total Returns], [Total Orders], 0)

Net Revenue = [Total Revenue] - [Total Refunds]

Returns by Date = CALCULATE(
    [Total Returns],
    USERELATIONSHIP(FactReturns[return_date], Calendar[Date])
)
```

---

## PHASE 1E — DAX Measures (Batch 3: Time Intelligence)

```
Add these measures to _Measures:

Revenue MTD = TOTALMTD([Total Revenue], Calendar[Date])

Revenue YTD = TOTALYTD([Total Revenue], Calendar[Date])

Revenue PY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(Calendar[Date]))

Revenue YoY Growth = DIVIDE([Total Revenue] - [Revenue PY], [Revenue PY], 0)

Orders PY = CALCULATE([Total Orders], SAMEPERIODLASTYEAR(Calendar[Date]))

Orders YoY Growth = DIVIDE([Total Orders] - [Orders PY], [Orders PY], 0)

Revenue L3M = CALCULATE(
    [Total Revenue],
    DATESINPERIOD(Calendar[Date], MAX(Calendar[Date]), -3, MONTH)
)

Revenue L12M = CALCULATE(
    [Total Revenue],
    DATESINPERIOD(Calendar[Date], MAX(Calendar[Date]), -12, MONTH)
)
```

---

## PHASE 1F — DAX Measures (Batch 4: Conditional Formatting)

```
Add these measures to _Measures:

Margin RAG Status = SWITCH(
    TRUE(),
    [Profit Margin] >= 0.3, "Green",
    [Profit Margin] >= 0.15, "Amber",
    "Red"
)

Margin RAG Color = SWITCH(
    TRUE(),
    [Profit Margin] >= 0.3, "#27AE60",
    [Profit Margin] >= 0.15, "#F39C12",
    "#E74C3C"
)

YoY RAG Color = SWITCH(
    TRUE(),
    [Revenue YoY Growth] > 0.05, "#27AE60",
    [Revenue YoY Growth] > -0.05, "#F39C12",
    "#E74C3C"
)

Return Rate RAG Color = SWITCH(
    TRUE(),
    [Return Rate] <= 0.05, "#27AE60",
    [Return Rate] <= 0.10, "#F39C12",
    "#E74C3C"
)
```

---

## PHASE 1G — Save

> Do this manually:

1. In Power BI Desktop: **File > Save As > Power BI Project (.pbip)**
2. Save to `C:\YOUR_SAVE_PATH\ECommerceDashboard`
3. **Close Power BI Desktop completely**

This creates the PBIR folder structure needed for Phase 2.

---

## PHASE 2 — Generate Visuals (PBIR)

> Paste this into Claude Code. Make sure you're in the project directory or provide the full path.

```
I have a Power BI project saved as .pbip with PBIR format at:
C:\YOUR_SAVE_PATH\ECommerceDashboard

The data model has these tables:
- FactSales (order_id, order_date, customer_id, product_id, store_id, quantity, unit_price, discount_pct, shipping_cost)
- FactReturns (return_id, order_id, return_date, reason_code, refund_amount)
- DimProduct (product_id, product_name, category, subcategory, brand, cost_price)
- DimCustomer (customer_id, customer_name, email, segment, city, country, registration_date)
- DimStore (store_id, store_name, channel, region)
- Calendar (Date, Year, Quarter, Month_Num, Month_Name, Year_Quarter, Year_Month, Day_of_Week, Is_Weekend)
- _Measures (all measures listed below)

Measures in _Measures:
Total Revenue, Total Cost, Total Profit, Profit Margin, Total Orders, Total Quantity,
Avg Order Value, Total Discount Given, Total Shipping, Total Customers,
Total Returns, Total Refunds, Return Rate, Net Revenue, Returns by Date,
Revenue MTD, Revenue YTD, Revenue PY, Revenue YoY Growth,
Orders PY, Orders YoY Growth, Revenue L3M, Revenue L12M,
Margin RAG Status, Margin RAG Color, YoY RAG Color, Return Rate RAG Color

Generate PBIR visual.json files for a 4-page dashboard. Use schema version 2.7.0. Canvas is 1280x720.

### Page 1 — Executive Overview
Layout: 4 KPI cards across the top, 3 charts below, 1 slicer.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=295): Total Revenue
- Card 2 (x=330, w=295): Total Profit
- Card 3 (x=640, w=295): Profit Margin
- Card 4 (x=950, w=295): Total Orders

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): DimProduct[category] vs Total Revenue
- Line chart (x=440, w=400): Calendar[Year_Month] vs Total Revenue
- Donut chart (x=860, w=380): DimStore[channel] vs Total Revenue

Row 3 (y=440, h=260):
- Area chart (x=20, w=600): Calendar[Year_Month] vs Total Profit
- Slicer (x=640, w=200): Calendar[Year]
- Clustered bar chart (x=860, w=380): DimStore[region] vs Total Orders

### Page 2 — Product Performance
Layout: category/brand analysis with drill-down potential.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=235): Total Revenue
- Card 2 (x=270, w=235): Avg Order Value
- Card 3 (x=520, w=235): Total Quantity
- Card 4 (x=770, w=235): Return Rate
- Slicer (x=1020, w=230): DimProduct[category]

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=610): DimProduct[subcategory] vs Total Revenue
- Clustered bar chart (x=650, w=600): DimProduct[brand] vs Total Profit

Row 3 (y=440, h=260):
- Table (x=20, w=1230): DimProduct[category], DimProduct[subcategory], DimProduct[brand], Total Revenue, Total Profit, Profit Margin, Total Quantity, Return Rate

### Page 3 — Customer & Trends
Layout: time intelligence and customer segmentation.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=295): Total Customers
- Card 2 (x=330, w=295): Revenue YoY Growth
- Card 3 (x=640, w=295): Revenue YTD
- Card 4 (x=950, w=295): Revenue L12M

Row 2 (y=140, h=280):
- Line chart (x=20, w=610): Calendar[Year_Month] vs Total Revenue, also add Revenue PY as second Y value
- Donut chart (x=650, w=290): DimCustomer[segment] vs Total Revenue
- Clustered bar chart (x=960, w=290): DimCustomer[country] vs Total Customers

Row 3 (y=440, h=260):
- Matrix / Pivot table (x=20, w=1230):
  Rows: DimCustomer[country]
  Columns: Calendar[Year]
  Values: Total Revenue, Total Orders

### Page 4 — Returns Analysis (drill-through target)
Layout: returns deep-dive with reason codes and trends.

Row 1 (y=10, h=110):
- Card 1 (x=20, w=295): Total Returns
- Card 2 (x=330, w=295): Total Refunds
- Card 3 (x=640, w=295): Return Rate
- Card 4 (x=950, w=295): Net Revenue

Row 2 (y=140, h=280):
- Clustered bar chart (x=20, w=400): FactReturns[reason_code] vs Total Returns
- Line chart (x=440, w=400): Calendar[Year_Month] vs Returns by Date
- Donut chart (x=860, w=380): DimProduct[category] vs Total Returns

Row 3 (y=440, h=260):
- Table (x=20, w=1230): FactReturns[reason_code], Total Returns, Total Refunds, Return Rate

Write all files directly into ECommerceDashboard.Report/definition/pages/
Update pages.json with the 4 page folders in pageOrder.
```

---

## PHASE 3 — Open and Polish

1. Open `ECommerceDashboard.pbip` in Power BI Desktop
2. All 4 pages should appear with data-bound visuals
3. Manual polish (~15-30 min):
   - Apply a color theme (View > Themes)
   - Add visual titles and format labels
   - Set conditional formatting on KPI cards using the RAG Color measures
   - Sync the Year slicer across pages (View > Sync Slicers)
   - Configure Page 4 as a drill-through page (add a drill-through field for DimProduct[category])
   - Add page navigation buttons
   - Adjust any overlapping visuals

---

## Schema Reference

### Star Schema Diagram

```
                    Calendar
                      |
                      | Date
                      |
DimProduct -----> FactSales <----- DimCustomer
  product_id       |    |           customer_id
                   |    |
              store_id  order_id
                   |       |
              DimStore  FactReturns ----> Calendar (INACTIVE via return_date)
```

### All Relationships

| From | To | Cardinality | Active | Cross-Filter |
|------|----|-------------|--------|--------------|
| FactSales[product_id] | DimProduct[product_id] | Many:1 | Yes | Single |
| FactSales[customer_id] | DimCustomer[customer_id] | Many:1 | Yes | Single |
| FactSales[store_id] | DimStore[store_id] | Many:1 | Yes | Single |
| FactSales[order_date] | Calendar[Date] | Many:1 | Yes | Single |
| FactReturns[order_id] | FactSales[order_id] | Many:1 | Yes | Single |
| FactReturns[return_date] | Calendar[Date] | Many:1 | No | Single |

### All Measures

| Measure | DAX | Category |
|---------|-----|----------|
| Total Revenue | SUMX(FactSales, quantity * unit_price * (1 - discount_pct)) | Core KPI |
| Total Cost | SUMX(FactSales, quantity * RELATED(DimProduct[cost_price])) | Core KPI |
| Total Profit | [Total Revenue] - [Total Cost] | Core KPI |
| Profit Margin | DIVIDE([Total Profit], [Total Revenue], 0) | Core KPI |
| Total Orders | DISTINCTCOUNT(FactSales[order_id]) | Core KPI |
| Total Quantity | SUM(FactSales[quantity]) | Core KPI |
| Avg Order Value | DIVIDE([Total Revenue], [Total Orders], 0) | Core KPI |
| Total Discount Given | SUMX(FactSales, quantity * unit_price * discount_pct) | Core KPI |
| Total Shipping | SUM(FactSales[shipping_cost]) | Core KPI |
| Total Customers | DISTINCTCOUNT(FactSales[customer_id]) | Core KPI |
| Total Returns | COUNTROWS(FactReturns) | Returns |
| Total Refunds | SUM(FactReturns[refund_amount]) | Returns |
| Return Rate | DIVIDE([Total Returns], [Total Orders], 0) | Returns |
| Net Revenue | [Total Revenue] - [Total Refunds] | Returns |
| Returns by Date | CALCULATE([Total Returns], USERELATIONSHIP(...)) | Returns |
| Revenue MTD | TOTALMTD([Total Revenue], Calendar[Date]) | Time Intel |
| Revenue YTD | TOTALYTD([Total Revenue], Calendar[Date]) | Time Intel |
| Revenue PY | CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(...)) | Time Intel |
| Revenue YoY Growth | DIVIDE([Total Revenue] - [Revenue PY], [Revenue PY], 0) | Time Intel |
| Orders PY | CALCULATE([Total Orders], SAMEPERIODLASTYEAR(...)) | Time Intel |
| Orders YoY Growth | DIVIDE([Total Orders] - [Orders PY], [Orders PY], 0) | Time Intel |
| Revenue L3M | CALCULATE([Total Revenue], DATESINPERIOD(..., -3, MONTH)) | Time Intel |
| Revenue L12M | CALCULATE([Total Revenue], DATESINPERIOD(..., -12, MONTH)) | Time Intel |
| Margin RAG Status | SWITCH(TRUE(), >= 0.3 Green, >= 0.15 Amber, Red) | Formatting |
| Margin RAG Color | SWITCH(TRUE(), >= 0.3 #27AE60, >= 0.15 #F39C12, #E74C3C) | Formatting |
| YoY RAG Color | SWITCH(TRUE(), > 0.05 #27AE60, > -0.05 #F39C12, #E74C3C) | Formatting |
| Return Rate RAG Color | SWITCH(TRUE(), <= 0.05 #27AE60, <= 0.10 #F39C12, #E74C3C) | Formatting |
