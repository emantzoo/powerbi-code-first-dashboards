"""
PBIR Visual Helper Functions — with built-in formatting defaults.

Drop-in replacement for the unformatted versions. Same function signatures,
same call sites — but every visual now includes professional formatting
in the `objects` property of the visual.json.
"""

import json, os, hashlib, shutil

# ── Path and schema constants ──────────────────────────────────────────────
BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\ecommerce\eCommerce_dashb.Report\definition\pages"

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


# ===== PAGE 1: Executive Overview =====
p1_id = uid("ec_p1_overview")
p1 = [
    make_title_bar("ec1_title", 0, 0, 1280, 50, "E-Commerce Dashboard"),
    make_card("ec1_rev", 20, 60, 295, 140, "_Measures", "Total Revenue"),
    make_card("ec1_profit", 330, 60, 295, 140, "_Measures", "Total Profit"),
    make_card("ec1_margin", 640, 60, 295, 140, "_Measures", "Profit Margin"),
    make_slicer("ec1_year", 950, 60, 300, 140, "Calendar", "Year"),
    make_clustered_bar("ec1_cat", 20, 220, 400, 280, "DimProduct", "category", "_Measures", "Total Revenue"),
    make_line_chart("ec1_trend", 440, 220, 400, 280, "Calendar", "Year_Month", "_Measures", "Total Revenue"),
    make_donut("ec1_channel", 860, 220, 390, 280, "DimStore", "channel", "_Measures", "Total Revenue"),
    make_area_chart("ec1_profit_area", 20, 520, 1230, 160, "Calendar", "Year_Month", "_Measures", "Total Profit"),
    make_button("ec1_btn_products", 1100, 670, 150, 40, "Products"),
]

# ===== PAGE 2: Product Performance =====
p2_id = uid("ec_p2_product")
p2 = [
    make_card("ec2_rev", 20, 10, 230, 140, "_Measures", "Total Revenue"),
    make_card("ec2_aov", 265, 10, 230, 140, "_Measures", "Avg Order Value"),
    make_card("ec2_qty", 510, 10, 230, 140, "_Measures", "Total Quantity"),
    make_card("ec2_rr", 755, 10, 230, 140, "_Measures", "Return Rate"),
    make_slicer("ec2_cat", 1000, 10, 250, 140, "DimProduct", "category"),
    make_clustered_bar_gradient("ec2_subcat", 20, 170, 610, 310, "DimProduct", "subcategory", "_Measures", "Total Revenue"),
    make_clustered_bar("ec2_brand", 650, 170, 600, 310, "DimProduct", "brand", "_Measures", "Total Profit"),
    make_table("ec2_tbl", 20, 500, 1230, 180, [
        ("DimProduct", "category", False),
        ("DimProduct", "subcategory", False),
        ("DimProduct", "brand", False),
        ("_Measures", "Total Revenue", True),
        ("_Measures", "Total Profit", True),
        ("_Measures", "Profit Margin", True),
        ("_Measures", "Total Quantity", True),
        ("_Measures", "Return Rate", True),
    ]),
    make_button("ec2_btn_back", 20, 670, 100, 40, "Back"),
    make_button("ec2_btn_customers", 1100, 670, 150, 40, "Customers"),
]

# ===== PAGE 3: Customer & Trends =====
p3_id = uid("ec_p3_customer")
p3 = [
    make_card("ec3_cust", 20, 10, 295, 140, "_Measures", "Total Customers"),
    make_card("ec3_yoy", 330, 10, 295, 140, "_Measures", "Revenue YoY Growth"),
    make_card("ec3_ytd", 640, 10, 295, 140, "_Measures", "Revenue YTD"),
    make_card("ec3_l12m", 950, 10, 295, 140, "_Measures", "Revenue L12M"),
    make_line_chart("ec3_trend", 20, 170, 610, 310, "Calendar", "Year_Month", "_Measures", "Total Revenue", "_Measures", "Revenue PY"),
    make_donut("ec3_seg", 650, 170, 300, 310, "DimCustomer", "segment", "_Measures", "Total Revenue"),
    make_clustered_bar("ec3_country", 970, 170, 280, 310, "DimCustomer", "country", "_Measures", "Total Customers"),
    make_matrix("ec3_matrix", 20, 500, 1230, 180,
        [("DimCustomer", "country")], [("Calendar", "Year")],
        [("_Measures", "Total Revenue"), ("_Measures", "Total Orders")]),
    make_button("ec3_btn_back", 20, 670, 100, 40, "Back"),
    make_button("ec3_btn_returns", 1100, 670, 150, 40, "Returns"),
]

# ===== PAGE 4: Returns Analysis =====
p4_id = uid("ec_p4_returns")
p4 = [
    make_card("ec4_returns", 20, 10, 295, 140, "_Measures", "Total Returns"),
    make_card("ec4_refunds", 330, 10, 295, 140, "_Measures", "Total Refunds"),
    make_card("ec4_rr", 640, 10, 295, 140, "_Measures", "Return Rate"),
    make_card("ec4_net", 950, 10, 295, 140, "_Measures", "Net Revenue"),
    make_clustered_bar("ec4_reason", 20, 170, 400, 310, "FactReturns", "reason_code", "_Measures", "Total Returns"),
    make_line_chart("ec4_trend", 440, 170, 400, 310, "Calendar", "Year_Month", "_Measures", "Returns by Date"),
    make_donut("ec4_cat", 860, 170, 390, 310, "DimProduct", "category", "_Measures", "Total Returns"),
    make_table("ec4_tbl", 20, 500, 1230, 180, [
        ("FactReturns", "reason_code", False),
        ("_Measures", "Total Returns", True),
        ("_Measures", "Total Refunds", True),
        ("_Measures", "Return Rate", True),
    ]),
    make_button("ec4_btn_back", 20, 670, 100, 40, "Back"),
]

# Remove old default page
old_page = os.path.join(BASE, "490f2ef98a69f04305b5")
if os.path.exists(old_page):
    shutil.rmtree(old_page)

# Write all pages
write_page(p1_id, "Executive Overview", p1)
write_page(p2_id, "Product Performance", p2)
write_page(p3_id, "Customer & Trends", p3)
write_page(p4_id, "Returns Analysis", p4)

# Update pages.json
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, p3_id, p4_id],
               "activePageName": p1_id}, f, indent=2)

print(f"Page 1 (Executive Overview): {p1_id} - {len(p1)} visuals")
print(f"Page 2 (Product Performance): {p2_id} - {len(p2)} visuals")
print(f"Page 3 (Customer & Trends): {p3_id} - {len(p3)} visuals")
print(f"Page 4 (Returns Analysis): {p4_id} - {len(p4)} visuals")
print("Done!")
