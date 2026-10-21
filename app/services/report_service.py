"""
Report generation and export service.
Generates comprehensive daily, weekly, and monthly reports with CSV export capabilities.
"""
import io
import csv
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from app.extensions import db
from app.models.campus_zone import CampusZone
from app.models.alert import Alert
from app.services.analytics import get_readings_dataframe, PARAMETERS_META
from app.utils.helpers import utc_now


def generate_period_report(
    period: str = "daily",
    zone_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate an environmental summary report for daily, weekly, or monthly intervals.
    """
    now = utc_now()
    if period == "daily":
        start_date = now - timedelta(days=1)
        period_title = "Past 24 Hours Summary"
    elif period == "weekly":
        start_date = now - timedelta(days=7)
        period_title = "Past 7 Days Weekly Report"
    elif period == "monthly":
        start_date = now - timedelta(days=30)
        period_title = "Past 30 Days Monthly Review"
    else:
        start_date = now - timedelta(days=1)
        period_title = "Daily Summary"

    df = get_readings_dataframe(zone_id=zone_id, start_date=start_date, end_date=now)

    if df.empty:
        return {
            "period": period,
            "title": period_title,
            "generated_at": now.isoformat(),
            "reading_count": 0,
            "zone_summaries": [],
            "parameter_summaries": {},
            "alert_count": 0
        }

    # Parameter summaries across entire campus or filtered zone
    param_summaries = {}
    for p in ["temperature", "humidity", "pm25", "pm10", "co2", "noise", "aqi"]:
        meta = PARAMETERS_META[p]
        series = df[p].dropna()
        if not series.empty:
            param_summaries[p] = {
                "label": meta["label"],
                "unit": meta["unit"],
                "mean": round(float(series.mean()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "std": round(float(series.std()), 2) if len(series) > 1 else 0.0
            }

    # Zone-by-zone summaries
    zone_summaries = []
    grouped = df.groupby(["zone_id", "zone_name"])
    for (zid, zname), group in grouped:
        zone_summaries.append({
            "zone_id": int(zid),
            "zone_name": str(zname),
            "reading_count": len(group),
            "avg_temperature": round(float(group["temperature"].mean()), 1),
            "avg_humidity": round(float(group["humidity"].mean()), 1),
            "avg_pm25": round(float(group["pm25"].mean()), 1),
            "avg_co2": round(float(group["co2"].mean()), 1),
            "avg_noise": round(float(group["noise"].mean()), 1),
            "avg_aqi": round(float(group["aqi"].mean()), 1)
        })

    # Alert count in this period
    alert_query = Alert.query.filter(Alert.created_at >= start_date)
    if zone_id:
        alert_query = alert_query.filter(Alert.zone_id == zone_id)
    alert_count = alert_query.count()

    return {
        "period": period,
        "title": period_title,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "generated_at": now.isoformat(),
        "reading_count": len(df),
        "zone_summaries": zone_summaries,
        "parameter_summaries": param_summaries,
        "alert_count": alert_count
    }


def export_readings_to_csv(
    zone_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> str:
    """
    Format filtered readings as a CSV string for browser download.
    """
    df = get_readings_dataframe(zone_id=zone_id, start_date=start_date, end_date=end_date)
    
    output = io.StringIO()
    if df.empty:
        writer = csv.writer(output)
        writer.writerow(["No data matches the selected filter parameters."])
        return output.getvalue()

    # Reorder and rename columns for clean external presentation
    export_cols = [
        "id", "timestamp", "zone_name", "sensor_code",
        "temperature", "humidity", "pm25", "pm10", "co2", "noise", "aqi", "weather_condition"
    ]
    available_cols = [c for c in export_cols if c in df.columns]
    export_df = df[available_cols].copy()
    export_df.columns = [
        "Reading_ID", "Timestamp_UTC", "Campus_Zone", "Sensor_Code",
        "Temperature_C", "Humidity_Pct", "PM2_5_ug_m3", "PM10_ug_m3",
        "CO2_ppm", "Noise_dB", "Air_Quality_Index", "Weather"
    ][:len(available_cols)]

    export_df.to_csv(output, index=False)
    return output.getvalue()
