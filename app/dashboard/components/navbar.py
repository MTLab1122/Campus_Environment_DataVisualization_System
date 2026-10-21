"""
Dashboard navigation bar component.
"""
from dash import html
import dash_bootstrap_components as dbc


def create_navbar() -> dbc.Navbar:
    """Create a modern responsive top navigation bar for the dashboard."""
    # Determine user authentication status
    user_nav_item = None
    try:
        from flask_login import current_user
        if current_user and current_user.is_authenticated:
            user_nav_item = dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem(
                        [
                            html.Span(current_user.username, className="fw-bold d-block text-dark small"),
                            html.Small(current_user.email, className="text-muted d-block text-truncate", style={"maxWidth": "180px"})
                        ],
                        header=True
                    ),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem([html.I(className="bi bi-geo-alt text-primary me-2"), "Campus Zones"], href="/admin/zones"),
                    dbc.DropdownMenuItem([html.I(className="bi bi-cpu text-info me-2"), "Hardware Sensors"], href="/admin/sensors"),
                    dbc.DropdownMenuItem([html.I(className="bi bi-bell text-warning me-2"), "Alert Thresholds"], href="/admin/thresholds"),
                    dbc.DropdownMenuItem([html.I(className="bi bi-pencil-square text-success me-2"), "Manual Telemetry"], href="/admin/readings/manual"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem([html.I(className="bi bi-box-arrow-right text-danger me-2"), "Sign Out"], href="/logout"),
                ],
                nav=True,
                in_navbar=True,
                label=[
                    html.I(className="bi bi-person-circle text-primary me-1"),
                    f" {current_user.username} ",
                    html.Span(current_user.role.upper(), className=f"badge {'bg-primary' if current_user.role == 'admin' else 'bg-secondary'} ms-1", style={"fontSize": "10px"})
                ],
                className="ms-2"
            )
    except Exception:
        pass

    if not user_nav_item:
        user_nav_item = dbc.NavItem(
            dbc.Button(
                [html.I(className="bi bi-box-arrow-in-right me-1"), "Sign In"],
                href="/login",
                color="primary",
                size="sm",
                className="ms-2 rounded-pill px-3 fw-semibold shadow-sm"
            )
        )

    return dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    html.I(className="bi bi-tree-fill text-success fs-4"),
                                    className="d-flex align-items-center me-2 p-2 bg-success-subtle rounded-circle"
                                )
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        html.H5("Campus Environment", className="mb-0 fw-bold text-dark"),
                                        html.Small("IoT Atmospheric Telemetry & Analytics", className="text-muted small")
                                    ]
                                )
                            )
                        ],
                        align="center",
                        className="g-0"
                    ),
                    href="/dashboard/",
                    style={"textDecoration": "none"}
                ),
                dbc.Nav(
                    [
                        dbc.NavItem(
                            dbc.NavLink(
                                [html.I(className="bi bi-speedometer2 me-1"), "Dashboard"],
                                href="/dashboard/",
                                active=True,
                                className="fw-semibold text-primary px-3 rounded-pill active-nav-pill"
                            )
                        ),
                        dbc.NavItem(
                            dbc.NavLink(
                                [html.I(className="bi bi-graph-up me-1"), "Analytics"],
                                href="#chart-trend-line",
                                className="fw-medium text-secondary px-2"
                            )
                        ),
                        dbc.NavItem(
                            dbc.NavLink(
                                [html.I(className="bi bi-bell me-1"), "Alerts"],
                                href="#section-alerts",
                                className="fw-medium text-secondary px-2"
                            )
                        ),
                        dbc.NavItem(
                            dbc.NavLink(
                                [html.I(className="bi bi-file-earmark-bar-graph me-1"), "Reports"],
                                href="#section-reports",
                                className="fw-medium text-secondary px-2"
                            )
                        ),
                        dbc.NavItem(
                            dbc.NavLink(
                                [html.I(className="bi bi-code-slash me-1 text-primary"), "API Docs"],
                                href="/api/docs",
                                className="fw-medium text-secondary px-2"
                            )
                        ),

                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem(
                                    [html.I(className="bi bi-geo-alt-fill me-2 text-primary"), "Campus Zones"],
                                    href="/admin/zones"
                                ),
                                dbc.DropdownMenuItem(
                                    [html.I(className="bi bi-cpu-fill me-2 text-info"), "Hardware Sensors"],
                                    href="/admin/sensors"
                                ),
                                dbc.DropdownMenuItem(
                                    [html.I(className="bi bi-sliders me-2 text-warning"), "Alert Thresholds"],
                                    href="/admin/thresholds"
                                ),
                                dbc.DropdownMenuItem(divider=True),
                                dbc.DropdownMenuItem(
                                    [html.I(className="bi bi-pencil-square me-2 text-success"), "Manual Ingestion Form"],
                                    href="/admin/readings/manual"
                                ),
                            ],
                            nav=True,
                            in_navbar=True,
                            label="Management",
                            className="fw-medium text-secondary px-1"
                        ),
                        user_nav_item
                    ],
                    className="ms-auto align-items-center flex-wrap",
                    navbar=True
                )
            ],
            fluid=True,
            className="px-4"
        ),
        color="white",
        dark=False,
        sticky="top",
        className="shadow-sm py-2 border-bottom border-light"
    )
