"""
Reporting and dashboard metrics export routes.
"""
from datetime import datetime
from flask import Blueprint, request, Response, render_template
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.environmental_reading import EnvironmentalReading
from app.services.report_service import generate_period_report, export_readings_to_csv
from app.services.analytics import (
    get_dashboard_summary_metrics,
    get_latest_zone_readings,
    calculate_campus_health_score,
    get_zone_radar_matrix,
    get_parameter_correlations
)
from app.services.alert_service import get_alert_statistics
from app.utils.helpers import api_response, api_error, parse_datetime, utc_now


reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/api/reports/summary", methods=["GET"])
def get_report_summary():
    """
    Generate an environmental summary report.
    Query parameters:
      - period: 'daily' | 'weekly' | 'monthly' (default: 'daily')
      - zone_id: int (optional)
    """
    period = request.args.get("period", "daily").lower()
    zone_id = request.args.get("zone_id", type=int)

    if period not in ["daily", "weekly", "monthly"]:
        return api_error("Period must be one of: 'daily', 'weekly', 'monthly'.", status_code=400)

    report = generate_period_report(period=period, zone_id=zone_id)
    return api_response(data=report, message=f"Generated {period} environmental report.")


@reports_bp.route("/api/reports/export-csv", methods=["GET"])
def export_csv_endpoint():
    """
    Download filtered environmental telemetry data as CSV file.
    Query parameters:
      - zone_id (int)
      - start_date (ISO)
      - end_date (ISO)
    """
    zone_id = request.args.get("zone_id", type=int)
    start_date = parse_datetime(request.args.get("start_date"))
    end_date = parse_datetime(request.args.get("end_date"))

    csv_data = export_readings_to_csv(zone_id=zone_id, start_date=start_date, end_date=end_date)
    filename = f"campus_environmental_data_{utc_now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "no-cache"
        }
    )


@reports_bp.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """
    Consolidated real-time operational metrics for campus dashboard overview.
    """
    zone_id = request.args.get("zone_id", type=int)

    total_zones = CampusZone.query.count()
    total_sensors = Sensor.query.count()
    online_sensors = Sensor.query.filter_by(status="online").count()
    total_readings = EnvironmentalReading.query.count()
    
    metrics = get_dashboard_summary_metrics(zone_id=zone_id)
    alert_stats = get_alert_statistics()
    latest_zones = get_latest_zone_readings()

    return api_response(
        data={
            "campus_overview": {
                "total_zones": total_zones,
                "total_sensors": total_sensors,
                "online_sensors": online_sensors,
                "total_readings": total_readings
            },
            "metrics": metrics,
            "alerts": alert_stats,
            "latest_zone_readings": latest_zones
        },
        message="Retrieved current campus environmental dashboard statistics."
    )


@reports_bp.route("/api/campus/health-index", methods=["GET"])
def get_campus_health_index():
    """
    Retrieve comprehensive Campus Environmental Health Index (CEHI) score, grade, and sub-indices.
    Query parameter:
      - zone_id (int, optional): filter for a specific zone
    """
    zone_id = request.args.get("zone_id", type=int)
    health_data = calculate_campus_health_score(zone_id=zone_id)
    return api_response(
        data=health_data,
        message="Retrieved Campus Environmental Health Index (CEHI) rating."
    )


@reports_bp.route("/api/analytics/radar", methods=["GET"])
def get_radar_matrix():
    """
    Retrieve normalized multi-dimensional radar comparison data across all campus zones.
    """
    radar_data = get_zone_radar_matrix()
    return api_response(
        data=radar_data,
        message="Retrieved multi-dimensional zone radar comparison matrix."
    )


@reports_bp.route("/api/analytics/correlations", methods=["GET"])
def get_correlations():
    """
    Retrieve pairwise Pearson correlation matrix between environmental telemetry parameters.
    """
    corr_data = get_parameter_correlations()
    return api_response(
        data=corr_data,
        message="Retrieved environmental parameter correlation matrix."
    )


@reports_bp.route("/api/docs", methods=["GET"])
def api_documentation_page():
    """
    Interactive web-based REST API Documentation and testing console.
    """
    return render_template("api_docs.html")

