"""
EnvironmentalReading model storing high-resolution time-series sensor telemetry.
"""
from app.extensions import db
from app.utils.helpers import utc_now


class EnvironmentalReading(db.Model):
    __tablename__ = "environmental_readings"

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True)
    zone_id = db.Column(db.Integer, db.ForeignKey("campus_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=utc_now, nullable=False, index=True)
    
    # Environmental Parameters
    temperature = db.Column(db.Float, nullable=False)  # °C
    humidity = db.Column(db.Float, nullable=False)     # %
    pm25 = db.Column(db.Float, nullable=False)         # µg/m³
    pm10 = db.Column(db.Float, nullable=False)         # µg/m³
    co2 = db.Column(db.Float, nullable=False)          # ppm
    noise = db.Column(db.Float, nullable=False)        # dB
    
    # Calculated / Auxiliary metrics
    aqi = db.Column(db.Integer, nullable=False)        # 0-500 scale
    weather_condition = db.Column(db.String(50), default="Clear", nullable=False)

    # Relationships
    sensor = db.relationship("Sensor", back_populates="readings")
    zone = db.relationship("CampusZone", back_populates="readings")
    alerts = db.relationship("Alert", back_populates="reading", lazy="select")

    def to_dict(self, include_names: bool = True) -> dict:
        data = {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "zone_id": self.zone_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "temperature": round(self.temperature, 2),
            "humidity": round(self.humidity, 2),
            "pm25": round(self.pm25, 2),
            "pm10": round(self.pm10, 2),
            "co2": round(self.co2, 2),
            "noise": round(self.noise, 2),
            "aqi": self.aqi,
            "weather_condition": self.weather_condition
        }
        if include_names:
            if self.zone:
                data["zone_name"] = self.zone.name
                data["zone_code"] = self.zone.code
            if self.sensor:
                data["sensor_code"] = self.sensor.sensor_code
                data["sensor_name"] = self.sensor.name
        return data

    def __repr__(self) -> str:
        return f"<Reading #{self.id} Zone:{self.zone_id} Temp:{self.temperature}°C PM2.5:{self.pm25} AQI:{self.aqi}>"
