"""
Routes package initialization.
Exports all blueprints for registration in the application factory.
"""
from app.routes.auth import auth_bp
from app.routes.zones import zones_bp
from app.routes.sensors import sensors_bp
from app.routes.readings import readings_bp
from app.routes.alerts import alerts_bp
from app.routes.reports import reports_bp

__all__ = [
    "auth_bp",
    "zones_bp",
    "sensors_bp",
    "readings_bp",
    "alerts_bp",
    "reports_bp"
]
