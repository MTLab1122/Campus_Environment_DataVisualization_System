"""
Alert evaluation and lifecycle service.
Monitors telemetry streams, detects threshold violations, and manages alert records.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.extensions import db
from app.models.alert import Alert, AlertThreshold
from app.models.environmental_reading import EnvironmentalReading
from app.utils.helpers import utc_now


DEFAULT_ALERT_THRESHOLDS = [
    {
        "parameter": "pm25",
        "unit": "µg/m³",
        "warning_min": None,
        "warning_max": 25.0,
        "poor_min": None,
        "poor_max": 35.0,
        "dangerous_min": None,
        "dangerous_max": 55.0,
        "description": "Fine particulate matter (PM2.5) air safety limits."
    },
    {
        "parameter": "pm10",
        "unit": "µg/m³",
        "warning_min": None,
        "warning_max": 50.0,
        "poor_min": None,
        "poor_max": 100.0,
        "dangerous_min": None,
        "dangerous_max": 150.0,
        "description": "Coarse particulate matter (PM10) air safety limits."
    },
    {
        "parameter": "co2",
        "unit": "ppm",
        "warning_min": None,
        "warning_max": 800.0,
        "poor_min": None,
        "poor_max": 1000.0,
        "dangerous_min": None,
        "dangerous_max": 2000.0,
        "description": "Carbon dioxide concentration thresholds for indoor ventilation."
    },
    {
        "parameter": "noise",
        "unit": "dB",
        "warning_min": None,
        "warning_max": 65.0,
        "poor_min": None,
        "poor_max": 70.0,
        "dangerous_min": None,
        "dangerous_max": 85.0,
        "description": "Acoustic noise thresholds for campus learning and residential environments."
    },
    {
        "parameter": "temperature",
        "unit": "°C",
        "warning_min": 18.0,
        "warning_max": 30.0,
        "poor_min": 14.0,
        "poor_max": 35.0,
        "dangerous_min": 10.0,
        "dangerous_max": 40.0,
        "description": "Thermal comfort and safety boundaries for campus occupants."
    },
    {
        "parameter": "humidity",
        "unit": "%",
        "warning_min": 30.0,
        "warning_max": 70.0,
        "poor_min": 20.0,
        "poor_max": 80.0,
        "dangerous_min": 15.0,
        "dangerous_max": 90.0,
        "description": "Relative humidity limits for respiratory wellness and mold prevention."
    }
]


def seed_default_thresholds() -> None:
    """Initialize standard alert threshold rules if not already present."""
    for item in DEFAULT_ALERT_THRESHOLDS:
        existing = AlertThreshold.query.filter_by(parameter=item["parameter"]).first()
        if not existing:
            threshold = AlertThreshold(
                parameter=item["parameter"],
                unit=item["unit"],
                warning_min=item["warning_min"],
                warning_max=item["warning_max"],
                poor_min=item["poor_min"],
                poor_max=item["poor_max"],
                dangerous_min=item["dangerous_min"],
                dangerous_max=item["dangerous_max"],
                description=item["description"]
            )
            db.session.add(threshold)
    db.session.commit()


def evaluate_reading_alerts(reading: EnvironmentalReading) -> List[Alert]:
    """
    Evaluate an incoming environmental reading against active thresholds.
    Creates and records Alert instances when safe boundaries are exceeded.
    """
    thresholds = AlertThreshold.query.all()
    threshold_map = {t.parameter.lower(): t for t in thresholds}
    created_alerts = []

    # Map of reading parameters to values and human readable names
    params_to_check = [
        ("pm25", reading.pm25, "PM2.5"),
        ("pm10", reading.pm10, "PM10"),
        ("co2", reading.co2, "CO2 Concentration"),
        ("noise", reading.noise, "Noise Level"),
        ("temperature", reading.temperature, "Temperature"),
        ("humidity", reading.humidity, "Relative Humidity")
    ]

    for param_key, val, param_name in params_to_check:
        rule = threshold_map.get(param_key)
        if not rule:
            continue

        severity = None
        threshold_val = 0.0
        reason = ""

        # Check dangerous boundary first
        if rule.dangerous_max is not None and val > rule.dangerous_max:
            severity = "Dangerous"
            threshold_val = rule.dangerous_max
            reason = f"{param_name} reached extreme high level of {val:.1f} {rule.unit} (Dangerous threshold: >{threshold_val:.1f} {rule.unit})"
        elif rule.dangerous_min is not None and val < rule.dangerous_min:
            severity = "Dangerous"
            threshold_val = rule.dangerous_min
            reason = f"{param_name} dropped to extreme low level of {val:.1f} {rule.unit} (Dangerous threshold: <{threshold_val:.1f} {rule.unit})"
        
        # Check poor boundary
        elif rule.poor_max is not None and val > rule.poor_max:
            severity = "Poor"
            threshold_val = rule.poor_max
            reason = f"{param_name} exceeded safe standard at {val:.1f} {rule.unit} (Poor threshold: >{threshold_val:.1f} {rule.unit})"
        elif rule.poor_min is not None and val < rule.poor_min:
            severity = "Poor"
            threshold_val = rule.poor_min
            reason = f"{param_name} dropped below standard at {val:.1f} {rule.unit} (Poor threshold: <{threshold_val:.1f} {rule.unit})"
        
        # Check warning boundary
        elif rule.warning_max is not None and val > rule.warning_max:
            severity = "Warning"
            threshold_val = rule.warning_max
            reason = f"{param_name} elevated to {val:.1f} {rule.unit} (Warning threshold: >{threshold_val:.1f} {rule.unit})"
        elif rule.warning_min is not None and val < rule.warning_min:
            severity = "Warning"
            threshold_val = rule.warning_min
            reason = f"{param_name} reduced to {val:.1f} {rule.unit} (Warning threshold: <{threshold_val:.1f} {rule.unit})"

        if severity:
            alert = Alert(
                reading_id=reading.id,
                sensor_id=reading.sensor_id,
                zone_id=reading.zone_id,
                parameter=param_key,
                measured_value=val,
                threshold_value=threshold_val,
                severity=severity,
                message=reason,
                is_resolved=False,
                created_at=reading.timestamp
            )
            db.session.add(alert)
            created_alerts.append(alert)

    if created_alerts:
        db.session.commit()

    return created_alerts


def resolve_alert(alert_id: int) -> Optional[Alert]:
    """Mark an active alert as resolved."""
    alert = db.session.get(Alert, alert_id)
    if alert and not alert.is_resolved:
        alert.is_resolved = True
        alert.resolved_at = utc_now()
        db.session.commit()
    return alert


def resolve_all_alerts(zone_id: Optional[int] = None) -> int:
    """Mark all active alerts (optionally filtered by zone) as resolved."""
    query = Alert.query.filter_by(is_resolved=False)
    if zone_id:
        query = query.filter_by(zone_id=zone_id)
    alerts = query.all()
    count = len(alerts)
    now = utc_now()
    for a in alerts:
        a.is_resolved = True
        a.resolved_at = now
    db.session.commit()
    return count


def get_active_alerts(zone_id: Optional[int] = None, limit: int = 50) -> List[Alert]:
    """Retrieve unresolved alerts, newest first."""
    query = Alert.query.filter_by(is_resolved=False)
    if zone_id:
        query = query.filter_by(zone_id=zone_id)
    return query.order_by(Alert.created_at.desc()).limit(limit).all()


def get_alert_statistics() -> Dict[str, Any]:
    """Get high-level alert metrics for dashboard summaries."""
    total_active = Alert.query.filter_by(is_resolved=False).count()
    dangerous_active = Alert.query.filter_by(is_resolved=False, severity="Dangerous").count()
    poor_active = Alert.query.filter_by(is_resolved=False, severity="Poor").count()
    warning_active = Alert.query.filter_by(is_resolved=False, severity="Warning").count()
    total_all_time = Alert.query.count()

    return {
        "total_active": total_active,
        "dangerous": dangerous_active,
        "poor": poor_active,
        "warning": warning_active,
        "total_all_time": total_all_time
    }
