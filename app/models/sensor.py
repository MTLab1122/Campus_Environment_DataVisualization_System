"""
Sensor model representing physical or simulated IoT telemetry devices.
"""
from app.extensions import db
from app.utils.helpers import utc_now


class Sensor(db.Model):
    __tablename__ = "sensors"

    id = db.Column(db.Integer, primary_key=True)
    sensor_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    zone_id = db.Column(db.Integer, db.ForeignKey("campus_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(60), default="CampusSense-IoT-v2.1", nullable=False)
    sensor_type = db.Column(db.String(80), default="Multi-Parameter Environmental Station", nullable=False)
    status = db.Column(db.String(20), default="online", nullable=False)  # online, offline, maintenance
    last_seen = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    zone = db.relationship("CampusZone", back_populates="sensors")
    readings = db.relationship("EnvironmentalReading", back_populates="sensor", cascade="all, delete-orphan", lazy="select")
    alerts = db.relationship("Alert", back_populates="sensor", cascade="all, delete-orphan", lazy="select")

    def to_dict(self, include_zone: bool = True) -> dict:
        data = {
            "id": self.id,
            "sensor_code": self.sensor_code,
            "zone_id": self.zone_id,
            "name": self.name,
            "model": self.model,
            "sensor_type": self.sensor_type,
            "status": self.status,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if include_zone and self.zone:
            data["zone_name"] = self.zone.name
            data["zone_code"] = self.zone.code
        return data

    def __repr__(self) -> str:
        return f"<Sensor {self.sensor_code} ({self.name}) - {self.status}>"
