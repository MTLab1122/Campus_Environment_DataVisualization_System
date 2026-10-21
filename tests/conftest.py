"""
Pytest test fixtures and configuration.
Sets up isolated in-memory SQLite database, test client, and seeded entities.
"""
import pytest
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.alert import AlertThreshold
from app.services.alert_service import seed_default_thresholds
import socket
import threading
import time
from werkzeug.serving import make_server
from app.utils.helpers import utc_now


def is_port_open(host="127.0.0.1", port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session", autouse=True)
def live_server_daemon():
    """Ensure a live server is running on port 5000 for end-to-end integration tests."""
    if is_port_open("127.0.0.1", 5000):
        yield
        return

    from app import create_app

    live_app = create_app("development")

    try:
        srv = make_server("127.0.0.1", 5000, live_app, threaded=True)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()

        # Wait for the server to accept connections
        for _ in range(40):
            if is_port_open("127.0.0.1", 5000):
                break
            time.sleep(0.1)

        yield
        srv.shutdown()
    except Exception as e:
        print(f"Note: Could not start live test server on port 5000: {e}")
        yield



@pytest.fixture(scope="function")
def app():
    """Create a clean Flask application configured for testing."""
    test_app = create_app("testing")
    
    with test_app.app_context():
        db.create_all()
        seed_default_thresholds()

        # Create test users
        admin = User(username="admin", email="admin@campus.edu", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

        viewer = User(username="viewer", email="viewer@campus.edu", role="viewer")
        viewer.set_password("viewer123")
        db.session.add(viewer)

        # Create test zone
        zone = CampusZone(
            name="Library",
            code="ZONE_LIB",
            description="Quiet study area",
            location_details="Building A"
        )
        db.session.add(zone)
        db.session.flush()

        # Create test sensor
        sensor = Sensor(
            sensor_code="ENV-SN-LIB-01",
            zone_id=zone.id,
            name="Library Sensor Node",
            model="CampusSense-v2",
            status="online",
            last_seen=utc_now()
        )
        db.session.add(sensor)
        db.session.commit()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Test HTTP client."""
    return app.test_client()


@pytest.fixture(scope="function")
def admin_client(app):
    """Client with authenticated admin session."""
    c = app.test_client()
    c.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    return c


@pytest.fixture(scope="function")
def viewer_client(app):
    """Client with authenticated viewer session."""
    c = app.test_client()
    c.post("/api/auth/login", json={"username": "viewer", "password": "viewer123"})
    return c

