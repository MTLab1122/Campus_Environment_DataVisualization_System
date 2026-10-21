"""
Plotly Dash integration module for Flask.
Mounts interactive analytical dashboard inside the Flask application.
"""
from dash import Dash
import dash_bootstrap_components as dbc
from app.dashboard.layout import create_dashboard_layout
from app.dashboard.callbacks import register_callbacks


def init_dashboard(flask_app) -> Dash:
    """
    Construct and attach the Plotly Dash analytical application to the existing Flask WSGI instance.
    """
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname=flask_app.config.get("DASHBOARD_URL_BASE", "/dashboard/"),
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
            "/static/css/custom.css"
        ],
        suppress_callback_exceptions=True
    )

    dash_app.title = "Campus Environment Data Visualization System"

    with flask_app.app_context():
        dash_app.layout = lambda: create_dashboard_layout(dash_app)
        register_callbacks(dash_app)

    return dash_app
