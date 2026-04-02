"""
PBIR Visual Helper Functions — with built-in formatting defaults.

Drop-in replacement for the unformatted versions. Same function signatures,
same call sites — but every visual now includes professional formatting
in the `objects` property of the visual.json.
"""

import json, os, hashlib, shutil

# ── Path and schema constants ──────────────────────────────────────────────
BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\supply_chain\supplyChain_dashb.Report\definition\pages"

SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"
SCHEMA_PAGE   = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"


# ── Formatting helper: build the expr/Literal wrapper ──────────────────────
def _lit(value):
    """Wrap a value in the PBIR Literal expression format."""
    return {"expr": {"Literal": {"Value": value}}}

def _solid(hex_color):
    """Wrap a hex color in the PBIR solid color format."""
    return {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hex_color}'"}}}}}

def _theme_color(color_id, percent=0):
    """Reference a theme data color."""
    return {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": color_id, "Percent": percent}}}}}


# ── Default formatting objects by visual category ──────────────────────────

def _card_objects():
    """Professional card formatting: accent bar, shadow, rounded corners, clean layout."""
    return {
        "layout": [
            {
                "properties": {
                    "style": _lit("'Table'"),
                    "orientation": _lit("1D"),
                    "rowCount": _lit("5L"),
                    "contentOrder": _lit("'referenceLabel_callout_image'")
                }
            },
            {
                "properties": {
                    "rectangleRoundedCurve": _lit("8L"),
                    "paddingUniform": _lit("10L"),
                    "backgroundTransparency": _lit("0D")
                },
                "selector": {"id": "default"}
            }
        ],
        "accentBar": [
            {
                "properties": {
                    "show": _lit("true")
                },
                "selector": {"id": "default"}
            }
        ],
        "shadowCustom": [
            {
                "properties": {
                    "show": _lit("true")
                },
                "selector": {"id": "default"}
            }
        ],
        "shapeCustomRectangle": [
            {
                "properties": {
                    "tileShape": _lit("'rectangleRoundedByPixel'")
                },
                "selector": {"id": "default"}
            }
        ]
    }


def _chart_objects(show_labels=False, label_position="'OutsideEnd'"):
    """Clean chart formatting: light gridlines, clean axis, optional data labels."""
    obj = {
        "categoryAxis": [
            {
                "properties": {
                    "fontSize": _lit("9L"),
                    "showAxisTitle": _lit("false")
                }
            }
        ],
        "valueAxis": [
            {
                "properties": {
                    "fontSize": _lit("9L"),
                    "showAxisTitle": _lit("false"),
                    "gridlineStyle": _lit("'dashed'"),
                    "gridlineColor": _solid("#E2E8F0")
                }
            }
        ]
    }
    if show_labels:
        obj["labels"] = [
            {
                "properties": {
                    "show": _lit("true"),
                    "labelPosition": _lit(label_position),
                    "fontSize": _lit("9L")
                }
            }
        ]
    return obj


def _line_chart_objects():
    """Line/area chart formatting: clean gridlines, no data labels, smooth markers."""
    return {
        "categoryAxis": [
            {
                "properties": {
                    "fontSize": _lit("9L"),
                    "showAxisTitle": _lit("false")
                }
            }
        ],
        "valueAxis": [
            {
                "properties": {
                    "fontSize": _lit("9L"),
                    "showAxisTitle": _lit("false"),
                    "gridlineStyle": _lit("'dashed'"),
                    "gridlineColor": _solid("#E2E8F0")
                }
            }
        ],
        "lineStyles": [
            {
                "properties": {
                    "strokeWidth": _lit("3L")
                }
            }
        ]
    }


def _table_objects():
    """Table formatting: styled headers, alternating rows, clean grid."""
    return {
        "columnHeaders": [
            {
                "properties": {
                    "bold": _lit("true"),
                    "fontSize": _lit("10L"),
                    "fontColor": _solid("#FFFFFF"),
                    "backColor": _theme_color(0)
                }
            }
        ],
        "values": [
            {
                "properties": {
                    "fontSize": _lit("10L"),
                    "backColor": _solid("#FFFFFF"),
                    "backColorAlternate": _solid("#F8FAFC")
                }
            }
        ],
        "grid": [
            {
                "properties": {
                    "gridHorizontal": _lit("true"),
                    "gridHorizontalColor": _solid("#E2E8F0"),
                    "gridVertical": _lit("false"),
                    "rowPadding": _lit("4L")
                }
            }
        ]
    }


def _matrix_objects():
    """Matrix formatting: styled headers, clean grid."""
    return {
        "columnHeaders": [
            {
                "properties": {
                    "bold": _lit("true"),
                    "fontSize": _lit("10L"),
                    "fontColor": _solid("#FFFFFF"),
                    "backColor": _theme_color(0)
                }
            }
        ],
        "rowHeaders": [
            {
                "properties": {
                    "fontSize": _lit("10L")
                }
            }
        ],
        "values": [
            {
                "properties": {
                    "fontSize": _lit("10L"),
                    "backColor": _solid("#FFFFFF"),
                    "backColorAlternate": _solid("#F8FAFC")
                }
            }
        ],
        "grid": [
            {
                "properties": {
                    "gridHorizontal": _lit("true"),
                    "gridHorizontalColor": _solid("#E2E8F0"),
                    "gridVertical": _lit("false"),
                    "rowPadding": _lit("4L")
                }
            }
        ]
    }


def _gauge_objects():
    """Gauge formatting: clean look."""
    return {
        "gaugeAxis": [
            {
                "properties": {
                    "fontSize": _lit("10L")
                }
            }
        ]
    }


def _slicer_objects():
    """Slicer formatting: clean dropdown-style look."""
    return {}


# ── Core helpers ───────────────────────────────────────────────────────────

def uid(seed):
    return hashlib.md5(seed.encode()).hexdigest()[:20]

def measure_field(table, measure):
    return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": table}}, "Property": measure}},
            "queryRef": f"{table}.{measure}", "nativeQueryRef": measure}

def column_field(table, column):
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": column}},
            "queryRef": f"{table}.{column}", "nativeQueryRef": column}

def make_visual(name, x, y, w, h, vtype, query_state=None, objects=None, visual_container_objects=None, z=1000, how_created=None):
    v = {"$schema": SCHEMA_VISUAL, "name": uid(name),
         "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": 0},
         "visual": {"visualType": vtype, "drillFilterOtherVisuals": True}}
    if query_state:
        v["visual"]["query"] = {"queryState": query_state}
    if objects:
        v["visual"]["objects"] = objects
    if visual_container_objects:
        v["visual"]["visualContainerObjects"] = visual_container_objects
    if how_created:
        v["howCreated"] = how_created
    return v

def write_visual(page_dir, visual_json):
    vdir = os.path.join(page_dir, "visuals", visual_json["name"])
    os.makedirs(vdir, exist_ok=True)
    with open(os.path.join(vdir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(visual_json, f, indent=2, ensure_ascii=False)

def write_page(page_id, display_name, visuals):
    page_dir = os.path.join(BASE, page_id)
    visuals_dir = os.path.join(page_dir, "visuals")
    if os.path.exists(visuals_dir):
        shutil.rmtree(visuals_dir)
    os.makedirs(visuals_dir, exist_ok=True)
    with open(os.path.join(page_dir, "page.json"), "w", encoding="utf-8") as f:
        json.dump({"$schema": SCHEMA_PAGE, "name": page_id, "displayName": display_name,
                    "displayOption": "FitToPage", "height": 720, "width": 1280}, f, indent=2)
    for v in visuals:
        write_visual(page_dir, v)


# ── Visual builder functions (same signatures, now with formatting) ────────

def make_card(name, x, y, w, h, table, measure):
    return make_visual(name, x, y, w, h, "cardVisual",
        {"Data": {"projections": [measure_field(table, measure)]}},
        objects=_card_objects())

def make_slicer(name, x, y, w, h, table, column):
    return make_visual(name, x, y, w, h, "slicer",
        {"Values": {"projections": [column_field(table, column)]}},
        objects=_slicer_objects())

def make_clustered_bar(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_clustered_column(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_line_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, val2_table=None, val2_measure=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Y": {"projections": [measure_field(val_table, val_measure)]}}
    if val2_table and val2_measure:
        qs["Y"]["projections"].append(measure_field(val2_table, val2_measure))
    return make_visual(name, x, y, w, h, "lineChart", qs,
        objects=_line_chart_objects())

def make_area_chart(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "areaChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_line_chart_objects())

def make_donut(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "donutChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_pie(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "pieChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_table(name, x, y, w, h, fields_list):
    projections = [measure_field(t, c) if m else column_field(t, c) for t, c, m in fields_list]
    return make_visual(name, x, y, w, h, "tableEx",
        {"Values": {"projections": projections}},
        objects=_table_objects())

def make_matrix(name, x, y, w, h, row_fields, col_fields, val_fields):
    rows = [column_field(t, c) for t, c in row_fields]
    cols = [column_field(t, c) for t, c in col_fields] if col_fields else []
    vals = [measure_field(t, m) for t, m in val_fields]
    qs = {"Rows": {"projections": rows}, "Values": {"projections": vals}}
    if cols:
        qs["Columns"] = {"projections": cols}
    return make_visual(name, x, y, w, h, "pivotTable", qs,
        objects=_matrix_objects())

def make_filled_map(name, x, y, w, h, loc_table, loc_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "filledMap",
        {"Category": {"projections": [column_field(loc_table, loc_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}})

def make_map(name, x, y, w, h, cat_table, cat_col, lat_table, lat_col, lng_table, lng_col, size_table, size_measure):
    return make_visual(name, x, y, w, h, "map",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [column_field(lat_table, lat_col)]},
         "X": {"projections": [column_field(lng_table, lng_col)]},
         "Size": {"projections": [measure_field(size_table, size_measure)]}})

def make_treemap(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, group_table=None, group_col=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Values": {"projections": [measure_field(val_table, val_measure)]}}
    if group_table and group_col:
        qs["Group"] = {"projections": [column_field(group_table, group_col)]}
    return make_visual(name, x, y, w, h, "treemap", qs)

def make_gauge(name, x, y, w, h, val_table, val_measure, target_table=None, target_measure=None, min_table=None, min_measure=None, max_table=None, max_measure=None):
    qs = {"Y": {"projections": [measure_field(val_table, val_measure)]}}
    if target_table and target_measure:
        qs["TargetValue"] = {"projections": [measure_field(target_table, target_measure)]}
    if min_table and min_measure:
        qs["MinValue"] = {"projections": [measure_field(min_table, min_measure)]}
    if max_table and max_measure:
        qs["MaxValue"] = {"projections": [measure_field(max_table, max_measure)]}
    return make_visual(name, x, y, w, h, "gauge", qs,
        objects=_gauge_objects())

def make_waterfall(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "waterfallChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_funnel(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "funnel",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'OutsideEnd'"))

def make_scatter(name, x, y, w, h, detail_table, detail_col, x_table, x_measure, y_table, y_measure, size_table=None, size_measure=None):
    qs = {"Category": {"projections": [column_field(detail_table, detail_col)]},
          "X": {"projections": [measure_field(x_table, x_measure)]},
          "Y": {"projections": [measure_field(y_table, y_measure)]}}
    if size_table and size_measure:
        qs["Size"] = {"projections": [measure_field(size_table, size_measure)]}
    return make_visual(name, x, y, w, h, "scatterChart", qs)

def make_ribbon(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "ribbonChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())

def make_stacked_column(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())

def make_stacked_bar(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())

def make_hundred_pct_stacked_bar(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "hundredPercentStackedBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())

def make_hundred_pct_stacked_column(name, x, y, w, h, cat_table, cat_col, series_table, series_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "hundredPercentStackedColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Series": {"projections": [column_field(series_table, series_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects())


# ── New visual types: title bars, buttons, conditional formatting ──────────

def make_title_bar(name, x, y, w, h, text, bg_color="#1E293B"):
    """Dashboard title bar — a styled text box with colored background."""
    return make_visual(name, x, y, w, h, "textbox",
        objects={
            "general": [
                {
                    "properties": {
                        "paragraphs": [
                            {
                                "textRuns": [
                                    {
                                        "value": text,
                                        "textStyle": {
                                            "fontFamily": "Segoe UI Semibold",
                                            "fontSize": "18px",
                                            "color": "#FFFFFF"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        },
        visual_container_objects={
            "background": [
                {
                    "properties": {
                        "show": _lit("true"),
                        "color": _solid(bg_color),
                        "transparency": _lit("0D")
                    }
                }
            ],
            "visualHeader": [
                {
                    "properties": {
                        "show": _lit("false")
                    }
                }
            ]
        },
        z=9000)


def make_button(name, x, y, w, h, text):
    """Navigation button — styled action button with text.
    Page navigation must be configured manually in Power BI Desktop
    (Format > Action > Page navigation).
    """
    obj = {
        "icon": [
            {
                "properties": {
                    "shapeType": _lit("'blank'")
                },
                "selector": {"id": "default"}
            },
            {
                "properties": {
                    "show": _lit("false")
                }
            }
        ],
        "text": [
            {
                "properties": {
                    "show": _lit("true")
                }
            },
            {
                "properties": {
                    "text": _lit(f"'{text}'"),
                    "horizontalAlignment": _lit("'center'")
                },
                "selector": {"id": "default"}
            }
        ]
    }
    return make_visual(name, x, y, w, h, "actionButton",
        objects=obj,
        z=8000,
        how_created="InsertVisualButton")


def _gradient_fill(measure_table, measure_name):
    """Build a conditional formatting gradient fill rule for bar/column chart data points."""
    return {
        "dataPoint": [
            {
                "properties": {
                    "fill": {
                        "solid": {
                            "color": {
                                "expr": {
                                    "FillRule": {
                                        "Input": {
                                            "Measure": {
                                                "Expression": {
                                                    "SourceRef": {
                                                        "Entity": measure_table
                                                    }
                                                },
                                                "Property": measure_name
                                            }
                                        },
                                        "FillRule": {
                                            "linearGradient2": {
                                                "min": {
                                                    "color": {
                                                        "Literal": {
                                                            "Value": "'minColor'"
                                                        }
                                                    }
                                                },
                                                "max": {
                                                    "color": {
                                                        "Literal": {
                                                            "Value": "'maxColor'"
                                                        }
                                                    }
                                                },
                                                "nullColoringStrategy": {
                                                    "strategy": {
                                                        "Literal": {
                                                            "Value": "'asZero'"
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "selector": {
                    "data": [
                        {
                            "dataViewWildcard": {
                                "matchingOption": 1
                            }
                        }
                    ]
                }
            }
        ]
    }


def make_clustered_bar_gradient(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    """Clustered bar chart with conditional formatting — bars colored by a min/max gradient."""
    base_objects = _chart_objects(show_labels=True, label_position="'OutsideEnd'")
    gradient_objects = _gradient_fill(val_table, val_measure)
    base_objects.update(gradient_objects)
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=base_objects)


def make_clustered_column_gradient(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    """Clustered column chart with conditional formatting — columns colored by a min/max gradient."""
    base_objects = _chart_objects(show_labels=True, label_position="'OutsideEnd'")
    gradient_objects = _gradient_fill(val_table, val_measure)
    base_objects.update(gradient_objects)
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=base_objects)


def make_r_visual(name, x, y, w, h, fields_list, r_script):
    """R script visual — embeds R code with data field bindings.
    fields_list: [(table, col_or_measure, is_measure_bool), ...]
    r_script: string of R code (will be escaped into PBIR literal format)
    """
    projections = [measure_field(t, c) if m else column_field(t, c) for t, c, m in fields_list]
    escaped = r_script.replace("'", "\\'")
    objects = {
        "script": [
            {
                "properties": {
                    "source": _lit(f"'{escaped}'"),
                    "provider": _lit("'R'")
                }
            }
        ]
    }
    return make_visual(name, x, y, w, h, "scriptVisual",
        {"Values": {"projections": projections}},
        objects=objects)


# ===== PAGE 1: Supply Chain KPIs =====
p1_id = uid("sc_page1_kpis")
p1 = [
    make_title_bar("sc1_title", 0, 0, 1280, 50, "Supply Chain Dashboard"),
    make_card("sc1_orders", 20, 60, 300, 140, "_Measures", "Total Orders"),
    make_card("sc1_value", 340, 60, 300, 140, "_Measures", "Total Order Value"),
    make_card("sc1_otd", 660, 60, 300, 140, "_Measures", "On Time Delivery Rate"),
    make_slicer("sc1_year", 980, 60, 270, 140, "Calendar", "Year"),
    make_line_chart("sc1_value_trend", 20, 220, 610, 280, "Calendar", "Year_Month", "_Measures", "Total Order Value", "_Measures", "Order Value PY"),
    make_donut("sc1_wh_donut", 650, 220, 600, 280, "DimWarehouse", "warehouse_name", "_Measures", "Total Quantity Ordered"),
    make_area_chart("sc1_otd_area", 20, 520, 1230, 160, "Calendar", "Year_Month", "_Measures", "On Time Delivery Rate"),
    make_button("sc1_btn_supplier", 1100, 670, 150, 40, "Suppliers"),
]

# ===== PAGE 2: Supplier Scorecard =====
p2_id = uid("sc_page2_supplier")
p2 = [
    make_card("sc2_suppliers", 20, 10, 230, 140, "_Measures", "Unique Suppliers Used"),
    make_card("sc2_reliability", 265, 10, 230, 140, "_Measures", "Supplier Avg Reliability"),
    make_card("sc2_variance", 510, 10, 230, 140, "_Measures", "Avg Lead Time Variance"),
    make_card("sc2_otd_change", 755, 10, 230, 140, "_Measures", "On Time Rate Change"),
    make_slicer("sc2_country", 1000, 10, 250, 140, "DimSupplier", "country"),
    make_clustered_bar_gradient("sc2_otd_bar", 20, 170, 610, 310, "DimSupplier", "supplier_name", "_Measures", "On Time Delivery Rate"),
    make_clustered_bar("sc2_value_bar", 650, 170, 600, 310, "DimSupplier", "supplier_name", "_Measures", "Total Order Value"),
    make_table("sc2_table", 20, 500, 1230, 160, [
        ("DimSupplier", "supplier_name", False),
        ("DimSupplier", "country", False),
        ("DimSupplier", "lead_time_days", False),
        ("DimSupplier", "reliability_rating", False),
        ("_Measures", "Total Orders", True),
        ("_Measures", "On Time Delivery Rate", True),
        ("_Measures", "Avg Lead Time Days", True),
        ("_Measures", "Avg Lead Time Variance", True),
        ("_Measures", "Total Order Value", True),
    ]),
    make_button("sc2_btn_back", 20, 670, 100, 40, "Back"),
    make_button("sc2_btn_inventory", 1100, 670, 150, 40, "Inventory"),
]

# ===== PAGE 3: Inventory Health =====
p3_id = uid("sc_page3_inventory")
p3 = [
    make_card("sc3_onhand", 20, 10, 230, 140, "_Measures", "Latest Inventory On Hand"),
    make_card("sc3_avail", 265, 10, 230, 140, "_Measures", "Available Inventory"),
    make_card("sc3_stockout", 510, 10, 230, 140, "_Measures", "Stockout Rate"),
    make_card("sc3_dos", 755, 10, 230, 140, "_Measures", "Days of Supply"),
    make_slicer("sc3_cat", 1000, 10, 250, 140, "DimProduct", "category"),
    make_clustered_bar("sc3_inv_by_wh", 20, 170, 610, 310, "DimWarehouse", "warehouse_name", "_Measures", "Latest Inventory On Hand"),
    make_clustered_column_gradient("sc3_stockout_bar", 650, 170, 600, 310, "DimProduct", "category", "_Measures", "Stockout Count"),
    make_matrix("sc3_matrix", 20, 500, 1230, 160,
        [("DimWarehouse", "warehouse_name")], [],
        [("_Measures", "Latest Inventory On Hand"), ("_Measures", "Available Inventory"),
         ("_Measures", "Warehouse Utilization"), ("_Measures", "Stockout Count"),
         ("_Measures", "Stockout Rate"), ("_Measures", "Below Reorder Point"),
         ("_Measures", "Inventory Turnover")]),
    make_button("sc3_btn_back", 20, 670, 100, 40, "Back"),
    make_button("sc3_btn_map", 1100, 670, 150, 40, "Logistics"),
]

# ===== PAGE 4: Global Logistics Map =====
p4_id = uid("sc_page4_map")
p4 = [
    make_card("sc4_shipments", 20, 10, 295, 60, "_Measures", "Route Shipment Count"),
    make_card("sc4_transit", 330, 10, 295, 60, "_Measures", "Route Avg Transit Days"),
    make_card("sc4_ontime", 640, 10, 295, 60, "_Measures", "Route On Time Pct"),
    make_card("sc4_cost", 950, 10, 295, 60, "_Measures", "Route Total Cost"),
    make_treemap("sc4_supplier_treemap", 20, 80, 420, 350, "DimSupplier", "city", "_Measures", "Total Orders", "DimSupplier", "country"),
    make_filled_map("sc4_supplier_map", 460, 80, 790, 350, "DimSupplier", "country", "_Measures", "Total Orders"),
    make_table("sc4_table", 20, 440, 1230, 220, [
        ("FactShipmentRoutes", "supplier_name", False),
        ("FactShipmentRoutes", "supplier_country", False),
        ("FactShipmentRoutes", "warehouse_name", False),
        ("FactShipmentRoutes", "warehouse_country", False),
        ("FactShipmentRoutes", "total_shipments", False),
        ("FactShipmentRoutes", "avg_transit_days", False),
        ("FactShipmentRoutes", "on_time_pct", False),
        ("FactShipmentRoutes", "total_cost", False),
    ]),
    make_button("sc4_btn_back", 20, 670, 100, 40, "Back"),
    make_button("sc4_btn_wh", 1100, 670, 150, 40, "Warehouses"),
]

# ===== PAGE 5: Warehouse Comparison =====
p5_id = uid("sc_page5_warehouse")
p5 = [
    make_card("sc5_orders", 20, 10, 300, 140, "_Measures", "Total Orders"),
    make_card("sc5_value", 340, 10, 300, 140, "_Measures", "Total Order Value"),
    make_card("sc5_util", 660, 10, 300, 140, "_Measures", "Warehouse Utilization"),
    make_slicer("sc5_wh", 980, 10, 270, 140, "DimWarehouse", "warehouse_name"),
    make_clustered_bar("sc5_cat_bar", 20, 170, 610, 310, "DimProduct", "category", "_Measures", "Total Quantity Ordered"),
    make_donut("sc5_sup_donut", 650, 170, 600, 310, "DimSupplier", "supplier_name", "_Measures", "Total Orders"),
    make_table("sc5_table", 20, 500, 1230, 160, [
        ("DimProduct", "product_name", False),
        ("DimProduct", "category", False),
        ("_Measures", "Total Quantity Ordered", True),
        ("_Measures", "Latest Inventory On Hand", True),
        ("_Measures", "Available Inventory", True),
        ("_Measures", "Stockout Count", True),
        ("_Measures", "Below Reorder Point", True),
    ]),
    make_button("sc5_btn_back", 20, 670, 100, 40, "Back"),
    make_button("sc5_btn_adv", 1100, 670, 150, 40, "Analytics"),
]

# ===== PAGE 6: Advanced Analytics =====
p6_id = uid("sc_page6_advanced")
p6 = [
    # Gauge: OTD Rate (value vs target)
    make_gauge("sc6_otd_gauge", 20, 10, 300, 220, "_Measures", "On Time Delivery Rate"),
    # Gauge: Warehouse Utilization
    make_gauge("sc6_util_gauge", 340, 10, 300, 220, "_Measures", "Warehouse Utilization"),
    # Gauge: Stockout Rate
    make_gauge("sc6_stockout_gauge", 660, 10, 300, 220, "_Measures", "Stockout Rate"),
    make_slicer("sc6_year", 980, 10, 270, 100, "Calendar", "Year"),
    # Scatter: Suppliers — Lead Time vs OTD Rate, sized by Order Value
    make_scatter("sc6_scatter", 20, 250, 620, 300,
        "DimSupplier", "supplier_name",
        "_Measures", "Avg Lead Time Days",
        "_Measures", "On Time Delivery Rate",
        "_Measures", "Total Order Value"),
    # Waterfall: Order Value by Category (shows cumulative contribution)
    make_waterfall("sc6_waterfall", 660, 250, 590, 300,
        "DimProduct", "category", "_Measures", "Total Order Value"),
    # Funnel: Orders by Product Category (pipeline view)
    make_funnel("sc6_funnel", 980, 120, 270, 200,
        "DimProduct", "category", "_Measures", "Total Orders"),
    # Ribbon: Category rank changes over time
    make_ribbon("sc6_ribbon", 20, 560, 940, 140,
        "Calendar", "Year_Month", "DimProduct", "category", "_Measures", "Total Order Value"),
    make_button("sc6_btn_back", 20, 670, 100, 40, "Back"),
    make_button("sc6_btn_showcase", 1100, 670, 150, 40, "Showcase"),
]

# ===== PAGE 7: Visual Showcase =====
p7_id = uid("sc_page7_showcase")
p7 = [
    # Stacked Column: Order Value by Month, stacked by Category
    make_stacked_column("sc7_stacked_col", 20, 10, 400, 280,
        "Calendar", "Year_Month", "DimProduct", "category", "_Measures", "Total Order Value"),
    # Stacked Bar: Orders by Supplier, stacked by Category
    make_stacked_bar("sc7_stacked_bar", 440, 10, 400, 280,
        "DimSupplier", "supplier_name", "DimProduct", "category", "_Measures", "Total Orders"),
    # Pie Chart: Order Value by Warehouse
    make_pie("sc7_pie", 860, 10, 390, 280,
        "DimWarehouse", "warehouse_name", "_Measures", "Total Order Value"),
    # 100% Stacked Column: Order mix by Month
    make_hundred_pct_stacked_column("sc7_100col", 20, 310, 400, 280,
        "Calendar", "Year_Month", "DimProduct", "category", "_Measures", "Total Quantity Ordered"),
    # 100% Stacked Bar: Supplier share by Category
    make_hundred_pct_stacked_bar("sc7_100bar", 440, 310, 400, 280,
        "DimProduct", "category", "DimSupplier", "supplier_name", "_Measures", "Total Order Value"),
    # Clustered Column: Monthly quantity comparison
    make_clustered_column("sc7_clust_col", 860, 310, 390, 280,
        "Calendar", "Year_Month", "_Measures", "Total Quantity Ordered"),
    # Slicer at bottom
    make_slicer("sc7_year", 20, 610, 200, 90, "Calendar", "Year"),
    make_slicer("sc7_cat", 240, 610, 200, 90, "DimProduct", "category"),
    make_button("sc7_btn_back", 1100, 670, 150, 40, "Overview"),
]

# Remove old default page
old_page = os.path.join(BASE, "f198b33e9cfe0eb15121")
if os.path.exists(old_page):
    shutil.rmtree(old_page)

# Write all pages
write_page(p1_id, "Supply Chain KPIs", p1)
write_page(p2_id, "Supplier Scorecard", p2)
write_page(p3_id, "Inventory Health", p3)
write_page(p4_id, "Global Logistics Map", p4)
write_page(p5_id, "Warehouse Comparison", p5)
write_page(p6_id, "Advanced Analytics", p6)
write_page(p7_id, "Visual Showcase", p7)

# Update pages.json
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, p3_id, p4_id, p5_id, p6_id, p7_id],
               "activePageName": p1_id}, f, indent=2)

print(f"Page 1 (Supply Chain KPIs): {p1_id} - {len(p1)} visuals")
print(f"Page 2 (Supplier Scorecard): {p2_id} - {len(p2)} visuals")
print(f"Page 3 (Inventory Health): {p3_id} - {len(p3)} visuals")
print(f"Page 4 (Global Logistics Map): {p4_id} - {len(p4)} visuals")
print(f"Page 5 (Warehouse Comparison): {p5_id} - {len(p5)} visuals")
print(f"Page 6 (Advanced Analytics): {p6_id} - {len(p6)} visuals")
print(f"Page 7 (Visual Showcase): {p7_id} - {len(p7)} visuals")
print("Done!")
