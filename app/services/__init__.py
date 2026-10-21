"""
Services package initialization.
Exports core analytics, alerts, simulation, and report routines.
"""
from app.services.alert_service import (
    evaluate_reading_alerts,
    resolve_alert,
    get_active_alerts,
    get_alert_statistics,
    seed_default_thresholds
)
from app.services.data_generator import (
    simulate_reading_values,
    generate_single_reading,
    seed_historical_telemetry
)
from app.services.analytics import (
    get_readings_dataframe,
    get_latest_zone_readings,
    get_dashboard_summary_metrics,
    get_zone_comparison_data,
    get_heatmap_matrix,
    PARAMETERS_META
)
from app.services.report_service import (
    generate_period_report,
    export_readings_to_csv
)

__all__ = [
    "evaluate_reading_alerts",
    "resolve_alert",
    "get_active_alerts",
    "get_alert_statistics",
    "seed_default_thresholds",
    "simulate_reading_values",
    "generate_single_reading",
    "seed_historical_telemetry",
    "get_readings_dataframe",
    "get_latest_zone_readings",
    "get_dashboard_summary_metrics",
    "get_zone_comparison_data",
    "get_heatmap_matrix",
    "PARAMETERS_META",
    "generate_period_report",
    "export_readings_to_csv"
]
