"""
Sensor management routes: REST API endpoints and Admin web views.
"""
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.utils.decorators import admin_required
from app.utils.helpers import api_response, api_error, utc_now

sensors_bp = Blueprint("sensors", __name__)


# --- Admin Web View ---

@sensors_bp.route("/admin/sensors", methods=["GET", "POST"])
@login_required
def admin_sensors():
    """Admin interface for provisioning, editing, and monitoring sensor telemetry hardware."""
    if request.method == "POST":
        if not current_user.is_admin:
            flash("Administrator privileges required to modify sensor stations.", "danger")
            return redirect(url_for("sensors.admin_sensors"))

        action = request.form.get("action", "create")

        if action == "create":
            sensor_code = request.form.get("sensor_code", "").strip().upper()
            zone_id = request.form.get("zone_id", type=int)
            name = request.form.get("name", "").strip()
            model = request.form.get("model", "CampusSense-IoT-v2.1").strip()
            sensor_type = request.form.get("sensor_type", "Multi-Parameter Environmental Station").strip()
            status = request.form.get("status", "online").strip()

            if not sensor_code or not zone_id or not name:
                flash("Sensor Code, Target Zone, and Name are required.", "warning")
            elif Sensor.query.filter_by(sensor_code=sensor_code).first():
                flash(f"Sensor Code '{sensor_code}' is already registered.", "danger")
            else:
                sensor = Sensor(
                    sensor_code=sensor_code,
                    zone_id=zone_id,
                    name=name,
                    model=model,
                    sensor_type=sensor_type,
                    status=status,
                    last_seen=utc_now() if status == "online" else None
                )
                db.session.add(sensor)
                db.session.commit()
                flash(f"Sensor '{sensor_code}' provisioned successfully.", "success")

        elif action in ["update", "edit"]:
            sensor_id = request.form.get("sensor_id", type=int)
            sensor = db.session.get(Sensor, sensor_id)
            if sensor:
                sensor.name = request.form.get("name", sensor.name).strip()
                sensor.model = request.form.get("model", sensor.model).strip()
                sensor.sensor_type = request.form.get("sensor_type", sensor.sensor_type).strip()
                new_zid = request.form.get("zone_id", type=int)
                if new_zid and db.session.get(CampusZone, new_zid):
                    sensor.zone_id = new_zid
                sensor.status = request.form.get("status", sensor.status).strip()
                db.session.commit()
                flash(f"Sensor '{sensor.sensor_code}' configuration updated.", "success")

        elif action == "delete":
            sensor_id = request.form.get("sensor_id", type=int)
            sensor = db.session.get(Sensor, sensor_id)
            if sensor:
                db.session.delete(sensor)
                db.session.commit()
                flash(f"Sensor '{sensor.sensor_code}' deleted.", "info")

        elif action == "update_status":
            sensor_id = request.form.get("sensor_id", type=int)
            new_status = request.form.get("new_status", "online")
            sensor = db.session.get(Sensor, sensor_id)
            if sensor:
                sensor.status = new_status
                if new_status == "online":
                    sensor.last_seen = utc_now()
                db.session.commit()
                flash(f"Sensor '{sensor.sensor_code}' status updated to {new_status}.", "success")

        elif action == "simulate_reading":
            sensor_id = request.form.get("sensor_id", type=int)
            from app.services.data_generator import generate_single_reading
            try:
                reading = generate_single_reading(sensor_id=sensor_id, save=True)
                flash(f"Simulated live telemetry for '{reading.sensor.sensor_code}' — Temp: {reading.temperature}°C, PM2.5: {reading.pm25} µg/m³, AQI: {reading.aqi}.", "success")
            except Exception as e:
                flash(f"Simulation failed: {str(e)}", "danger")

        return redirect(url_for("sensors.admin_sensors"))

    sensors = Sensor.query.order_by(Sensor.id.asc()).all()
    zones = CampusZone.query.order_by(CampusZone.name.asc()).all()
    return render_template("admin_sensors.html", sensors=sensors, zones=zones)


# --- REST API Endpoints ---

@sensors_bp.route("/api/sensors", methods=["GET"])
def get_sensors():
    """
    Retrieve all sensors.
    Optional query parameters: ?zone_id=1&status=online
    """
    query = Sensor.query
    zone_id = request.args.get("zone_id", type=int)
    status = request.args.get("status")

    if zone_id:
        query = query.filter_by(zone_id=zone_id)
    if status:
        query = query.filter_by(status=status.lower())

    sensors = query.order_by(Sensor.id.asc()).all()
    return api_response(
        data=[s.to_dict(include_zone=True) for s in sensors],
        message=f"Retrieved {len(sensors)} sensor devices."
    )


@sensors_bp.route("/api/sensors", methods=["POST"])
@login_required
@admin_required
def create_sensor():
    """Register a new sensor station (Admin only)."""
    data = request.get_json(silent=True) or {}
    sensor_code = data.get("sensor_code", "").strip().upper()
    zone_id = data.get("zone_id")
    name = data.get("name", "").strip()
    model = data.get("model", "CampusSense-IoT-v2.1").strip()
    sensor_type = data.get("sensor_type", "Multi-Parameter Environmental Station").strip()
    status = data.get("status", "online").lower()

    if not sensor_code or not zone_id or not name:
        return api_error("Fields 'sensor_code', 'zone_id', and 'name' are required.", status_code=400)

    if not db.session.get(CampusZone, zone_id):
        return api_error(f"Target Zone ID {zone_id} does not exist.", status_code=404)

    if Sensor.query.filter_by(sensor_code=sensor_code).first():
        return api_error(f"Sensor with code '{sensor_code}' already exists.", status_code=409)

    sensor = Sensor(
        sensor_code=sensor_code,
        zone_id=zone_id,
        name=name,
        model=model,
        sensor_type=sensor_type,
        status=status,
        last_seen=utc_now() if status == "online" else None
    )
    db.session.add(sensor)
    db.session.commit()

    return api_response(
        data=sensor.to_dict(include_zone=True),
        message="Sensor provisioned successfully.",
        status_code=201
    )


@sensors_bp.route("/api/sensors/<int:sensor_id>", methods=["GET"])
def get_sensor(sensor_id: int):
    """Retrieve specific sensor telemetry metadata and recent readings."""
    sensor = db.session.get(Sensor, sensor_id)
    if not sensor:
        return api_error(f"Sensor with ID {sensor_id} not found.", status_code=404)

    recent_readings = [r.to_dict(include_names=False) for r in sensor.readings[-10:]]
    result = sensor.to_dict(include_zone=True)
    result["recent_readings"] = recent_readings

    return api_response(data=result)


@sensors_bp.route("/api/sensors/<int:sensor_id>", methods=["PUT"])
@login_required
@admin_required
def update_sensor(sensor_id: int):
    """Update sensor station configuration or operational status (Admin only)."""
    sensor = db.session.get(Sensor, sensor_id)
    if not sensor:
        return api_error(f"Sensor with ID {sensor_id} not found.", status_code=404)

    data = request.get_json(silent=True) or {}

    if "name" in data and data["name"].strip():
        sensor.name = data["name"].strip()
    if "model" in data:
        sensor.model = data["model"].strip()
    if "sensor_type" in data:
        sensor.sensor_type = data["sensor_type"].strip()
    if "status" in data:
        sensor.status = data["status"].strip().lower()
        if sensor.status == "online":
            sensor.last_seen = utc_now()
    if "zone_id" in data:
        new_zid = data["zone_id"]
        if not db.session.get(CampusZone, new_zid):
            return api_error(f"Zone ID {new_zid} does not exist.", status_code=404)
        sensor.zone_id = new_zid

    db.session.commit()
    return api_response(data=sensor.to_dict(include_zone=True), message="Sensor updated successfully.")


@sensors_bp.route("/api/sensors/<int:sensor_id>", methods=["DELETE"])
@login_required
@admin_required
def delete_sensor(sensor_id: int):
    """Decommission and remove a sensor (Admin only)."""
    sensor = db.session.get(Sensor, sensor_id)
    if not sensor:
        return api_error(f"Sensor with ID {sensor_id} not found.", status_code=404)

    code = sensor.sensor_code
    db.session.delete(sensor)
    db.session.commit()

    return api_response(message=f"Sensor '{code}' (ID {sensor_id}) deleted successfully.")
