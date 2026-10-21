"""
Dashboard filter panel component.
Provides dynamic filtering across Campus Zone, Parameter, Date Range, and Time Range.
"""
from datetime import datetime, timedelta
from dash import html, dcc
import dash_bootstrap_components as dbc
from app.utils.helpers import utc_now


def create_filter_panel(zones_list: list) -> dbc.Card:
    """Create the interactive top filter control bar."""
    now = utc_now()
    seven_days_ago = now - timedelta(days=7)

    zone_options = [{"label": "All Campus Zones", "value": "ALL"}]
    for z in zones_list:
        zone_options.append({"label": f"{z.name} ({z.code})", "value": z.id})

    parameter_options = [
        {"label": "PM2.5 Particulate (µg/m³)", "value": "pm25"},
        {"label": "PM10 Particulate (µg/m³)", "value": "pm10"},
        {"label": "Carbon Dioxide (CO2 ppm)", "value": "co2"},
        {"label": "Noise Level (dB)", "value": "noise"},
        {"label": "Temperature (°C)", "value": "temperature"},
        {"label": "Relative Humidity (%)", "value": "humidity"},
        {"label": "Air Quality Index (AQI)", "value": "aqi"}
    ]

    return dbc.Card(
        dbc.CardBody(
            [
                # Row 1: Primary Controls and Actions
                dbc.Row(
                    [
                        # Zone Dropdown
                        dbc.Col(
                            [
                                html.Label(
                                    [html.I(className="bi bi-geo-alt me-1 text-primary"), "Campus Zone"],
                                    className="form-label fw-semibold text-secondary small mb-1"
                                ),
                                dcc.Dropdown(
                                    id="filter-zone",
                                    options=zone_options,
                                    value="ALL",
                                    clearable=False,
                                    className="dash-dropdown"
                                )
                            ],
                            xs=12, sm=6, md=3, lg=3,
                            className="mb-2"
                        ),

                        # Parameter Dropdown
                        dbc.Col(
                            [
                                html.Label(
                                    [html.I(className="bi bi-sliders2 me-1 text-primary"), "Primary Parameter"],
                                    className="form-label fw-semibold text-secondary small mb-1"
                                ),
                                dcc.Dropdown(
                                    id="filter-parameter",
                                    options=parameter_options,
                                    value="pm25",
                                    clearable=False,
                                    className="dash-dropdown"
                                )
                            ],
                            xs=12, sm=6, md=3, lg=3,
                            className="mb-2"
                        ),

                        # Date Range Picker
                        dbc.Col(
                            [
                                html.Label(
                                    [html.I(className="bi bi-calendar3 me-1 text-primary"), "Telemetry Date Range"],
                                    className="form-label fw-semibold text-secondary small mb-1"
                                ),
                                html.Div(
                                    dcc.DatePickerRange(
                                        id="filter-date-range",
                                        start_date=seven_days_ago.date(),
                                        end_date=now.date(),
                                        display_format="YYYY-MM-DD",
                                        className="dash-datepicker w-100"
                                    ),
                                    className="d-flex"
                                )
                            ],
                            xs=12, sm=6, md=3, lg=3,
                            className="mb-2"
                        ),

                        # Action Buttons Row
                        dbc.Col(
                            [
                                html.Label("Telemetry Actions", className="form-label fw-semibold text-secondary small mb-1 d-block"),
                                html.Div(
                                    [
                                        dbc.Button(
                                            [html.I(className="bi bi-arrow-clockwise me-1"), "Refresh"],
                                            id="btn-refresh-data",
                                            color="primary",
                                            size="sm",
                                            className="px-2 fw-medium shadow-sm"
                                        ),
                                        dbc.Button(
                                            [html.I(className="bi bi-arrow-counterclockwise me-1"), "Reset"],
                                            id="btn-reset-filters",
                                            color="outline-secondary",
                                            size="sm",
                                            className="px-2 fw-medium"
                                        ),
                                        dbc.Button(
                                            [html.I(className="bi bi-lightning-charge-fill me-1"), "Simulate"],
                                            id="btn-simulate-reading",
                                            color="success",
                                            outline=True,
                                            size="sm",
                                            className="px-2 fw-medium shadow-sm",
                                            title="Generate live telemetry reading immediately"
                                        ),
                                        dbc.Button(
                                            [html.I(className="bi bi-download me-1"), "CSV"],
                                            id="btn-export-csv",
                                            color="outline-dark",
                                            size="sm",
                                            className="px-2 fw-medium shadow-sm"
                                        ),
                                        dcc.Download(id="download-dataframe-csv")
                                    ],
                                    className="d-flex align-items-center gap-1 flex-wrap"
                                )
                            ],
                            xs=12, sm=6, md=3, lg=3,
                            className="mb-2 d-flex flex-column justify-content-end"
                        )
                    ],
                    align="center"
                ),

                # Row 2: Quick Parameter Pills
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.Small("Quick Parameter Select:", className="text-muted fw-semibold me-2 d-none d-md-inline"),
                                        dbc.ButtonGroup(
                                            [
                                                dbc.Button("PM2.5", id="pill-param-pm25", size="sm", color="light", className="border px-2 py-1 small fw-medium"),
                                                dbc.Button("PM10", id="pill-param-pm10", size="sm", color="light", className="border px-2 py-1 small fw-medium"),
                                                dbc.Button("CO2", id="pill-param-co2", size="sm", color="light", className="border px-2 py-1 small fw-medium"),
                                                dbc.Button("Noise", id="pill-param-noise", size="sm", color="light", className="border px-2 py-1 small fw-medium"),
                                                dbc.Button("Temperature", id="pill-param-temperature", size="sm", color="light", className="border px-2 py-1 small fw-medium"),
                                                dbc.Button("Humidity", id="pill-param-humidity", size="sm", color="light", className="border px-2 py-1 small fw-medium"),
                                                dbc.Button("AQI", id="pill-param-aqi", size="sm", color="light", className="border px-2 py-1 small fw-medium"),
                                            ],
                                            className="flex-wrap gap-1"
                                        )
                                    ],
                                    className="d-flex align-items-center flex-wrap pt-2 mt-1 border-top border-light"
                                )
                            ],
                            xs=12
                        )
                    ]
                ),

                # Row 3: Time range slider
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.Small("Daily Hour Window Filter: ", className="text-muted fw-semibold me-2"),
                                        html.Span(id="time-slider-output", className="text-primary fw-bold small"),
                                    ],
                                    className="d-flex align-items-center mb-1"
                                ),
                                dcc.RangeSlider(
                                    id="filter-time-range",
                                    min=0,
                                    max=23,
                                    step=1,
                                    marks={i: f"{i:02d}:00" for i in range(0, 24, 3)},
                                    value=[0, 23],
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ],
                            xs=12
                        )
                    ],
                    className="mt-2 pt-2 border-top border-light"
                )
            ],
            className="p-3"
        ),
        className="shadow-sm border-0 rounded-3 mb-4"
    )
