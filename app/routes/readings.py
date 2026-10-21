"""
Environmental telemetry reading routes: Ingestion API, queries, and manual entry forms.
"""
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.environmental_reading import EnvironmentalReading
from app.services.alert_service import evaluate_reading_alerts
from app.services.analytics import get_latest_zone_readings
from app.utils.aqi_calculator import calculate_aqi
from app.utils.decorators import admin_required
from app.utils.helpers import api_response, api_error, parse_datetime, utc_now

readings_bp = Blueprint("readings", __name__)


# --- Admin Manual Entry Web View ---

@readings_bp.route("/admin/readings/manual", methods=["GET", "POST"])
@login_required
def manual_entry():
    """Admin interface for manual data entry of environmental readings."""
    if request.method == "POST":
        if not current_user.is_admin:
            flash("Administrator privileges required to record manual readings.", "danger")
            return redirect(url_for("readings.manual_entry"))

        sensor_id = request.form.get("sensor_id", type=int)
        temperature = request.form.get("temperature", type=float)
        humidity = request.form.get("humidity", type=float)
        pm25 = request.form.get("pm25", type=float)
        pm10 = request.form.get("pm10", type=float)
        co2 = request.form.get("co2", type=float)
        noise = request.form.get("noise", type=float)
        weather_condition = request.form.get("weather_condition", "Sunny").strip()
        custom_time = request.form.get("timestamp")

        if None in [sensor_id, temperature, humidity, pm25, pm10, co2, noise]:
            flash("All numerical telemetry fields are mandatory.", "warning")
        else:
            sensor = db.session.get(Sensor, sensor_id)
            if not sensor:
                flash("Selected sensor does not exist.", "danger")
            else:
                timestamp = parse_datetime(custom_time) or utc_now()
                aqi = calculate_aqi(pm25, pm10)

                reading = EnvironmentalReading(
                    sensor_id=sensor.id,
                    zone_id=sensor.zone_id,
                    timestamp=timestamp,
                    temperature=temperature,
                    humidity=humidity,
                    pm25=pm25,
                    pm10=pm10,
                    co2=co2,
                    noise=noise,
                    aqi=aqi,
                    weather_condition=weather_condition
                )
                db.session.add(reading)
                sensor.last_seen = timestamp
                db.session.commit()

                # Trigger alert thresholds
                alerts = evaluate_reading_alerts(reading)
                if alerts:
                    flash(f"Manual reading saved! Generated {len(alerts)} alert notification(s).", "warning")
                else:
                    flash(f"Manual reading logged successfully for {sensor.name} (AQI: {aqi}).", "success")

                return redirect(url_for("readings.manual_entry"))

    sensors = Sensor.query.order_by(Sensor.name.asc()).all()
    latest_readings = EnvironmentalReading.query.order_by(EnvironmentalReading.id.desc()).limit(15).all()
    return render_template("manual_entry.html", sensors=sensors, latest_readings=latest_readings)


# --- REST API Endpoints ---

@readings_bp.route("/api/readings", methods=["GET"])
def get_readings():
    """
    Retrieve time-series environmental readings with multi-dimensional filtering.
    Query parameters:
      - zone_id (int)
      - sensor_id (int)
      - start_date (ISO string or YYYY-MM-DD)
      - end_date (ISO string or YYYY-MM-DD)
      - limit (int, default 100, max 2000)
      - page (int, default 1)
    """
    query = EnvironmentalReading.query

    zone_id = request.args.get("zone_id", type=int)
    sensor_id = request.args.get("sensor_id", type=int)
    start_date = parse_datetime(request.args.get("start_date"))
    end_date = parse_datetime(request.args.get("end_date"))
    limit = min(request.args.get("limit", default=100, type=int), 2000)
    page = max(request.args.get("page", default=1, type=int), 1)

    if zone_id:
        query = query.filter(EnvironmentalReading.zone_id == zone_id)
    if sensor_id:
        query = query.filter(EnvironmentalReading.sensor_id == sensor_id)
    if start_date:
        query = query.filter(EnvironmentalReading.timestamp >= start_date)
    if end_date:
        query = query.filter(EnvironmentalReading.timestamp <= end_date)

    total_count = query.count()
    readings = query.order_by(EnvironmentalReading.timestamp.desc())\
                    .offset((page - 1) * limit)\
                    .limit(limit)\
                    .all()

    return api_response(
        data={
            "readings": [r.to_dict(include_names=True) for r in readings],
            "total_count": total_count,
            "page": page,
            "limit": limit
        },
        message=f"Retrieved {len(readings)} environmental readings."
    )


@readings_bp.route("/api/readings", methods=["POST"])
def create_reading():
    """
    Ingest an environmental reading from IoT hardware stations or automated simulation.
    Accepts JSON payload:
    {
      "sensor_code": "ENV-SN-LIB-01" (or "sensor_id": 1),
      "temperature": 23.4,
      "humidity": 45.2,
      "pm25": 14.5,
      "pm10": 26.0,
      "co2": 580.0,
      "noise": 42.0,
      "aqi": 52 (optional, auto-calculated if omitted),
      "weather_condition": "Sunny" (optional),
      "timestamp": "2026-10-18T10:00:00" (optional, defaults to now)
    }
    """
    data = request.get_json(silent=True) or {}

    # Identify sensor
    sensor = None
    if "sensor_id" in data:
        sensor = db.session.get(Sensor, data["sensor_id"])
    elif "sensor_code" in data:
        sensor = Sensor.query.filter_by(sensor_code=data["sensor_code"].strip()).first()

    if not sensor:
        return api_error("Valid 'sensor_id' or 'sensor_code' is required.", status_code=400)

    # Validate numerical fields
    req_fields = ["temperature", "humidity", "pm25", "pm10", "co2", "noise"]
    missing = [f for f in req_fields if f not in data or data[f] is None]
    if missing:
        return api_error(f"Missing required telemetry parameters: {', '.join(missing)}", status_code=400)

    try:
        temp = float(data["temperature"])
        hum = float(data["humidity"])
        pm25 = float(data["pm25"])
        pm10 = float(data["pm10"])
        co2 = float(data["co2"])
        noise = float(data["noise"])
    except (ValueError, TypeError) as e:
        return api_error(f"Invalid numerical telemetry value: {str(e)}", status_code=400)

    # Calculate or retrieve AQI
    aqi = int(data["aqi"]) if "aqi" in data and data["aqi"] is not None else calculate_aqi(pm25, pm10)
    weather = data.get("weather_condition", "Clear")
    timestamp = parse_datetime(data.get("timestamp")) or utc_now()

    reading = EnvironmentalReading(
        sensor_id=sensor.id,
        zone_id=sensor.zone_id,
        timestamp=timestamp,
        temperature=temp,
        humidity=hum,
        pm25=pm25,
        pm10=pm10,
        co2=co2,
        noise=noise,
        aqi=aqi,
        weather_condition=weather
    )
    db.session.add(reading)
    sensor.last_seen = timestamp
    sensor.status = "online"
    db.session.commit()

    # Alert evaluation
    alerts = evaluate_reading_alerts(reading)

    return api_response(
        data={
            "reading": reading.to_dict(include_names=True),
            "alerts_triggered": [a.to_dict(include_names=False) for a in alerts]
        },
        message="Environmental reading ingested successfully.",
        status_code=201
    )


@readings_bp.route("/api/readings/latest", methods=["GET"])
def get_latest():
    """Retrieve the latest environmental reading for every campus zone."""
    latest_readings = get_latest_zone_readings()
    return api_response(
        data=latest_readings,
        message=f"Retrieved latest readings for {len(latest_readings)} campus zones."
    )


@readings_bp.route("/api/readings/simulate-pulse", methods=["POST"])
def simulate_telemetry_pulse():
    """
    Simulate an instantaneous realistic IoT telemetry reading burst and trigger threshold evaluation.
    Optional JSON payload or query param:
      - zone_id (int)
    """
    from app.services.data_generator import generate_single_reading
    data = request.get_json(silent=True) or {}
    zone_id = data.get("zone_id") or request.args.get("zone_id", type=int)

    reading = generate_single_reading(zone_id=zone_id)
    if not reading:
        return api_error("No provisioned sensors found to generate telemetry.", status_code=400)

    alerts = evaluate_reading_alerts(reading)

    return api_response(
        data={
            "reading": reading.to_dict(include_names=True),
            "alerts_triggered": [a.to_dict(include_names=False) for a in alerts]
        },
        message=f"Simulated live telemetry reading for {reading.zone.name if reading.zone else 'Campus Zone'}.",
        status_code=201
    )

