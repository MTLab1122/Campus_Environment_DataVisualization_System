"""
Comprehensive end-to-end runtime functional validation script.
Performs real HTTP requests against the live running server to test every feature.
"""
import sys
import json
import requests

import pytest

BASE_URL = "http://127.0.0.1:5000"


def test_runtime_all():
    session = requests.Session()
    print("\n" + "=" * 60)
    print("  EXECUTING COMPREHENSIVE RUNTIME VALIDATION")
    print("=" * 60)

    # 1. Test Root Redirect
    print("[1/10] Testing Root Redirect...")
    try:
        r = session.get(f"{BASE_URL}/", allow_redirects=False, timeout=3)
    except requests.exceptions.ConnectionError:
        pytest.skip("Live server at http://127.0.0.1:5000 is not running.")
    assert r.status_code == 302, f"Expected 302 redirect from root, got {r.status_code}"
    print("  [+] Root redirects to:", r.headers.get("Location"))

    # 2. Test Dashboard HTML & Dash Endpoints
    print("[2/10] Testing Plotly Dash Core Endpoints...")
    r_dash = session.get(f"{BASE_URL}/dashboard/")
    assert r_dash.status_code == 200, f"Expected 200 on /dashboard/, got {r_dash.status_code}"
    assert "Campus Environment" in r_dash.text, "Dashboard HTML missing title"

    # Dash layout
    r_layout = session.get(f"{BASE_URL}/dashboard/_dash-layout")
    assert r_layout.status_code == 200, f"Expected 200 for _dash-layout, got {r_layout.status_code}"
    layout_data = r_layout.json()
    assert "props" in layout_data, "Dash layout JSON invalid"
    print("  [+] Dash layout loaded successfully.")

    # Dash dependencies (callbacks)
    r_deps = session.get(f"{BASE_URL}/dashboard/_dash-dependencies")
    assert r_deps.status_code == 200, f"Expected 200 for _dash-dependencies, got {r_deps.status_code}"
    deps = r_deps.json()
    print(f"  [+] Dash registered callbacks verified: {len(deps)} callbacks active.")

    # 3. Test Dash Callback Execution (Master Dashboard Update)
    print("[3/10] Testing Master Dashboard Reactive Callback...")
    # Find master callback in deps
    # The output contains container-metric-cards, chart-trend-line, etc.
    callback_payload = {
        "output": "..container-metric-cards.children...container-alerts-panel.children...chart-trend-line.figure...chart-gauge.figure...chart-zone-bar.figure...chart-distribution-box.figure...chart-diurnal-heatmap.figure...table-filtered-readings.data...label-table-count.children...label-last-refreshed.children...container-zone-quick-list.children..",
        "outputs": [
            {"id": "container-metric-cards", "property": "children"},
            {"id": "container-alerts-panel", "property": "children"},
            {"id": "chart-trend-line", "property": "figure"},
            {"id": "chart-gauge", "property": "figure"},
            {"id": "chart-zone-bar", "property": "figure"},
            {"id": "chart-distribution-box", "property": "figure"},
            {"id": "chart-diurnal-heatmap", "property": "figure"},
            {"id": "table-filtered-readings", "property": "data"},
            {"id": "label-table-count", "property": "children"},
            {"id": "label-last-refreshed", "property": "children"},
            {"id": "container-zone-quick-list", "property": "children"}
        ],
        "inputs": [
            {"id": "filter-zone", "property": "value", "value": "ALL"},
            {"id": "filter-parameter", "property": "value", "value": "pm25"},
            {"id": "filter-date-range", "property": "start_date", "value": "2026-10-10"},
            {"id": "filter-date-range", "property": "end_date", "value": "2026-10-19"},
            {"id": "filter-time-range", "property": "value", "value": [0, 23]},
            {"id": "btn-refresh-data", "property": "n_clicks", "value": 1},
            {"id": "interval-auto-refresh", "property": "n_intervals", "value": 0},
            {"id": "store-alert-resolved-trigger", "property": "data", "value": 0},
            {"id": "store-simulated-reading-trigger", "property": "data", "value": 0}
        ],
        "changedPropIds": ["btn-refresh-data.n_clicks"]
    }
    r_cb = session.post(f"{BASE_URL}/dashboard/_dash-update-component", json=callback_payload)
    assert r_cb.status_code == 200, f"Expected 200 for dashboard callback, got {r_cb.status_code}: {r_cb.text}"
    cb_data = r_cb.json()
    assert "response" in cb_data, "Callback response missing data"
    print("  [+] Master dashboard callback executed with real SQLite data; charts and KPI cards generated.")

    # 4. Test Report Period Switching Callback
    print("[4/10] Testing Report Card Update...")
    r_rep = session.get(f"{BASE_URL}/api/reports/summary?period=daily")
    assert r_rep.status_code == 200
    rep_json = r_rep.json()["data"]
    assert "zone_summaries" in rep_json
    print(f"  [+] Daily report generated across {len(rep_json['zone_summaries'])} zones.")

    r_rep_w = session.get(f"{BASE_URL}/api/reports/summary?period=weekly")
    assert r_rep_w.status_code == 200
    r_rep_m = session.get(f"{BASE_URL}/api/reports/summary?period=monthly")
    assert r_rep_m.status_code == 200
    print("  [+] Weekly and Monthly reports verified.")

    # 5. Test Authentication API & Web Sessions
    print("[5/10] Testing Authentication & RBAC...")
    # Admin login
    r_login = session.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert r_login.status_code == 200, f"Admin login failed: {r_login.text}"
    assert r_login.json()["data"]["user"]["role"] == "admin"

    # Current user
    r_me = session.get(f"{BASE_URL}/api/auth/me")
    assert r_me.status_code == 200
    assert r_me.json()["data"]["user"]["username"] == "admin"
    print("  [+] Admin authenticated session verified.")

    # 6. Test Admin Zone CRUD
    print("[6/10] Testing Admin Zone Operations...")
    r_create_zone = session.post(f"{BASE_URL}/api/zones", json={
        "name": "Botanical Conservatory",
        "code": "ZONE_BOTANIC",
        "description": "Greenhouse research facility",
        "location_details": "East Bio-Quad"
    })
    assert r_create_zone.status_code == 201, f"Failed to create zone: {r_create_zone.text}"
    new_zone_id = r_create_zone.json()["data"]["id"]
    print(f"  [+] Created zone: ID {new_zone_id}")

    # Update zone
    r_update_zone = session.put(f"{BASE_URL}/api/zones/{new_zone_id}", json={
        "description": "Updated greenhouse research facility with smart glass"
    })
    assert r_update_zone.status_code == 200

    # Delete zone
    r_del_zone = session.delete(f"{BASE_URL}/api/zones/{new_zone_id}")
    assert r_del_zone.status_code == 200
    print("  [+] Admin Zone CRUD cycle verified.")

    # 7. Test Admin Sensor Operations
    print("[7/10] Testing Admin Sensor Provisioning...")
    r_create_sensor = session.post(f"{BASE_URL}/api/sensors", json={
        "sensor_code": "ENV-SN-TEST-99",
        "zone_id": 1,
        "name": "Temporary Test Station",
        "model": "CampusSense-v2.1",
        "status": "online"
    })
    assert r_create_sensor.status_code == 201, f"Failed to provision sensor: {r_create_sensor.text}"
    new_sensor_id = r_create_sensor.json()["data"]["id"]

    r_update_sensor = session.put(f"{BASE_URL}/api/sensors/{new_sensor_id}", json={"status": "maintenance"})
    assert r_update_sensor.status_code == 200
    assert r_update_sensor.json()["data"]["status"] == "maintenance"

    r_del_sensor = session.delete(f"{BASE_URL}/api/sensors/{new_sensor_id}")
    assert r_del_sensor.status_code == 200
    print("  [+] Admin Sensor Provisioning cycle verified.")

    # 8. Test Telemetry Ingestion (IoT endpoint) & Alert Triggering
    print("[8/10] Testing Telemetry Ingestion & Real-Time Alert Evaluation...")
    # Ingest reading with elevated PM2.5 (62.0 > 55.0 dangerous) and elevated CO2 (1400 > 1000 poor)
    r_ingest = session.post(f"{BASE_URL}/api/readings", json={
        "sensor_code": "ENV-SN-LIB-01",
        "temperature": 24.2,
        "humidity": 49.0,
        "pm25": 62.0,
        "pm10": 45.0,
        "co2": 1400.0,
        "noise": 42.0,
        "weather_condition": "Clear"
    })
    assert r_ingest.status_code == 201, f"Ingestion failed: {r_ingest.text}"
    ingest_data = r_ingest.json()["data"]
    reading = ingest_data["reading"]
    alerts = ingest_data["alerts_triggered"]
    assert reading["aqi"] > 150, f"AQI calculation incorrect, got {reading['aqi']}"
    assert len(alerts) >= 2, f"Expected at least 2 alerts triggered, got {len(alerts)}"
    print(f"  [+] Ingested reading ID {reading['id']} with computed AQI {reading['aqi']}.")
    print(f"  [+] Real-time alerts generated: {[a['severity'] + ' on ' + a['parameter'] for a in alerts]}")

    # 9. Test Alert Resolution
    print("[9/10] Testing Alert Query & Resolution...")
    r_alerts = session.get(f"{BASE_URL}/api/alerts?is_resolved=false&limit=5")
    assert r_alerts.status_code == 200
    active_alerts = r_alerts.json()["data"]["alerts"]
    assert len(active_alerts) > 0
    target_alert_id = active_alerts[0]["id"]

    r_resolve = session.put(f"{BASE_URL}/api/alerts/{target_alert_id}/resolve")
    assert r_resolve.status_code == 200
    assert r_resolve.json()["data"]["is_resolved"] is True
    print(f"  [+] Alert #{target_alert_id} resolved successfully.")

    # 10. Test CSV Export & Dashboard Stats
    print("[10/10] Testing CSV Data Export & Top-level Stats...")
    r_csv = session.get(f"{BASE_URL}/api/reports/export-csv")
    assert r_csv.status_code == 200
    assert "text/csv" in r_csv.headers.get("Content-Type", "")
    csv_lines = r_csv.text.strip().split("\n")
    assert len(csv_lines) > 10, "CSV export returned insufficient data"
    print(f"  [+] CSV Export verified: {len(csv_lines)} rows downloaded.")

    r_stats = session.get(f"{BASE_URL}/api/dashboard/stats")
    assert r_stats.status_code == 200
    stats_data = r_stats.json()["data"]
    print(f"  [+] Campus Overview: {stats_data['campus_overview']}")

    # Test Admin Web Template Views
    print("\n  [+] Verifying Admin Web HTML Views...")
    for path in ["/admin/zones", "/admin/sensors", "/admin/thresholds", "/admin/readings/manual"]:
        r_view = session.get(f"{BASE_URL}{path}")
        assert r_view.status_code == 200, f"Failed GET {path}: {r_view.status_code}"
        print(f"      - {path} -> HTTP 200 OK")

    print("\n" + "=" * 60)
    print("  ALL RUNTIME FUNCTIONALITY TESTS PASSED WITH ZERO ERRORS!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_runtime_all()
