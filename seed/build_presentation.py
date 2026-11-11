from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Campus_Environment_System_Approval_Presentation.pptx"
ASSETS = ROOT / "docs" / "screenshots"

W, H = 13.333, 7.5
BG = "0B1220"
PANEL = "111D31"
PANEL_2 = "17243A"
WHITE = "F7FAFC"
MUTED = "A8B5C8"
CYAN = "39D0FF"
MINT = "41D6A4"
AMBER = "FFB454"
CORAL = "FF6F61"
LINE = "263A55"


def rgb(hex_value):
    return RGBColor.from_string(hex_value)


def add_box(slide, x, y, w, h, fill=PANEL, radius=True, line_color=None, transparency=0):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    shape.fill.transparency = transparency
    shape.line.color.rgb = rgb(line_color or fill)
    shape.line.transparency = 0 if line_color else 100
    return shape


def add_text(slide, text, x, y, w, h, size=18, color=WHITE, bold=False,
             font="Aptos", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP,
             margin=0.04, italic=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = rgb(color)
    return box


def add_rich_text(slide, runs, x, y, w, h, size=16, color=WHITE, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    p = tf.paragraphs[0]
    p.alignment = align
    for item in runs:
        run = p.add_run()
        run.text = item[0]
        run.font.name = item[3] if len(item) > 3 else "Aptos"
        run.font.size = Pt(item[1] if len(item) > 1 else size)
        run.font.bold = item[2] if len(item) > 2 else False
        run.font.color.rgb = rgb(item[4] if len(item) > 4 else color)
    return box


def add_line(slide, x, y, w, color=CYAN, thickness=2):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(thickness / 72))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(color)
    shape.line.fill.background()
    return shape


def add_footer(slide, page, label="CAMPUS ENVIRONMENT DATA VISUALIZATION SYSTEM"):
    add_line(slide, 0.55, 7.12, 12.22, LINE, 1)
    add_text(slide, label, 0.58, 7.18, 8.5, 0.18, 7.5, MUTED, bold=True)
    add_text(slide, f"{page:02d}", 12.15, 7.14, 0.55, 0.22, 9, CYAN, bold=True, align=PP_ALIGN.RIGHT)


def add_title(slide, eyebrow, title, subtitle=None, page=None):
    add_text(slide, eyebrow.upper(), 0.62, 0.38, 6.8, 0.22, 9, CYAN, bold=True)
    add_text(slide, title, 0.58, 0.72, 11.6, 0.62, 27, WHITE, bold=True, font="Aptos Display")
    add_line(slide, 0.62, 1.47, 1.0, CYAN, 3)
    if subtitle:
        add_text(slide, subtitle, 0.62, 1.60, 11.9, 0.36, 11.5, MUTED)
    if page is not None:
        add_footer(slide, page)


def add_bullet(slide, title, body, x, y, w, accent=CYAN, title_size=14, body_size=10.5):
    add_box(slide, x, y, 0.09, 0.58, accent, radius=False)
    add_text(slide, title, x + 0.2, y - 0.01, w - 0.2, 0.24, title_size, WHITE, bold=True)
    add_text(slide, body, x + 0.2, y + 0.26, w - 0.2, 0.34, body_size, MUTED)


def add_metric(slide, value, label, x, y, w, accent=CYAN):
    add_box(slide, x, y, w, 1.02, PANEL, line_color=LINE)
    add_text(slide, value, x + 0.16, y + 0.12, w - 0.32, 0.42, 25, accent, bold=True, font="Aptos Display")
    add_text(slide, label.upper(), x + 0.16, y + 0.64, w - 0.32, 0.2, 8.5, MUTED, bold=True)


def add_picture(slide, filename, x, y, w, h, border=LINE):
    path = ASSETS / filename
    slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w), height=Inches(h))
    outline = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    outline.fill.background()
    outline.line.color.rgb = rgb(border)
    outline.line.width = Pt(1.2)


def add_tag(slide, text, x, y, w, accent=CYAN):
    add_box(slide, x, y, w, 0.28, PANEL_2, line_color=accent)
    add_text(slide, text, x, y + 0.01, w, 0.22, 8.5, accent, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def new_slide(prs, bg=BG):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(bg)
    return slide


def build():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)

    # 01: Cover
    slide = new_slide(prs)
    add_box(slide, 8.85, 0, 4.48, 7.5, PANEL, radius=False)
    add_box(slide, 9.18, 0.65, 3.78, 5.86, PANEL_2, radius=False, line_color=LINE)
    add_picture(slide, "fig_01_dashboard_overview.png", 9.36, 0.85, 3.42, 2.45)
    add_picture(slide, "fig_03_spatial_radar_comparison.png", 9.36, 3.48, 1.62, 2.56)
    add_picture(slide, "fig_04_diurnal_heatmap.png", 11.16, 3.48, 1.62, 2.56)
    add_text(slide, "SMART CAMPUS / ENVIRONMENTAL INTELLIGENCE", 0.7, 0.66, 6.8, 0.25, 10, CYAN, bold=True)
    add_text(slide, "Campus Environment\nData Visualization System", 0.66, 1.25, 7.5, 1.45, 31, WHITE, bold=True, font="Aptos Display")
    add_text(slide, "A Python-based platform for hyper-local telemetry,\nhealth scoring, and evidence-led campus decisions.", 0.7, 3.05, 6.3, 0.62, 16, MUTED)
    add_line(slide, 0.72, 4.03, 1.45, MINT, 4)
    add_text(slide, "UNIVERSITY APPROVAL PRESENTATION", 0.7, 4.36, 4.5, 0.28, 10, MINT, bold=True)
    add_text(slide, "Department of Information Engineering\nComputer Application Technology\nWuhu Vocational And Technical University", 0.7, 4.78, 5.8, 0.82, 13, WHITE)
    add_text(slide, "Prepared for academic review · 2026", 0.7, 6.72, 5.2, 0.25, 9, MUTED)

    # 02: Executive snapshot
    slide = new_slide(prs)
    add_title(slide, "01 / Executive snapshot", "From scattered readings to campus-wide environmental intelligence", "The project turns raw environmental telemetry into an operational view that people can understand and act on.", 2)
    add_metric(slide, "8", "Campus zones modeled", 0.62, 2.25, 2.25, CYAN)
    add_metric(slide, "6", "Core physical parameters", 3.03, 2.25, 2.25, MINT)
    add_metric(slide, "100", "Point CEHI scale", 5.44, 2.25, 2.25, AMBER)
    add_metric(slide, "27/27", "Automated tests passed", 7.85, 2.25, 2.25, CORAL)
    add_box(slide, 0.62, 3.65, 7.05, 2.45, PANEL, line_color=LINE)
    add_text(slide, "The approval case", 0.9, 3.96, 3.2, 0.3, 17, WHITE, bold=True)
    add_bullet(slide, "Useful", "A single dashboard connects air quality, thermal comfort, ventilation, and noise.", 0.9, 4.48, 6.15, CYAN)
    add_bullet(slide, "Defensible", "AQI follows US EPA breakpoint interpolation; CEHI exposes a transparent weighted score.", 0.9, 5.18, 6.15, MINT)
    add_box(slide, 7.95, 3.65, 4.65, 2.45, PANEL_2, line_color=LINE)
    add_text(slide, "A compact technical thesis", 8.25, 3.96, 3.8, 0.3, 17, WHITE, bold=True)
    add_text(slide, "Can a unified Python stack deliver a responsive, testable, and visually rich smart-campus monitoring system?", 8.25, 4.55, 3.85, 0.78, 18, CYAN, bold=True, font="Aptos Display")
    add_text(slide, "This project demonstrates that it can.", 8.25, 5.55, 3.75, 0.28, 11, MUTED)

    # 03: Problem
    slide = new_slide(prs)
    add_title(slide, "02 / The problem", "Campus conditions change by zone, hour, and activity", "Traditional inspection and isolated logs do not provide the context needed for timely action.", 3)
    add_box(slide, 0.62, 2.23, 4.0, 3.98, PANEL, line_color=LINE)
    add_text(slide, "What is missing today", 0.92, 2.55, 3.2, 0.28, 18, WHITE, bold=True)
    add_bullet(slide, "Hyper-local visibility", "Municipal or single-point weather data misses the library, gate, cafeteria, and lab as distinct environments.", 0.92, 3.12, 3.2, CORAL)
    add_bullet(slide, "Early warning", "Manual checks are periodic; CO2, particulate, or noise spikes can happen between inspections.", 0.92, 4.06, 3.2, AMBER)
    add_bullet(slide, "Shared understanding", "Raw logs and vendor silos make it difficult for facilities, faculty, and students to see the same evidence.", 0.92, 5.0, 3.2, CYAN)
    add_box(slide, 4.95, 2.23, 7.65, 3.98, PANEL_2, line_color=LINE)
    add_text(slide, "The campus is a living dataset", 5.3, 2.56, 4.8, 0.28, 18, WHITE, bold=True)
    add_tag(slide, "TRAFFIC", 5.35, 3.22, 1.15, CORAL)
    add_tag(slide, "OCCUPANCY", 6.68, 3.22, 1.42, AMBER)
    add_tag(slide, "VENTILATION", 8.28, 3.22, 1.55, MINT)
    add_tag(slide, "WEATHER", 10.02, 3.22, 1.25, CYAN)
    add_line(slide, 5.38, 4.02, 6.78, LINE, 1)
    add_text(slide, "Morning commute", 5.4, 4.34, 1.7, 0.25, 12, WHITE, bold=True)
    add_text(slide, "→", 7.2, 4.29, 0.4, 0.3, 18, CORAL, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "PM spike at gate", 7.72, 4.34, 1.8, 0.25, 12, WHITE, bold=True)
    add_text(slide, "→", 9.72, 4.29, 0.4, 0.3, 18, CORAL, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Actionable alert", 10.22, 4.34, 1.55, 0.25, 12, WHITE, bold=True)
    add_text(slide, "The system makes those relationships visible in one place, with a history that can be inspected later.", 5.4, 5.15, 6.4, 0.52, 16, CYAN, bold=True, font="Aptos Display")

    # 04: Solution
    slide = new_slide(prs)
    add_title(slide, "03 / The solution", "One platform, four decision layers", "The system is designed as a continuous loop: collect, calculate, interpret, respond.", 4)
    steps = [
        ("01", "COLLECT", "Sensor or manual telemetry enters through validated REST endpoints.", CYAN),
        ("02", "CALCULATE", "AQI and CEHI are computed from transparent, reusable services.", MINT),
        ("03", "INTERPRET", "Dash visuals reveal trends, zone differences, distributions, and time patterns.", AMBER),
        ("04", "RESPOND", "Threshold alerts, admin workflows, and reports support campus action.", CORAL),
    ]
    x = 0.62
    for num, title, body, accent in steps:
        add_box(slide, x, 2.4, 2.82, 2.56, PANEL, line_color=LINE)
        add_text(slide, num, x + 0.22, 2.64, 0.7, 0.45, 24, accent, bold=True, font="Aptos Display")
        add_line(slide, x + 0.22, 3.2, 0.68, accent, 3)
        add_text(slide, title, x + 0.22, 3.52, 2.2, 0.25, 15, WHITE, bold=True)
        add_text(slide, body, x + 0.22, 3.94, 2.3, 0.7, 11, MUTED)
        x += 3.08
    add_box(slide, 0.62, 5.42, 12.0, 0.78, PANEL_2, line_color=LINE)
    add_rich_text(slide, [("Sensor node", 12, True, "Aptos", CYAN), ("  →  ", 12, True, "Aptos", MUTED), ("Flask API", 12, True, "Aptos", MINT), ("  →  ", 12, True, "Aptos", MUTED), ("AQI / CEHI", 12, True, "Aptos", AMBER), ("  →  ", 12, True, "Aptos", MUTED), ("SQLite + Pandas", 12, True, "Aptos", WHITE), ("  →  ", 12, True, "Aptos", MUTED), ("Dash dashboard", 12, True, "Aptos", CORAL)], 1.0, 5.66, 11.2, 0.28, align=PP_ALIGN.CENTER)

    # 05: Architecture
    slide = new_slide(prs)
    add_title(slide, "04 / Architecture", "A unified Python stack keeps the system understandable", "The design separates presentation, routing, analytics, and persistence while keeping deployment compact.", 5)
    layers = [
        ("PRESENTATION", "Flask views  ·  Plotly Dash  ·  Bootstrap 5", CYAN),
        ("ROUTING", "Auth  ·  Zones  ·  Sensors  ·  Readings  ·  Alerts  ·  Reports", MINT),
        ("ANALYTICS", "Telemetry generator  ·  EPA AQI  ·  CEHI  ·  Pandas statistics  ·  Alert engine", AMBER),
        ("PERSISTENCE", "SQLAlchemy ORM  ·  Users  ·  Zones  ·  Sensors  ·  Readings  ·  Alerts  ·  SQLite", CORAL),
    ]
    y = 2.3
    for label, body, accent in layers:
        add_box(slide, 1.0, y, 11.25, 0.78, PANEL, line_color=LINE)
        add_box(slide, 1.0, y, 2.18, 0.78, accent, radius=False)
        add_text(slide, label, 1.12, y + 0.22, 1.95, 0.25, 11, BG, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, body, 3.55, y + 0.22, 8.2, 0.28, 12, WHITE, bold=True)
        if y < 4.7:
            add_text(slide, "↓", 6.35, y + 0.82, 0.5, 0.25, 16, MUTED, bold=True, align=PP_ALIGN.CENTER)
        y += 1.08
    add_text(slide, "Why this matters academically: the same language handles web routing, visualization, statistics, and persistence, reducing integration friction and improving reproducibility.", 1.05, 6.72, 11.0, 0.28, 10.5, MUTED, italic=True, align=PP_ALIGN.CENTER)

    # 06: Data model and algorithms
    slide = new_slide(prs)
    add_title(slide, "05 / Data and intelligence", "The platform turns telemetry into a common language for campus health", "Each reading becomes both a record for analysis and a signal for immediate operational response.", 6)
    add_box(slide, 0.62, 2.25, 4.08, 3.85, PANEL, line_color=LINE)
    add_text(slide, "Eight modeled zones", 0.94, 2.57, 3.0, 0.28, 17, WHITE, bold=True)
    zones = ["Main Gate", "Library", "Classroom Block", "Cafeteria", "Hostel", "Playground", "Parking Area", "Laboratory Block"]
    for idx, zone in enumerate(zones):
        col = idx // 4
        row = idx % 4
        add_tag(slide, zone, 0.95 + col * 1.75, 3.15 + row * 0.56, 1.55, [CYAN, MINT, AMBER, CORAL][row])
    add_box(slide, 4.98, 2.25, 3.42, 3.85, PANEL_2, line_color=LINE)
    add_text(slide, "Six physical signals", 5.28, 2.57, 2.6, 0.28, 17, WHITE, bold=True)
    signals = [("Temperature", "°C", AMBER), ("Humidity", "%", CYAN), ("PM2.5 / PM10", "µg/m³", CORAL), ("CO₂", "ppm", MINT), ("Noise", "dB", "D66BFF"), ("AQI", "index", "7BA7FF")]
    for idx, (name, unit, accent) in enumerate(signals):
        yy = 3.14 + idx * 0.44
        add_text(slide, name, 5.3, yy, 1.85, 0.22, 11, WHITE, bold=True)
        add_text(slide, unit, 7.25, yy, 0.72, 0.22, 10, accent, bold=True, align=PP_ALIGN.RIGHT)
    add_box(slide, 8.68, 2.25, 3.95, 3.85, PANEL, line_color=LINE)
    add_text(slide, "Transparent scoring", 8.98, 2.57, 3.0, 0.28, 17, WHITE, bold=True)
    add_text(slide, "AQI", 9.0, 3.15, 0.7, 0.25, 15, CYAN, bold=True)
    add_text(slide, "US EPA breakpoint interpolation\nComposite value = max(PM2.5, PM10)", 9.82, 3.08, 2.35, 0.6, 10.5, MUTED)
    add_line(slide, 9.0, 3.94, 3.0, LINE, 1)
    add_text(slide, "CEHI", 9.0, 4.28, 0.7, 0.25, 15, MINT, bold=True)
    add_text(slide, "Air 35%  ·  CO₂ 25%\nNoise 20%  ·  Thermal 20%", 9.82, 4.18, 2.35, 0.62, 10.5, MUTED)
    add_text(slide, "Every score can be explained, audited, and compared across zones.", 9.0, 5.46, 3.1, 0.34, 11, WHITE, bold=True)

    # 07: Dashboard
    slide = new_slide(prs)
    add_title(slide, "06 / Product experience", "The dashboard is built for scanning first, exploring second", "Executive KPIs answer “how are we doing?”; interactive charts answer “where, when, and why?”", 7)
    add_picture(slide, "fig_01_dashboard_overview.png", 0.62, 2.2, 8.0, 4.35)
    add_box(slide, 8.92, 2.2, 3.7, 4.35, PANEL, line_color=LINE)
    add_text(slide, "At a glance", 9.25, 2.52, 2.6, 0.28, 17, WHITE, bold=True)
    add_bullet(slide, "KPI hierarchy", "CEHI, AQI, temperature, humidity, particulates, CO₂, and noise are surfaced together.", 9.25, 3.05, 2.95, CYAN, body_size=10)
    add_bullet(slide, "Filterable context", "Zone, parameter, date range, and hour window support focused investigation.", 9.25, 4.08, 2.95, MINT, body_size=10)
    add_bullet(slide, "Operational signal", "Alerts and status colors keep attention on conditions that need a response.", 9.25, 5.11, 2.95, CORAL, body_size=10)

    # 08: Visual analytics
    slide = new_slide(prs)
    add_title(slide, "07 / Visual analytics", "Three views reveal three different kinds of truth", "The project does not rely on one chart: it combines trend, spatial comparison, and diurnal pattern recognition.", 8)
    add_picture(slide, "fig_02_trend_analysis.png", 0.62, 2.25, 4.0, 2.76)
    add_picture(slide, "fig_03_spatial_radar_comparison.png", 4.82, 2.25, 4.0, 2.76)
    add_picture(slide, "fig_04_diurnal_heatmap.png", 9.02, 2.25, 3.6, 2.76)
    add_text(slide, "TREND", 0.68, 5.25, 1.2, 0.2, 9, CYAN, bold=True)
    add_text(slide, "What changed over time?", 0.68, 5.55, 3.4, 0.25, 13, WHITE, bold=True)
    add_text(slide, "Time-series curves expose spikes, recovery, and long-running drift.", 0.68, 5.88, 3.45, 0.34, 10.5, MUTED)
    add_text(slide, "SPACE", 4.88, 5.25, 1.2, 0.2, 9, MINT, bold=True)
    add_text(slide, "Which zones differ?", 4.88, 5.55, 3.4, 0.25, 13, WHITE, bold=True)
    add_text(slide, "Radar and comparison views make cross-zone health profiles legible.", 4.88, 5.88, 3.45, 0.34, 10.5, MUTED)
    add_text(slide, "TIME OF DAY", 9.08, 5.25, 1.8, 0.2, 9, AMBER, bold=True)
    add_text(slide, "When do risks cluster?", 9.08, 5.55, 3.0, 0.25, 13, WHITE, bold=True)
    add_text(slide, "The heatmap turns recurring daily patterns into a planning signal.", 9.08, 5.88, 3.1, 0.34, 10.5, MUTED)

    # 09: Governance
    slide = new_slide(prs)
    add_title(slide, "08 / Governance and control", "The system supports both analysis and administration", "A usable monitoring platform needs a controlled path from insight to configuration.", 9)
    add_picture(slide, "fig_06_zone_management.png", 0.62, 2.25, 3.78, 2.5)
    add_picture(slide, "fig_07_sensor_fleet.png", 4.78, 2.25, 3.78, 2.5)
    add_picture(slide, "fig_08_alert_thresholds.png", 8.94, 2.25, 3.68, 2.5)
    add_text(slide, "ZONE MANAGEMENT", 0.68, 5.02, 2.6, 0.2, 9, CYAN, bold=True)
    add_text(slide, "Keep the campus model aligned with physical reality.", 0.68, 5.3, 3.5, 0.25, 12.5, WHITE, bold=True)
    add_text(slide, "SENSOR FLEET", 4.84, 5.02, 2.6, 0.2, 9, MINT, bold=True)
    add_text(slide, "Provision stations and monitor their status.", 4.84, 5.3, 3.5, 0.25, 12.5, WHITE, bold=True)
    add_text(slide, "THRESHOLD ENGINE", 9.0, 5.02, 2.6, 0.2, 9, CORAL, bold=True)
    add_text(slide, "Tune warning, poor, and dangerous bands.", 9.0, 5.3, 3.3, 0.25, 12.5, WHITE, bold=True)
    add_box(slide, 0.62, 6.1, 12.0, 0.48, PANEL_2, line_color=LINE)
    add_text(slide, "RBAC: Admin manages the system; Viewer consumes insight. Manual entry and API ingestion support real deployments.", 0.9, 6.24, 11.45, 0.2, 10.5, MUTED, align=PP_ALIGN.CENTER)

    # 10: API and workflow
    slide = new_slide(prs)
    add_title(slide, "09 / Integration", "Designed to grow from demo telemetry into real sensor operations", "The current simulator provides realistic data; the API boundary creates a clean path toward hardware and building systems.", 10)
    add_picture(slide, "fig_10_api_docs_portal.png", 0.62, 2.25, 6.28, 3.98)
    add_box(slide, 7.3, 2.25, 5.32, 3.98, PANEL, line_color=LINE)
    add_text(slide, "Integration surface", 7.66, 2.57, 3.2, 0.28, 18, WHITE, bold=True)
    add_bullet(slide, "RESTful ingestion", "Structured JSON endpoints accept readings and expose zones, sensors, alerts, reports, and health indexes.", 7.66, 3.14, 4.3, CYAN)
    add_bullet(slide, "Manual fallback", "A controlled entry view keeps the system demonstrable and usable before hardware is connected.", 7.66, 4.06, 4.3, MINT)
    add_bullet(slide, "Future-ready", "MQTT, BACnet, HVAC automation, and predictive forecasting can connect without changing the user-facing thesis.", 7.66, 4.98, 4.3, AMBER)

    # 11: Validation
    slide = new_slide(prs)
    add_title(slide, "10 / Validation", "The prototype is tested as a system, not just as a screen", "Automated checks cover data, logic, access control, interactions, and live HTTP behavior.", 11)
    add_metric(slide, "27", "Test cases executed", 0.62, 2.35, 2.75, CYAN)
    add_metric(slide, "100%", "Pass rate", 3.56, 2.35, 2.75, MINT)
    add_metric(slide, "14.56 s", "Full suite runtime", 6.5, 2.35, 2.75, AMBER)
    add_metric(slide, "<50 ms", "Reported API response", 9.44, 2.35, 2.75, CORAL)
    add_box(slide, 0.62, 3.9, 7.35, 2.15, PANEL, line_color=LINE)
    add_text(slide, "Coverage map", 0.95, 4.2, 2.0, 0.28, 17, WHITE, bold=True)
    coverage = [("Authentication & RBAC", CYAN), ("Telemetry & API", MINT), ("AQI / CEHI algorithms", AMBER), ("Analytics & callbacks", "7BA7FF"), ("Database integrity", CORAL), ("Runtime E2E audit", "D66BFF")]
    for idx, (label, accent) in enumerate(coverage):
        col = idx % 2
        row = idx // 2
        add_box(slide, 0.95 + col * 3.35, 4.72 + row * 0.4, 2.95, 0.25, PANEL_2, line_color=LINE)
        add_box(slide, 0.95 + col * 3.35, 4.72 + row * 0.4, 0.08, 0.25, accent, radius=False)
        add_text(slide, label, 1.14 + col * 3.35, 4.755 + row * 0.4, 2.55, 0.16, 9.5, WHITE, bold=True)
    add_box(slide, 8.3, 3.9, 4.32, 2.15, PANEL_2, line_color=LINE)
    add_text(slide, "What the result means", 8.62, 4.2, 3.4, 0.28, 17, WHITE, bold=True)
    add_text(slide, "The core workflow is repeatable: the same request, calculation, storage path, and response can be exercised automatically.", 8.62, 4.78, 3.55, 0.66, 16, CYAN, bold=True, font="Aptos Display")
    add_text(slide, "Evidence from the project test suite and thesis evaluation.", 8.62, 5.67, 3.2, 0.2, 9.5, MUTED)

    # 12: Roadmap
    slide = new_slide(prs)
    add_title(slide, "11 / Roadmap", "A credible foundation for the next research iteration", "The current scope is intentionally focused; the extension path is clear and technically coherent.", 12)
    roadmap = [
        ("NOW", "Validated monitoring platform", "Python full stack · simulated telemetry · explainable scores · operational dashboard", CYAN),
        ("NEXT", "Connect the physical campus", "MQTT / BACnet adapters · calibration workflows · real sensor health and discovery", MINT),
        ("LATER", "Move from reactive to predictive", "2–4 hour forecasts for PM and CO₂ · anomaly detection · demand-controlled ventilation", AMBER),
    ]
    for idx, (stage, title, body, accent) in enumerate(roadmap):
        y = 2.35 + idx * 1.23
        add_box(slide, 0.62, y, 12.0, 0.92, PANEL if idx != 1 else PANEL_2, line_color=LINE)
        add_box(slide, 0.62, y, 1.35, 0.92, accent, radius=False)
        add_text(slide, stage, 0.72, y + 0.31, 1.15, 0.23, 11, BG, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, title, 2.35, y + 0.17, 3.4, 0.24, 15, WHITE, bold=True)
        add_text(slide, body, 5.72, y + 0.18, 6.35, 0.42, 11, MUTED)
    add_box(slide, 0.62, 6.28, 12.0, 0.48, PANEL_2, line_color=LINE)
    add_text(slide, "The approval decision unlocks the next step: pilot the platform against a small set of real campus sensing points.", 0.9, 6.42, 11.45, 0.2, 10.5, WHITE, bold=True, align=PP_ALIGN.CENTER)

    # 13: Close
    slide = new_slide(prs)
    add_box(slide, 8.95, 0, 4.38, 7.5, PANEL, radius=False)
    add_picture(slide, "fig_01_dashboard_overview.png", 9.34, 0.9, 3.55, 2.45)
    add_picture(slide, "fig_09_manual_telemetry_entry.png", 9.34, 3.68, 3.55, 2.15)
    add_text(slide, "12 / REQUEST FOR APPROVAL", 0.7, 0.72, 5.7, 0.25, 10, CYAN, bold=True)
    add_text(slide, "A practical smart-campus\nplatform with a clear\nresearch runway.", 0.66, 1.42, 7.35, 1.65, 31, WHITE, bold=True, font="Aptos Display")
    add_line(slide, 0.72, 3.58, 1.45, MINT, 4)
    add_text(slide, "The project combines a meaningful campus problem, a complete working implementation, explainable analytics, and measurable verification.", 0.72, 4.05, 6.85, 0.75, 17, MUTED)
    add_box(slide, 0.72, 5.25, 6.65, 0.78, PANEL_2, line_color=LINE)
    add_text(slide, "Approval requested: accept the system for university presentation, evaluation, and pilot discussion.", 1.0, 5.49, 6.1, 0.28, 12.5, CYAN, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Thank you", 0.72, 6.52, 2.2, 0.3, 18, WHITE, bold=True, font="Aptos Display")
    add_text(slide, "Questions and discussion", 2.25, 6.57, 3.5, 0.22, 10, MUTED)

    prs.save(OUT)
    print(f"Created {OUT}")


if __name__ == "__main__":
    build()