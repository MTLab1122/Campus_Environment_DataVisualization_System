import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
driver = webdriver.Chrome(options=options)

try:
    print("Logging into admin...")
    driver.get("http://127.0.0.1:5000/login")
    time.sleep(1)
    driver.find_element(By.NAME, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("admin123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    
    print("Navigating to real manual entry page /admin/readings/manual...")
    driver.get("http://127.0.0.1:5000/admin/readings/manual")
    time.sleep(2)
    driver.save_screenshot("thesis_assets/screenshots/fig_09_manual_telemetry_entry.png")
    driver.save_screenshot("docs/screenshots/fig_09_manual_telemetry_entry.png")
    print("Successfully captured real manual entry page: /admin/readings/manual")
finally:
    driver.quit()
