"""
Authentication and role-based authorization decorators.
"""
from functools import wraps
from flask import request, redirect, url_for, flash
from flask_login import current_user
from app.utils.helpers import api_error


def admin_required(f):
    """
    Ensure the accessing user is logged in and possesses the 'admin' role.
    Gracefully handles both JSON API requests and standard browser page routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_api = request.path.startswith("/api/")
        
        if not current_user.is_authenticated:
            if is_api:
                return api_error(message="Authentication required. Please log in.", status_code=401)
            flash("Authentication required. Please log in with admin privileges.", "warning")
            return redirect(url_for("auth.login", next=request.url))
            
        if not getattr(current_user, "is_admin", False):
            if is_api:
                return api_error(message="Forbidden. Admin privilege required for this operation.", status_code=403)
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("auth.dashboard_redirect"))
            
        return f(*args, **kwargs)
    return decorated_function


def viewer_or_admin_required(f):
    """
    Ensure the user is authenticated with either 'viewer' or 'admin' role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_api = request.path.startswith("/api/")
        
        if not current_user.is_authenticated:
            if is_api:
                return api_error(message="Authentication required. Please log in.", status_code=401)
            flash("Please sign in to view environmental monitoring data.", "info")
            return redirect(url_for("auth.login", next=request.url))
            
        return f(*args, **kwargs)
    return decorated_function
