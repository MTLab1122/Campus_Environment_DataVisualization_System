import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "campus-env-secret-key-default-2026")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    JSON_SORT_KEYS = False
    
    # Dashboard configuration
    DASHBOARD_URL_BASE = "/dashboard/"
    
    # Campus Environmental Constants
    CAMPUS_ZONES_DEFAULT = [
        {"name": "Main Gate", "code": "ZONE_GATE", "description": "Campus entrance and primary security checkpoint with high vehicle transit."},
        {"name": "Library", "code": "ZONE_LIB", "description": "Central academic library and quiet study zone requiring acoustic regulation."},
        {"name": "Classroom Block", "code": "ZONE_CLASS", "description": "Multi-storey instructional facility with high daytime student density."},
        {"name": "Cafeteria", "code": "ZONE_CAFE", "description": "Student and faculty dining center with active kitchen ventilation requirements."},
        {"name": "Hostel", "code": "ZONE_HOSTEL", "description": "Residential hall with peak overnight and weekend occupancy."},
        {"name": "Playground", "code": "ZONE_PLAY", "description": "Open-air sports arena and track vulnerable to ambient weather and heat."},
        {"name": "Parking Area", "code": "ZONE_PARK", "description": "Surface parking lot with commuter exhaust emissions during peak hours."},
        {"name": "Laboratory Block", "code": "ZONE_LAB", "description": "Science and engineering labs requiring strict temperature and ventilation controls."}
    ]


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    db_path = BASE_DIR / "campus_environment.db"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{db_path}")


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'campus_environment.db'}")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
