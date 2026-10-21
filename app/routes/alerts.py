"""
Alert management routes: In-depth threshold configuration, alert history, and resolution.
"""
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.alert import Alert, AlertThreshold
from app.services.alert_service import resolve_alert, resolve_all_alerts, get_active_alerts, get_alert_statistics
from app.utils.decorators import admin_required
from app.utils.helpers import api_response, api_error

alerts_bp = Blueprint("alerts", __name__)


# --- Admin Web View ---

@alerts_bp.route("/admin/thresholds", methods=["GET", "POST"])
@login_required
def admin_thresholds():
    """Admin interface for customizing safe/warning/poor/dangerous environmental thresholds and reviewing alerts."""
    if request.method == "POST":
        if not current_user.is_admin:
            flash("Administrator privileges required to modify alert rules or resolve alerts.", "danger")
            return redirect(url_for("alerts.admin_thresholds"))

        action = request.form.get("action", "update_threshold")

        if action == "resolve_alert":
            alert_id = request.form.get("alert_id", type=int)
            resolved = resolve_alert(alert_id)
            if resolved:
                flash(f"Alert #{alert_id} ({resolved.parameter.upper()}) marked as resolved.", "success")
            else:
                flash("Alert not found.", "warning")

        elif action == "resolve_all":
            count = resolve_all_alerts()
            flash(f"All {count} active alerts have been marked as resolved.", "info")

        elif action == "update_threshold":
            threshold_id = request.form.get("threshold_id", type=int)
            threshold = db.session.get(AlertThreshold, threshold_id)
            if threshold:
                try:
                    threshold.warning_min = float(request.form.get("warning_min")) if request.form.get("warning_min") else None
                    threshold.warning_max = float(request.form.get("warning_max")) if request.form.get("warning_max") else None
                    threshold.poor_min = float(request.form.get("poor_min")) if request.form.get("poor_min") else None
                    threshold.poor_max = float(request.form.get("poor_max")) if request.form.get("poor_max") else None
                    threshold.dangerous_min = float(request.form.get("dangerous_min")) if request.form.get("dangerous_min") else None
                    threshold.dangerous_max = float(request.form.get("dangerous_max")) if request.form.get("dangerous_max") else None
                    threshold.description = request.form.get("description", "").strip()
                    db.session.commit()
                    flash(f"Thresholds for parameter '{threshold.parameter.upper()}' updated successfully.", "success")
                except ValueError as e:
                    flash(f"Invalid threshold boundary number: {str(e)}", "danger")

        return redirect(url_for("alerts.admin_thresholds"))

    thresholds = AlertThreshold.query.order_by(AlertThreshold.parameter.asc()).all()
    stats = get_alert_statistics()
    recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(25).all()
    return render_template("admin_thresholds.html", thresholds=thresholds, stats=stats, recent_alerts=recent_alerts)


# --- REST API Endpoints ---

@alerts_bp.route("/api/alerts", methods=["GET"])
def get_alerts():
    """
    Retrieve system alerts.
    Query parameters:
      - zone_id (int)
      - is_resolved (true/false)
      - severity (Warning, Poor, Dangerous)
      - limit (int, default 50)
    """
    query = Alert.query
    zone_id = request.args.get("zone_id", type=int)
    severity = request.args.get("severity")
    is_resolved_param = request.args.get("is_resolved")
    limit = min(request.args.get("limit", default=50, type=int), 500)

    if zone_id:
        query = query.filter(Alert.zone_id == zone_id)
    if severity:
        query = query.filter(Alert.severity.ilike(severity))
    if is_resolved_param is not None:
        is_resolved_bool = is_resolved_param.lower() in ["true", "1", "yes"]
        query = query.filter(Alert.is_resolved == is_resolved_bool)

    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    stats = get_alert_statistics()

    return api_response(
        data={
            "alerts": [a.to_dict(include_names=True) for a in alerts],
            "statistics": stats
        },
        message=f"Retrieved {len(alerts)} alerts."
    )


@alerts_bp.route("/api/alerts/<int:alert_id>/resolve", methods=["PUT", "POST"])
def resolve_alert_endpoint(alert_id: int):
    """Mark an active alert as resolved."""
    alert = resolve_alert(alert_id)
    if not alert:
        return api_error(f"Alert with ID {alert_id} not found.", status_code=404)

    return api_response(
        data=alert.to_dict(include_names=True),
        message=f"Alert #{alert_id} resolved successfully."
    )


@alerts_bp.route("/api/alerts/resolve-all", methods=["PUT", "POST"])
def resolve_all_endpoint():
    """Mark all active alerts as resolved."""
    zone_id = request.args.get("zone_id", type=int)
    count = resolve_all_alerts(zone_id=zone_id)
    return api_response(
        data={"resolved_count": count},
        message=f"Successfully resolved {count} active alerts."
    )


@alerts_bp.route("/api/alerts/thresholds", methods=["GET"])
def get_thresholds():
    """Retrieve all configurable alert threshold boundaries."""
    thresholds = AlertThreshold.query.order_by(AlertThreshold.parameter.asc()).all()
    return api_response(
        data=[t.to_dict() for t in thresholds],
        message=f"Retrieved {len(thresholds)} alert threshold rules."
    )


@alerts_bp.route("/api/alerts/thresholds/<int:threshold_id>", methods=["PUT"])
@login_required
@admin_required
def update_threshold(threshold_id: int):
    """Update threshold limits for an environmental parameter (Admin only)."""
    threshold = db.session.get(AlertThreshold, threshold_id)
    if not threshold:
        return api_error(f"Threshold ID {threshold_id} not found.", status_code=404)

    data = request.get_json(silent=True) or {}

    for field in ["warning_min", "warning_max", "poor_min", "poor_max", "dangerous_min", "dangerous_max"]:
        if field in data:
            setattr(threshold, field, float(data[field]) if data[field] is not None else None)

    if "description" in data:
        threshold.description = data["description"]

    db.session.commit()
    return api_response(
        data=threshold.to_dict(),
        message=f"Threshold limits for '{threshold.parameter}' updated successfully."
    )
