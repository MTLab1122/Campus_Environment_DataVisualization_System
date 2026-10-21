"""
Database initialization and realistic telemetry seeding script.
Populates standard administrative users, campus zones, IoT sensor stations,
alert threshold boundaries, and 7+ days of historical environmental time-series data.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python search path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.alert import AlertThreshold
from app.services.alert_service import seed_default_thresholds
from app.services.data_generator import seed_historical_telemetry


def seed_database(days: int = 7) -> None:
    """Execute complete database schema generation and population."""
    app = create_app("development")

    with app.app_context():
        print("Creating database schema tables...")
        db.create_all()

        # 1. Seed Users
        print("Provisioning system user accounts...")
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@campus.edu",
                role="admin",
                is_active_account=True
            )
            admin.set_password("admin123")
            db.session.add(admin)
            print("  [+] Created default Admin account: admin / admin123")
        else:
            print("  [*] Admin account already exists.")

        viewer = User.query.filter_by(username="viewer").first()
        if not viewer:
            viewer = User(
                username="viewer",
                email="viewer@campus.edu",
                role="viewer",
                is_active_account=True
            )
            viewer.set_password("viewer123")
            db.session.add(viewer)
            print("  [+] Created default Viewer account: viewer / viewer123")
        else:
            print("  [*] Viewer account already exists.")

        db.session.commit()

        # 2. Seed Campus Zones
        print("Provisioning campus geographic zones...")
        zone_definitions = [
            {
                "name": "Main Gate",
                "code": "ZONE_GATE",
                "location_details": "South Entrance Portal, Checkpoint A",
                "description": "Primary campus vehicle and pedestrian gateway subject to traffic pulse emissions."
            },
            {
                "name": "Library",
                "code": "ZONE_LIB",
                "location_details": "Central Academic Complex, Building A",
                "description": "Quiet study environment and digital archives requiring strict noise and humidity limits."
            },
            {
                "name": "Classroom Block",
                "code": "ZONE_CLASS",
                "location_details": "Instructional Towers 1-4",
                "description": "High-density multi-story lecture rooms with daytime occupancy and CO2 monitoring needs."
            },
            {
                "name": "Cafeteria",
                "code": "ZONE_CAFE",
                "location_details": "Student Union Center, Ground Floor",
                "description": "Dining and culinary preparation hub featuring high peak heat and kitchen particulate loads."
            },
            {
                "name": "Hostel",
                "code": "ZONE_HOSTEL",
                "location_details": "North Residential Sector, Dormitories 1-6",
                "description": "Student residential quarters with elevated evening and nocturnal occupancy."
            },
            {
                "name": "Playground",
                "code": "ZONE_PLAY",
                "location_details": "Athletic Stadium and Running Track",
                "description": "Open-air athletics arena sensitive to solar radiation and ambient airborne dust."
            },
            {
                "name": "Parking Area",
                "code": "ZONE_PARK",
                "location_details": "West Commuter Lot and Transit Bays",
                "description": "Paved vehicular parking with morning and evening internal combustion exhaust concentrations."
            },
            {
                "name": "Laboratory Block",
                "code": "ZONE_LAB",
                "location_details": "Science & Engineering Research Complex",
                "description": "Precision chemical and electronic labs demanding stable temperature and fume safety."
            }
        ]

        created_zones = {}
        for zd in zone_definitions:
            zone = CampusZone.query.filter_by(code=zd["code"]).first()
            if not zone:
                zone = CampusZone(
                    name=zd["name"],
                    code=zd["code"],
                    location_details=zd["location_details"],
                    description=zd["description"]
                )
                db.session.add(zone)
                db.session.flush()
                print(f"  [+] Added Campus Zone: {zone.name} ({zone.code})")
            else:
                print(f"  [*] Zone exists: {zone.name} ({zone.code})")
            created_zones[zone.code] = zone

        db.session.commit()

        # 3. Seed Sensors
        print("Provisioning IoT telemetry sensor stations...")
        sensor_definitions = [
            ("ENV-SN-GATE-01", "ZONE_GATE", "Main Gate Multi-Sensor Station", "CampusSense-IoT-v2.1"),
            ("ENV-SN-LIB-01", "ZONE_LIB", "Library Central Hall Environmental Node", "AeroSense-Pro-Indoor"),
            ("ENV-SN-CLASS-01", "ZONE_CLASS", "Classroom Block Tower B Monitor", "CampusSense-IoT-v2.1"),
            ("ENV-SN-CAFE-01", "ZONE_CAFE", "Cafeteria Dining Hall Air Station", "CampusSense-Kitchen-Safe"),
            ("ENV-SN-HOSTEL-01", "ZONE_HOSTEL", "Hostel Quad Residential Node", "AeroSense-Pro-Indoor"),
            ("ENV-SN-PLAY-01", "ZONE_PLAY", "Playground Weather & Dust Station", "SolarSense-Outdoor-v3"),
            ("ENV-SN-PARK-01", "ZONE_PARK", "Parking Surface Telemetry Station", "SolarSense-Outdoor-v3"),
            ("ENV-SN-LAB-01", "ZONE_LAB", "Laboratory Cleanroom Monitor", "PrecisionLab-Sense-X")
        ]

        for code, z_code, name, model in sensor_definitions:
            sensor = Sensor.query.filter_by(sensor_code=code).first()
            if not sensor:
                zone = created_zones.get(z_code)
                sensor = Sensor(
                    sensor_code=code,
                    zone_id=zone.id,
                    name=name,
                    model=model,
                    sensor_type="Multi-Parameter Environmental Station",
                    status="online",
                    last_seen=datetime.utcnow()
                )
                db.session.add(sensor)
                print(f"  [+] Provisioned Sensor: {code} -> {zone.name}")
            else:
                print(f"  [*] Sensor exists: {code}")

        db.session.commit()

        # 4. Seed Alert Thresholds
        print("Configuring safety thresholds...")
        seed_default_thresholds()
        print("  [+] Alert thresholds verified.")

        # 5. Seed Historical Environmental Readings (7 Days)
        print(f"Generating realistic {days}-day time-series telemetry...")
        reading_count = seed_historical_telemetry(days=days, interval_hours=1)
        print(f"  [+] Seeded {reading_count} historical sensor telemetry records.")

        print("\n" + "=" * 60)
        print("  DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("  * SQLite Database: campus_environment.db")
        print("  * Admin Login:     admin / admin123")
        print("  * Viewer Login:    viewer / viewer123")
        print("  * Run Server:      python run.py")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    seed_database(days=7)
