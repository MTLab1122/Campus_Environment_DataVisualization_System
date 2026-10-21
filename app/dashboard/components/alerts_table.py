"""
Active alerts table component for dashboard monitoring.
"""
from typing import List
from dash import html
import dash_bootstrap_components as dbc
from app.models.alert import Alert


def create_alerts_panel(alerts: List[Alert]) -> dbc.Card:
    """Create interactive alerts overview card."""
    if not alerts:
        content = html.Div(
            [
                html.Div(
                    html.I(className="bi bi-shield-check text-success fs-1"),
                    className="mb-2"
                ),
                html.H6("No Active Environmental Anomalies", className="text-dark fw-bold mb-1"),
                html.P("All campus environmental parameters are currently within calibrated baseline limits.", className="text-muted small mb-0")
            ],
            className="text-center py-4 bg-light rounded-3 border border-dashed"
        )
    else:
        rows = []
        for a in alerts:
            if a.severity == "Dangerous":
                badge_color = "danger"
                border_style = "border-start border-danger border-4"
                icon = "bi-exclamation-triangle-fill text-danger"
            elif a.severity == "Poor":
                badge_color = "warning"
                border_style = "border-start border-warning border-4"
                icon = "bi-exclamation-circle-fill text-warning"
            else:
                badge_color = "info"
                border_style = "border-start border-info border-4"
                icon = "bi-info-circle-fill text-info"

            time_str = a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else "Recent"
            zone_name = a.zone.name if a.zone else f"Zone #{a.zone_id}"

            item = html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.I(className=f"bi {icon} me-2"),
                                            html.Span(a.severity.upper(), className=f"badge bg-{badge_color} text-uppercase me-2 fw-bold"),
                                            html.Span(zone_name, className="fw-bold text-dark"),
                                            html.Span(f" • {time_str}", className="text-muted small ms-1"),
                                        ],
                                        className="d-flex align-items-center"
                                    ),
                                    html.P(a.message, className="small text-secondary mb-0 mt-1 ps-4")
                                ],
                                xs=9, md=10
                            ),
                            dbc.Col(
                                [
                                    dbc.Button(
                                        [html.I(className="bi bi-check2 me-1"), "Resolve"],
                                        id={"type": "btn-resolve-alert", "index": a.id},
                                        color="success",
                                        outline=True,
                                        size="sm",
                                        className="py-1 px-3 small rounded-pill fw-semibold shadow-sm"
                                    )
                                ],
                                xs=3, md=2,
                                className="d-flex align-items-center justify-content-end"
                            )
                        ],
                        align="center"
                    )
                ],
                className=f"p-3 mb-2 bg-white rounded-3 shadow-sm {border_style}"
            )
            rows.append(item)

        content = html.Div(rows, style={"maxHeight": "360px", "overflowY": "auto"}, className="pe-1")

    # Header buttons
    header_buttons = [
        html.A(
            [html.I(className="bi bi-sliders me-1"), "Threshold Settings"],
            href="/admin/thresholds",
            className="btn btn-sm btn-outline-secondary rounded-pill px-3 me-2"
        )
    ]
    if alerts:
        header_buttons.insert(
            0,
            dbc.Button(
                [html.I(className="bi bi-check-all me-1"), "Resolve All"],
                id="btn-resolve-all-alerts",
                color="outline-success",
                size="sm",
                className="rounded-pill px-3 me-2 fw-semibold shadow-sm"
            )
        )

    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.H5(
                                [
                                    html.I(className="bi bi-bell-fill text-danger me-2"),
                                    "Active Environmental Alerts",
                                    html.Span(f"{len(alerts)} Active", className="badge bg-danger ms-2 fs-6 rounded-pill fw-semibold") if alerts else None
                                ],
                                className="fw-bold mb-0 d-flex align-items-center"
                            ),
                            xs=12, md=7
                        ),
                        dbc.Col(
                            html.Div(header_buttons, className="d-flex justify-content-md-end align-items-center mt-2 mt-md-0"),
                            xs=12, md=5
                        )
                    ],
                    align="center",
                    className="mb-3"
                ),
                content
            ],
            className="p-3"
        ),
        id="section-alerts",
        className="shadow-sm border-0 rounded-3 mb-4"
    )
