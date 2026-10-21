"""
CampusZone model representing geographic/facility zones across the campus.
"""
from app.extensions import db
from app.utils.helpers import utc_now


class CampusZone(db.Model):
    __tablename__ = "campus_zones"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    location_details = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    sensors = db.relationship("Sensor", back_populates="zone", cascade="all, delete-orphan", lazy="select")
    readings = db.relationship("EnvironmentalReading", back_populates="zone", cascade="all, delete-orphan", lazy="select")
    alerts = db.relationship("Alert", back_populates="zone", cascade="all, delete-orphan", lazy="select")

    def to_dict(self, include_sensor_count: bool = False) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "location_details": self.location_details,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if include_sensor_count:
            data["sensor_count"] = len(self.sensors)
        return data

    def __repr__(self) -> str:
        return f"<CampusZone {self.name} ({self.code})>"
