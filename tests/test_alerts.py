"""
Tests for environmental alert evaluation, threshold logic, and AQI calculations.
"""
from datetime import datetime
from app.extensions import db
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.environmental_reading import EnvironmentalReading
from app.models.alert import Alert, AlertThreshold
from app.utils.helpers import utc_now
from app.services.alert_service import evaluate_reading_alerts, resolve_alert
from app.utils.aqi_calculator import calculate_aqi, get_aqi_details


def test_aqi_calculation():
    """Verify EPA standard piecewise AQI calculation."""
    # Good range (0-50)
    aqi_good = calculate_aqi(pm25=8.0, pm10=15.0)
    assert 0 <= aqi_good <= 50
    assert get_aqi_details(aqi_good)["category"] == "Good"

    # Moderate range (51-100)
    aqi_mod = calculate_aqi(pm25=25.0, pm10=60.0)
    assert 51 <= aqi_mod <= 100
    assert get_aqi_details(aqi_mod)["category"] == "Moderate"

    # Poor / Dangerous range
    aqi_high = calculate_aqi(pm25=80.0, pm10=180.0)
    assert aqi_high > 150
    assert get_aqi_details(aqi_high)["category"] in ["Poor", "Very Poor", "Dangerous"]


def test_alert_rule_evaluation(app):
    """Verify automatic alert generation when telemetry breaches thresholds."""
    with app.app_context():
        zone = CampusZone.query.filter_by(code="ZONE_LIB").first()
        sensor = Sensor.query.filter_by(sensor_code="ENV-SN-LIB-01").first()

        # Reading exceeding PM2.5 dangerous limit (> 55 µg/m³) and CO2 poor limit (> 1000 ppm)
        reading = EnvironmentalReading(
            sensor_id=sensor.id,
            zone_id=zone.id,
            timestamp=utc_now(),
            temperature=24.0,
            humidity=50.0,
            pm25=65.0,       # Dangerous (> 55.0)
            pm10=40.0,
            co2=1250.0,      # Poor (> 1000.0)
            noise=40.0,
            aqi=156,
            weather_condition="Overcast"
        )
        db.session.add(reading)
        db.session.commit()

        alerts = evaluate_reading_alerts(reading)
        assert len(alerts) >= 2

        severities = {a.parameter: a.severity for a in alerts}
        assert severities["pm25"] == "Dangerous"
        assert severities["co2"] == "Poor"


def test_alert_resolution(app):
    """Verify marking alerts as resolved."""
    with app.app_context():
        zone = CampusZone.query.filter_by(code="ZONE_LIB").first()
        sensor = Sensor.query.filter_by(sensor_code="ENV-SN-LIB-01").first()

        alert = Alert(
            sensor_id=sensor.id,
            zone_id=zone.id,
            parameter="noise",
            measured_value=78.0,
            threshold_value=70.0,
            severity="Poor",
            message="Noise exceeded 70 dB",
            is_resolved=False
        )
        db.session.add(alert)
        db.session.commit()

        alert_id = alert.id
        assert alert.is_resolved is False

        resolved = resolve_alert(alert_id)
        assert resolved is not None
        assert resolved.is_resolved is True
        assert resolved.resolved_at is not None
