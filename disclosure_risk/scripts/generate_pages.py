"""
PBIR Visual Helper Functions — with built-in formatting defaults.

Disclosure Risk: Order Data — Privacy & Disclosure-Risk Assessment
3 pages: Field Risk Register, SDC Scenario Ladder, Risk Heatmap & Deep-dive

Built against schema-level metadata only (see data/generate_risk_data.py):
a per-field risk register and an SDC scenario ladder with indicative
re-identification-risk and information-loss indices. No real data or
identifiers are used. Pure DAX — no R required.
"""

import json, os, hashlib, shutil

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# UPDATE this path to match your saved .pbip project location
BASE = r"C:\Users\emant\Documents\powerbi-code-first-dashboards\disclosure_risk\disclosure_risk_dash.Report\definition\pages"

SCHEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"
SCHEMA_PAGE   = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"

HEADER_COLOR = "#3B2A57"   # privacy/purple slate to distinguish from the surveillance dashboard
FIELD = "DimField"
SCEN = "DimScenario"
M = "_Measures"


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


def make_card(name, x, y, w, h, table, measure):
    return make_visual(name, x, y, w, h, "cardVisual",
        {"Data": {"projections": [measure_field(table, measure)]}}, objects=_card_objects())

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

def make_donut(name, x, y, w, h, cat_table, cat_col, val_table, val_measure):
    return make_visual(name, x, y, w, h, "donutChart",
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

def make_treemap(name, x, y, w, h, cat_table, cat_col, val_table, val_measure, group_table=None, group_col=None):
    qs = {"Category": {"projections": [column_field(cat_table, cat_col)]},
          "Values": {"projections": [measure_field(val_table, val_measure)]}}
    if group_table and group_col:
        qs["Group"] = {"projections": [column_field(group_table, group_col)]}
    return make_visual(name, x, y, w, h, "treemap", qs)

def make_scatter(name, x, y, w, h, detail_table, detail_col, x_table, x_measure, y_table, y_measure, size_table=None, size_measure=None):
    qs = {"Category": {"projections": [column_field(detail_table, detail_col)]},
          "X": {"projections": [measure_field(x_table, x_measure)]},
          "Y": {"projections": [measure_field(y_table, y_measure)]}}
    if size_table and size_measure:
        qs["Size"] = {"projections": [measure_field(size_table, size_measure)]}
    return make_visual(name, x, y, w, h, "scatterChart", qs)


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


# ── Auto-generated page backgrounds ────────────────────────────────────────
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
    sr = sorted(rects, key=lambda r: r[1])
    clusters, cur = [], [sr[0]]
    for rect in sr[1:]:
        if abs(rect[1] - max(r[1] for r in cur)) <= ROW_GAP:
            cur.append(rect)
        else:
            clusters.append(cur); cur = [rect]
    clusters.append(cur)
    boxes = []
    for cl in clusters:
        min_x = max(0, min(r[0] for r in cl) - PAD)
        min_y = max(HEADER_H + 2, min(r[1] for r in cl) - PAD)
        max_x = min(W, max(r[0] + r[2] for r in cl) + PAD)
        max_y = min(H - FOOTER_H - 2, max(r[1] + r[3] for r in cl) + PAD)
        boxes.append((min_x, min_y, max_x - min_x, max_y - min_y))
    return rects, boxes

def _get_palette(colors=None):
    p = dict(bg="#F1F0F6", container="#FFFFFF", border="#E3E0EC", accent="#7C3AED",
             header_bg=HEADER_COLOR, footer_bg="#F8FAFC", dot_color="#E3E0EC",
             divider="#CBC6DA", header_text="#FFFFFF")
    if colors:
        p.update(colors)
    return p

def make_background(page_name, visuals, display_name=None, colors=None):
    W, H, RADIUS, HEADER_H, FOOTER_H, GRID = 1280, 720, 12, 50, 40, 40
    palette = _get_palette(colors)
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
        draw.rectangle([0, H - FOOTER_H, W, H], fill=_hex_to_rgb(palette["footer_bg"]) + (128,))
        png_path = os.path.join(bg_dir, f"{page_name}.png")
        img.save(png_path, "PNG")
        print(f"Background PNG: {png_path}")
        return png_path
    else:
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
               f'  <rect width="{W}" height="{H}" fill="{palette["bg"]}"/>',
               f'  <rect x="0" y="0" width="{W}" height="{HEADER_H}" fill="{palette["header_bg"]}"/>']
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

# ===== PAGE 1: Field Risk Register =====
p1_id = uid("dr_page1_register")
p1 = [
    make_title_bar("dr1_title", 0, 0, 1280, 50, "Order Data — Privacy & Disclosure-Risk Assessment  |  Field Risk Register"),
    make_card("dr1_fields", 20, 60, 230, 140, M, "Field Count"),
    make_card("dr1_di", 265, 60, 230, 140, M, "Direct Identifiers"),
    make_card("dr1_high", 510, 60, 230, 140, M, "High Risk Fields"),
    make_card("dr1_sdc", 755, 60, 230, 140, M, "Fields Needing SDC"),
    make_slicer("dr1_slicer_schema", 1000, 60, 250, 65, FIELD, "schema_category"),
    make_slicer("dr1_slicer_class", 1000, 135, 250, 65, FIELD, "sdc_class"),
    # Fields by risk level
    make_clustered_bar("dr1_byrisk", 20, 215, 400, 310, FIELD, "risk_level", M, "Field Count"),
    # Fields by disclosure-control class
    make_donut("dr1_byclass", 435, 215, 395, 310, FIELD, "sdc_class", M, "Field Count"),
    # Fields by recommended SDC method
    make_treemap("dr1_bymethod", 845, 215, 405, 310, FIELD, "sdc_method", M, "Field Count"),
    # Register table
    make_table("dr1_table", 20, 540, 1230, 140, [
        (FIELD, "field", False),
        (FIELD, "schema_category", False),
        (FIELD, "sdc_class", False),
        (FIELD, "risk_level", False),
        (FIELD, "sdc_method", False),
        (FIELD, "info_loss_metric", False),
        (FIELD, "pct_empty", False),
    ]),
    make_button("dr1_btn_scen", 1030, 670, 110, 40, "Scenarios"),
    make_button("dr1_btn_heat", 1150, 670, 110, 40, "Heatmap"),
]

# ===== PAGE 2: SDC Scenario Ladder =====
p2_id = uid("dr_page2_scenarios")
p2 = [
    make_title_bar("dr2_title", 0, 0, 1280, 50, "SDC Scenario Ladder — Privacy vs Utility Trade-off"),
    make_card("dr2_count", 20, 60, 230, 140, M, "Scenario Count"),
    make_card("dr2_minrisk", 265, 60, 230, 140, M, "Lowest Risk Index"),
    make_card("dr2_maxutil", 510, 60, 230, 140, M, "Highest Utility Loss"),
    make_card("dr2_gain", 755, 60, 230, 140, M, "Avg Protection Gain"),
    make_slicer("dr2_slicer_time", 1000, 60, 250, 65, SCEN, "time_generalization"),
    make_slicer("dr2_slicer_round", 1000, 135, 250, 65, SCEN, "price_rounding"),
    # Privacy-utility frontier
    make_scatter("dr2_frontier", 20, 215, 610, 310, SCEN, "scenario_id",
                 M, "Utility Loss", M, "Risk Index", M, "Protection Gain"),
    # Risk index across the ladder
    make_line_chart("dr2_risk_line", 650, 215, 600, 150, SCEN, "scenario_id",
                    M, "Risk Index", M, "Utility Loss"),
    # Utility loss by scenario
    make_clustered_bar("dr2_util_bar", 650, 375, 600, 150, SCEN, "scenario_id", M, "Utility Loss"),
    # Scenario detail
    make_table("dr2_table", 20, 540, 1230, 140, [
        (SCEN, "scenario_id", False),
        (SCEN, "time_generalization", False),
        (SCEN, "price_rounding", False),
        (SCEN, "quantity_topcoding", False),
        (M, "Risk Index", True),
        (M, "Utility Loss", True),
        (M, "Protection Gain", True),
    ]),
    make_button("dr2_btn_back", 20, 670, 100, 40, "Register"),
    make_button("dr2_btn_heat", 1150, 670, 110, 40, "Heatmap"),
]

# ===== PAGE 3: Risk Heatmap & Deep-dive =====
p3_id = uid("dr_page3_heatmap")
p3 = [
    make_title_bar("dr3_title", 0, 0, 1280, 50, "Risk Heatmap & Deep-dive"),
    make_card("dr3_avg", 20, 60, 230, 140, M, "Avg Risk Weight"),
    make_card("dr3_qi", 265, 60, 230, 140, M, "Quasi Identifiers"),
    make_card("dr3_sens", 510, 60, 230, 140, M, "Sensitive Fields"),
    make_card("dr3_sparse", 755, 60, 230, 140, M, "Sparse Fields"),
    make_slicer("dr3_slicer_schema", 1000, 60, 250, 140, FIELD, "schema_category"),
    # Heatmap: disclosure-control class x risk level
    make_matrix("dr3_heatmap", 20, 215, 610, 310,
                [(FIELD, "sdc_class")], [(FIELD, "risk_level")], [(M, "Field Count")]),
    # Fields by SDC method
    make_clustered_bar("dr3_bymethod", 650, 215, 600, 150, FIELD, "sdc_method", M, "Field Count"),
    # Avg risk weight by schema category
    make_clustered_column("dr3_byschema", 650, 375, 600, 150, FIELD, "schema_category", M, "Avg Risk Weight"),
    # High-risk fields table
    make_table("dr3_table", 20, 540, 1230, 140, [
        (FIELD, "field", False),
        (FIELD, "sdc_class", False),
        (FIELD, "risk_level", False),
        (FIELD, "risk_weight", False),
        (FIELD, "research_interest", False),
        (FIELD, "needs_sdc", False),
    ]),
    make_button("dr3_btn_back", 20, 670, 100, 40, "Register"),
    make_button("dr3_btn_scen", 1030, 670, 110, 40, "Scenarios"),
]


# ===================================================================
# WRITE ALL PAGES
# ===================================================================
if __name__ == "__main__":
    write_page(p1_id, "Field Risk Register", p1)
    write_page(p2_id, "SDC Scenario Ladder", p2)
    write_page(p3_id, "Risk Heatmap & Deep-dive", p3)

    for pg_name, pg_id, pg_visuals, pg_title in [
        ("field_register", p1_id, p1, "Field Risk Register"),
        ("scenario_ladder", p2_id, p2, "SDC Scenario Ladder"),
        ("risk_heatmap", p3_id, p3, "Risk Heatmap & Deep-dive"),
    ]:
        bg_path = make_background(pg_name, pg_visuals, display_name=pg_title)
        if bg_path and bg_path.endswith(".png"):
            write_background(pg_id, bg_path)

    with open(os.path.join(BASE, "pages.json"), "w", encoding="utf-8") as f:
        json.dump({"$schema": SCHEMA_PAGES, "pageOrder": [p1_id, p2_id, p3_id],
                   "activePageName": p1_id}, f, indent=2)

    REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(BASE))))
    THEME_PATH = os.path.join(REPO_ROOT, "themes", "code-first-dashboard.json")
    if os.path.exists(THEME_PATH):
        write_theme(THEME_PATH)

    print(f"Page 1 (Field Risk Register): {p1_id} - {len(p1)} visuals")
    print(f"Page 2 (SDC Scenario Ladder): {p2_id} - {len(p2)} visuals")
    print(f"Page 3 (Risk Heatmap & Deep-dive): {p3_id} - {len(p3)} visuals")
    print("Done!")
