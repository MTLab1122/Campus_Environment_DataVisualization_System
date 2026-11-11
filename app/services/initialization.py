"""Idempotent application data initialization helpers."""

from app.extensions import db
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.user import User
from config import Config


def seed_demo_users() -> None:
    """Ensure the development demo accounts exist without changing passwords."""
    accounts = (
        ("admin", "admin@campus.edu", "admin", "admin123"),
        ("viewer", "viewer@campus.edu", "viewer", "viewer123"),
    )

    changed = False
    for username, email, role, password in accounts:
        user = User.query.filter_by(username=username).first()
        if user:
            continue

        user = User(username=username, email=email, role=role, is_active_account=True)
        user.set_password(password)
        db.session.add(user)
        changed = True

    if changed:
        db.session.commit()


def seed_demo_catalog() -> None:
    """Ensure the configured zones and one demo sensor per zone exist."""
    changed = False
    for zone_data in Config.CAMPUS_ZONES_DEFAULT:
        zone = CampusZone.query.filter_by(code=zone_data["code"]).first()
        if not zone:
            zone = CampusZone(
                name=zone_data["name"],
                code=zone_data["code"],
                description=zone_data["description"],
                location_details=zone_data["name"],
            )
            db.session.add(zone)
            db.session.flush()
            changed = True

        sensor_code = f"ENV-SN-{zone.code.removeprefix('ZONE_')}-01"
        if not Sensor.query.filter_by(sensor_code=sensor_code).first():
            db.session.add(Sensor(
                sensor_code=sensor_code,
                zone_id=zone.id,
                name=f"{zone.name} Environmental Node",
                model="CampusSense-IoT-v2.1",
                sensor_type="Multi-Parameter Environmental Station",
                status="online",
            ))
            changed = True

    if changed:
        db.session.commit()