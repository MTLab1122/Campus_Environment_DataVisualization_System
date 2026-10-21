"""
Automated genuine screenshot capture script using Selenium and Chrome headless.
Captures actual running pages from http://127.0.0.1:5000/ and saves them to thesis_assets/screenshots/
"""
import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCREENSHOTS_DIR = Path("thesis_assets/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    return driver

def capture_all():
    driver = setup_driver()
    base_url = "http://127.0.0.1:5000"
    print(f"Browser initialized. Targeting: {base_url}")

    try:
        # 1. Capture Login Page
        print("Capturing 1: Login Page...")
        driver.get(f"{base_url}/login")
        time.sleep(2)
        driver.save_screenshot(str(SCREENSHOTS_DIR / "fig_05_auth_login.png"))
        print("  -> Saved fig_05_auth_login.png")

        # 2. Perform Login as Admin
        print("Logging in as admin...")
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("admin")
        password_input.send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        print("  -> Logged in successfully.")

        # 3. Capture Dashboard (Main Overview & Visual Analytics)
        print("Capturing Dashboard Overview...")
        driver.get(f"{base_url}/dashboard/")
        # Wait for Plotly dash graphs to load
        time.sleep(6)
        
        # Save Full Dashboard Overview
        driver.set_window_size(1920, 1200)
        time.sleep(1)
        driver.save_screenshot(str(SCREENSHOTS_DIR / "fig_01_dashboard_overview.png"))
        print("  -> Saved fig_01_dashboard_overview.png")

        # Scroll to Trend Curves & Gauges
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(1)
        driver.save_screenshot(str(SCREENSHOTS_DIR / "fig_02_trend_analysis.png"))
        print("  -> Saved fig_02_trend_analysis.png")

        # Scroll to Spatial Comparison & Radar Chart
        driver.execute_script("window.scrollTo(0, 1050);")
        time.sleep(1)
        driver.save_screenshot(str(SCREENSHOTS_DIR / "fig_03_spatial_radar_comparison.png"))
        print("  -> Saved fig_03_spatial_radar_comparison.png")

        # Scroll to Diurnal Heatmap & Diagnostics
        driver.execute_script("window.scrollTo(0, 1600);")
        time.sleep(1)
        driver.save_screenshot(str(SCREENSHOTS_DIR / "fig_04_diurnal_heatmap.png"))
        print("  -> Saved fig_04_diurnal_heatmap.png")

        # 4. Capture Admin Zones Console
        print("Capturing 6: Admin Zones...")
        driver.get(f"{base_url}/admin/zones")
        time.sleep(2)
        driver.save_screenshot(str(SCREENSHOTS_DIR / "fig_06_zone_management.png"))
        print("  -> Saved fig_06_zone_management.png")

        # 5. Capture Admin Sensors Console
        print("Capturing 7: Admin Sensors...")
        driver.get(f"{base_url}/admin/sensors")
        time.sleep(2)
        driver.save_screenshot(str(SCREENSHOTS_DIR / "fig_07_sensor_fleet.png"))
        print("  -> Saved fig_07_sensor_fleet.png")

        # 6. Capture Alert Thresholds Console
        print("Capturing 8: Alert Thresholds...")
        driver.get(f"{base_url}/admin/thresholds")
        time.sleep(2)
        driver.save_screenshot(str(SCREENSHOTS_DIR / "fig_08_alert_thresholds.png"))
        print("  -> Saved fig_08_alert_thresholds.png")

        # 7. Capture Manual Telemetry Entry Form
        print("Capturing 9: Manual Telemetry Entry...")
        driver.get(f"{base_url}/manual-entry")
        time.sleep(2)
        driver.save_screenshot(str(SCREENSHOTS_DIR / "fig_09_manual_telemetry_entry.png"))
        print("  -> Saved fig_09_manual_telemetry_entry.png")

        # 8. Capture API Docs Portal
        print("Capturing 10: API Documentation Portal...")
        driver.get(f"{base_url}/api/docs")
        time.sleep(2)
        driver.save_screenshot(str(SCREENSHOTS_DIR / "fig_10_api_docs_portal.png"))
        print("  -> Saved fig_10_api_docs_portal.png")

        print("\nAll genuine screenshots captured successfully!")

    finally:
        driver.quit()
        print("Browser driver cleanly terminated.")

if __name__ == "__main__":
    capture_all()
