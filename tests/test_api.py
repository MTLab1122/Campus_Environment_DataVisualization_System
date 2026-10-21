"""
Integration tests for Flask REST API endpoints.
Validates HTTP methods, payload schemas, authorization guards, and response status codes.
"""
import json


def test_auth_login_and_me(client):
    """Test user authentication workflow."""
    # Test invalid credentials
    res = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert res.status_code == 401
    assert res.get_json()["success"] is False

    # Test valid admin login
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["user"]["role"] == "admin"

    # Test /api/auth/me
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["data"]["authenticated"] is True
    assert me_res.get_json()["data"]["user"]["username"] == "admin"


def test_get_zones(client):
    """Test retrieving campus zones list."""
    res = client.get("/api/zones")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert data["data"][0]["code"] == "ZONE_LIB"


def test_create_zone_unauthenticated(client):
    """Test unauthenticated client receives 401 on protected endpoint."""
    res = client.post("/api/zones", json={"name": "Classroom", "code": "ZONE_C1"})
    assert res.status_code == 401
    assert res.get_json()["success"] is False


def test_create_zone_forbidden_for_viewer(viewer_client):
    """Test authenticated viewer receives 403 on admin-only endpoint."""
    res = viewer_client.post("/api/zones", json={"name": "Classroom", "code": "ZONE_C2"})
    assert res.status_code == 403
    assert res.get_json()["success"] is False


def test_create_zone_admin_success(admin_client):
    """Test authenticated admin successfully provisions campus zone."""
    zone_payload = {
        "name": "Classroom Complex",
        "code": "ZONE_CLASS",
        "description": "Lecture Halls",
        "location_details": "Block B"
    }
    res = admin_client.post("/api/zones", json=zone_payload)
    assert res.status_code == 201
    assert res.get_json()["data"]["code"] == "ZONE_CLASS"


def test_sensor_endpoints(admin_client):
    """Test sensor creation, retrieval, and status update."""
    res = admin_client.post("/api/sensors", json={
        "sensor_code": "ENV-SN-LIB-02",
        "zone_id": 1,
        "name": "Library Secondary Monitor",
        "model": "CampusSense-v2",
        "status": "online"
    })
    assert res.status_code == 201
    sensor_id = res.get_json()["data"]["id"]

    # Retrieve sensor
    get_res = admin_client.get(f"/api/sensors/{sensor_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["data"]["sensor_code"] == "ENV-SN-LIB-02"

    # Update sensor
    put_res = admin_client.put(f"/api/sensors/{sensor_id}", json={"status": "maintenance"})
    assert put_res.status_code == 200
    assert put_res.get_json()["data"]["status"] == "maintenance"


def test_telemetry_reading_ingestion(client):
    """Test IoT reading submission endpoint with automated AQI calculation."""
    reading_payload = {
        "sensor_code": "ENV-SN-LIB-01",
        "temperature": 24.5,
        "humidity": 45.0,
        "pm25": 18.0,
        "pm10": 32.0,
        "co2": 620.0,
        "noise": 38.5,
        "weather_condition": "Clear"
    }
    res = client.post("/api/readings", json=reading_payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert "reading" in data["data"]
    # Verify AQI calculation was automatically performed
    assert data["data"]["reading"]["aqi"] > 0


def test_get_readings_with_filters(client):
    """Test reading query filtering parameters."""
    res = client.get("/api/readings?limit=10&page=1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "readings" in data["data"]
    assert "total_count" in data["data"]


def test_dashboard_stats_and_reports(client):
    """Test reporting and consolidated dashboard statistics endpoints."""
    # Summary stats
    stats_res = client.get("/api/dashboard/stats")
    assert stats_res.status_code == 200
    assert "campus_overview" in stats_res.get_json()["data"]
    assert "metrics" in stats_res.get_json()["data"]

    # Daily report
    rep_res = client.get("/api/reports/summary?period=daily")
    assert rep_res.status_code == 200
    assert rep_res.get_json()["data"]["period"] == "daily"

    # CSV download
    csv_res = client.get("/api/reports/export-csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers.get("Content-Type", "")
