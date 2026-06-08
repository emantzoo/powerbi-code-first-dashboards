"""
PBIR Visual Helper Functions — with built-in formatting defaults.

Market Orders: Order Activity & Surveillance (single trading date)
4 pages: Order Activity Overview, Order Lifecycle & Flow, Surveillance & Anomalies,
         Firm & Instrument Insights

Built against a fully synthetic, single-day order-event dataset
(see data/generate_order_data.py). No real or proprietary data is used.
All visuals are bound to DAX measures / derived columns defined in
MarketOrders_Dashboard_Prompts.md — pure DAX, no R required.
"""

import json, os, hashlib, shutil

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# ── Path and schema constants ──────────────────────────────────────────────
# UPDATE this path to match your saved .pbip project location
BASE = r"C:\Users\emantzouni\Documents\powerbi-code-first-dashboards\market_orders\market_orders_dash.Report\definition\pages"

SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"
SCHEMA_PAGE   = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"

HEADER_COLOR = "#1B2A4A"
TABLE = "OrderEvents"   # name of the loaded fact table


# ── Formatting helpers ─────────────────────────────────────────────────────
def _lit(value):
    return {"expr": {"Literal": {"Value": value}}}

def _solid(hex_color):
    return {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hex_color}'"}}}}}

def _theme_color(color_id, percent=0):
    return {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": color_id, "Percent": percent}}}}}


def _card_objects():
    return {
        "layout": [
            {"properties": {"style": _lit("'Table'"), "orientation": _lit("1D"),
                            "rowCount": _lit("5L"), "contentOrder": _lit("'referenceLabel_callout_image'")}},
            {"properties": {"rectangleRoundedCurve": _lit("8L"), "paddingUniform": _lit("10L"),
                            "backgroundTransparency": _lit("0D")}, "selector": {"id": "default"}}
        ],
        "accentBar": [{"properties": {"show": _lit("true")}, "selector": {"id": "default"}}],
        "shadowCustom": [{"properties": {"show": _lit("true")}, "selector": {"id": "default"}}],
        "shapeCustomRectangle": [{"properties": {"tileShape": _lit("'rectangleRoundedByPixel'")}, "selector": {"id": "default"}}]
    }


def _chart_objects(show_labels=False, label_position="'OutsideEnd'"):
    obj = {
        "categoryAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false")}}],
        "valueAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false"),
                                       "gridlineStyle": _lit("'dashed'"), "gridlineColor": _solid("#E2E8F0")}}]
    }
    if show_labels:
        obj["labels"] = [{"properties": {"show": _lit("true"), "labelPosition": _lit(label_position), "fontSize": _lit("9L")}}]
    return obj


def _line_chart_objects():
    return {
        "categoryAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false")}}],
        "valueAxis": [{"properties": {"fontSize": _lit("9L"), "showAxisTitle": _lit("false"),
                                       "gridlineStyle": _lit("'dashed'"), "gridlineColor": _solid("#E2E8F0")}}],
        "lineStyles": [{"properties": {"strokeWidth": _lit("3L")}}]
    }


def _table_objects():
    return {
        "columnHeaders": [{"properties": {"bold": _lit("true"), "fontSize": _lit("10L"),
                                           "fontColor": _solid("#FFFFFF"), "backColor": _theme_color(0)}}],
        "values": [{"properties": {"fontSize": _lit("10L"), "backColor": _solid("#FFFFFF"),
                                    "backColorAlternate": _solid("#F8FAFC")}}],
        "grid": [{"properties": {"gridHorizontal": _lit("true"), "gridHorizontalColor": _solid("#E2E8F0"),
                                  "gridVertical": _lit("false"), "rowPadding": _lit("4L")}}]
    }


def _matrix_objects():
    return {
        "columnHeaders": [{"properties": {"bold": _lit("true"), "fontSize": _lit("10L"),
                                           "fontColor": _solid("#FFFFFF"), "backColor": _theme_color(0)}}],
        "rowHeaders": [{"properties": {"fontSize": _lit("10L")}}],
        "values": [{"properties": {"fontSize": _lit("10L"), "backColor": _solid("#FFFFFF"),
                                    "backColorAlternate": _solid("#F8FAFC")}}],
        "grid": [{"properties": {"gridHorizontal": _lit("true"), "gridHorizontalColor": _solid("#E2E8F0"),
                                  "gridVertical": _lit("false"), "rowPadding": _lit("4L")}}]
    }


def _gauge_objects():
    return {"gaugeAxis": [{"properties": {"fontSize": _lit("10L")}}]}


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
    report_dir = os.path.dirname(BASE)
    report_json_path = os.path.join(report_dir, "report.json")
    if not os.path.exists(report_json_path):
        return
    with open(theme_path, "r", encoding="utf-8") as f:
        theme = json.load(f)
    theme_name = theme.get("name", "CustomTheme")
    theme_dest_dir = os.path.join(report_dir, "..", "StaticResources", "SharedResources", "BaseThemes")
    os.makedirs(theme_dest_dir, exist_ok=True)
    shutil.copy2(theme_path, os.path.join(theme_dest_dir, os.path.basename(theme_path)))
    with open(report_json_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    report["themeCollection"]["baseTheme"] = {
        "name": theme_name,
        "reportVersionAtImport": {"visual": "2.7.0", "report": "3.2.0", "page": "2.3.0"},
        "type": "SharedResources"
    }
    packages = report.get("resourcePackages", [])
    shared_pkg = next((p for p in packages if p.get("name") == "SharedResources"), None)
    if shared_pkg is None:
        shared_pkg = {"name": "SharedResources", "type": "SharedResources", "items": []}
        packages.append(shared_pkg)
    shared_pkg["items"] = [{"name": theme_name, "path": f"BaseThemes/{os.path.basename(theme_path)}", "type": "BaseTheme"}]
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


# ── Visual builder functions ───────────────────────────────────────────────
def make_card(name, x, y, w, h, table, measure):
    # Use the classic `card` visual (Values role), not the new `cardVisual` (Data role).
    # Hand-authored `cardVisual` JSON renders blank in Power BI Desktop; the classic `card`
    # binds reliably. The cardVisual-only styling (_card_objects: layout/accentBar/etc.) does
    # not apply to the classic card, so it is intentionally omitted.
    return make_visual(name, x, y, w, h, "card",
        {"Values": {"projections": [measure_field(table, measure)]}})

def make_slicer(name, x, y, w, h, table, column):
    return make_visual(name, x, y, w, h, "slicer",
        {"Values": {"projections": [column_field(table, column)]}})

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
    return make_visual(name, x, y, w, h, "lineChart", qs, objects=_line_chart_objects())

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
        {"Values": {"projections": projections}}, objects=_table_objects())

def make_matrix(name, x, y, w, h, row_fields, col_fields, val_fields):
    rows = [column_field(t, c) for t, c in row_fields]
    cols = [column_field(t, c) for t, c in col_fields] if col_fields else []
    vals = [measure_field(t, m) for t, m in val_fields]
    qs = {"Rows": {"projections": rows}, "Values": {"projections": vals}}
    if cols:
        qs["Columns"] = {"projections": cols}
    return make_visual(name, x, y, w, h, "pivotTable", qs, objects=_matrix_objects())

def make_gauge(name, x, y, w, h, val_table, val_measure, target_table=None, target_measure=None, min_table=None, min_measure=None, max_table=None, max_measure=None):
    qs = {"Y": {"projections": [measure_field(val_table, val_measure)]}}
    if target_table and target_measure:
        qs["TargetValue"] = {"projections": [measure_field(target_table, target_measure)]}
    if min_table and min_measure:
        qs["MinValue"] = {"projections": [measure_field(min_table, min_measure)]}
    if max_table and max_measure:
        qs["MaxValue"] = {"projections": [measure_field(max_table, max_measure)]}
    return make_visual(name, x, y, w, h, "gauge", qs, objects=_gauge_objects())

def make_scatter(name, x, y, w, h, detail_table, detail_col, x_table, x_measure, y_table, y_measure, size_table=None, size_measure=None):
    qs = {"Category": {"projections": [column_field(detail_table, detail_col)]},
          "X": {"projections": [measure_field(x_table, x_measure)]},
          "Y": {"projections": [measure_field(y_table, y_measure)]}}
    if size_table and size_measure:
        qs["Size"] = {"projections": [measure_field(size_table, size_measure)]}
    return make_visual(name, x, y, w, h, "scatterChart", qs)

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


def make_funnel(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "funnel",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}},
        objects=_chart_objects(show_labels=True, label_position="'InsideCenter'"))

def make_treemap(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, group_table=None, group_col=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Values": {"projections": [measure_field(val_table, val_measure)]}}
    if group_table and group_col:
        qs["Group"] = {"projections": [column_field(group_table, group_col)]}
    return make_visual(name, x, y, w, h, "treemap", qs)


def make_title_bar(name, x, y, w, h, text, bg_color=HEADER_COLOR):
    return make_visual(name, x, y, w, h, "textbox",
        objects={"general": [{"properties": {"paragraphs": [
            {"textRuns": [{"value": text, "textStyle": {"fontFamily": "Segoe UI Semibold",
                                                         "fontSize": "18px", "color": "#FFFFFF"}}]}]}}]},
        visual_container_objects={
            "background": [{"properties": {"show": _lit("true"), "color": _solid(bg_color), "transparency": _lit("0D")}}],
            "visualHeader": [{"properties": {"show": _lit("false")}}]
        }, z=9000)


def make_button(name, x, y, w, h, text):
    obj = {
        "icon": [{"properties": {"shapeType": _lit("'blank'")}, "selector": {"id": "default"}},
                 {"properties": {"show": _lit("false")}}],
        "text": [{"properties": {"show": _lit("true")}},
                 {"properties": {"text": _lit(f"'{text}'"), "horizontalAlignment": _lit("'center'")},
                  "selector": {"id": "default"}}]
    }
    return make_visual(name, x, y, w, h, "actionButton", objects=obj, z=8000, how_created="InsertVisualButton")


def _gradient_fill(measure_table, measure_name):
    return {"dataPoint": [{
        "properties": {"fill": {"solid": {"color": {"expr": {"FillRule": {
            "Input": {"Measure": {"Expression": {"SourceRef": {"Entity": measure_table}}, "Property": measure_name}},
            "FillRule": {"linearGradient2": {
                "min": {"color": {"Literal": {"Value": "'minColor'"}}},
                "max": {"color": {"Literal": {"Value": "'maxColor'"}}},
                "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'asZero'"}}}}}
        }}}}}},
        "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}]}


def make_clustered_bar_gradient(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    base = _chart_objects(show_labels=True, label_position="'OutsideEnd'")
    base.update(_gradient_fill(val_table, val_measure))
    return make_visual(name, x, y, w, h, "clusteredBarChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}}, objects=base)


def make_clustered_column_gradient(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    base = _chart_objects(show_labels=True, label_position="'OutsideEnd'")
    base.update(_gradient_fill(val_table, val_measure))
    return make_visual(name, x, y, w, h, "clusteredColumnChart",
        {"Category": {"projections": [column_field(cat_table, cat_col)]},
         "Y": {"projections": [measure_field(val_table, val_measure)]}}, objects=base)


# ── Auto-generated page backgrounds (PNG via Pillow, SVG fallback) ─────────
def _hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _cluster_visuals(visuals):
    PAD, HEADER_H, FOOTER_H, ROW_GAP = 10, 50, 40, 80
    W, H = 1280, 720
    rects = []
    for v in visuals:
        pos = v.get("position", {})
        x, y, w, h = pos.get("x", 0), pos.get("y", 0), pos.get("width", 0), pos.get("height", 0)
        if v.get("visual", {}).get("visualType", "") in ("textbox", "actionButton"):
            continue
        if w > 0 and h > 0:
            rects.append((x, y, w, h))
    if not rects:
        return rects, []
    sorted_rects = sorted(rects, key=lambda r: r[1])
    clusters, current = [], [sorted_rects[0]]
    for rect in sorted_rects[1:]:
        if abs(rect[1] - max(r[1] for r in current)) <= ROW_GAP:
            current.append(rect)
        else:
            clusters.append(current); current = [rect]
    clusters.append(current)
    boxes = []
    for cl in clusters:
        min_x = max(0, min(r[0] for r in cl) - PAD)
        min_y = max(HEADER_H + 2, min(r[1] for r in cl) - PAD)
        max_x = min(W, max(r[0] + r[2] for r in cl) + PAD)
        max_y = min(H - FOOTER_H - 2, max(r[1] + r[3] for r in cl) + PAD)
        boxes.append((min_x, min_y, max_x - min_x, max_y - min_y))
    return rects, boxes


def _get_palette(style="light", colors=None):
    if style == "dark":
        p = dict(bg="#0F172A", container="#1E293B", border="#334155", accent="#60A5FA",
                 header_bg=HEADER_COLOR, footer_bg="#1E293B", dot_color="#334155",
                 divider="#334155", header_text="#FFFFFF")
    else:
        p = dict(bg="#F1F5F9", container="#FFFFFF", border="#E2E8F0", accent="#2563EB",
                 header_bg=HEADER_COLOR, footer_bg="#F8FAFC", dot_color="#E2E8F0",
                 divider="#CBD5E1", header_text="#FFFFFF")
    if colors:
        p.update(colors)
    return p


def make_background(page_name, visuals, style="light", display_name=None, colors=None):
    W, H, RADIUS, HEADER_H, FOOTER_H, GRID = 1280, 720, 12, 50, 40, 40
    palette = _get_palette(style, colors)
    _, boxes = _cluster_visuals(visuals)
    bg_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backgrounds")
    os.makedirs(bg_dir, exist_ok=True)

    if HAS_PILLOW:
        img = Image.new("RGB", (W, H), _hex_to_rgb(palette["bg"]))
        draw = ImageDraw.Draw(img, "RGBA")
        dot_rgba = _hex_to_rgb(palette["dot_color"]) + (80,)
        for gx in range(GRID, W, GRID):
            for gy in range(HEADER_H + GRID, H - FOOTER_H, GRID):
                draw.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=dot_rgba)
        draw.rectangle([0, 0, W, HEADER_H], fill=_hex_to_rgb(palette["header_bg"]))
        if display_name:
            try:
                font = ImageFont.truetype("segoeuib.ttf", 16)
            except OSError:
                try:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
                except OSError:
                    font = ImageFont.load_default()
            draw.text((20, 15), display_name, fill=_hex_to_rgb(palette["header_text"]), font=font)
        container_rgba = _hex_to_rgb(palette["container"]) + (153,)
        border_rgb = _hex_to_rgb(palette["border"])
        accent_rgba = _hex_to_rgb(palette["accent"]) + (204,)
        for (bx, by, bw, bh) in boxes:
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=RADIUS,
                                   fill=container_rgba, outline=border_rgb, width=1)
            stripe_h = int(min(bh - 2 * RADIUS, bh * 0.6))
            stripe_y = int(by + (bh - stripe_h) / 2)
            draw.rounded_rectangle([bx, stripe_y, bx + 4, stripe_y + stripe_h], radius=2, fill=accent_rgba)
        divider_rgba = _hex_to_rgb(palette["divider"]) + (100,)
        sb = sorted(boxes, key=lambda b: b[1])
        for i in range(len(sb) - 1):
            bot, nxt = sb[i][1] + sb[i][3], sb[i + 1][1]
            if nxt - bot > 10:
                dy = int((bot + nxt) / 2)
                for dx in range(20, W - 20, 10):
                    draw.line([dx, dy, dx + 6, dy], fill=divider_rgba, width=1)
        draw.rectangle([0, H - FOOTER_H, W, H], fill=_hex_to_rgb(palette["footer_bg"]) + (128,))
        png_path = os.path.join(bg_dir, f"{page_name}.png")
        img.save(png_path, "PNG")
        print(f"Background PNG: {png_path}")
        return png_path
    else:
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
               f'  <rect width="{W}" height="{H}" fill="{palette["bg"]}"/>']
        svg.append(f'  <rect x="0" y="0" width="{W}" height="{HEADER_H}" fill="{palette["header_bg"]}"/>')
        if display_name:
            svg.append(f'  <text x="20" y="33" font-family="Segoe UI Semibold, sans-serif" '
                       f'font-size="16" fill="{palette["header_text"]}">{display_name}</text>')
        for (bx, by, bw, bh) in boxes:
            svg.append(f'  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{RADIUS}" ry="{RADIUS}" '
                       f'fill="{palette["container"]}" stroke="{palette["border"]}" stroke-width="1" opacity="0.6"/>')
        svg.append(f'  <rect x="0" y="{H - FOOTER_H}" width="{W}" height="{FOOTER_H}" fill="{palette["footer_bg"]}" opacity="0.5"/>')
        svg.append('</svg>')
        svg_path = os.path.join(bg_dir, f"{page_name}.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write('\n'.join(svg))
        print(f"Background SVG (install Pillow for PNG+auto-embed): {svg_path}")
        return svg_path


def write_background(page_id, png_path):
    if not os.path.exists(png_path) or not png_path.endswith(".png"):
        return
    report_dir = os.path.dirname(BASE)
    page_json_path = os.path.join(BASE, page_id, "page.json")
    report_json_path = os.path.join(report_dir, "report.json")
    file_hash = hashlib.md5(open(png_path, "rb").read()).hexdigest()[:16]
    resource_name = f"bg_{file_hash}.png"
    res_dir = os.path.join(report_dir, "..", "StaticResources", "RegisteredResources")
    os.makedirs(res_dir, exist_ok=True)
    shutil.copy2(png_path, os.path.join(res_dir, resource_name))
    with open(page_json_path, "r", encoding="utf-8") as f:
        page = json.load(f)
    page["objects"] = {
        "background": [{"properties": {
            "image": {"image": {
                "name": {"expr": {"Literal": {"Value": f"'{os.path.basename(png_path)}'"}}},
                "url": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources",
                                                          "PackageType": 1, "ItemName": resource_name}}},
                "scaling": {"expr": {"Literal": {"Value": "'Normal'"}}}}},
            "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
        "displayArea": [{"properties": {"verticalAlignment": {"expr": {"Literal": {"Value": "'Top'"}}}}}]
    }
    with open(page_json_path, "w", encoding="utf-8") as f:
        json.dump(page, f, indent=2, ensure_ascii=False)
    with open(report_json_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    packages = report.get("resourcePackages", [])
    reg_pkg = next((p for p in packages if p.get("name") == "RegisteredResources"), None)
    if reg_pkg is None:
        reg_pkg = {"name": "RegisteredResources", "type": "RegisteredResources", "items": []}
        packages.append(reg_pkg)
    if resource_name not in {it["name"] for it in reg_pkg["items"]}:
        reg_pkg["items"].append({"name": resource_name, "path": resource_name, "type": "Image"})
    report["resourcePackages"] = packages
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Background embedded: {resource_name} -> page {page_id}")


# ===================================================================
# PAGE DEFINITIONS
# ===================================================================
M = "_Measures"

# ===== PAGE 1: Order Activity Overview =====
p1_id = uid("mo_page1_overview")
p1 = [
    make_title_bar("mo1_title", 0, 0, 1280, 50, "Market Orders — Order Activity & Surveillance  |  Trade Date 2025-07-11"),
    make_card("mo1_events", 20, 60, 230, 140, M, "Total Events"),
    make_card("mo1_new", 265, 60, 230, 140, M, "New Orders"),
    make_card("mo1_trades", 510, 60, 230, 140, M, "Trades"),
    make_card("mo1_otr", 755, 60, 230, 140, M, "Order to Trade Ratio"),
    make_slicer("mo1_slicer_mic", 1000, 60, 250, 65, TABLE, "MIC"),
    make_slicer("mo1_slicer_obc", 1000, 135, 250, 65, TABLE, "order_book_code"),
    # Intraday event volume
    make_line_chart("mo1_intraday", 20, 215, 740, 310, TABLE, "EventHour", M, "Total Events"),
    # Event type breakdown
    make_donut("mo1_eventtype", 780, 215, 470, 310, TABLE, "order_event_type", M, "Total Events"),
    # Instrument summary
    make_table("mo1_table", 20, 540, 1230, 140, [
        (TABLE, "order_book_code", False),
        (M, "New Orders", True),
        (M, "Trades", True),
        (M, "Traded Notional", True),
        (M, "Order to Trade Ratio", True),
    ]),
    make_button("mo1_btn_flow", 920, 670, 110, 40, "Lifecycle"),
    make_button("mo1_btn_surv", 1040, 670, 110, 40, "Surveillance"),
    make_button("mo1_btn_insight", 1160, 670, 100, 40, "Insights"),
]

# ===== PAGE 2: Order Lifecycle & Flow =====
p2_id = uid("mo_page2_flow")
p2 = [
    make_title_bar("mo2_title", 0, 0, 1280, 50, "Order Lifecycle & Flow"),
    make_card("mo2_new", 20, 60, 230, 140, M, "New Orders"),
    make_card("mo2_mod", 265, 60, 230, 140, M, "Modifications"),
    make_card("mo2_cancel", 510, 60, 230, 140, M, "Cancellations"),
    make_card("mo2_cancelrate", 755, 60, 230, 140, M, "Cancel Rate"),
    make_slicer("mo2_slicer_cap", 1000, 60, 250, 140, TABLE, "trading_capacity"),
    # Events by hour, split by event type
    make_stacked_column("mo2_byhour", 20, 215, 740, 310, TABLE, "EventHour",
                        TABLE, "order_event_type", M, "Total Events"),
    # Traded quantity by side
    make_donut("mo2_side", 780, 215, 470, 310, TABLE, "buy_sell", M, "Traded Quantity"),
    # Order type class mix
    make_clustered_bar("mo2_otype", 20, 540, 610, 140, TABLE, "order_type_class", M, "New Orders"),
    # Capacity mix by instrument
    make_hundred_pct_stacked_bar("mo2_cap_instr", 650, 540, 600, 140, TABLE, "order_book_code",
                                 TABLE, "trading_capacity", M, "Total Events"),
    make_button("mo2_btn_back", 20, 670, 100, 40, "Overview"),
    make_button("mo2_btn_surv", 1040, 670, 110, 40, "Surveillance"),
    make_button("mo2_btn_insight", 1160, 670, 100, 40, "Insights"),
]

# ===== PAGE 3: Surveillance & Anomalies =====
p3_id = uid("mo_page3_surveillance")
p3 = [
    make_title_bar("mo3_title", 0, 0, 1280, 50, "Surveillance & Anomalies — Order-to-Trade, Rapid Cancels, Off-Market Prices"),
    make_card("mo3_anom", 20, 60, 230, 140, M, "Anomaly Events"),
    make_card("mo3_rate", 265, 60, 230, 140, M, "Anomaly Rate"),
    make_card("mo3_offmkt", 510, 60, 230, 140, M, "Off-Market Events"),
    make_card("mo3_rapid", 755, 60, 230, 140, M, "Rapid Cancel Events"),
    make_slicer("mo3_slicer_obc", 1000, 60, 250, 65, TABLE, "order_book_code"),
    make_slicer("mo3_slicer_type", 1000, 135, 250, 65, TABLE, "AnomalyType"),
    # Order-to-trade ratio by firm (gradient — highlights outliers)
    make_clustered_bar_gradient("mo3_otr_firm", 20, 215, 610, 310, TABLE, "investment_firm_lei",
                                M, "Order to Trade Ratio"),
    # Off-market events by instrument
    make_clustered_column("mo3_offmkt_instr", 650, 215, 600, 150, TABLE, "order_book_code",
                          M, "Off-Market Events"),
    # Rapid cancels by firm
    make_clustered_bar("mo3_rapid_firm", 650, 375, 600, 150, TABLE, "investment_firm_lei",
                       M, "Rapid Cancel Events"),
    # Flagged events detail
    make_table("mo3_table", 20, 540, 1230, 140, [
        (TABLE, "order_ID", False),
        (TABLE, "order_book_code", False),
        (TABLE, "investment_firm_lei", False),
        (TABLE, "order_event_type", False),
        (TABLE, "AnomalyType", False),
        (M, "Avg Abs Price Dev bps", True),
        (M, "Min Cancel Latency ms", True),
    ]),
    make_button("mo3_btn_back", 20, 670, 100, 40, "Overview"),
    make_button("mo3_btn_flow", 920, 670, 110, 40, "Lifecycle"),
    make_button("mo3_btn_insight", 1160, 670, 100, 40, "Insights"),
]

# ===== PAGE 4: Firm & Instrument Insights =====
p4_id = uid("mo_page4_insights")
p4 = [
    make_title_bar("mo4_title", 0, 0, 1280, 50, "Firm & Instrument Insights"),
    make_card("mo4_firms", 20, 60, 230, 140, M, "Distinct Firms"),
    make_card("mo4_instr", 265, 60, 230, 140, M, "Distinct Instruments"),
    make_card("mo4_orders", 510, 60, 230, 140, M, "Distinct Orders"),
    make_card("mo4_avgsize", 755, 60, 230, 140, M, "Avg Order Size"),
    make_slicer("mo4_slicer_mic", 1000, 60, 250, 140, TABLE, "MIC"),
    # Top instruments by traded notional
    make_clustered_bar_gradient("mo4_topinstr", 20, 215, 610, 310, TABLE, "order_book_code",
                                M, "Traded Notional"),
    # Firms by event volume
    make_clustered_bar("mo4_firms_events", 650, 215, 600, 150, TABLE, "investment_firm_lei",
                       M, "Total Events"),
    # Per-firm OTR vs anomaly rate
    make_scatter("mo4_scatter", 650, 375, 600, 150, TABLE, "investment_firm_lei",
                 M, "Order to Trade Ratio", M, "Anomaly Rate", M, "Total Events"),
    # Firm scorecard
    make_table("mo4_table", 20, 540, 1230, 140, [
        (TABLE, "investment_firm_lei", False),
        (M, "Total Events", True),
        (M, "New Orders", True),
        (M, "Trades", True),
        (M, "Order to Trade Ratio", True),
        (M, "Anomaly Events", True),
        (M, "Anomaly Rate", True),
    ]),
    make_button("mo4_btn_back", 20, 670, 100, 40, "Overview"),
    make_button("mo4_btn_flow", 920, 670, 110, 40, "Lifecycle"),
    make_button("mo4_btn_surv", 1040, 670, 110, 40, "Surveillance"),
]

# ===== PAGE 5: Execution Quality & Liquidity =====
p5_id = uid("mo_page5_execution")
p5 = [
    make_title_bar("mo5_title", 0, 0, 1280, 50, "Execution Quality & Liquidity"),
    make_card("mo5_fillrate", 20, 60, 230, 140, M, "Order Fill Rate"),
    make_card("mo5_qtyfill", 265, 60, 230, 140, M, "Quantity Fill Rate"),
    make_card("mo5_ttf", 510, 60, 230, 140, M, "Avg Time to Fill s"),
    make_card("mo5_passive", 755, 60, 230, 140, M, "Passive Fill Share"),
    make_slicer("mo5_slicer_obc", 1000, 60, 250, 140, TABLE, "order_book_code"),
    # Order lifecycle funnel (event-type stages)
    make_funnel("mo5_funnel", 20, 215, 400, 310, TABLE, "order_event_type", M, "Total Events"),
    # Fill rate by instrument
    make_clustered_column("mo5_fill_instr", 435, 215, 395, 310, TABLE, "order_book_code", M, "Order Fill Rate"),
    # Intraday time-to-fill
    make_line_chart("mo5_ttf_hour", 845, 215, 405, 310, TABLE, "EventHour", M, "Avg Time to Fill s"),
    # Execution scorecard
    make_table("mo5_table", 20, 540, 1230, 140, [
        (TABLE, "order_book_code", False),
        (M, "New Orders", True),
        (M, "Trades", True),
        (M, "Order Fill Rate", True),
        (M, "Quantity Fill Rate", True),
        (M, "Avg Time to Fill s", True),
        (M, "Passive Fill Share", True),
    ]),
    make_button("mo5_btn_back", 20, 670, 100, 40, "Overview"),
    make_button("mo5_btn_surv", 1030, 670, 110, 40, "Surveillance"),
    make_button("mo5_btn_part", 1150, 670, 110, 40, "Participants"),
]

# ===== PAGE 6: Participants & Order Composition =====
p6_id = uid("mo_page6_participants")
p6 = [
    make_title_bar("mo6_title", 0, 0, 1280, 50, "Participants & Order Composition"),
    make_card("mo6_clients", 20, 60, 230, 140, M, "Distinct Clients"),
    make_card("mo6_dea", 265, 60, 230, 140, M, "DEA Share"),
    make_card("mo6_algo", 510, 60, 230, 140, M, "Algo Share"),
    make_card("mo6_lp", 755, 60, 230, 140, M, "Liquidity Provision Share"),
    make_slicer("mo6_slicer_cap", 1000, 60, 250, 65, TABLE, "trading_capacity"),
    make_slicer("mo6_slicer_mic", 1000, 135, 250, 65, TABLE, "MIC"),
    # Order-size distribution (histogram)
    make_clustered_column("mo6_size", 20, 215, 400, 310, TABLE, "SizeBucket", M, "New Orders"),
    # Validity-period mix
    make_donut("mo6_validity", 435, 215, 395, 310, TABLE, "validity_period", M, "New Orders"),
    # Trading-capacity mix
    make_donut("mo6_capacity", 845, 215, 405, 310, TABLE, "trading_capacity", M, "Total Events"),
    # Top firms by orders
    make_clustered_bar("mo6_firms", 20, 540, 610, 140, TABLE, "investment_firm_lei", M, "Distinct Orders"),
    # Events by instrument, grouped by venue
    make_treemap("mo6_treemap", 650, 540, 600, 140, TABLE, "order_book_code", M, "Total Events",
                 group_table=TABLE, group_col="MIC"),
    make_button("mo6_btn_back", 20, 670, 100, 40, "Overview"),
    make_button("mo6_btn_exec", 1030, 670, 110, 40, "Execution"),
    make_button("mo6_btn_insight", 1150, 670, 110, 40, "Insights"),
]

# ===== PAGE 7: Intraday Microstructure =====
p7_id = uid("mo_page7_microstructure")
p7 = [
    make_title_bar("mo7_title", 0, 0, 1280, 50, "Intraday Microstructure — Imbalance, Cumulative Flow, Activity Heatmap"),
    make_card("mo7_buy", 20, 60, 230, 140, M, "Buy Events"),
    make_card("mo7_sell", 265, 60, 230, 140, M, "Sell Events"),
    make_card("mo7_imbal", 510, 60, 230, 140, M, "Buy/Sell Imbalance"),
    make_card("mo7_events", 755, 60, 230, 140, M, "Total Events"),
    make_slicer("mo7_slicer_obc", 1000, 60, 250, 140, TABLE, "order_book_code"),
    # Buy vs sell events through the session
    make_line_chart("mo7_imbalance", 20, 215, 610, 310, TABLE, "EventHour", M, "Buy Events", M, "Sell Events"),
    # Cumulative event flow
    make_area_chart("mo7_cumulative", 650, 215, 600, 150, TABLE, "EventHour", M, "Cumulative Events"),
    # Quote-distance (limit vs reference) distribution
    make_clustered_column("mo7_distance", 650, 375, 600, 150, TABLE, "DistanceBucket", M, "New Orders"),
    # Activity heatmap: instrument x hour
    make_matrix("mo7_heatmap", 20, 540, 1230, 140,
                [(TABLE, "order_book_code")], [(TABLE, "EventHour")], [(M, "Total Events")]),
    make_button("mo7_btn_back", 20, 670, 100, 40, "Overview"),
    make_button("mo7_btn_exec", 1030, 670, 110, 40, "Execution"),
    make_button("mo7_btn_clients", 1150, 670, 110, 40, "Clients"),
]

# ===== PAGE 8: Client Concentration =====
p8_id = uid("mo_page8_clients")
p8 = [
    make_title_bar("mo8_title", 0, 0, 1280, 50, "Client Concentration"),
    make_card("mo8_clients", 20, 60, 230, 140, M, "Distinct Clients"),
    make_card("mo8_top5", 265, 60, 230, 140, M, "Top 5 Client Share"),
    make_card("mo8_hhi", 510, 60, 230, 140, M, "Client HHI"),
    make_card("mo8_notional", 755, 60, 230, 140, M, "Traded Notional"),
    make_slicer("mo8_slicer_obc", 1000, 60, 250, 65, TABLE, "order_book_code"),
    make_slicer("mo8_slicer_mic", 1000, 135, 250, 65, TABLE, "MIC"),
    # Top clients by traded notional
    make_clustered_bar_gradient("mo8_topclients", 20, 215, 610, 310, TABLE, "client_ID", M, "Traded Notional"),
    # Client share treemap
    make_treemap("mo8_treemap", 650, 215, 600, 150, TABLE, "client_ID", M, "Traded Notional"),
    # Clients by order count
    make_clustered_bar("mo8_clientorders", 650, 375, 600, 150, TABLE, "client_ID", M, "Distinct Orders"),
    # Client scorecard
    make_table("mo8_table", 20, 540, 1230, 140, [
        (TABLE, "client_ID", False),
        (M, "Distinct Orders", True),
        (M, "Trades", True),
        (M, "Traded Quantity", True),
        (M, "Traded Notional", True),
    ]),
    make_button("mo8_btn_back", 20, 670, 100, 40, "Overview"),
    make_button("mo8_btn_micro", 1020, 670, 130, 40, "Microstructure"),
    make_button("mo8_btn_surv", 1160, 670, 100, 40, "Surveillance"),
]


# ===================================================================
# WRITE ALL PAGES
# ===================================================================
if __name__ == "__main__":
    write_page(p1_id, "Order Activity Overview", p1)
    write_page(p2_id, "Order Lifecycle & Flow", p2)
    write_page(p3_id, "Surveillance & Anomalies", p3)
    write_page(p4_id, "Firm & Instrument Insights", p4)
    write_page(p5_id, "Execution Quality & Liquidity", p5)
    write_page(p6_id, "Participants & Order Composition", p6)
    write_page(p7_id, "Intraday Microstructure", p7)
    write_page(p8_id, "Client Concentration", p8)

    for pg_name, pg_id, pg_visuals, pg_title in [
        ("order_overview", p1_id, p1, "Order Activity Overview"),
        ("order_flow", p2_id, p2, "Order Lifecycle & Flow"),
        ("surveillance", p3_id, p3, "Surveillance & Anomalies"),
        ("firm_insights", p4_id, p4, "Firm & Instrument Insights"),
        ("execution_quality", p5_id, p5, "Execution Quality & Liquidity"),
        ("participants", p6_id, p6, "Participants & Order Composition"),
        ("microstructure", p7_id, p7, "Intraday Microstructure"),
        ("client_concentration", p8_id, p8, "Client Concentration"),
    ]:
        bg_path = make_background(pg_name, pg_visuals, display_name=pg_title)
        if bg_path and bg_path.endswith(".png"):
            write_background(pg_id, bg_path)

    with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
        json.dump({"$schema": SCHEMA_PAGES,
                   "pageOrder": [p1_id, p2_id, p3_id, p4_id, p5_id, p6_id, p7_id, p8_id],
                   "activePageName": p1_id}, f, indent=2)

    REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(BASE))))
    THEME_PATH = os.path.join(REPO_ROOT, "themes", "code-first-dashboard.json")
    if os.path.exists(THEME_PATH):
        write_theme(THEME_PATH)

    print(f"Page 1 (Order Activity Overview): {p1_id} - {len(p1)} visuals")
    print(f"Page 2 (Order Lifecycle & Flow): {p2_id} - {len(p2)} visuals")
    print(f"Page 3 (Surveillance & Anomalies): {p3_id} - {len(p3)} visuals")
    print(f"Page 4 (Firm & Instrument Insights): {p4_id} - {len(p4)} visuals")
    print(f"Page 5 (Execution Quality & Liquidity): {p5_id} - {len(p5)} visuals")
    print(f"Page 6 (Participants & Order Composition): {p6_id} - {len(p6)} visuals")
    print(f"Page 7 (Intraday Microstructure): {p7_id} - {len(p7)} visuals")
    print(f"Page 8 (Client Concentration): {p8_id} - {len(p8)} visuals")
    print("Done!")
