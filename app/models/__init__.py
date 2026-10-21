"""
Models package initialization.
Exports all database entities.
"""
from app.models.user import User
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.environmental_reading import EnvironmentalReading
from app.models.alert import Alert, AlertThreshold

__all__ = [
    "User",
    "CampusZone",
    "Sensor",
    "EnvironmentalReading",
    "Alert",
    "AlertThreshold"
]
