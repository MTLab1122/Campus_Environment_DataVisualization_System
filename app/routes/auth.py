"""
Authentication routes for web sessions and REST API endpoints.
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.utils.helpers import api_response, api_error

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    """Root route redirecting to the interactive Plotly Dash dashboard."""
    return redirect("/dashboard/")


@auth_bp.route("/dashboard-redirect")
def dashboard_redirect():
    """Helper redirect to dashboard."""
    return redirect("/dashboard/")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Web login interface."""
    if current_user.is_authenticated:
        return redirect("/dashboard/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        remember = bool(request.form.get("remember"))

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.username}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or "/dashboard/")
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration interface (creates default viewer role)."""
    if current_user.is_authenticated:
        return redirect("/dashboard/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not email or not password:
            flash("All fields are required.", "warning")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "warning")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "warning")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email address is already registered.", "warning")
            return render_template("register.html")

        # Create new viewer user
        new_user = User(
            username=username,
            email=email,
            role="viewer"
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Registration successful! Welcome to Campus Environmental Monitoring.", "success")
        return redirect("/dashboard/")

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Web logout handler."""
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


# --- REST API Authentication Endpoints ---

@auth_bp.route("/api/auth/login", methods=["POST"])
def api_login():
    """
    JSON API login endpoint.
    Payload: {"username": "admin", "password": "..."}
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return api_error("Username and password are required.", status_code=400)

    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if not user or not user.check_password(password):
        return api_error("Invalid credentials.", status_code=401)

    login_user(user)
    return api_response(
        data={"user": user.to_dict()},
        message=f"Login successful. Authenticated as {user.username} ({user.role})."
    )


@auth_bp.route("/api/auth/logout", methods=["POST"])
def api_logout():
    """JSON API logout endpoint."""
    if current_user.is_authenticated:
        logout_user()
    return api_response(message="Logged out successfully.")


@auth_bp.route("/api/auth/me", methods=["GET"])
def api_current_user():
    """Return currently authenticated user profile or anonymous status."""
    if not current_user.is_authenticated:
        return api_response(
            data={"authenticated": False, "user": None},
            message="No active session."
        )
    return api_response(
        data={"authenticated": True, "user": current_user.to_dict()},
        message="Session active."
    )
