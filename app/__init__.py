"""
Application factory module for Campus Environment Data Visualization System.
Constructs Flask WSGI application, initializes database extensions, mounts blueprints and Plotly Dash.
"""
import os
from flask import Flask, jsonify, render_template, request
from config import config_by_name
from app.extensions import db, login_manager


def create_app(config_name: str = None) -> Flask:
    """
    Construct and configure the Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    config_cls = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_cls)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Flask Blueprints
    from app.routes.auth import auth_bp
    from app.routes.zones import zones_bp
    from app.routes.sensors import sensors_bp
    from app.routes.readings import readings_bp
    from app.routes.alerts import alerts_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(zones_bp)
    app.register_blueprint(sensors_bp)
    app.register_blueprint(readings_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(reports_bp)

    # Register error handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Resource endpoint not found.", "status_code": 404}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Internal server processing error.", "status_code": 500}), 500
        return render_template("500.html"), 500

    # Mount interactive Plotly Dash analytical application
    # Skip dashboard mounting during pytest tests if running in lightweight test mode without server
    if not app.config.get("TESTING", False):
        with app.app_context():
            db.create_all()
        from app.dashboard import init_dashboard
        init_dashboard(app)

    return app
