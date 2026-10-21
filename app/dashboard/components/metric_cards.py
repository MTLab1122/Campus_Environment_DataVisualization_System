"""
Dashboard metric cards component.
Renders summary KPI cards for Temperature, Humidity, PM2.5, PM10, CO2, Noise, and AQI.
"""
from typing import Dict, Any
from dash import html
import dash_bootstrap_components as dbc


def build_metric_card(
    title: str,
    value: str,
    unit: str,
    icon: str,
    color_class: str,
    trend_text: str = "",
    trend_positive: bool = True
) -> dbc.Card:
    """Helper to build a unified aesthetic KPI card."""
    trend_icon = "bi-arrow-up" if trend_positive else "bi-arrow-down"
    trend_color = "text-danger" if (trend_positive and title in ["PM2.5", "PM10", "CO2", "Noise", "AQI"]) else "text-success"
    
    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.P(title, className="text-muted fw-semibold text-uppercase small mb-1"),
                                html.H3(
                                    [
                                        f"{value}",
                                        html.Span(f" {unit}", className="fs-6 text-muted fw-normal ms-1")
                                    ],
                                    className="fw-bold mb-1 text-dark"
                                ),
                                html.Small(
                                    [
                                        html.I(className=f"bi {trend_icon} me-1 {trend_color}"),
                                        html.Span(trend_text, className=trend_color)
                                    ] if trend_text else "Real-time reading",
                                    className="small"
                                )
                            ],
                            xs=9
                        ),
                        dbc.Col(
                            html.Div(
                                html.I(className=f"bi {icon} fs-3"),
                                className=f"p-3 rounded-circle text-center d-flex align-items-center justify-content-center {color_class}",
                                style={"width": "54px", "height": "54px"}
                            ),
                            xs=3,
                            className="d-flex justify-content-end align-items-center"
                        )
                    ],
                    align="center"
                )
            ],
            className="p-3"
        ),
        className="shadow-sm border-0 rounded-3 h-100 metric-hover-card"
    )


def create_metric_cards_row(metrics: Dict[str, Any]) -> dbc.Row:
    """Construct a responsive, perfectly balanced grid of environmental metric cards."""
    temp_data = metrics.get("temperature", {})
    hum_data = metrics.get("humidity", {})
    pm25_data = metrics.get("pm25", {})
    pm10_data = metrics.get("pm10", {})
    co2_data = metrics.get("co2", {})
    noise_data = metrics.get("noise", {})
    aqi_data = metrics.get("aqi", {})
    aqi_details = metrics.get("aqi_details", {"category": "Good", "color": "#10B981", "badge": "success"})

    # Health advisory based on AQI category
    cat = aqi_details.get("category", "Good")
    advisories = {
        "Good": "Air quality is satisfactory; atmospheric pollution poses little or no health risk across all campus zones.",
        "Moderate": "Air quality is acceptable; unusually sensitive individuals should consider limiting prolonged outdoor exertion.",
        "Unhealthy for Sensitive Groups": "Sensitive groups (asthma/respiratory) may experience health effects; general campus public is less affected.",
        "Unhealthy": "Some members of the campus public may experience health effects; sensitive members may experience more serious effects.",
        "Very Unhealthy": "Health alert: The risk of health effects is increased for everyone on campus. Limit outdoor sports.",
        "Hazardous": "Health warning of emergency conditions: Everyone is likely to be affected. Shelter indoors with air filtration."
    }
    advisory = advisories.get(cat, "Continuous multi-zone ambient surveillance active.")
    aqi_color = aqi_details.get("color", "#10B981")

    # Campus Health Score
    health = metrics.get("health_score", {})
    h_score = health.get("score", 85.0)
    h_grade = health.get("grade", "A")
    h_label = health.get("grade_label", "Very Good")
    sub_indices = health.get("sub_indices", {})

    return dbc.Row(
        [
            # Left Column: Hero AQI & Campus Health Index Card
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("CAMPUS COMPOSITE AQI", className="text-white-50 fw-bold small text-uppercase", style={"letterSpacing": "0.08em"}),
                                            html.H2(f"{int(aqi_data.get('current', 0))}", className="display-4 fw-bold text-white mb-0 mt-1"),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        f"Status: {cat}",
                                                        className="badge bg-white text-dark fw-bold px-2 py-1 me-2 rounded-pill shadow-sm"
                                                    ),
                                                    html.Small("EPA Standard", className="text-white-50")
                                                ],
                                                className="mt-2"
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span("HEALTH INDEX", className="text-white-50 fw-semibold d-block", style={"fontSize": "10px", "letterSpacing": "0.06em"}),
                                                    html.Span(f"{h_score}", className="fs-3 fw-bold text-white"),
                                                    html.Span(f"/100", className="small text-white-50 ms-1"),
                                                    html.Span(f"Grade {h_grade}", className="badge bg-dark bg-opacity-25 text-white d-block mt-1 fw-bold", style={"fontSize": "10px"})
                                                ],
                                                className="text-end bg-white bg-opacity-10 p-2 rounded-3 border border-white border-opacity-10"
                                            )
                                        ],
                                        className="d-none d-sm-block text-end"
                                    )
                                ],
                                className="d-flex justify-content-between align-items-start"
                            ),
                            # Mini Health Indicators
                            html.Div(
                                [
                                    html.Div([html.Span("Air", className="text-white-50 small d-block", style={"fontSize": "10px"}), html.Span(f"{sub_indices.get('air_quality', 85):.0f}%", className="fw-bold text-white small")], className="text-center flex-fill"),
                                    html.Div([html.Span("Ventilation", className="text-white-50 small d-block", style={"fontSize": "10px"}), html.Span(f"{sub_indices.get('ventilation', 85):.0f}%", className="fw-bold text-white small")], className="text-center flex-fill border-start border-white border-opacity-25"),
                                    html.Div([html.Span("Acoustics", className="text-white-50 small d-block", style={"fontSize": "10px"}), html.Span(f"{sub_indices.get('acoustics', 80):.0f}%", className="fw-bold text-white small")], className="text-center flex-fill border-start border-white border-opacity-25"),
                                    html.Div([html.Span("Thermal", className="text-white-50 small d-block", style={"fontSize": "10px"}), html.Span(f"{sub_indices.get('thermal_comfort', 85):.0f}%", className="fw-bold text-white small")], className="text-center flex-fill border-start border-white border-opacity-25"),
                                ],
                                className="d-flex bg-black bg-opacity-10 rounded-2 p-2 mt-2"
                            ),
                            html.P(
                                advisory,
                                className="small text-white text-opacity-75 mb-0 mt-2 pt-2 border-top border-white border-opacity-10",
                                style={"lineHeight": "1.3", "fontSize": "12px"}
                            )
                        ],
                        className="p-3 d-flex flex-column justify-content-between h-100"
                    ),
                    style={
                        "background": f"linear-gradient(135deg, {aqi_color} 0%, {aqi_color}dd 100%)",
                        "boxShadow": f"0 10px 20px -5px {aqi_color}40"
                    },
                    className="border-0 rounded-3 text-white h-100 metric-hover-card"
                ),
                xs=12, lg=4,
                className="mb-3"
            ),


            # Right Column: 6 Core Environmental Parameter Cards in 3x2 Grid
            dbc.Col(
                dbc.Row(
                    [
                        # Temperature
                        dbc.Col(
                            build_metric_card(
                                title="Temperature",
                                value=f"{temp_data.get('current', 0.0)}",
                                unit="°C",
                                icon="bi-thermometer-half",
                                color_class="bg-warning-subtle text-warning",
                                trend_text=f"{abs(temp_data.get('trend_pct', 0.0))}% vs 24h",
                                trend_positive=temp_data.get('trend_pct', 0.0) >= 0
                            ),
                            xs=12, sm=6, md=4,
                            className="mb-3"
                        ),
                        # Humidity
                        dbc.Col(
                            build_metric_card(
                                title="Humidity",
                                value=f"{hum_data.get('current', 0.0)}",
                                unit="%",
                                icon="bi-droplet-half",
                                color_class="bg-info-subtle text-info",
                                trend_text=f"{abs(hum_data.get('trend_pct', 0.0))}% vs 24h",
                                trend_positive=hum_data.get('trend_pct', 0.0) >= 0
                            ),
                            xs=12, sm=6, md=4,
                            className="mb-3"
                        ),
                        # PM2.5
                        dbc.Col(
                            build_metric_card(
                                title="PM2.5",
                                value=f"{pm25_data.get('current', 0.0)}",
                                unit="µg/m³",
                                icon="bi-wind",
                                color_class="bg-danger-subtle text-danger",
                                trend_text=f"{abs(pm25_data.get('trend_pct', 0.0))}% vs 24h",
                                trend_positive=pm25_data.get('trend_pct', 0.0) >= 0
                            ),
                            xs=12, sm=6, md=4,
                            className="mb-3"
                        ),
                        # PM10
                        dbc.Col(
                            build_metric_card(
                                title="PM10",
                                value=f"{pm10_data.get('current', 0.0)}",
                                unit="µg/m³",
                                icon="bi-clouds",
                                color_class="bg-warning-subtle text-warning",
                                trend_text=f"{abs(pm10_data.get('trend_pct', 0.0))}% vs 24h",
                                trend_positive=pm10_data.get('trend_pct', 0.0) >= 0
                            ),
                            xs=12, sm=6, md=4,
                            className="mb-3"
                        ),
                        # CO2
                        dbc.Col(
                            build_metric_card(
                                title="CO2 Level",
                                value=f"{int(co2_data.get('current', 0))}",
                                unit="ppm",
                                icon="bi-cloud-haze2",
                                color_class="bg-success-subtle text-success",
                                trend_text=f"{abs(co2_data.get('trend_pct', 0.0))}% vs 24h",
                                trend_positive=co2_data.get('trend_pct', 0.0) >= 0
                            ),
                            xs=12, sm=6, md=4,
                            className="mb-3"
                        ),
                        # Noise
                        dbc.Col(
                            build_metric_card(
                                title="Noise",
                                value=f"{noise_data.get('current', 0.0)}",
                                unit="dB",
                                icon="bi-volume-up",
                                color_class="bg-primary-subtle text-primary",
                                trend_text=f"{abs(noise_data.get('trend_pct', 0.0))}% vs 24h",
                                trend_positive=noise_data.get('trend_pct', 0.0) >= 0
                            ),
                            xs=12, sm=6, md=4,
                            className="mb-3"
                        ),
                    ],
                    className="g-3"
                ),
                xs=12, lg=8,
                className="mb-3"
            )
        ],
        className="g-3"
    )
