"""
AQI Calculation utility based on standard US EPA breakpoint formulas.
Supports PM2.5 and PM10 concentration-to-index conversions.
"""
from typing import Dict, Any, Tuple


# EPA Breakpoints for PM2.5 (µg/m³, 24-hr avg or instantaneous)
# Format: (C_low, C_high, I_low, I_high)
PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50),
    (12.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 500.4, 301, 500)
]

# EPA Breakpoints for PM10 (µg/m³)
PM10_BREAKPOINTS = [
    (0.0, 54.0, 0, 50),
    (55.0, 154.0, 51, 100),
    (155.0, 254.0, 101, 150),
    (255.0, 354.0, 151, 200),
    (355.0, 424.0, 201, 300),
    (425.0, 604.0, 301, 500)
]


def _calculate_individual_aqi(concentration: float, breakpoints: list) -> int:
    """Calculate sub-index AQI for a single pollutant using linear interpolation."""
    c = max(0.0, concentration)
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= c <= c_high:
            # Linear interpolation formula: I = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low
            aqi = ((i_high - i_low) / (c_high - c_low)) * (c - c_low) + i_low
            return int(round(aqi))
    
    # Beyond highest breakpoint
    if c > breakpoints[-1][1]:
        return 500
    return 0


def calculate_aqi(pm25: float, pm10: float) -> int:
    """
    Compute comprehensive AQI from PM2.5 and PM10.
    According to standard guidelines, composite AQI is the maximum of the sub-indices.
    """
    aqi_pm25 = _calculate_individual_aqi(pm25, PM25_BREAKPOINTS)
    aqi_pm10 = _calculate_individual_aqi(pm10, PM10_BREAKPOINTS)
    return max(aqi_pm25, aqi_pm10)


def get_aqi_details(aqi_value: int) -> Dict[str, Any]:
    """
    Return status descriptor, color code, and advisory based on AQI value.
    """
    val = max(0, int(aqi_value))
    if val <= 50:
        return {
            "category": "Good",
            "color": "#10B981",       # Emerald Green
            "badge": "success",
            "level": 1,
            "advisory": "Air quality is satisfactory and poses little or no risk."
        }
    elif val <= 100:
        return {
            "category": "Moderate",
            "color": "#F59E0B",       # Amber
            "badge": "warning",
            "level": 2,
            "advisory": "Air quality is acceptable; sensitive individuals should consider limiting prolonged outdoor exertion."
        }
    elif val <= 150:
        return {
            "category": "Unhealthy for Sensitive Groups",
            "color": "#F97316",       # Orange
            "badge": "warning",
            "level": 3,
            "advisory": "Members of sensitive groups may experience health effects."
        }
    elif val <= 200:
        return {
            "category": "Poor",
            "color": "#EF4444",       # Red
            "badge": "danger",
            "level": 4,
            "advisory": "Everyone may begin to experience health effects; sensitive groups may experience more serious effects."
        }
    elif val <= 300:
        return {
            "category": "Very Poor",
            "color": "#8B5CF6",       # Purple
            "badge": "danger",
            "level": 5,
            "advisory": "Health alert: risk of health effects increased for everyone."
        }
    else:
        return {
            "category": "Dangerous",
            "color": "#7F1D1D",       # Maroon
            "badge": "danger",
            "level": 6,
            "advisory": "Health warnings of emergency conditions. Entire population is more likely to be affected."
        }
