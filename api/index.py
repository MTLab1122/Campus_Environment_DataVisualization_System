"""
Serverless entry point for Vercel deployment.
Routes incoming WSGI HTTP requests to the Flask & Plotly Dash application.
"""
import os
import sys
import shutil
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# In serverless environments like Vercel, the filesystem is read-only except /tmp
tmp_db = Path("/tmp/campus_environment.db")
source_db = BASE_DIR / "instance" / "campus_environment.db"

if not tmp_db.exists():
    if source_db.exists():
        try:
            shutil.copyfile(source_db, tmp_db)
        except Exception as e:
            print("Notice: could not copy pre-seeded database to /tmp:", e)

# Point SQLite to /tmp on serverless or fallback to relative db
if tmp_db.exists():
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db}"
elif not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = f"sqlite:///{source_db}"

os.environ["FLASK_ENV"] = "production"

from app import create_app
from app.extensions import db
from app.services.alert_service import seed_default_thresholds

# Create the WSGI application instance expected by Vercel's Python runtime
app = create_app("production")

with app.app_context():
    try:
        db.create_all()
        seed_default_thresholds()
    except Exception as e:
        print("Initialization notice:", e)

# Expose WSGI handler
handler = app
