"""
Unit tests for SQLAlchemy models and database relationships.
"""
from datetime import datetime
from app.extensions import db
from app.models.user import User
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.environmental_reading import EnvironmentalReading
from app.models.alert import Alert, AlertThreshold
from app.utils.helpers import utc_now


def test_user_password_hashing(app):
    """Verify that passwords are securely hashed and validated."""
    with app.app_context():
        user = User(username="testuser", email="test@campus.edu", role="viewer")
        user.set_password("secretpass")
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "secretpass"
        assert user.check_password("secretpass") is True
        assert user.check_password("wrongpass") is False
        assert user.is_admin is False


def test_admin_user_role(app):
    """Verify admin role resolution."""
    with app.app_context():
        admin = User.query.filter_by(username="admin").first()
        assert admin is not None
        assert admin.is_admin is True
        assert admin.to_dict()["role"] == "admin"


def test_campus_zone_model(app):
    """Verify CampusZone creation and sensor relationship."""
    with app.app_context():
        zone = CampusZone(
            name="Cafeteria",
            code="ZONE_CAFE",
            description="Dining hall",
            location_details="Block C"
        )
        db.session.add(zone)
        db.session.commit()

        assert zone.id is not None
        assert zone.code == "ZONE_CAFE"
        assert repr(zone) == "<CampusZone Cafeteria (ZONE_CAFE)>"


def test_sensor_and_reading_relationship(app):
    """Verify sensor and reading foreign key cascading relationships."""
    with app.app_context():
        zone = CampusZone.query.filter_by(code="ZONE_LIB").first()
        sensor = Sensor.query.filter_by(sensor_code="ENV-SN-LIB-01").first()

        assert sensor.zone_id == zone.id
        assert sensor.zone.name == "Library"

        reading = EnvironmentalReading(
            sensor_id=sensor.id,
            zone_id=zone.id,
            timestamp=utc_now(),
            temperature=22.5,
            humidity=50.0,
            pm25=12.0,
            pm10=20.0,
            co2=550.0,
            noise=38.0,
            aqi=45,
            weather_condition="Clear"
        )
        db.session.add(reading)
        db.session.commit()

        assert reading.id is not None
        assert reading.sensor.sensor_code == "ENV-SN-LIB-01"
        assert reading.zone.code == "ZONE_LIB"
        assert reading.to_dict()["aqi"] == 45


def test_alert_model(app):
    """Verify Alert model fields and status tracking."""
    with app.app_context():
        zone = CampusZone.query.filter_by(code="ZONE_LIB").first()
        sensor = Sensor.query.filter_by(sensor_code="ENV-SN-LIB-01").first()

        alert = Alert(
            sensor_id=sensor.id,
            zone_id=zone.id,
            parameter="pm25",
            measured_value=58.5,
            threshold_value=55.0,
            severity="Dangerous",
            message="PM2.5 exceeded dangerous limit of 55 µg/m³",
            is_resolved=False
        )
        db.session.add(alert)
        db.session.commit()

        assert alert.id is not None
        assert alert.is_resolved is False
        assert alert.severity == "Dangerous"
        assert alert.to_dict()["parameter"] == "pm25"
