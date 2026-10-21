"""
Flask extensions initialization module.
Prevents circular imports between application factory, models, and routes.
"""
from flask import request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please authenticate to access this resource."
login_manager.login_message_category = "warning"


@login_manager.unauthorized_handler
def handle_unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "message": "Authentication required. Please log in.",
            "errors": []
        }), 401
    flash(login_manager.login_message, login_manager.login_message_category)
    return redirect(url_for(login_manager.login_view, next=request.url))

