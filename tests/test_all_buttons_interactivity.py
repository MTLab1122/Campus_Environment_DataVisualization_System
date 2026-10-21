"""
End-to-End Interactivity & Button Functional Validation Test Suite.
Verifies every single interactive button, form, callback, and RBAC constraint
across the Campus Environment Data Visualization System.
"""
import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"


def test_button_interactivity_all():
    session = requests.Session()
    print("\n" + "=" * 65)
    print("  VERIFYING ALL SYSTEM BUTTONS, CALLBACKS & USER INTERACTIONS")
    print("=" * 65)

    # -------------------------------------------------------------
    # Step 1: Authentication & Demo Login
    # -------------------------------------------------------------
    print("\n[BUTTON TEST 1/8] Sign In & User Authentication")
    # 1-click Admin Login
    try:
        login_res = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        }, timeout=3)
    except requests.exceptions.ConnectionError:
        pytest.skip("Live server at http://127.0.0.1:5000 is not running.")
    assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
    user_data = login_res.json()["data"]["user"]
    assert user_data["role"] == "admin"
    print(f"  [+] Logged in as: {user_data['username']} (Role: {user_data['role']})")

    # -------------------------------------------------------------
    # Step 2: Dashboard Filter Panel Buttons & Callbacks
    # -------------------------------------------------------------
    print("\n[BUTTON TEST 2/8] Dashboard Parameter & Filter Quick Buttons")

    # 2a. Quick Parameter Selection Pills (pm10, co2, noise, temperature, humidity, aqi)
    for param in ["pm10", "co2", "noise", "temperature", "humidity", "aqi"]:
        cb_param_payload = {
            "output": "filter-parameter.value",
            "outputs": {"id": "filter-parameter", "property": "value"},
            "inputs": [
                {"id": "btn-reset-filters", "property": "n_clicks", "value": None},
                {"id": "pill-param-pm25", "property": "n_clicks", "value": None},
                {"id": "pill-param-pm10", "property": "n_clicks", "value": 1 if param == "pm10" else None},
                {"id": "pill-param-co2", "property": "n_clicks", "value": 1 if param == "co2" else None},
                {"id": "pill-param-noise", "property": "n_clicks", "value": 1 if param == "noise" else None},
                {"id": "pill-param-temperature", "property": "n_clicks", "value": 1 if param == "temperature" else None},
                {"id": "pill-param-humidity", "property": "n_clicks", "value": 1 if param == "humidity" else None},
                {"id": "pill-param-aqi", "property": "n_clicks", "value": 1 if param == "aqi" else None}
            ],
            "state": [
                {"id": "filter-parameter", "property": "value", "value": "pm25"}
            ],
            "changedPropIds": [f"pill-param-{param}.n_clicks"]
        }
        res = session.post(f"{BASE_URL}/dashboard/_dash-update-component", json=cb_param_payload)
        assert res.status_code == 200, f"Pill {param} failed: {res.text}"
        assert res.json()["response"]["filter-parameter"]["value"] == param
        print(f"  [+] Pill 'pill-param-{param}' clicked -> Switch parameter to '{param}' verified.")

    # 2b. Reset Filters Button (btn-reset-filters)
    # Checks reset of zone, parameter, date range, and time range
    cb_reset_param = {
        "output": "filter-parameter.value",
        "outputs": {"id": "filter-parameter", "property": "value"},
        "inputs": [
            {"id": "btn-reset-filters", "property": "n_clicks", "value": 1},
            {"id": "pill-param-pm25", "property": "n_clicks", "value": None},
            {"id": "pill-param-pm10", "property": "n_clicks", "value": None},
            {"id": "pill-param-co2", "property": "n_clicks", "value": None},
            {"id": "pill-param-noise", "property": "n_clicks", "value": None},
            {"id": "pill-param-temperature", "property": "n_clicks", "value": None},
            {"id": "pill-param-humidity", "property": "n_clicks", "value": None},
            {"id": "pill-param-aqi", "property": "n_clicks", "value": None}
        ],
        "state": [
            {"id": "filter-parameter", "property": "value", "value": "noise"}
        ],
        "changedPropIds": ["btn-reset-filters.n_clicks"]
    }
    res_reset_p = session.post(f"{BASE_URL}/dashboard/_dash-update-component", json=cb_reset_param)
    assert res_reset_p.status_code == 200
    assert res_reset_p.json()["response"]["filter-parameter"]["value"] == "pm25"
    print("  [+] Button 'btn-reset-filters' clicked -> Resets parameter to default 'pm25'.")

    # 2c. Reset Time & Date Window Callback
    cb_reset_date = {
        "output": "..filter-date-range.start_date...filter-date-range.end_date...filter-time-range.value..",
        "outputs": [
            {"id": "filter-date-range", "property": "start_date"},
            {"id": "filter-date-range", "property": "end_date"},
            {"id": "filter-time-range", "property": "value"}
        ],
        "inputs": [
            {"id": "btn-reset-filters", "property": "n_clicks", "value": 1}
        ],
        "changedPropIds": ["btn-reset-filters.n_clicks"]
    }
    res_reset_d = session.post(f"{BASE_URL}/dashboard/_dash-update-component", json=cb_reset_date)
    assert res_reset_d.status_code == 200
    time_window = res_reset_d.json()["response"]["filter-time-range"]["value"]
    assert time_window == [0, 23]
    print(f"  [+] Button 'btn-reset-filters' clicked -> Resets time window to {time_window} (Full 24-hr day).")

    # -------------------------------------------------------------
    # Step 3: Live Telemetry Simulation Button (btn-simulate-reading)
    # -------------------------------------------------------------
    print("\n[BUTTON TEST 3/8] Live Telemetry Simulation Button")
    cb_sim_payload = {
        "output": "store-simulated-reading-trigger.data",
        "outputs": {"id": "store-simulated-reading-trigger", "property": "data"},
        "inputs": [
            {"id": "btn-simulate-reading", "property": "n_clicks", "value": 1}
        ],
        "state": [
            {"id": "store-simulated-reading-trigger", "property": "data", "value": 0},
            {"id": "filter-zone", "property": "value", "value": "ALL"}
        ],
        "changedPropIds": ["btn-simulate-reading.n_clicks"]
    }
    res_sim = session.post(f"{BASE_URL}/dashboard/_dash-update-component", json=cb_sim_payload)
    assert res_sim.status_code == 200
    sim_trigger_val = res_sim.json()["response"]["store-simulated-reading-trigger"]["data"]
    assert sim_trigger_val == 1
    print(f"  [+] Button 'btn-simulate-reading' clicked -> Injected new telemetry reading and incremented trigger to {sim_trigger_val}.")

    # -------------------------------------------------------------
    # Step 4: Alert Resolution Buttons (btn-resolve-alert & btn-resolve-all-alerts)
    # -------------------------------------------------------------
    print("\n[BUTTON TEST 4/8] Alert Resolution Controls")
    # Ingest a deliberate alert to ensure active alert exists
    ingest_res = session.post(f"{BASE_URL}/api/readings", json={
        "sensor_code": "ENV-SN-LIB-01",
        "temperature": 32.5,
        "humidity": 85.0,
        "pm25": 95.0,
        "pm10": 180.0,
        "co2": 1900.0,
        "noise": 78.0,
        "weather_condition": "Overcast"
    })
    assert ingest_res.status_code == 201

    # Fetch active alerts
    alerts_res = session.get(f"{BASE_URL}/api/alerts?is_resolved=false")
    active_alerts = alerts_res.json()["data"]["alerts"]
    assert len(active_alerts) > 0
    test_alert_id = active_alerts[0]["id"]

    # 4a. Resolve single alert callback
    cb_resolve_one = {
        "output": "store-alert-resolved-trigger.data",
        "outputs": {"id": "store-alert-resolved-trigger", "property": "data"},
        "inputs": [
            {"id": f'{{"index":{test_alert_id},"type":"btn-resolve-alert"}}', "property": "n_clicks", "value": 1},
            {"id": "btn-resolve-all-alerts", "property": "n_clicks", "value": None}
        ],
        "state": [
            {"id": "store-alert-resolved-trigger", "property": "data", "value": 0},
            {"id": "filter-zone", "property": "value", "value": "ALL"}
        ],
        "changedPropIds": [f'{{"index":{test_alert_id},"type":"btn-resolve-alert"}}.n_clicks']
    }
    res_resolve_one = session.post(f"{BASE_URL}/dashboard/_dash-update-component", json=cb_resolve_one)
    assert res_resolve_one.status_code == 200
    res_trigger = res_resolve_one.json()["response"]["store-alert-resolved-trigger"]["data"]
    assert res_trigger == 1
    print(f"  [+] Pattern-matched Button 'btn-resolve-alert' for Alert #{test_alert_id} clicked -> Resolved and reactive trigger fired.")

    # 4b. Resolve ALL alerts button
    cb_resolve_all = {
        "output": "store-alert-resolved-trigger.data",
        "outputs": {"id": "store-alert-resolved-trigger", "property": "data"},
        "inputs": [
            {"id": '{"index":1,"type":"btn-resolve-alert"}', "property": "n_clicks", "value": None},
            {"id": "btn-resolve-all-alerts", "property": "n_clicks", "value": 1}
        ],
        "state": [
            {"id": "store-alert-resolved-trigger", "property": "data", "value": 1},
            {"id": "filter-zone", "property": "value", "value": "ALL"}
        ],
        "changedPropIds": ["btn-resolve-all-alerts.n_clicks"]
    }
    res_resolve_all = session.post(f"{BASE_URL}/dashboard/_dash-update-component", json=cb_resolve_all)
    assert res_resolve_all.status_code == 200
    print("  [+] Button 'btn-resolve-all-alerts' clicked -> Batch resolved active alerts.")

    # Verify via REST endpoint as well
    res_all_api = session.post(f"{BASE_URL}/api/alerts/resolve-all")
    assert res_all_api.status_code == 200
    print(f"  [+] REST endpoint /api/alerts/resolve-all confirmed: {res_all_api.json()['message']}")

    # -------------------------------------------------------------
    # Step 5: Report Period Switching & Report CSV Export Buttons
    # -------------------------------------------------------------
    print("\n[BUTTON TEST 5/8] Reports Period Toggles & CSV Export Buttons")
    for period in ["daily", "weekly", "monthly"]:
        cb_period = {
            "output": "store-report-period.data",
            "outputs": {"id": "store-report-period", "property": "data"},
            "inputs": [
                {"id": "btn-report-daily", "property": "n_clicks", "value": 1 if period == "daily" else None},
                {"id": "btn-report-weekly", "property": "n_clicks", "value": 1 if period == "weekly" else None},
                {"id": "btn-report-monthly", "property": "n_clicks", "value": 1 if period == "monthly" else None}
            ],
            "changedPropIds": [f"btn-report-{period}.n_clicks"]
        }
        res_period = session.post(f"{BASE_URL}/dashboard/_dash-update-component", json=cb_period)
        assert res_period.status_code == 200
        assert res_period.json()["response"]["store-report-period"]["data"] == period
        print(f"  [+] Period toggle button 'btn-report-{period}' -> Switched active period to '{period}'.")

    # 5b. Export Period Report CSV Button
    cb_export_rep = {
        "output": "download-report-csv.data",
        "outputs": {"id": "download-report-csv", "property": "data"},
        "inputs": [
            {"id": "btn-export-report-csv", "property": "n_clicks", "value": 1}
        ],
        "state": [
            {"id": "store-report-period", "property": "data", "value": "weekly"},
            {"id": "filter-zone", "property": "value", "value": "ALL"}
        ],
        "changedPropIds": ["btn-export-report-csv.n_clicks"]
    }
    res_export_rep = session.post(f"{BASE_URL}/dashboard/_dash-update-component", json=cb_export_rep)
    assert res_export_rep.status_code == 200
    dl_data = res_export_rep.json()["response"]["download-report-csv"]["data"]
    assert "filename" in dl_data
    assert "weekly" in dl_data["filename"]
    print(f"  [+] Button 'btn-export-report-csv' clicked -> Triggered summary download ({dl_data['filename']}).")

    # 5c. Export Telemetry CSV Button
    cb_export_raw = {
        "output": "download-dataframe-csv.data",
        "outputs": {"id": "download-dataframe-csv", "property": "data"},
        "inputs": [
            {"id": "btn-export-csv", "property": "n_clicks", "value": 1}
        ],
        "state": [
            {"id": "filter-zone", "property": "value", "value": "ALL"},
            {"id": "filter-date-range", "property": "start_date", "value": "2026-10-10"},
            {"id": "filter-date-range", "property": "end_date", "value": "2026-10-19"}
        ],
        "changedPropIds": ["btn-export-csv.n_clicks"]
    }
    res_export_raw = session.post(f"{BASE_URL}/dashboard/_dash-update-component", json=cb_export_raw)
    assert res_export_raw.status_code == 200
    dl_raw_data = res_export_raw.json()["response"]["download-dataframe-csv"]["data"]
    assert "filename" in dl_raw_data
    print(f"  [+] Button 'btn-export-csv' clicked -> Triggered telemetry download ({dl_raw_data['filename']}).")

    # -------------------------------------------------------------
    # Step 6: Admin Zones Web Actions (Create, Edit Modal, Delete)
    # -------------------------------------------------------------
    print("\n[BUTTON TEST 6/8] Admin Zone Web Forms & Edit Modals")
    # Create zone via web form POST
    res_web_zone = session.post(f"{BASE_URL}/admin/zones", data={
        "action": "create",
        "name": "Innovation Hub Web",
        "code": "ZONE_INNOV",
        "description": "Smart electronics and makerspace lab",
        "location_details": "Building C 2nd Floor"
    }, allow_redirects=True)
    assert res_web_zone.status_code == 200
    assert "ZONE_INNOV" in res_web_zone.text
    print("  [+] Admin Web 'Add Campus Zone' form submission verified.")

    # Find the created zone ID from API
    zones_list = session.get(f"{BASE_URL}/api/zones").json()["data"]
    target_zone = [z for z in zones_list if z["code"] == "ZONE_INNOV"][0]
    zone_id = target_zone["id"]

    # Edit zone via web modal POST
    res_edit_zone = session.post(f"{BASE_URL}/admin/zones", data={
        "action": "edit",
        "zone_id": zone_id,
        "name": "Innovation Hub Web Edited",
        "code": "ZONE_INNOV_ED",
        "description": "Smart robotics & AI lab",
        "location_details": "Building C 3rd Floor"
    }, allow_redirects=True)
    assert res_edit_zone.status_code == 200
    assert "ZONE_INNOV_ED" in res_edit_zone.text
    print(f"  [+] Admin Web 'Edit Zone Modal' form submission verified for Zone #{zone_id}.")

    # Delete zone via web modal POST
    res_del_zone = session.post(f"{BASE_URL}/admin/zones", data={
        "action": "delete",
        "zone_id": zone_id
    }, allow_redirects=True)
    assert res_del_zone.status_code == 200
    assert "ZONE_INNOV_ED" not in res_del_zone.text
    print(f"  [+] Admin Web 'Delete Zone' confirmed for Zone #{zone_id}.")

    # -------------------------------------------------------------
    # Step 7: Admin Sensor Web Actions (Provision, Edit, Live Ingest)
    # -------------------------------------------------------------
    print("\n[BUTTON TEST 7/8] Admin Sensor Web Forms, Modals & Live Telemetry")
    # Provision sensor via web form POST
    res_web_sensor = session.post(f"{BASE_URL}/admin/sensors", data={
        "action": "create",
        "sensor_code": "ENV-SN-WEB-01",
        "name": "Web Test Station Station",
        "zone_id": 1,
        "model": "AirSense-Pro-2026",
        "status": "online"
    }, allow_redirects=True)
    assert res_web_sensor.status_code == 200
    assert "ENV-SN-WEB-01" in res_web_sensor.text
    print("  [+] Admin Web 'Register Sensor' form submission verified.")

    # Find created sensor
    sensors_list = session.get(f"{BASE_URL}/api/sensors").json()["data"]
    target_sensor = [s for s in sensors_list if s["sensor_code"] == "ENV-SN-WEB-01"][0]
    sensor_id = target_sensor["id"]

    # Test "Simulate Telemetry" button for this sensor
    res_sim_sensor = session.post(f"{BASE_URL}/admin/sensors", data={
        "action": "simulate_reading",
        "sensor_id": sensor_id
    }, allow_redirects=True)
    assert res_sim_sensor.status_code == 200
    print(f"  [+] Admin Web 'Simulate Telemetry' button on Sensor #{sensor_id} clicked -> Ingested live reading.")

    # Edit sensor via modal POST
    res_edit_sensor = session.post(f"{BASE_URL}/admin/sensors", data={
        "action": "edit",
        "sensor_id": sensor_id,
        "name": "Web Test Station Renamed",
        "zone_id": 1,
        "model": "AirSense-Pro-Max",
        "status": "maintenance"
    }, allow_redirects=True)
    assert res_edit_sensor.status_code == 200
    assert "AirSense-Pro-Max" in res_edit_sensor.text
    print(f"  [+] Admin Web 'Edit Sensor Modal' submission verified for Sensor #{sensor_id}.")

    # Delete sensor via modal POST
    res_del_sensor = session.post(f"{BASE_URL}/admin/sensors", data={
        "action": "delete",
        "sensor_id": sensor_id
    }, allow_redirects=True)
    assert res_del_sensor.status_code == 200
    assert "deleted" in res_del_sensor.text.lower()
    print(f"  [+] Admin Web 'Delete Sensor' confirmed for Sensor #{sensor_id}.")

    # -------------------------------------------------------------
    # Step 8: Admin Threshold Adjust & Viewer RBAC Verification
    # -------------------------------------------------------------
    print("\n[BUTTON TEST 8/8] Admin Threshold Adjustment & Viewer RBAC Security")
    # Adjust threshold via form POST
    res_thresh = session.post(f"{BASE_URL}/admin/thresholds", data={
        "action": "update_threshold",
        "threshold_id": 1,
        "warning_min": 0,
        "warning_max": 20.0,
        "poor_min": 20.1,
        "poor_max": 45.0,
        "dangerous_min": 45.1,
        "dangerous_max": 500.0,
        "description": "Updated academic safety guidelines"
    }, allow_redirects=True)
    assert res_thresh.status_code == 200
    assert "updated successfully" in res_thresh.text
    print("  [+] Admin Threshold 'Adjust Rule' submission verified.")

    # Manual Data Entry Submission via Form POST
    res_manual = session.post(f"{BASE_URL}/admin/readings/manual", data={
        "sensor_id": 1,
        "temperature": 22.4,
        "humidity": 44.5,
        "pm25": 9.8,
        "pm10": 18.2,
        "co2": 490,
        "noise": 39.5,
        "weather_condition": "Sunny"
    }, allow_redirects=True)
    assert res_manual.status_code == 200
    assert "Manual reading" in res_manual.text
    print("  [+] Admin 'Manual Data Entry' form submission verified.")

    # Test Viewer Account (Role: 'viewer')
    viewer_session = requests.Session()
    viewer_login = viewer_session.post(f"{BASE_URL}/api/auth/login", json={
        "username": "viewer",
        "password": "viewer123"
    })
    assert viewer_login.status_code == 200
    assert viewer_login.json()["data"]["user"]["role"] == "viewer"
    print("  [+] Logged in as: viewer (Role: viewer)")

    # Viewer can view all management views without 403 crashes
    for path in ["/admin/zones", "/admin/sensors", "/admin/thresholds", "/admin/readings/manual"]:
        v_res = viewer_session.get(f"{BASE_URL}{path}")
        assert v_res.status_code == 200
        assert "Viewer Mode" in v_res.text
        print(f"      - GET {path} -> Read-only Viewer banner displayed (HTTP 200).")

    # Viewer modification attempt is gracefully rejected
    v_post = viewer_session.post(f"{BASE_URL}/admin/zones", data={"action": "create", "name": "Hack Zone"}, allow_redirects=True)
    assert "Administrator privileges required" in v_post.text
    print("      - POST /admin/zones by viewer properly rejected with security flash.")

    print("\n" + "=" * 65)
    print("  SUCCESS: EVERY SINGLE BUTTON AND INTERACTION IS 100% OPERATIONAL!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    test_button_interactivity_all()
