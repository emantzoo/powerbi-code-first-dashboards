"""
PBIR Visual Helper Functions — with built-in formatting defaults.

PortPulse: Piraeus Port Congestion & Waiting Time Analyzer
4 pages: Port Overview, Trends & Patterns, Vessel Detail, Cost Impact
"""

import json, os, hashlib, shutil

# ── Path and schema constants ──────────────────────────────────────────────
# UPDATE this path to match your saved .pbip project location
BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\portpulse\portpulse_dash.Report\definition\pages"

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

def make_map(name, x, y, w, h, cat_table, cat_col, lat_table, lat_measure, lng_table, lng_measure, size_table, size_measure):
    """Azure bubble map — Category is text label, Lat/Lon/Size are measures."""
    return make_visual(name, x, y, w, h, "map",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(lat_table, lat_measure)]},
         "X": {"projections": [measure_field(lng_table, lng_measure)]},
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
    # Escape single quotes for PBIR literal wrapper; json.dumps handles \n naturally
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


# ===================================================================
# PAGE DEFINITIONS
# ===================================================================

# ===== PAGE 1: Port Overview =====
p1_id = uid("pp_page1_overview")
p1 = [
    make_title_bar("pp1_title", 0, 0, 1280, 50, "PortPulse — Piraeus Port Congestion Monitor", bg_color="#0F2B46"),
    # KPI cards row
    make_card("pp1_waiting", 20, 60, 230, 140, "_Measures", "Waiting Vessels"),
    make_card("pp1_wait_hrs", 265, 60, 230, 140, "_Measures", "Avg Wait Hours"),
    make_card("pp1_congestion", 510, 60, 230, 140, "_Measures", "Congestion Index"),
    make_card("pp1_cost", 755, 60, 230, 140, "_Measures", "Total Waiting Cost USD"),
    # Slicers (right side)
    make_slicer("pp1_slicer_type", 1000, 60, 250, 65, "AIS_Positions", "vessel_type"),
    make_slicer("pp1_slicer_flag", 1000, 135, 250, 65, "AIS_Positions", "flag"),
    # Map — vessel positions (takes up main area)
    make_map("pp1_map", 20, 215, 740, 310,
        "AIS_Positions", "vessel_name",
        "_Measures", "Avg Lat",
        "_Measures", "Avg Lon",
        "_Measures", "Total Positions"),
    # Slicer for Status
    make_slicer("pp1_slicer_status", 780, 215, 200, 65, "AIS_Positions", "Status"),
    # Bar chart — wait time by vessel type
    make_clustered_bar("pp1_wait_by_type", 780, 290, 470, 235, "AIS_Positions", "vessel_type",
        "_Measures", "Avg Wait Hours"),
    # Table at bottom
    make_table("pp1_table", 20, 540, 1230, 140, [
        ("AIS_Positions", "vessel_name", False),
        ("AIS_Positions", "vessel_type", False),
        ("AIS_Positions", "flag", False),
        ("AIS_Positions", "Status", False),
        ("_Measures", "Avg Wait Hours", True),
        ("_Measures", "Congestion Index", True),
    ]),
    # Nav buttons
    make_button("pp1_btn_trends", 920, 670, 110, 40, "Trends"),
    make_button("pp1_btn_vessels", 1040, 670, 110, 40, "Vessels"),
    make_button("pp1_btn_costs", 1160, 670, 100, 40, "Costs"),
]

# ===== PAGE 2: Trends & Patterns =====
p2_id = uid("pp_page2_trends")
p2 = [
    # KPI cards
    make_card("pp2_daily_wait", 20, 10, 300, 140, "_Measures", "Daily Waiting Count"),
    make_card("pp2_7d_avg", 340, 10, 300, 140, "_Measures", "Waiting 7D Avg"),
    make_card("pp2_total_vessels", 660, 10, 300, 140, "_Measures", "Total Vessels"),
    make_slicer("pp2_slicer_type", 980, 10, 270, 140, "AIS_Positions", "vessel_type"),
    # Line chart — congestion trend (date × daily waiting + 7D avg)
    make_line_chart("pp2_trend", 20, 170, 1230, 260, "AIS_Positions", "date",
        "_Measures", "Daily Waiting Count", "_Measures", "Waiting 7D Avg"),
    # Bar chart — wait time by day of week
    make_clustered_bar("pp2_by_dow", 20, 450, 400, 210, "AIS_Positions", "day_of_week",
        "_Measures", "Avg Wait Hours"),
    # Column chart — waiting vessels by hour
    make_clustered_column("pp2_by_hour", 440, 450, 400, 210, "AIS_Positions", "hour",
        "_Measures", "Waiting Vessels"),
    # R visual — congestion forecast (ARIMA)
    # NOTE: Requires R packages: forecast, ggplot2. Falls back to empty if R not configured.
    make_r_visual("pp2_r_forecast", 860, 450, 390, 210,
        [("AIS_Positions", "date", False),
         ("AIS_Positions", "mmsi", False),
         ("AIS_Positions", "Status", False)],
        r"""library(forecast)
library(ggplot2)
dataset$date <- as.Date(dataset$date)
daily <- dataset %>%
  dplyr::group_by(date) %>%
  dplyr::summarise(waiting = dplyr::n_distinct(mmsi[Status == "Waiting"])) %>%
  dplyr::arrange(date)
if (nrow(daily) >= 3) {
  ts_data <- ts(daily$waiting, frequency = 7)
  fit <- auto.arima(ts_data)
  fc <- forecast(fit, h = 3)
  fc_df <- data.frame(
    date = seq(max(daily$date) + 1, by = "day", length.out = 3),
    forecast = as.numeric(fc$mean),
    lower = as.numeric(fc$lower[,2]),
    upper = as.numeric(fc$upper[,2])
  )
  p <- ggplot() +
    geom_line(data = daily, aes(x = date, y = waiting), color = "#2c3e50", linewidth = 1) +
    geom_ribbon(data = fc_df, aes(x = date, ymin = lower, ymax = upper), fill = "#3498db", alpha = 0.2) +
    geom_line(data = fc_df, aes(x = date, y = forecast), color = "#3498db", linewidth = 1, linetype = "dashed") +
    labs(title = "Congestion Forecast (3-day)", x = "", y = "Waiting Vessels") +
    theme_minimal()
  print(p)
}
"""),
    # Nav buttons
    make_button("pp2_btn_back", 20, 670, 100, 40, "Back"),
    make_button("pp2_btn_vessels", 1040, 670, 110, 40, "Vessels"),
    make_button("pp2_btn_costs", 1160, 670, 100, 40, "Costs"),
]

# ===== PAGE 3: Vessel Detail =====
p3_id = uid("pp_page3_vessels")
p3 = [
    # KPI cards
    make_card("pp3_total", 20, 10, 300, 140, "_Measures", "Total Vessels"),
    make_card("pp3_avg_speed", 340, 10, 300, 140, "_Measures", "Avg Speed"),
    make_slicer("pp3_slicer_type", 660, 10, 280, 140, "AIS_Positions", "vessel_type"),
    make_slicer("pp3_slicer_status", 960, 10, 280, 140, "AIS_Positions", "Status"),
    # Detail table — full vessel listing
    make_table("pp3_table", 20, 170, 1230, 260, [
        ("AIS_Positions", "mmsi", False),
        ("AIS_Positions", "vessel_name", False),
        ("AIS_Positions", "flag", False),
        ("AIS_Positions", "vessel_type", False),
        ("AIS_Positions", "Status", False),
        ("AIS_Positions", "Zone", False),
        ("_Measures", "Avg Speed", True),
        ("_Measures", "Avg Wait Hours", True),
    ]),
    # R visual — anomaly detection (Isolation Forest computed inline)
    make_r_visual("pp3_r_anomaly", 20, 450, 600, 230,
        [("AIS_Positions", "lon", False),
         ("AIS_Positions", "lat", False),
         ("AIS_Positions", "speed_knots", False),
         ("AIS_Positions", "hour", False)],
        r"""library(ggplot2)
library(solitude)
features <- dataset[, c("speed_knots", "lat", "lon", "hour")]
features[] <- lapply(features, as.numeric)
iso <- isolationForest$new(sample_size = min(256, nrow(features)), num_trees = 100)
iso$fit(features)
scores <- iso$predict(features)
dataset$anomaly <- ifelse(scores$anomaly_score >= quantile(scores$anomaly_score, 0.90),
                          "Anomaly", "Normal")
p <- ggplot(dataset, aes(x = lon, y = lat, color = anomaly)) +
  geom_point(aes(size = speed_knots), alpha = 0.6) +
  scale_color_manual(values = c("Normal" = "#95a5a6", "Anomaly" = "#e74c3c")) +
  labs(title = "Anomaly Detection (Isolation Forest)",
       x = "Longitude", y = "Latitude",
       color = "Status", size = "Speed (kn)") +
  theme_minimal() +
  coord_fixed(ratio = 1.3)
print(p)
"""),
    # R visual — vessel behaviour clusters (K-means computed inline)
    make_r_visual("pp3_r_clusters", 640, 450, 610, 230,
        [("AIS_Positions", "mmsi", False),
         ("AIS_Positions", "vessel_type", False),
         ("AIS_Positions", "speed_knots", False),
         ("AIS_Positions", "lat", False)],
        r"""library(ggplot2)
library(dplyr)
vessel_summary <- dataset %>%
  group_by(mmsi, vessel_type) %>%
  summarise(avg_speed = mean(speed_knots, na.rm = TRUE),
            pct_slow = mean(speed_knots < 1.0, na.rm = TRUE),
            avg_lat = mean(lat, na.rm = TRUE),
            n_pos = n(), .groups = "drop")
set.seed(42)
cf <- scale(vessel_summary[, c("avg_speed", "pct_slow", "avg_lat")])
km <- kmeans(cf, centers = 4, nstart = 25)
vessel_summary$cluster <- factor(km$cluster)
p <- ggplot(vessel_summary, aes(x = avg_speed, y = pct_slow,
                                 color = cluster, size = n_pos)) +
  geom_point(alpha = 0.7) +
  scale_color_brewer(palette = "Set1") +
  labs(title = "Vessel Behaviour Clusters (K-means)",
       x = "Avg Speed (kn)", y = "% Time Slow (<1 kn)",
       color = "Cluster", size = "Positions") +
  theme_minimal()
print(p)
"""),
    # Nav buttons
    make_button("pp3_btn_back", 20, 670, 100, 40, "Back"),
    make_button("pp3_btn_trends", 920, 670, 110, 40, "Trends"),
    make_button("pp3_btn_costs", 1160, 670, 100, 40, "Costs"),
]

# ===== PAGE 4: Cost Impact =====
p4_id = uid("pp_page4_costs")
p4 = [
    # KPI cards
    make_card("pp4_total_cost", 20, 10, 300, 140, "_Measures", "Total Waiting Cost USD"),
    make_card("pp4_waiting", 340, 10, 300, 140, "_Measures", "Waiting Vessels"),
    make_card("pp4_wait_hrs", 660, 10, 300, 140, "_Measures", "Avg Wait Hours"),
    make_slicer("pp4_slicer_type", 980, 10, 270, 140, "AIS_Positions", "vessel_type"),
    # Donut — cost breakdown by vessel type
    make_donut("pp4_donut", 20, 170, 400, 310, "AIS_Positions", "vessel_type",
        "_Measures", "Total Waiting Cost USD"),
    # Gradient bar — cost per vessel (top waiters)
    make_clustered_bar_gradient("pp4_cost_bar", 440, 170, 810, 310, "AIS_Positions", "vessel_name",
        "_Measures", "Total Waiting Cost USD"),
    # Cost detail table
    make_table("pp4_table", 20, 500, 1230, 180, [
        ("AIS_Positions", "mmsi", False),
        ("AIS_Positions", "vessel_name", False),
        ("AIS_Positions", "vessel_type", False),
        ("AIS_Positions", "flag", False),
        ("_Measures", "Avg Wait Hours", True),
        ("_Measures", "Total Waiting Cost USD", True),
    ]),
    # Nav buttons
    make_button("pp4_btn_back", 20, 670, 100, 40, "Back"),
    make_button("pp4_btn_trends", 920, 670, 110, 40, "Trends"),
    make_button("pp4_btn_vessels", 1040, 670, 110, 40, "Vessels"),
]


# ===================================================================
# WRITE ALL PAGES
# ===================================================================

write_page(p1_id, "Port Overview", p1)
write_page(p2_id, "Trends & Patterns", p2)
write_page(p3_id, "Vessel Detail", p3)
write_page(p4_id, "Cost Impact", p4)

# Update pages.json
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, p3_id, p4_id],
               "activePageName": p1_id}, f, indent=2)

print(f"Page 1 (Port Overview): {p1_id} - {len(p1)} visuals")
print(f"Page 2 (Trends & Patterns): {p2_id} - {len(p2)} visuals")
print(f"Page 3 (Vessel Detail): {p3_id} - {len(p3)} visuals")
print(f"Page 4 (Cost Impact): {p4_id} - {len(p4)} visuals")
print("Done!")
print("\nNOTE: R script visuals (anomaly scatter, cluster plot, ARIMA forecast)")
print("must be added manually in Power BI Desktop.")
