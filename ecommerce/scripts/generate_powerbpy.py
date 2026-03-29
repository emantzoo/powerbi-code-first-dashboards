"""
E-Commerce Dashboard built with powerbpy library.

This is a "quick try" to see how powerbpy compares to the custom generate_pages.py script.

Key differences from the custom script approach:
  - powerbpy loads CSVs directly (no need for Power BI Desktop + MCP for Phase 0-1)
  - Works with raw columns + aggregation (Sum/Count/Average), NOT DAX measures
  - No relationships, no Calendar table, no custom DAX — just flat aggregations per CSV
  - Fewer visual types supported (no donut, matrix, treemap, filled map)
  - But: creates the entire .pbip project from scratch in one script

Limitations compared to the DAX-based dashboard:
  - No cross-table calculations (e.g., Total Cost = SUMX with RELATED)
  - No time intelligence (YoY, YTD, L12M, SAMEPERIODLASTYEAR)
  - No profit margin, return rate, or other derived measures
  - No Calendar table for proper date filtering
"""

from powerbpy import Dashboard
import os

# --- Config ---
PROJECT_DIR = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\ecommerce\ecommerce_powerbpy"
DATA_DIR = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\ecommerce\data"

# Clean up if exists (for re-runs)
if os.path.exists(PROJECT_DIR):
    import shutil
    shutil.rmtree(PROJECT_DIR)

# --- Create dashboard and load data ---
dash = Dashboard.create(PROJECT_DIR)

dash.add_local_csv(os.path.join(DATA_DIR, "FactSales.csv"))
dash.add_local_csv(os.path.join(DATA_DIR, "FactReturns.csv"))
dash.add_local_csv(os.path.join(DATA_DIR, "DimProduct.csv"))
dash.add_local_csv(os.path.join(DATA_DIR, "DimCustomer.csv"))
dash.add_local_csv(os.path.join(DATA_DIR, "DimStore.csv"))

# ===== PAGE 1: Sales Overview =====
p1 = dash.new_page("Sales Overview")

p1.add_card(data_source="FactSales", measure_name="unit_price",
            visual_id="card_revenue", height=110, width=295,
            x_position=20, y_position=10, card_title="Total Revenue (unit_price)")

p1.add_card(data_source="FactSales", measure_name="quantity",
            visual_id="card_qty", height=110, width=295,
            x_position=330, y_position=10, card_title="Total Quantity")

p1.add_card(data_source="FactSales", measure_name="shipping_cost",
            visual_id="card_shipping", height=110, width=295,
            x_position=640, y_position=10, card_title="Total Shipping Cost")

p1.add_card(data_source="FactSales", measure_name="order_id",
            visual_id="card_orders", height=110, width=295,
            x_position=950, y_position=10, card_title="Order Count")

p1.add_chart(visual_id="bar_category", data_source="DimProduct",
             chart_type="clusteredBarChart",
             chart_title="Revenue by Category",
             x_axis_title="Category", y_axis_title="Cost Price",
             x_axis_var="category", y_axis_var="cost_price",
             y_axis_var_aggregation_type="Sum",
             height=280, width=400, x_position=20, y_position=140)

p1.add_chart(visual_id="line_trend", data_source="FactSales",
             chart_type="lineChart",
             chart_title="Revenue Trend",
             x_axis_title="Order Date", y_axis_title="Unit Price",
             x_axis_var="order_date", y_axis_var="unit_price",
             y_axis_var_aggregation_type="Sum",
             height=280, width=400, x_position=440, y_position=140)

p1.add_chart(visual_id="bar_region", data_source="DimStore",
             chart_type="barChart",
             chart_title="Stores by Channel",
             x_axis_title="Channel", y_axis_title="Count",
             x_axis_var="channel", y_axis_var="store_id",
             y_axis_var_aggregation_type="Count",
             height=280, width=380, x_position=860, y_position=140)

p1.add_chart(visual_id="area_shipping", data_source="FactSales",
             chart_type="areaChart",
             chart_title="Shipping Cost Over Time",
             x_axis_title="Date", y_axis_title="Shipping Cost",
             x_axis_var="order_date", y_axis_var="shipping_cost",
             y_axis_var_aggregation_type="Sum",
             height=260, width=600, x_position=20, y_position=440)

p1.add_slicer(data_source="DimProduct", column_name="category",
              visual_id="slicer_cat", height=260, width=200,
              x_position=640, y_position=440, title="Category")

p1.add_chart(visual_id="bar_region2", data_source="DimStore",
             chart_type="columnChart",
             chart_title="Orders by Region",
             x_axis_title="Region", y_axis_title="Count",
             x_axis_var="region", y_axis_var="store_id",
             y_axis_var_aggregation_type="Count",
             height=260, width=380, x_position=860, y_position=440)

# ===== PAGE 2: Product Performance =====
p2 = dash.new_page("Product Performance")

p2.add_card(data_source="FactSales", measure_name="unit_price",
            visual_id="p2_card_rev", height=110, width=235,
            x_position=20, y_position=10, card_title="Total Revenue")

p2.add_card(data_source="FactSales", measure_name="discount_pct",
            visual_id="p2_card_disc", height=110, width=235,
            x_position=270, y_position=10, card_title="Total Discount")

p2.add_card(data_source="FactSales", measure_name="quantity",
            visual_id="p2_card_qty", height=110, width=235,
            x_position=520, y_position=10, card_title="Total Quantity")

p2.add_card(data_source="FactReturns", measure_name="refund_amount",
            visual_id="p2_card_refunds", height=110, width=235,
            x_position=770, y_position=10, card_title="Total Refunds")

p2.add_slicer(data_source="DimProduct", column_name="category",
              visual_id="p2_slicer_cat", height=110, width=230,
              x_position=1020, y_position=10, title="Category")

p2.add_chart(visual_id="p2_subcat_bar", data_source="DimProduct",
             chart_type="clusteredBarChart",
             chart_title="Products by Subcategory",
             x_axis_title="Subcategory", y_axis_title="Cost",
             x_axis_var="subcategory", y_axis_var="cost_price",
             y_axis_var_aggregation_type="Sum",
             height=280, width=610, x_position=20, y_position=140)

p2.add_chart(visual_id="p2_brand_bar", data_source="DimProduct",
             chart_type="clusteredBarChart",
             chart_title="Products by Brand",
             x_axis_title="Brand", y_axis_title="Cost",
             x_axis_var="brand", y_axis_var="cost_price",
             y_axis_var_aggregation_type="Sum",
             height=280, width=600, x_position=650, y_position=140)

p2.add_table(visual_id="p2_table", data_source="DimProduct",
             variables=["category", "subcategory", "brand", "cost_price"],
             height=260, width=1230, x_position=20, y_position=440,
             table_title="Product Details")

# ===== PAGE 3: Customer Analysis =====
p3 = dash.new_page("Customer Analysis")

p3.add_card(data_source="DimCustomer", measure_name="customer_id",
            visual_id="p3_card_cust", height=110, width=295,
            x_position=20, y_position=10, card_title="Total Customers")

p3.add_card(data_source="FactSales", measure_name="unit_price",
            visual_id="p3_card_rev", height=110, width=295,
            x_position=330, y_position=10, card_title="Total Revenue")

p3.add_card(data_source="FactSales", measure_name="quantity",
            visual_id="p3_card_qty", height=110, width=295,
            x_position=640, y_position=10, card_title="Total Quantity")

p3.add_card(data_source="FactSales", measure_name="shipping_cost",
            visual_id="p3_card_ship", height=110, width=295,
            x_position=950, y_position=10, card_title="Total Shipping")

p3.add_chart(visual_id="p3_trend", data_source="FactSales",
             chart_type="lineChart",
             chart_title="Revenue Over Time",
             x_axis_title="Date", y_axis_title="Revenue",
             x_axis_var="order_date", y_axis_var="unit_price",
             y_axis_var_aggregation_type="Sum",
             height=280, width=610, x_position=20, y_position=140)

p3.add_chart(visual_id="p3_segment", data_source="DimCustomer",
             chart_type="columnChart",
             chart_title="Customers by Segment",
             x_axis_title="Segment", y_axis_title="Count",
             x_axis_var="segment", y_axis_var="customer_id",
             y_axis_var_aggregation_type="Count",
             height=280, width=290, x_position=650, y_position=140)

p3.add_chart(visual_id="p3_country", data_source="DimCustomer",
             chart_type="barChart",
             chart_title="Customers by Country",
             x_axis_title="Country", y_axis_title="Count",
             x_axis_var="country", y_axis_var="customer_id",
             y_axis_var_aggregation_type="Count",
             height=280, width=290, x_position=960, y_position=140)

p3.add_table(visual_id="p3_table", data_source="DimCustomer",
             variables=["customer_name", "segment", "city", "country"],
             height=260, width=1230, x_position=20, y_position=440,
             table_title="Customer Directory")

# ===== PAGE 4: Returns Analysis =====
p4 = dash.new_page("Returns Analysis")

p4.add_card(data_source="FactReturns", measure_name="return_id",
            visual_id="p4_card_returns", height=110, width=295,
            x_position=20, y_position=10, card_title="Total Returns")

p4.add_card(data_source="FactReturns", measure_name="refund_amount",
            visual_id="p4_card_refunds", height=110, width=295,
            x_position=330, y_position=10, card_title="Total Refunds")

p4.add_card(data_source="FactSales", measure_name="unit_price",
            visual_id="p4_card_rev", height=110, width=295,
            x_position=640, y_position=10, card_title="Total Revenue")

p4.add_card(data_source="FactSales", measure_name="quantity",
            visual_id="p4_card_qty", height=110, width=295,
            x_position=950, y_position=10, card_title="Total Qty Sold")

p4.add_chart(visual_id="p4_reason_bar", data_source="FactReturns",
             chart_type="clusteredBarChart",
             chart_title="Returns by Reason",
             x_axis_title="Reason", y_axis_title="Count",
             x_axis_var="reason_code", y_axis_var="return_id",
             y_axis_var_aggregation_type="Count",
             height=280, width=400, x_position=20, y_position=140)

p4.add_chart(visual_id="p4_trend", data_source="FactReturns",
             chart_type="lineChart",
             chart_title="Returns Over Time",
             x_axis_title="Date", y_axis_title="Refund Amount",
             x_axis_var="return_date", y_axis_var="refund_amount",
             y_axis_var_aggregation_type="Sum",
             height=280, width=400, x_position=440, y_position=140)

p4.add_chart(visual_id="p4_refund_bar", data_source="FactReturns",
             chart_type="columnChart",
             chart_title="Refunds by Reason",
             x_axis_title="Reason", y_axis_title="Refund Amount",
             x_axis_var="reason_code", y_axis_var="refund_amount",
             y_axis_var_aggregation_type="Sum",
             height=280, width=380, x_position=860, y_position=140)

p4.add_table(visual_id="p4_table", data_source="FactReturns",
             variables=["return_id", "order_id", "return_date", "reason_code", "refund_amount"],
             height=260, width=1230, x_position=20, y_position=440,
             table_title="Returns Detail")

print(f"Dashboard created at: {PROJECT_DIR}")
print(f"Pages: {dash.list_pages()}")
print("Done! Open the .pbip file in Power BI Desktop.")
