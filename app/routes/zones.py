"""
Campus zone management routes: REST API endpoints and Admin web views.
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.campus_zone import CampusZone
from app.utils.decorators import admin_required
from app.utils.helpers import api_response, api_error

zones_bp = Blueprint("zones", __name__)


# --- Admin Web View ---

@zones_bp.route("/admin/zones", methods=["GET", "POST"])
@login_required
def admin_zones():
    """Admin dashboard page for viewing, creating, and modifying campus zones."""
    if request.method == "POST":
        if not current_user.is_admin:
            flash("Administrator privileges required to create, edit, or delete campus zones.", "danger")
            return redirect(url_for("zones.admin_zones"))

        action = request.form.get("action", "create")
        
        if action == "create":
            name = request.form.get("name", "").strip()
            code = request.form.get("code", "").strip().upper()
            description = request.form.get("description", "").strip()
            location = request.form.get("location_details", "").strip()

            if not name or not code:
                flash("Zone name and code are mandatory.", "warning")
            elif CampusZone.query.filter((CampusZone.name == name) | (CampusZone.code == code)).first():
                flash("A zone with this name or code already exists.", "danger")
            else:
                new_zone = CampusZone(
                    name=name,
                    code=code,
                    description=description,
                    location_details=location
                )
                db.session.add(new_zone)
                db.session.commit()
                flash(f"Campus zone '{name}' created successfully.", "success")

        elif action in ["update", "edit"]:
            zone_id = request.form.get("zone_id", type=int)
            zone = db.session.get(CampusZone, zone_id)
            if zone:
                name = request.form.get("name", "").strip()
                code = request.form.get("code", "").strip().upper()
                if name:
                    zone.name = name
                if code:
                    zone.code = code
                zone.description = request.form.get("description", "").strip()
                zone.location_details = request.form.get("location_details", "").strip()
                db.session.commit()
                flash(f"Zone '{zone.name}' updated successfully.", "success")

        elif action == "delete":
            zone_id = request.form.get("zone_id", type=int)
            zone = db.session.get(CampusZone, zone_id)
            if zone:
                db.session.delete(zone)
                db.session.commit()
                flash(f"Zone '{zone.name}' and all associated sensors removed.", "info")

        return redirect(url_for("zones.admin_zones"))

    zones = CampusZone.query.order_by(CampusZone.name.asc()).all()
    return render_template("admin_zones.html", zones=zones)


# --- REST API Endpoints ---

@zones_bp.route("/api/zones", methods=["GET"])
def get_zones():
    """Retrieve all campus zones."""
    zones = CampusZone.query.order_by(CampusZone.id.asc()).all()
    return api_response(
        data=[z.to_dict(include_sensor_count=True) for z in zones],
        message=f"Retrieved {len(zones)} campus zones."
    )


@zones_bp.route("/api/zones", methods=["POST"])
@login_required
@admin_required
def create_zone():
    """Create a new campus zone (Admin only)."""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    code = data.get("code", "").strip().upper()
    description = data.get("description", "").strip()
    location_details = data.get("location_details", "").strip()

    if not name or not code:
        return api_error("Both 'name' and 'code' fields are required.", status_code=400)

    if CampusZone.query.filter_by(name=name).first():
        return api_error(f"A zone with name '{name}' already exists.", status_code=409)

    if CampusZone.query.filter_by(code=code).first():
        return api_error(f"A zone with code '{code}' already exists.", status_code=409)

    zone = CampusZone(
        name=name,
        code=code,
        description=description,
        location_details=location_details
    )
    db.session.add(zone)
    db.session.commit()

    return api_response(
        data=zone.to_dict(),
        message="Campus zone created successfully.",
        status_code=201
    )


@zones_bp.route("/api/zones/<int:zone_id>", methods=["GET"])
def get_zone(zone_id: int):
    """Retrieve specific campus zone details and associated sensors."""
    zone = db.session.get(CampusZone, zone_id)
    if not zone:
        return api_error(f"Zone with ID {zone_id} not found.", status_code=404)

    result = zone.to_dict(include_sensor_count=True)
    result["sensors"] = [s.to_dict(include_zone=False) for s in zone.sensors]
    return api_response(data=result)


@zones_bp.route("/api/zones/<int:zone_id>", methods=["PUT"])
@login_required
@admin_required
def update_zone(zone_id: int):
    """Update campus zone attributes (Admin only)."""
    zone = db.session.get(CampusZone, zone_id)
    if not zone:
        return api_error(f"Zone with ID {zone_id} not found.", status_code=404)

    data = request.get_json(silent=True) or {}
    if "name" in data and data["name"].strip():
        new_name = data["name"].strip()
        conflict = CampusZone.query.filter(CampusZone.name == new_name, CampusZone.id != zone_id).first()
        if conflict:
            return api_error(f"Name '{new_name}' is already used by another zone.", status_code=409)
        zone.name = new_name

    if "code" in data and data["code"].strip():
        new_code = data["code"].strip().upper()
        conflict = CampusZone.query.filter(CampusZone.code == new_code, CampusZone.id != zone_id).first()
        if conflict:
            return api_error(f"Code '{new_code}' is already used by another zone.", status_code=409)
        zone.code = new_code

    if "description" in data:
        zone.description = data["description"]
    if "location_details" in data:
        zone.location_details = data["location_details"]

    db.session.commit()
    return api_response(data=zone.to_dict(), message="Campus zone updated successfully.")


@zones_bp.route("/api/zones/<int:zone_id>", methods=["DELETE"])
@login_required
@admin_required
def delete_zone(zone_id: int):
    """Delete a campus zone and cascading sensors/readings (Admin only)."""
    zone = db.session.get(CampusZone, zone_id)
    if not zone:
        return api_error(f"Zone with ID {zone_id} not found.", status_code=404)

    zone_name = zone.name
    db.session.delete(zone)
    db.session.commit()

    return api_response(message=f"Campus zone '{zone_name}' (ID {zone_id}) deleted successfully.")
