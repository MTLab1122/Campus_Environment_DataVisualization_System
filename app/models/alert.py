"""
Alert and AlertThreshold models for environmental anomaly monitoring.
"""
from app.extensions import db
from app.utils.helpers import utc_now


class AlertThreshold(db.Model):
    __tablename__ = "alert_thresholds"

    id = db.Column(db.Integer, primary_key=True)
    parameter = db.Column(db.String(50), unique=True, nullable=False, index=True)
    unit = db.Column(db.String(20), nullable=False)
    
    # Safe/Warning/Poor/Dangerous bounds
    warning_min = db.Column(db.Float, nullable=True)
    warning_max = db.Column(db.Float, nullable=True)
    poor_min = db.Column(db.Float, nullable=True)
    poor_max = db.Column(db.Float, nullable=True)
    dangerous_min = db.Column(db.Float, nullable=True)
    dangerous_max = db.Column(db.Float, nullable=True)
    
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "parameter": self.parameter,
            "unit": self.unit,
            "warning_min": self.warning_min,
            "warning_max": self.warning_max,
            "poor_min": self.poor_min,
            "poor_max": self.poor_max,
            "dangerous_min": self.dangerous_min,
            "dangerous_max": self.dangerous_max,
            "description": self.description,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return f"<AlertThreshold {self.parameter} ({self.unit})>"


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    reading_id = db.Column(db.Integer, db.ForeignKey("environmental_readings.id", ondelete="SET NULL"), nullable=True, index=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = db.Column(db.Integer, db.ForeignKey("campus_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    
    parameter = db.Column(db.String(50), nullable=False, index=True)
    measured_value = db.Column(db.Float, nullable=False)
    threshold_value = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), nullable=False, index=True)  # Warning, Poor, Dangerous
    message = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    reading = db.relationship("EnvironmentalReading", back_populates="alerts")
    sensor = db.relationship("Sensor", back_populates="alerts")
    zone = db.relationship("CampusZone", back_populates="alerts")

    def to_dict(self, include_names: bool = True) -> dict:
        data = {
            "id": self.id,
            "reading_id": self.reading_id,
            "sensor_id": self.sensor_id,
            "zone_id": self.zone_id,
            "parameter": self.parameter,
            "measured_value": round(self.measured_value, 2),
            "threshold_value": round(self.threshold_value, 2),
            "severity": self.severity,
            "message": self.message,
            "is_resolved": self.is_resolved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }
        if include_names:
            if self.zone:
                data["zone_name"] = self.zone.name
                data["zone_code"] = self.zone.code
            if self.sensor:
                data["sensor_code"] = self.sensor.sensor_code
        return data

    def __repr__(self) -> str:
        return f"<Alert #{self.id} [{self.severity}] {self.parameter}={self.measured_value}>"
