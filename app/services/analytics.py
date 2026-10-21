"""
Environmental data analytics service utilizing Pandas and NumPy.
Performs statistical summaries, zone comparisons, temporal aggregations, and matrix computations.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sqlalchemy import func
from app.extensions import db
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.environmental_reading import EnvironmentalReading
from app.utils.aqi_calculator import get_aqi_details
from app.utils.helpers import utc_now


PARAMETERS_META = {
    "temperature": {"label": "Temperature", "unit": "°C", "color": "#F59E0B"},
    "humidity": {"label": "Relative Humidity", "unit": "%", "color": "#3B82F6"},
    "pm25": {"label": "PM2.5 Concentration", "unit": "µg/m³", "color": "#EF4444"},
    "pm10": {"label": "PM10 Concentration", "unit": "µg/m³", "color": "#8B5CF6"},
    "co2": {"label": "CO2 Concentration", "unit": "ppm", "color": "#10B981"},
    "noise": {"label": "Noise Level", "unit": "dB", "color": "#EC4899"},
    "aqi": {"label": "Air Quality Index (AQI)", "unit": "Index", "color": "#6366F1"}
}


def get_readings_dataframe(
    zone_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 10000
) -> pd.DataFrame:
    """
    Fetch filtered telemetry and return a structured Pandas DataFrame.
    """
    query = db.session.query(
        EnvironmentalReading.id,
        EnvironmentalReading.timestamp,
        EnvironmentalReading.zone_id,
        CampusZone.name.label("zone_name"),
        CampusZone.code.label("zone_code"),
        Sensor.sensor_code,
        EnvironmentalReading.temperature,
        EnvironmentalReading.humidity,
        EnvironmentalReading.pm25,
        EnvironmentalReading.pm10,
        EnvironmentalReading.co2,
        EnvironmentalReading.noise,
        EnvironmentalReading.aqi,
        EnvironmentalReading.weather_condition
    ).join(CampusZone, EnvironmentalReading.zone_id == CampusZone.id)\
     .join(Sensor, EnvironmentalReading.sensor_id == Sensor.id)

    if zone_id:
        query = query.filter(EnvironmentalReading.zone_id == zone_id)
    if start_date:
        query = query.filter(EnvironmentalReading.timestamp >= start_date)
    if end_date:
        query = query.filter(EnvironmentalReading.timestamp <= end_date)

    query = query.order_by(EnvironmentalReading.timestamp.asc()).limit(limit)

    rows = query.all()
    if not rows:
        return pd.DataFrame(columns=[
            "id", "timestamp", "zone_id", "zone_name", "zone_code", "sensor_code",
            "temperature", "humidity", "pm25", "pm10", "co2", "noise", "aqi", "weather_condition"
        ])

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def calculate_parameter_stats(series: pd.Series) -> Dict[str, float]:
    """Compute basic statistical aggregates for a numerical series."""
    if series.empty:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "std": 0.0, "median": 0.0}
    return {
        "mean": round(float(series.mean()), 2),
        "min": round(float(series.min()), 2),
        "max": round(float(series.max()), 2),
        "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
        "median": round(float(series.median()), 2)
    }


def get_latest_zone_readings() -> List[Dict[str, Any]]:
    """
    Retrieve the most recent environmental reading for each campus zone.
    """
    zones = CampusZone.query.all()
    results = []

    for zone in zones:
        latest = EnvironmentalReading.query.filter_by(zone_id=zone.id)\
            .order_by(EnvironmentalReading.timestamp.desc()).first()
        
        if latest:
            reading_dict = latest.to_dict(include_names=True)
            aqi_info = get_aqi_details(latest.aqi)
            reading_dict["aqi_category"] = aqi_info["category"]
            reading_dict["aqi_color"] = aqi_info["color"]
            reading_dict["aqi_badge"] = aqi_info["badge"]
            results.append(reading_dict)
        else:
            results.append({
                "zone_id": zone.id,
                "zone_name": zone.name,
                "zone_code": zone.code,
                "timestamp": None,
                "temperature": None,
                "humidity": None,
                "pm25": None,
                "pm10": None,
                "co2": None,
                "noise": None,
                "aqi": None,
                "aqi_category": "No Data",
                "aqi_color": "#9CA3AF",
                "weather_condition": "N/A"
            })
            
    return results


def get_dashboard_summary_metrics(zone_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Calculate headline metric cards: current reading, 24-hr mean, and trend vs prior 24 hours.
    """
    now = utc_now()
    last_24h = now - timedelta(hours=24)
    prev_24h = last_24h - timedelta(hours=24)

    # Current readings query
    base_q = EnvironmentalReading.query
    if zone_id:
        base_q = base_q.filter_by(zone_id=zone_id)
        
    latest = base_q.order_by(EnvironmentalReading.timestamp.desc()).first()

    # Recent 24 hours dataframe
    df_recent = get_readings_dataframe(zone_id=zone_id, start_date=last_24h, end_date=now)
    # Prior 24 hours dataframe (for trend computation)
    df_prior = get_readings_dataframe(zone_id=zone_id, start_date=prev_24h, end_date=last_24h)

    params = ["temperature", "humidity", "pm25", "pm10", "co2", "noise", "aqi"]
    metrics = {}

    for param in params:
        curr_val = getattr(latest, param) if latest else 0.0
        meta = PARAMETERS_META.get(param, {"label": param.title(), "unit": ""})
        
        recent_mean = float(df_recent[param].mean()) if not df_recent.empty else curr_val
        prior_mean = float(df_prior[param].mean()) if not df_prior.empty else recent_mean
        
        # Calculate percent change trend
        if prior_mean > 0:
            trend_pct = round(((recent_mean - prior_mean) / prior_mean) * 100.0, 1)
        else:
            trend_pct = 0.0

        metrics[param] = {
            "current": round(float(curr_val), 1) if curr_val is not None else 0.0,
            "mean_24h": round(recent_mean, 1),
            "trend_pct": trend_pct,
            "unit": meta["unit"],
            "label": meta["label"]
        }

    # Add AQI status category
    aqi_val = metrics["aqi"]["current"] if metrics["aqi"]["current"] else 0
    aqi_details = get_aqi_details(int(aqi_val))
    metrics["aqi_details"] = aqi_details
    metrics["latest_timestamp"] = latest.timestamp.isoformat() if latest else None
    metrics["health_score"] = calculate_campus_health_score(zone_id=zone_id)

    return metrics



def get_zone_comparison_data() -> pd.DataFrame:
    """
    Aggregate 7-day average metrics grouped by Campus Zone for bar charts.
    """
    seven_days_ago = utc_now() - timedelta(days=7)
    df = get_readings_dataframe(start_date=seven_days_ago)
    
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby(["zone_id", "zone_name"]).agg({
        "temperature": "mean",
        "humidity": "mean",
        "pm25": "mean",
        "pm10": "mean",
        "co2": "mean",
        "noise": "mean",
        "aqi": "mean"
    }).reset_index()

    for col in ["temperature", "humidity", "pm25", "pm10", "co2", "noise", "aqi"]:
        grouped[col] = grouped[col].round(2)

    return grouped


def get_heatmap_matrix(parameter: str = "pm25", days: int = 7) -> Dict[str, Any]:
    """
    Generate Zone x Hour-of-Day average matrix for heatmap visualization.
    """
    if parameter not in PARAMETERS_META:
        parameter = "pm25"

    start_date = utc_now() - timedelta(days=days)
    df = get_readings_dataframe(start_date=start_date)

    if df.empty:
        return {"zones": [], "hours": list(range(24)), "z": []}

    df["hour"] = df["timestamp"].dt.hour

    pivot = df.pivot_table(
        index="zone_name",
        columns="hour",
        values=parameter,
        aggfunc="mean"
    ).round(1)

    # Ensure all hours 0-23 are represented
    for h in range(24):
        if h not in pivot.columns:
            pivot[h] = np.nan
    pivot = pivot.reindex(columns=sorted(pivot.columns))

    return {
        "zones": pivot.index.tolist(),
        "hours": [f"{h:02d}:00" for h in pivot.columns],
        "z": pivot.fillna(0).values.tolist(),
        "parameter_label": PARAMETERS_META[parameter]["label"],
        "unit": PARAMETERS_META[parameter]["unit"]
    }


def calculate_campus_health_score(zone_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Compute comprehensive Campus Environmental Health Index (CEHI) on a 0-100 scale.
    Combines weighted sub-indices for AQI, CO2 ventilation, acoustic peace, and thermal comfort.
    """
    base_q = EnvironmentalReading.query
    if zone_id:
        base_q = base_q.filter_by(zone_id=zone_id)
        
    latest = base_q.order_by(EnvironmentalReading.timestamp.desc()).first()

    if not latest:
        return {
            "score": 85.0,
            "grade": "A",
            "grade_label": "Very Good",
            "color": "#10B981",
            "sub_indices": {
                "air_quality": 88.0,
                "ventilation": 85.0,
                "acoustics": 82.0,
                "thermal_comfort": 86.0
            },
            "advisory": "Telemetry initialized. Campus environmental conditions within recommended guidelines.",
            "zone_id": zone_id
        }

    aqi = latest.aqi or 50.0
    co2 = latest.co2 or 550.0
    noise = latest.noise or 50.0
    temp = latest.temperature or 22.0
    hum = latest.humidity or 50.0

    # 1. Air Quality Sub-score (0-100)
    aqi_sub = max(0.0, min(100.0, 100.0 - (aqi * 0.5)))

    # 2. IAQ Ventilation / CO2 Sub-score (0-100)
    if co2 <= 500:
        co2_sub = 100.0
    elif co2 <= 800:
        co2_sub = 100.0 - (co2 - 500.0) * (20.0 / 300.0)
    elif co2 <= 1200:
        co2_sub = 80.0 - (co2 - 800.0) * (30.0 / 400.0)
    elif co2 <= 2000:
        co2_sub = 50.0 - (co2 - 1200.0) * (35.0 / 800.0)
    else:
        co2_sub = max(0.0, 15.0 - (co2 - 2000.0) * 0.02)

    # 3. Acoustic Sub-score (0-100)
    if noise <= 45:
        noise_sub = 100.0
    elif noise <= 65:
        noise_sub = 100.0 - (noise - 45.0) * 2.0
    elif noise <= 85:
        noise_sub = 60.0 - (noise - 65.0) * 2.5
    else:
        noise_sub = max(0.0, 10.0 - (noise - 85.0))

    # 4. Thermal Comfort Sub-score (0-100)
    temp_penalty = abs(temp - 22.0) * 3.5
    hum_penalty = abs(hum - 50.0) * 0.9
    thermal_sub = max(0.0, min(100.0, 100.0 - temp_penalty - hum_penalty))

    # Composite Index (Weights: Air 35%, Ventilation 25%, Acoustics 20%, Thermal 20%)
    cehi = round(aqi_sub * 0.35 + co2_sub * 0.25 + noise_sub * 0.20 + thermal_sub * 0.20, 1)

    if cehi >= 90:
        grade = "A+"
        grade_label = "Optimal"
        color = "#10B981"
        advisory = "Outstanding campus conditions across all environmental indicators."
    elif cehi >= 80:
        grade = "A"
        grade_label = "Very Good"
        color = "#10B981"
        advisory = "High environmental quality with safe indoor and outdoor levels."
    elif cehi >= 70:
        grade = "B"
        grade_label = "Good"
        color = "#3B82F6"
        advisory = "Normal ambient levels; light ventilation recommended in dense halls."
    elif cehi >= 60:
        grade = "C"
        grade_label = "Moderate Warning"
        color = "#F59E0B"
        advisory = "Elevated particulate or acoustic levels; inspect HVAC and noise sources."
    elif cehi >= 50:
        grade = "D"
        grade_label = "Poor"
        color = "#F97316"
        advisory = "Substandard air quality or ventilation; indoor mitigation active."
    else:
        grade = "F"
        grade_label = "Critical Alert"
        color = "#EF4444"
        advisory = "Hazardous conditions detected; immediate facility response advised."

    return {
        "score": cehi,
        "grade": grade,
        "grade_label": grade_label,
        "color": color,
        "sub_indices": {
            "air_quality": round(aqi_sub, 1),
            "ventilation": round(co2_sub, 1),
            "acoustics": round(noise_sub, 1),
            "thermal_comfort": round(thermal_sub, 1)
        },
        "advisory": advisory,
        "zone_id": zone_id
    }


def get_zone_radar_matrix() -> Dict[str, Any]:
    """
    Generate normalized multi-dimensional performance scores across campus zones for radar charts.
    """
    categories = ["Air Cleanliness", "Acoustic Quietness", "IAQ Ventilation", "Thermal Comfort", "Particle Safety"]
    zones = CampusZone.query.order_by(CampusZone.name.asc()).all()
    zone_profiles = []

    for zone in zones:
        latest = EnvironmentalReading.query.filter_by(zone_id=zone.id)\
            .order_by(EnvironmentalReading.timestamp.desc()).first()

        if latest:
            air = round(max(0.0, min(100.0, 100.0 - (latest.aqi or 50) * 0.5)), 1)
            acoustics = round(max(0.0, min(100.0, 100.0 - max(0.0, (latest.noise or 50) - 30) * 1.6)), 1)
            ventilation = round(max(0.0, min(100.0, 100.0 - max(0.0, (latest.co2 or 600) - 400) * 0.06)), 1)
            thermal = round(max(0.0, min(100.0, 100.0 - abs((latest.temperature or 22) - 22) * 3.5 - abs((latest.humidity or 50) - 50) * 0.8)), 1)
            particle = round(max(0.0, min(100.0, 100.0 - (latest.pm25 or 20) * 1.5)), 1)
        else:
            air, acoustics, ventilation, thermal, particle = 85.0, 80.0, 85.0, 85.0, 85.0

        zone_profiles.append({
            "zone_id": zone.id,
            "zone_name": zone.name,
            "zone_code": zone.code,
            "values": [air, acoustics, ventilation, thermal, particle]
        })

    return {
        "categories": categories,
        "zones": zone_profiles
    }


def get_parameter_correlations() -> Dict[str, Any]:
    """
    Compute pairwise Pearson correlation coefficients between environmental parameters.
    """
    df = get_readings_dataframe(limit=5000)
    params = ["temperature", "humidity", "pm25", "pm10", "co2", "noise", "aqi"]
    
    if df.empty or len(df) < 5:
        matrix = {p1: {p2: 1.0 if p1 == p2 else 0.0 for p2 in params} for p1 in params}
        return {"parameters": params, "matrix": matrix}

    corr_df = df[params].corr().round(2).fillna(0.0)
    matrix = corr_df.to_dict()
    return {"parameters": params, "matrix": matrix}

