"""
Main application execution entry point.
Launches the Flask application and integrated Plotly Dash telemetry dashboard.
"""
import os
from app import create_app
from app.extensions import db
from app.services.alert_service import seed_default_thresholds

env = os.environ.get("FLASK_ENV", "development")
app = create_app(env)

# Ensure database tables and initial thresholds exist
with app.app_context():
    db.create_all()
    seed_default_thresholds()

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"

    print("\n" + "=" * 65)
    print("  CAMPUS ENVIRONMENT DATA VISUALIZATION SYSTEM")
    print(f"  * Dashboard URL: http://{host}:{port}/dashboard/")
    print(f"  * REST API Base: http://{host}:{port}/api/")
    print(f"  * Admin Console: http://{host}:{port}/admin/zones")
    print(f"  * Environment:   {env.capitalize()}")
    print("=" * 65 + "\n")

    app.run(host=host, port=port, debug=debug)
