"""
Plotly Dash layout assembly for the Campus Environment Data Visualization System.
"""
from datetime import datetime
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from app.models.campus_zone import CampusZone
from app.dashboard.components.navbar import create_navbar
from app.dashboard.components.filter_panel import create_filter_panel
from app.utils.helpers import utc_now


def create_dashboard_layout(dash_app=None) -> html.Div:
    """Construct full dashboard DOM tree with responsive layout containers."""
    try:
        zones = CampusZone.query.order_by(CampusZone.name.asc()).all()
    except Exception:
        zones = []

    return html.Div(
        [
            # Navigation Bar
            create_navbar(),

            # Main Application Container
            dbc.Container(
                [
                    # Header Banner
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H2("Campus Environmental Intelligence Dashboard", className="fw-bold text-dark mb-1"),
                                    html.P(
                                        "Multi-zone IoT atmospheric telemetry, indoor air safety, acoustic surveillance, and predictive quality analysis.",
                                        className="text-muted"
                                    )
                                ],
                                xs=12, md=8
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                [html.I(className="bi bi-circle-fill text-success me-2 fs-6 pulse-green"), "Telemetry Engine Online"],
                                                className="badge bg-success-subtle text-success border border-success-subtle px-3 py-2 rounded-pill fs-6 fw-semibold"
                                            ),
                                            html.Small(
                                                f"Refreshed: {utc_now().strftime('%Y-%m-%d %H:%M UTC')}",
                                                id="label-last-refreshed",
                                                className="text-muted d-block mt-1"
                                            )
                                        ],
                                        className="text-md-end"
                                    )
                                ],
                                xs=12, md=4,
                                className="d-flex align-items-center justify-content-md-end mt-2 mt-md-0"
                            )
                        ],
                        className="my-3 py-2"
                    ),

                    # Filter Control Panel
                    create_filter_panel(zones),

                    # Dynamic Metric Cards Container (Populated via callback)
                    html.Div(id="container-metric-cards", className="mb-4"),

                    # Active Alerts Notification Container (Populated via callback)
                    html.Div(id="container-alerts-panel"),

                    # Primary Visualizations Row (Trend Line Chart + Gauge Chart)
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            dcc.Loading(
                                                dcc.Graph(
                                                    id="chart-trend-line",
                                                    config={"displayModeBar": True, "responsive": True},
                                                    style={"height": "420px"}
                                                ),
                                                type="default"
                                            )
                                        ],
                                        className="p-2"
                                    ),
                                    className="shadow-sm border-0 rounded-3 h-100"
                                ),
                                xs=12, lg=8,
                                className="mb-4"
                            ),
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            dcc.Loading(
                                                dcc.Graph(
                                                    id="chart-gauge",
                                                    config={"displayModeBar": False, "responsive": True},
                                                    style={"height": "250px"}
                                                ),
                                                type="default"
                                            ),
                                            html.Div(
                                                id="container-zone-quick-list",
                                                className="mt-2 border-top border-light pt-2",
                                                style={"maxHeight": "160px", "overflowY": "auto"}
                                            )
                                        ],
                                        className="p-3"
                                    ),
                                    className="shadow-sm border-0 rounded-3 h-100"
                                ),
                                xs=12, lg=4,
                                className="mb-4"
                            )
                        ],
                        className="g-3"
                    ),

                    # Secondary Visualizations Row (Bar Comparison + Distribution Box Plot)
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            dcc.Loading(
                                                dcc.Graph(
                                                    id="chart-zone-bar",
                                                    config={"displayModeBar": True, "responsive": True},
                                                    style={"height": "380px"}
                                                ),
                                                type="default"
                                            )
                                        ],
                                        className="p-2"
                                    ),
                                    className="shadow-sm border-0 rounded-3 h-100"
                                ),
                                xs=12, lg=6,
                                className="mb-4"
                            ),
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            dcc.Loading(
                                                dcc.Graph(
                                                    id="chart-distribution-box",
                                                    config={"displayModeBar": True, "responsive": True},
                                                    style={"height": "380px"}
                                                ),
                                                type="default"
                                            )
                                        ],
                                        className="p-2"
                                    ),
                                    className="shadow-sm border-0 rounded-3 h-100"
                                ),
                                xs=12, lg=6,
                                className="mb-4"
                            )
                        ],
                        className="g-3"
                    ),

                    # Tertiary Visualizations Row (Diurnal Heatmap)
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            dcc.Loading(
                                                dcc.Graph(
                                                    id="chart-diurnal-heatmap",
                                                    config={"displayModeBar": True, "responsive": True},
                                                    style={"height": "380px"}
                                                ),
                                                type="default"
                                            )
                                        ],
                                        className="p-2"
                                    ),
                                    className="shadow-sm border-0 rounded-3 h-100"
                                ),
                                xs=12,
                                className="mb-4"
                            )
                        ]
                    ),

                    # Quaternary Visualizations Row (Multi-Dimensional Radar Chart)
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            dcc.Loading(
                                                dcc.Graph(
                                                    id="chart-zone-radar",
                                                    config={"displayModeBar": True, "responsive": True},
                                                    style={"height": "420px"}
                                                ),
                                                type="default"
                                            )
                                        ],
                                        className="p-2"
                                    ),
                                    className="shadow-sm border-0 rounded-3 h-100"
                                ),
                                xs=12,
                                className="mb-4"
                            )
                        ]
                    ),

                    # Interactive Filtered Readings Data Table

                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        html.H5(
                                                            [html.I(className="bi bi-table text-primary me-2"), "Filtered Environmental Readings"],
                                                            className="fw-bold mb-0"
                                                        ),
                                                        xs=8
                                                    ),
                                                    dbc.Col(
                                                        html.Small(id="label-table-count", className="text-muted fw-semibold"),
                                                        xs=4,
                                                        className="text-end"
                                                    )
                                                ],
                                                align="center",
                                                className="mb-3"
                                            ),
                                            dcc.Loading(
                                                dash_table.DataTable(
                                                    id="table-filtered-readings",
                                                    columns=[
                                                        {"name": "ID", "id": "id"},
                                                        {"name": "Timestamp", "id": "timestamp_str"},
                                                        {"name": "Campus Zone", "id": "zone_name"},
                                                        {"name": "Sensor Code", "id": "sensor_code"},
                                                        {"name": "Temp (°C)", "id": "temperature"},
                                                        {"name": "Humidity (%)", "id": "humidity"},
                                                        {"name": "PM2.5 (µg/m³)", "id": "pm25"},
                                                        {"name": "PM10 (µg/m³)", "id": "pm10"},
                                                        {"name": "CO2 (ppm)", "id": "co2"},
                                                        {"name": "Noise (dB)", "id": "noise"},
                                                        {"name": "AQI", "id": "aqi"},
                                                        {"name": "Weather", "id": "weather_condition"}
                                                    ],
                                                    data=[],
                                                    page_size=12,
                                                    page_action="native",
                                                    sort_action="native",
                                                    filter_action="native",
                                                    style_table={"overflowX": "auto"},
                                                    style_as_list_view=True,
                                                    style_header={
                                                        "backgroundColor": "#F8FAFC",
                                                        "fontWeight": "bold",
                                                        "color": "#334155",
                                                        "borderBottom": "2px solid #E2E8F0"
                                                    },
                                                    style_cell={
                                                        "fontFamily": "Inter, sans-serif",
                                                        "fontSize": "13px",
                                                        "padding": "10px 12px",
                                                        "textAlign": "left"
                                                    },
                                                    style_data_conditional=[
                                                        {"if": {"row_index": "odd"}, "backgroundColor": "#FDFDFD"},
                                                        {
                                                            "if": {"filter_query": "{aqi} > 100", "column_id": "aqi"},
                                                            "color": "#EF4444",
                                                            "fontWeight": "bold"
                                                        }
                                                    ]
                                                ),
                                                type="default"
                                            )
                                        ],
                                        className="p-3"
                                    ),
                                    className="shadow-sm border-0 rounded-3 mb-4"
                                ),
                                xs=12
                            )
                        ]
                    ),

                    # Reports Summary Section (Populated via callback)
                    html.Div(id="container-reports-card"),

                    # System State Stores and Poll Interval
                    dcc.Store(id="store-report-period", data="daily"),
                    dcc.Store(id="store-alert-resolved-trigger", data=0),
                    dcc.Store(id="store-simulated-reading-trigger", data=0),
                    dcc.Interval(id="interval-auto-refresh", interval=60000, n_intervals=0)  # 60s
                ],
                fluid=True,
                className="px-4 py-2"
            ),

            # Footer
            html.Footer(
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Small("Campus Environment Data Visualization System • Python Full-Stack Architecture", className="text-muted"),
                                    xs=12, md=6
                                ),
                                dbc.Col(
                                    html.Small("Powered by Flask, Plotly Dash, SQLAlchemy, and Pandas", className="text-muted text-md-end"),
                                    xs=12, md=6,
                                    className="text-md-end"
                                )
                            ]
                        )
                    ],
                    fluid=True,
                    className="px-4 py-3 border-top mt-5 bg-white"
                )
            )
        ],
        className="bg-light min-vh-100"
    )
