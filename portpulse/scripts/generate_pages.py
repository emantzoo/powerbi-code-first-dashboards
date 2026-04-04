"""
PBIR Visual Helper Functions — with built-in formatting defaults.

PortPulse: Piraeus Port Congestion & Waiting Time Analyzer
4 pages: Port Overview, Trends & Patterns, Vessel Detail, Cost Impact
"""

import json, os, hashlib, shutil, base64

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

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

def write_theme(theme_path):
    """Copy a theme JSON into the PBIR project and update report.json to reference it."""
    report_dir = os.path.dirname(BASE)  # .Report/definition/
    report_json_path = os.path.join(report_dir, "report.json")
    if not os.path.exists(report_json_path):
        return
    with open(theme_path, "r", encoding="utf-8") as f:
        theme = json.load(f)
    theme_name = theme.get("name", "CustomTheme")
    # Copy theme into StaticResources
    theme_dest_dir = os.path.join(report_dir, "..", "StaticResources", "SharedResources", "BaseThemes")
    os.makedirs(theme_dest_dir, exist_ok=True)
    dest_file = os.path.join(theme_dest_dir, os.path.basename(theme_path))
    shutil.copy2(theme_path, dest_file)
    # Update report.json
    with open(report_json_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    report["themeCollection"]["baseTheme"] = {
        "name": theme_name,
        "reportVersionAtImport": {"visual": "2.7.0", "report": "3.2.0", "page": "2.3.0"},
        "type": "SharedResources"
    }
    # Update SharedResources package (preserve other packages like RegisteredResources)
    packages = report.get("resourcePackages", [])
    shared_pkg = None
    for pkg in packages:
        if pkg.get("name") == "SharedResources":
            shared_pkg = pkg
            break
    if shared_pkg is None:
        shared_pkg = {"name": "SharedResources", "type": "SharedResources", "items": []}
        packages.append(shared_pkg)
    shared_pkg["items"] = [{"name": theme_name,
                            "path": f"BaseThemes/{os.path.basename(theme_path)}",
                            "type": "BaseTheme"}]
    report["resourcePackages"] = packages
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Theme applied: {theme_name}")


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


def _hex_to_rgb(hex_color):
    """Convert '#RRGGBB' to (R, G, B) tuple."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _alpha_blend(fg_rgb, bg_rgb, alpha):
    """Blend fg over bg with given alpha (0.0-1.0)."""
    return tuple(int(fg * alpha + bg * (1 - alpha)) for fg, bg in zip(fg_rgb, bg_rgb))


def _cluster_visuals(visuals):
    """Extract visual positions and cluster into row groups.
    Returns (rects, group_boxes) where group_boxes are (x, y, w, h) bounding boxes.
    """
    PAD = 10
    HEADER_H = 50
    FOOTER_H = 40
    W, H = 1280, 720
    ROW_GAP = 80

    rects = []
    for v in visuals:
        pos = v.get("position", {})
        x, y, w, h = pos.get("x", 0), pos.get("y", 0), pos.get("width", 0), pos.get("height", 0)
        vtype = v.get("visual", {}).get("visualType", "")
        if vtype in ("textbox", "actionButton"):
            continue
        if w > 0 and h > 0:
            rects.append((x, y, w, h))

    if not rects:
        return rects, []

    sorted_rects = sorted(rects, key=lambda r: r[1])
    clusters = []
    current_cluster = [sorted_rects[0]]
    for rect in sorted_rects[1:]:
        if abs(rect[1] - max(r[1] for r in current_cluster)) <= ROW_GAP:
            current_cluster.append(rect)
        else:
            clusters.append(current_cluster)
            current_cluster = [rect]
    clusters.append(current_cluster)

    group_boxes = []
    for cluster in clusters:
        min_x = max(0, min(r[0] for r in cluster) - PAD)
        min_y = max(HEADER_H + 2, min(r[1] for r in cluster) - PAD)
        max_x = min(W, max(r[0] + r[2] for r in cluster) + PAD)
        max_y = min(H - FOOTER_H - 2, max(r[1] + r[3] for r in cluster) + PAD)
        group_boxes.append((min_x, min_y, max_x - min_x, max_y - min_y))

    return rects, group_boxes


def _get_palette(style="light", colors=None):
    """Return color palette dict for the given style."""
    if style == "dark":
        palette = dict(
            bg="#0F172A", container="#1E293B", border="#334155",
            accent="#60A5FA", header_bg="#1E293B", footer_bg="#1E293B",
            dot_color="#334155", divider="#334155", header_text="#FFFFFF")
    else:
        palette = dict(
            bg="#F1F5F9", container="#FFFFFF", border="#E2E8F0",
            accent="#2563EB", header_bg="#1E293B", footer_bg="#F8FAFC",
            dot_color="#E2E8F0", divider="#CBD5E1", header_text="#FFFFFF")
    if colors:
        palette.update(colors)
    return palette


def make_background(page_name, visuals, style="light", display_name=None, colors=None):
    """Generate a 1280x720 background image (PNG if Pillow available, else SVG).

    Clusters visuals by y-position proximity, draws rounded-rect group containers,
    header bar with page title, footer bar, accent stripes, and subtle grid dots.

    Returns the path to the generated file.
    """
    W, H = 1280, 720
    RADIUS = 12
    HEADER_H = 50
    FOOTER_H = 40
    GRID_SPACING = 40

    palette = _get_palette(style, colors)
    _, group_boxes = _cluster_visuals(visuals)

    bg_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backgrounds")
    os.makedirs(bg_dir, exist_ok=True)

    if HAS_PILLOW:
        # ── Render PNG directly with Pillow ──
        bg_rgb = _hex_to_rgb(palette["bg"])
        img = Image.new("RGB", (W, H), bg_rgb)
        draw = ImageDraw.Draw(img, "RGBA")

        # Grid dots
        dot_rgb = _hex_to_rgb(palette["dot_color"])
        dot_rgba = dot_rgb + (80,)  # ~30% opacity
        for gx in range(GRID_SPACING, W, GRID_SPACING):
            for gy in range(HEADER_H + GRID_SPACING, H - FOOTER_H, GRID_SPACING):
                draw.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=dot_rgba)

        # Header bar
        header_rgb = _hex_to_rgb(palette["header_bg"])
        draw.rectangle([0, 0, W, HEADER_H], fill=header_rgb)

        # Header title text
        if display_name:
            txt_rgb = _hex_to_rgb(palette["header_text"])
            try:
                font = ImageFont.truetype("segoeuib.ttf", 16)
            except OSError:
                try:
                    font = ImageFont.truetype("segoeui.ttf", 16)
                except OSError:
                    font = ImageFont.load_default()
            draw.text((20, 15), display_name, fill=txt_rgb, font=font)

        # Container zones
        container_rgb = _hex_to_rgb(palette["container"])
        border_rgb = _hex_to_rgb(palette["border"])
        accent_rgb = _hex_to_rgb(palette["accent"])
        container_rgba = container_rgb + (153,)  # 0.6 opacity
        for (bx, by, bw, bh) in group_boxes:
            draw.rounded_rectangle(
                [bx, by, bx + bw, by + bh],
                radius=RADIUS, fill=container_rgba, outline=border_rgb, width=1)
            # Accent stripe
            stripe_h = int(min(bh - 2 * RADIUS, bh * 0.6))
            stripe_y = int(by + (bh - stripe_h) / 2)
            accent_rgba = accent_rgb + (204,)  # 0.8 opacity
            draw.rounded_rectangle(
                [bx, stripe_y, bx + 4, stripe_y + stripe_h],
                radius=2, fill=accent_rgba)

        # Section dividers
        divider_rgb = _hex_to_rgb(palette["divider"])
        divider_rgba = divider_rgb + (100,)  # ~0.4 opacity
        sorted_boxes = sorted(group_boxes, key=lambda b: b[1])
        for i in range(len(sorted_boxes) - 1):
            box_bottom = sorted_boxes[i][1] + sorted_boxes[i][3]
            next_box_top = sorted_boxes[i + 1][1]
            if next_box_top - box_bottom > 10:
                div_y = int((box_bottom + next_box_top) / 2)
                # Dashed line (draw segments)
                for dx in range(20, W - 20, 10):
                    draw.line([dx, div_y, dx + 6, div_y], fill=divider_rgba, width=1)

        # Footer bar
        footer_rgb = _hex_to_rgb(palette["footer_bg"])
        footer_rgba = footer_rgb + (128,)  # 0.5 opacity
        draw.rectangle([0, H - FOOTER_H, W, H], fill=footer_rgba)

        png_path = os.path.join(bg_dir, f"{page_name}.png")
        img.save(png_path, "PNG")
        print(f"Background PNG: {png_path}")
        return png_path

    else:
        # ── Fallback: SVG output ──
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            f'  <rect width="{W}" height="{H}" fill="{palette["bg"]}"/>',
            f'  <g opacity="0.5">',
        ]
        for gx in range(GRID_SPACING, W, GRID_SPACING):
            for gy in range(HEADER_H + GRID_SPACING, H - FOOTER_H, GRID_SPACING):
                svg_parts.append(f'    <circle cx="{gx}" cy="{gy}" r="0.8" fill="{palette["dot_color"]}"/>')
        svg_parts.append('  </g>')
        svg_parts.append(f'  <rect x="0" y="0" width="{W}" height="{HEADER_H}" fill="{palette["header_bg"]}"/>')
        if display_name:
            svg_parts.append(
                f'  <text x="20" y="33" font-family="Segoe UI Semibold, sans-serif" '
                f'font-size="16" fill="{palette["header_text"]}">{display_name}</text>')
        for (bx, by, bw, bh) in group_boxes:
            svg_parts.append(
                f'  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" '
                f'rx="{RADIUS}" ry="{RADIUS}" fill="{palette["container"]}" '
                f'stroke="{palette["border"]}" stroke-width="1" opacity="0.6"/>')
            stripe_h = min(bh - 2 * RADIUS, bh * 0.6)
            stripe_y = by + (bh - stripe_h) / 2
            svg_parts.append(
                f'  <rect x="{bx}" y="{stripe_y:.0f}" width="4" height="{stripe_h:.0f}" '
                f'rx="2" ry="2" fill="{palette["accent"]}" opacity="0.8"/>')
        svg_parts.append(
            f'  <rect x="0" y="{H - FOOTER_H}" width="{W}" height="{FOOTER_H}" '
            f'fill="{palette["footer_bg"]}" opacity="0.5"/>')
        svg_parts.append('</svg>')
        svg_path = os.path.join(bg_dir, f"{page_name}.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write('\n'.join(svg_parts))
        print(f"Background SVG (install Pillow for PNG+auto-embed): {svg_path}")
        return svg_path


def write_background(page_id, png_path):
    """Embed a PNG background into a PBIR page: copies to RegisteredResources,
    patches page.json with background image reference, and updates report.json
    with RegisteredResources package entry.
    """
    if not os.path.exists(png_path) or not png_path.endswith(".png"):
        return

    report_dir = os.path.dirname(BASE)  # .Report/definition/
    page_json_path = os.path.join(BASE, page_id, "page.json")
    report_json_path = os.path.join(report_dir, "report.json")

    # Generate a unique resource filename (Power BI style: Picture1<random digits>.png)
    file_hash = hashlib.md5(open(png_path, "rb").read()).hexdigest()[:16]
    resource_name = f"bg_{file_hash}.png"

    # Copy PNG to RegisteredResources
    res_dir = os.path.join(report_dir, "..", "StaticResources", "RegisteredResources")
    os.makedirs(res_dir, exist_ok=True)
    shutil.copy2(png_path, os.path.join(res_dir, resource_name))

    # Patch page.json — add background image object
    with open(page_json_path, "r", encoding="utf-8") as f:
        page = json.load(f)
    page["objects"] = {
        "background": [{
            "properties": {
                "image": {
                    "image": {
                        "name": {"expr": {"Literal": {"Value": f"'{os.path.basename(png_path)}'"}}},
                        "url": {"expr": {"ResourcePackageItem": {
                            "PackageName": "RegisteredResources",
                            "PackageType": 1,
                            "ItemName": resource_name
                        }}},
                        "scaling": {"expr": {"Literal": {"Value": "'Normal'"}}}
                    }
                },
                "transparency": {"expr": {"Literal": {"Value": "0D"}}}
            }
        }],
        "displayArea": [{
            "properties": {
                "verticalAlignment": {"expr": {"Literal": {"Value": "'Top'"}}}
            }
        }]
    }
    with open(page_json_path, "w", encoding="utf-8") as f:
        json.dump(page, f, indent=2, ensure_ascii=False)

    # Patch report.json — ensure RegisteredResources package exists with this image
    with open(report_json_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    packages = report.get("resourcePackages", [])
    # Find or create RegisteredResources package
    reg_pkg = None
    for pkg in packages:
        if pkg.get("name") == "RegisteredResources":
            reg_pkg = pkg
            break
    if reg_pkg is None:
        reg_pkg = {"name": "RegisteredResources", "type": "RegisteredResources", "items": []}
        packages.append(reg_pkg)
    # Add image item if not already present
    existing_names = {item["name"] for item in reg_pkg["items"]}
    if resource_name not in existing_names:
        reg_pkg["items"].append({"name": resource_name, "path": resource_name, "type": "Image"})
    report["resourcePackages"] = packages
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Background embedded: {resource_name} -> page {page_id}")


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
    make_title_bar("pp2_title", 0, 0, 1280, 50, "Trends & Patterns", bg_color="#0F2B46"),
    # KPI cards
    make_card("pp2_daily_wait", 20, 60, 300, 140, "_Measures", "Daily Waiting Count"),
    make_card("pp2_7d_avg", 340, 60, 300, 140, "_Measures", "Waiting 7D Avg"),
    make_card("pp2_total_vessels", 660, 60, 300, 140, "_Measures", "Total Vessels"),
    make_slicer("pp2_slicer_type", 980, 60, 270, 140, "AIS_Positions", "vessel_type"),
    # Line chart — congestion trend (date × daily waiting + 7D avg)
    make_line_chart("pp2_trend", 20, 220, 1230, 260, "AIS_Positions", "date",
        "_Measures", "Daily Waiting Count", "_Measures", "Waiting 7D Avg"),
    # Bar chart — wait time by day of week
    make_clustered_bar("pp2_by_dow", 20, 500, 400, 160, "AIS_Positions", "day_of_week",
        "_Measures", "Avg Wait Hours"),
    # Column chart — waiting vessels by hour
    make_clustered_column("pp2_by_hour", 440, 500, 400, 160, "AIS_Positions", "hour",
        "_Measures", "Waiting Vessels"),
    # R visual — congestion forecast (ARIMA)
    # NOTE: Requires R packages: forecast, ggplot2. Falls back to empty if R not configured.
    make_r_visual("pp2_r_forecast", 860, 500, 390, 160,
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
    make_title_bar("pp3_title", 0, 0, 1280, 50, "Vessel Detail", bg_color="#0F2B46"),
    # KPI cards
    make_card("pp3_total", 20, 60, 300, 140, "_Measures", "Total Vessels"),
    make_card("pp3_avg_speed", 340, 60, 300, 140, "_Measures", "Avg Speed"),
    make_slicer("pp3_slicer_type", 660, 60, 280, 140, "AIS_Positions", "vessel_type"),
    make_slicer("pp3_slicer_status", 960, 60, 280, 140, "AIS_Positions", "Status"),
    # Detail table — full vessel listing
    make_table("pp3_table", 20, 220, 1230, 220, [
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
    make_r_visual("pp3_r_anomaly", 20, 460, 600, 200,
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
    make_r_visual("pp3_r_clusters", 640, 460, 610, 200,
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
    make_title_bar("pp4_title", 0, 0, 1280, 50, "Cost Impact", bg_color="#0F2B46"),
    # KPI cards
    make_card("pp4_total_cost", 20, 60, 300, 140, "_Measures", "Total Waiting Cost USD"),
    make_card("pp4_waiting", 340, 60, 300, 140, "_Measures", "Waiting Vessels"),
    make_card("pp4_wait_hrs", 660, 60, 300, 140, "_Measures", "Avg Wait Hours"),
    make_slicer("pp4_slicer_type", 980, 60, 270, 140, "AIS_Positions", "vessel_type"),
    # Donut — cost breakdown by vessel type
    make_donut("pp4_donut", 20, 220, 400, 260, "AIS_Positions", "vessel_type",
        "_Measures", "Total Waiting Cost USD"),
    # Gradient bar — cost per vessel (top waiters)
    make_clustered_bar_gradient("pp4_cost_bar", 440, 220, 810, 260, "AIS_Positions", "vessel_name",
        "_Measures", "Total Waiting Cost USD"),
    # Cost detail table
    make_table("pp4_table", 20, 500, 1230, 160, [
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

# Generate background images and embed into PBIR pages
for pg_name, pg_id, pg_visuals, pg_title in [
    ("port_overview", p1_id, p1, "Port Overview"),
    ("trends_patterns", p2_id, p2, "Trends & Patterns"),
    ("vessel_detail", p3_id, p3, "Vessel Detail"),
    ("cost_impact", p4_id, p4, "Cost Impact"),
]:
    bg_path = make_background(pg_name, pg_visuals, display_name=pg_title)
    if bg_path and bg_path.endswith(".png"):
        write_background(pg_id, bg_path)

# Update pages.json
with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
    json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, p3_id, p4_id],
               "activePageName": p1_id}, f, indent=2)

# Apply theme — resolve repo root from BASE (pages -> definition -> .Report -> project -> repo)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(BASE))))
THEME_PATH = os.path.join(REPO_ROOT, "themes", "code-first-dashboard.json")
if os.path.exists(THEME_PATH):
    write_theme(THEME_PATH)

print(f"Page 1 (Port Overview): {p1_id} - {len(p1)} visuals")
print(f"Page 2 (Trends & Patterns): {p2_id} - {len(p2)} visuals")
print(f"Page 3 (Vessel Detail): {p3_id} - {len(p3)} visuals")
print(f"Page 4 (Cost Impact): {p4_id} - {len(p4)} visuals")
print("Done!")
