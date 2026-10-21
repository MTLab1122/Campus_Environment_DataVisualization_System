"""
Unit and integration tests for Campus Environmental Health Index (CEHI),
zone radar matrix, parameter correlations, and enhanced API endpoints.
"""
import pytest
from app.services.analytics import (
    calculate_campus_health_score,
    get_zone_radar_matrix,
    get_parameter_correlations
)
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.environmental_reading import EnvironmentalReading


def test_calculate_campus_health_score(app):
    """Test calculation of Campus Environmental Health Index."""
    with app.app_context():
        # Test without readings (default fallback)
        fallback = calculate_campus_health_score()
        assert "score" in fallback
        assert "grade" in fallback
        assert "sub_indices" in fallback
        assert 0 <= fallback["score"] <= 100

        # Add a reading with known values
        zone = CampusZone.query.first()
        sensor = Sensor.query.first()
        reading = EnvironmentalReading(
            sensor_id=sensor.id,
            zone_id=zone.id,
            temperature=22.0,
            humidity=50.0,
            pm25=12.0,
            pm10=25.0,
            co2=500.0,
            noise=45.0,
            aqi=40.0,
            weather_condition="Sunny"
        )
        from app.extensions import db
        db.session.add(reading)
        db.session.commit()

        health = calculate_campus_health_score(zone_id=zone.id)
        assert health["score"] >= 80.0
        assert health["grade"] in ["A+", "A"]
        assert health["sub_indices"]["air_quality"] > 70.0
        assert health["sub_indices"]["ventilation"] > 70.0


def test_zone_radar_matrix(app):
    """Test normalized multi-dimensional radar comparison matrix."""
    with app.app_context():
        radar = get_zone_radar_matrix()
        assert "categories" in radar
        assert len(radar["categories"]) == 5
        assert "zones" in radar
        assert len(radar["zones"]) >= 1
        for z in radar["zones"]:
            assert "zone_name" in z
            assert "values" in z
            assert len(z["values"]) == 5
            for v in z["values"]:
                assert 0.0 <= v <= 100.0


def test_parameter_correlations(app):
    """Test pairwise Pearson correlation matrix."""
    with app.app_context():
        corr = get_parameter_correlations()
        assert "parameters" in corr
        assert "matrix" in corr
        assert len(corr["parameters"]) == 7
        for p in corr["parameters"]:
            assert p in corr["matrix"]
            assert p in corr["matrix"][p]


def test_api_health_index_endpoint(client):
    """Test GET /api/campus/health-index endpoint."""
    res = client.get("/api/campus/health-index")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "score" in data["data"]
    assert "grade" in data["data"]


def test_api_radar_endpoint(client):
    """Test GET /api/analytics/radar endpoint."""
    res = client.get("/api/analytics/radar")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "categories" in data["data"]
    assert "zones" in data["data"]


def test_api_correlations_endpoint(client):
    """Test GET /api/analytics/correlations endpoint."""
    res = client.get("/api/analytics/correlations")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "matrix" in data["data"]


def test_api_simulate_pulse_endpoint(client):
    """Test POST /api/readings/simulate-pulse endpoint."""
    res = client.post("/api/readings/simulate-pulse", json={})
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert "reading" in data["data"]
    assert "alerts_triggered" in data["data"]


def test_api_docs_html_page(client):
    """Test GET /api/docs interactive documentation page."""
    res = client.get("/api/docs")
    assert res.status_code == 200
    assert "REST API Reference" in res.text or "REST API Documentation" in res.text
