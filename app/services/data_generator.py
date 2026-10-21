"""
Realistic mock IoT sensor data generation engine.
Simulates environmental dynamics, diurnal cycles, human activities, and traffic patterns.
"""
import math
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app.extensions import db
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.environmental_reading import EnvironmentalReading
from app.utils.aqi_calculator import calculate_aqi
from app.utils.helpers import utc_now
from app.services.alert_service import evaluate_reading_alerts


# Zone-specific environmental behavior profiles
ZONE_PROFILES = {
    "ZONE_LIB": {
        "base_temp": 22.0, "temp_variance": 1.2,
        "base_humidity": 48.0, "humidity_variance": 4.0,
        "base_pm25": 10.0, "pm25_variance": 4.0,
        "base_pm10": 18.0, "pm10_variance": 6.0,
        "base_co2": 520.0, "co2_variance": 120.0,
        "base_noise": 36.0, "noise_variance": 5.0,
        "is_indoor": True,
        "peak_hours": [14, 15, 16, 17]  # Afternoon study crowds increase CO2
    },
    "ZONE_CLASS": {
        "base_temp": 23.0, "temp_variance": 2.0,
        "base_humidity": 52.0, "humidity_variance": 6.0,
        "base_pm25": 16.0, "pm25_variance": 7.0,
        "base_pm10": 28.0, "pm10_variance": 10.0,
        "base_co2": 680.0, "co2_variance": 380.0,
        "base_noise": 52.0, "noise_variance": 16.0,
        "is_indoor": True,
        "peak_hours": [9, 10, 11, 14, 15]  # Lecture periods
    },
    "ZONE_CAFE": {
        "base_temp": 25.5, "temp_variance": 3.0,
        "base_humidity": 62.0, "humidity_variance": 10.0,
        "base_pm25": 28.0, "pm25_variance": 15.0,
        "base_pm10": 45.0, "pm10_variance": 20.0,
        "base_co2": 750.0, "co2_variance": 350.0,
        "base_noise": 66.0, "noise_variance": 14.0,
        "is_indoor": True,
        "peak_hours": [12, 13, 18, 19]  # Lunch & dinner service
    },
    "ZONE_PLAY": {
        "base_temp": 24.0, "temp_variance": 5.5,
        "base_humidity": 55.0, "humidity_variance": 14.0,
        "base_pm25": 22.0, "pm25_variance": 10.0,
        "base_pm10": 55.0, "pm10_variance": 26.0,
        "base_co2": 420.0, "co2_variance": 40.0,
        "base_noise": 56.0, "noise_variance": 18.0,
        "is_indoor": False,
        "peak_hours": [16, 17, 18]  # Sports & recreation
    },
    "ZONE_PARK": {
        "base_temp": 25.0, "temp_variance": 5.0,
        "base_humidity": 50.0, "humidity_variance": 12.0,
        "base_pm25": 38.0, "pm25_variance": 22.0,
        "base_pm10": 68.0, "pm10_variance": 35.0,
        "base_co2": 580.0, "co2_variance": 160.0,
        "base_noise": 60.0, "noise_variance": 12.0,
        "is_indoor": False,
        "peak_hours": [8, 9, 17, 18]  # Vehicle arrivals/departures
    },
    "ZONE_GATE": {
        "base_temp": 24.5, "temp_variance": 4.5,
        "base_humidity": 52.0, "humidity_variance": 10.0,
        "base_pm25": 32.0, "pm25_variance": 18.0,
        "base_pm10": 58.0, "pm10_variance": 28.0,
        "base_co2": 510.0, "co2_variance": 100.0,
        "base_noise": 64.0, "noise_variance": 10.0,
        "is_indoor": False,
        "peak_hours": [8, 9, 12, 17, 18]  # Main transit gate
    },
    "ZONE_LAB": {
        "base_temp": 21.5, "temp_variance": 1.0,
        "base_humidity": 45.0, "humidity_variance": 3.0,
        "base_pm25": 12.0, "pm25_variance": 6.0,
        "base_pm10": 20.0, "pm10_variance": 8.0,
        "base_co2": 550.0, "co2_variance": 180.0,
        "base_noise": 42.0, "noise_variance": 8.0,
        "is_indoor": True,
        "peak_hours": [10, 11, 14, 15]  # Lab sessions
    },
    "ZONE_HOSTEL": {
        "base_temp": 23.5, "temp_variance": 2.5,
        "base_humidity": 54.0, "humidity_variance": 8.0,
        "base_pm25": 18.0, "pm25_variance": 8.0,
        "base_pm10": 30.0, "pm10_variance": 12.0,
        "base_co2": 620.0, "co2_variance": 320.0,
        "base_noise": 48.0, "noise_variance": 16.0,
        "is_indoor": True,
        "peak_hours": [20, 21, 22, 23]  # Evening residence
    }
}

WEATHER_CONDITIONS = ["Sunny", "Partly Cloudy", "Clear", "Overcast", "Light Breeze", "Humid"]


def simulate_reading_values(zone_code: str, timestamp: datetime) -> Dict[str, Any]:
    """
    Calculate realistic environmental parameters for a given zone and timestamp,
    incorporating diurnal temperature equations and occupancy cycles.
    """
    profile = ZONE_PROFILES.get(zone_code, ZONE_PROFILES["ZONE_LIB"])
    hour = timestamp.hour + (timestamp.minute / 60.0)

    # Solar Diurnal Sine Curve: Min around 5 AM, Max around 3 PM (15:00)
    # sin((h - 9) * 2pi / 24) is -1 at 3 AM/9-6, +1 at 3 PM
    solar_factor = math.sin((hour - 9.0) * (2.0 * math.pi / 24.0))

    if profile["is_indoor"]:
        # Indoor HVAC dampens temperature fluctuations
        temp_delta = solar_factor * 1.5 + random.uniform(-0.4, 0.4)
        humidity_delta = -solar_factor * 2.0 + random.uniform(-1.5, 1.5)
    else:
        # Outdoor ambient shifts significantly with sunlight
        temp_delta = solar_factor * 5.0 + random.uniform(-1.0, 1.0)
        humidity_delta = -solar_factor * 12.0 + random.uniform(-3.0, 3.0)

    # Activity boost during peak zone hours
    is_peak = int(timestamp.hour) in profile["peak_hours"]
    peak_factor = random.uniform(1.3, 1.8) if is_peak else 1.0

    # Temperature calculation
    temperature = profile["base_temp"] + temp_delta + (1.2 if is_peak and profile["is_indoor"] else 0.0)
    temperature = max(12.0, min(42.0, temperature))

    # Humidity calculation (inversely correlated with temperature)
    humidity = profile["base_humidity"] + humidity_delta + (5.0 if zone_code == "ZONE_CAFE" and is_peak else 0.0)
    humidity = max(18.0, min(95.0, humidity))

    # CO2 calculation (human exhalation increases with occupancy)
    co2_occupancy = profile["co2_variance"] * (1.6 if is_peak else 0.3) * random.uniform(0.7, 1.3)
    co2 = profile["base_co2"] + co2_occupancy
    # Occasional poorly ventilated classroom/cafeteria spike
    if is_peak and random.random() < 0.08:
        co2 += random.uniform(300.0, 600.0)
    co2 = max(380.0, min(2800.0, co2))

    # Noise calculation
    noise_boost = (profile["noise_variance"] * 1.2) if is_peak else (-profile["noise_variance"] * 0.4)
    # Late night quiet factor
    if 0 <= timestamp.hour <= 5:
        noise_boost -= 8.0
    noise = profile["base_noise"] + noise_boost + random.uniform(-3.0, 4.0)
    noise = max(28.0, min(96.0, noise))

    # PM2.5 and PM10 calculation
    pm_traffic = (profile["pm25_variance"] * 1.4) if (is_peak and not profile["is_indoor"]) else (random.uniform(-2.0, 4.0))
    # Occasional dust or rush hour spike
    if zone_code in ["ZONE_PARK", "ZONE_GATE"] and is_peak and random.random() < 0.12:
        pm_traffic += random.uniform(15.0, 30.0)
    
    pm25 = max(4.0, profile["base_pm25"] + pm_traffic + random.uniform(-2.0, 4.0))
    pm10 = max(pm25 + 5.0, profile["base_pm10"] + (pm_traffic * 1.7) + random.uniform(-4.0, 8.0))

    # Calculate AQI from PM2.5 and PM10
    aqi = calculate_aqi(pm25, pm10)

    # Weather condition
    if hour > 19 or hour < 6:
        weather = "Clear Night"
    elif temperature > 28.0:
        weather = "Sunny"
    elif humidity > 75.0:
        weather = "Overcast"
    else:
        weather = random.choice(WEATHER_CONDITIONS)

    return {
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "pm25": round(pm25, 2),
        "pm10": round(pm10, 2),
        "co2": round(co2, 2),
        "noise": round(noise, 2),
        "aqi": aqi,
        "weather_condition": weather
    }


def generate_single_reading(
    sensor_id: Optional[int] = None,
    zone_id: Optional[int] = None,
    timestamp: Optional[datetime] = None,
    save: bool = True
) -> Optional[EnvironmentalReading]:
    """Generate a single reading for a specified sensor or zone and optionally commit to database."""
    sensor = None
    if sensor_id is not None:
        sensor = db.session.get(Sensor, sensor_id)
    elif zone_id is not None:
        sensor = Sensor.query.filter_by(zone_id=zone_id).first()
    else:
        sensor = Sensor.query.first()

    if not sensor:
        return None


    if timestamp is None:
        timestamp = utc_now()

    zone = sensor.zone
    zone_code = zone.code if zone else "ZONE_LIB"
    telemetry = simulate_reading_values(zone_code, timestamp)

    reading = EnvironmentalReading(
        sensor_id=sensor.id,
        zone_id=sensor.zone_id,
        timestamp=timestamp,
        temperature=telemetry["temperature"],
        humidity=telemetry["humidity"],
        pm25=telemetry["pm25"],
        pm10=telemetry["pm10"],
        co2=telemetry["co2"],
        noise=telemetry["noise"],
        aqi=telemetry["aqi"],
        weather_condition=telemetry["weather_condition"]
    )

    if save:
        db.session.add(reading)
        sensor.last_seen = timestamp
        sensor.status = "online"
        db.session.commit()
        # Evaluate alert thresholds
        evaluate_reading_alerts(reading)

    return reading


def seed_historical_telemetry(days: int = 7, interval_hours: int = 1) -> int:
    """
    Generate comprehensive historical readings for all active sensors across past N days.
    Guarantees realistic temporal trends and alert generation for visualization.
    """
    sensors = Sensor.query.all()
    if not sensors:
        return 0

    end_time = utc_now()
    start_time = end_time - timedelta(days=days)
    
    total_generated = 0
    readings_batch = []
    current_time = start_time

    # Generate timestamp steps
    timestamps = []
    while current_time <= end_time:
        timestamps.append(current_time)
        current_time += timedelta(hours=interval_hours)

    print(f"Generating realistic telemetry across {len(sensors)} sensors for {len(timestamps)} time points...")

    for ts in timestamps:
        for sensor in sensors:
            zone_code = sensor.zone.code if sensor.zone else "ZONE_LIB"
            telemetry = simulate_reading_values(zone_code, ts)
            
            reading = EnvironmentalReading(
                sensor_id=sensor.id,
                zone_id=sensor.zone_id,
                timestamp=ts,
                temperature=telemetry["temperature"],
                humidity=telemetry["humidity"],
                pm25=telemetry["pm25"],
                pm10=telemetry["pm10"],
                co2=telemetry["co2"],
                noise=telemetry["noise"],
                aqi=telemetry["aqi"],
                weather_condition=telemetry["weather_condition"]
            )
            readings_batch.append(reading)
            total_generated += 1

            # Commit in batches of 500 for optimal performance
            if len(readings_batch) >= 500:
                db.session.bulk_save_objects(readings_batch)
                db.session.commit()
                readings_batch = []

    if readings_batch:
        db.session.bulk_save_objects(readings_batch)
        db.session.commit()

    # Now evaluate alerts on the generated dataset
    print("Evaluating historical telemetry for alert generation...")
    # Sample recent readings and check for threshold breaches
    sample_readings = EnvironmentalReading.query.order_by(EnvironmentalReading.id.desc()).limit(200).all()
    for r in sample_readings:
        evaluate_reading_alerts(r)

    print(f"Successfully generated {total_generated} environmental readings.")
    return total_generated
