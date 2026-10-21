"""
Reports component displaying daily, weekly, and monthly environmental summaries.
"""
from typing import Dict, Any
from dash import html, dcc
import dash_bootstrap_components as dbc
from app.utils.aqi_calculator import get_aqi_details


def create_reports_card(report_data: Dict[str, Any]) -> dbc.Card:
    """Render structured report summary card."""
    zone_summaries = report_data.get("zone_summaries", [])
    period = report_data.get("period", "daily").lower()
    period_title = report_data.get("title", "Environmental Report")
    alert_count = report_data.get("alert_count", 0)
    reading_count = report_data.get("reading_count", 0)

    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Campus Zone", className="ps-3"),
                    html.Th("Readings Count"),
                    html.Th("Avg Temp (°C)"),
                    html.Th("Avg Humidity (%)"),
                    html.Th("Avg PM2.5 (µg/m³)"),
                    html.Th("Avg CO2 (ppm)"),
                    html.Th("Avg Noise (dB)"),
                    html.Th("Calculated AQI", className="pe-3")
                ],
                className="table-light text-uppercase small text-secondary"
            )
        )
    ]

    table_rows = []
    for z in zone_summaries:
        aqi_val = int(z.get("avg_aqi", 0))
        aqi_meta = get_aqi_details(aqi_val)
        table_rows.append(
            html.Tr(
                [
                    html.Td(html.Strong(z.get("zone_name")), className="ps-3 text-dark"),
                    html.Td(f"{z.get('reading_count', 0):,}"),
                    html.Td(f"{z.get('avg_temperature', 0):.1f}"),
                    html.Td(f"{z.get('avg_humidity', 0):.1f}"),
                    html.Td(f"{z.get('avg_pm25', 0):.1f}"),
                    html.Td(f"{int(z.get('avg_co2', 0))}"),
                    html.Td(f"{z.get('avg_noise', 0):.1f}"),
                    html.Td(
                        html.Span(
                            f"AQI {aqi_val} • {aqi_meta['category']}",
                            className=f"badge bg-{aqi_meta['badge']}-subtle text-{aqi_meta['badge']} border border-{aqi_meta['badge']}-subtle rounded-pill px-2 py-1 small fw-bold"
                        ),
                        className="pe-3"
                    )
                ]
            )
        )

    if not table_rows:
        table_body = [
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                "No telemetry aggregated for this period. Try switching period or resetting filters.",
                                colSpan=8,
                                className="text-center text-muted py-4"
                            )
                        ]
                    )
                ]
            )
        ]
    else:
        table_body = [html.Tbody(table_rows)]

    table = dbc.Table(
        table_header + table_body,
        bordered=False,
        hover=True,
        responsive=True,
        striped=True,
        className="mb-0 align-middle small"
    )

    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H5(
                                    [html.I(className="bi bi-file-earmark-bar-graph-fill text-primary me-2"), period_title],
                                    className="fw-bold mb-1"
                                ),
                                html.Div(
                                    [
                                        html.Span(f"Total Telemetry: {reading_count:,} records", className="badge bg-light text-secondary border me-2"),
                                        html.Span(f"Anomalies: {alert_count}", className="badge bg-danger-subtle text-danger border border-danger-subtle me-2" if alert_count > 0 else "badge bg-success-subtle text-success border border-success-subtle me-2"),
                                        html.Span(f"Monitored Zones: {len(zone_summaries)}", className="badge bg-info-subtle text-info border border-info-subtle"),
                                    ],
                                    className="d-flex align-items-center flex-wrap mt-1"
                                )
                            ],
                            xs=12, md=7
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    dbc.ButtonGroup(
                                        [
                                            dbc.Button("Daily (24h)", id="btn-report-daily", color="primary" if period == "daily" else "outline-primary", size="sm", className="fw-medium"),
                                            dbc.Button("Weekly (7d)", id="btn-report-weekly", color="primary" if period == "weekly" else "outline-primary", size="sm", className="fw-medium"),
                                            dbc.Button("Monthly (30d)", id="btn-report-monthly", color="primary" if period == "monthly" else "outline-primary", size="sm", className="fw-medium")
                                        ],
                                        className="shadow-sm"
                                    ),
                                    dbc.Button(
                                        [html.I(className="bi bi-download me-1"), "Export Report"],
                                        id="btn-export-report-csv",
                                        color="outline-secondary",
                                        size="sm",
                                        className="ms-2 rounded-pill fw-medium shadow-sm"
                                    ),
                                    dcc.Download(id="download-report-csv")
                                ],
                                className="d-flex justify-content-md-end align-items-center mt-2 mt-md-0"
                            ),
                            xs=12, md=5
                        )
                    ],
                    align="center",
                    className="mb-3"
                ),
                table
            ],
            className="p-3"
        ),
        id="section-reports",
        className="shadow-sm border-0 rounded-3 mb-4"
    )
