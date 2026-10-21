"""
Plotly Dash callback registration.
Handles multi-dimensional filtering, dynamic graph generation, CSV export,
quick parameter switching, live data simulation, and instant alert resolution.
"""
from datetime import datetime, timedelta
from typing import Optional
from dash import Input, Output, State, ALL, ctx, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from app.extensions import db
from app.models.campus_zone import CampusZone
from app.models.sensor import Sensor
from app.models.environmental_reading import EnvironmentalReading
from app.models.alert import Alert
from app.services.analytics import (
    get_readings_dataframe,
    get_dashboard_summary_metrics,
    get_latest_zone_readings,
    get_heatmap_matrix,
    get_zone_radar_matrix,
    PARAMETERS_META
)
from app.services.alert_service import get_active_alerts, resolve_alert, resolve_all_alerts
from app.services.data_generator import generate_single_reading
from app.services.report_service import generate_period_report
from app.dashboard.components.metric_cards import create_metric_cards_row
from app.dashboard.components.alerts_table import create_alerts_panel
from app.utils.helpers import utc_now
from app.dashboard.components.charts import (
    create_trend_line_chart,
    create_zone_comparison_bar,
    create_gauge_chart,
    create_distribution_box_plot,
    create_heatmap_chart,
    create_zone_radar_chart
)
from app.dashboard.components.reports_view import create_reports_card



def register_callbacks(dash_app):
    """Register all interactive callbacks on the Dash application instance."""

    # 1. Time Slider Label Update Callback
    @dash_app.callback(
        Output("time-slider-output", "children"),
        Input("filter-time-range", "value")
    )
    def update_time_label(hours):
        if not hours or len(hours) != 2:
            return "00:00 to 23:00 UTC (Full Day)"
        if hours[0] == 0 and hours[1] == 23:
            return "00:00 to 23:00 UTC (Full Day)"
        return f"{hours[0]:02d}:00 - {hours[1]:02d}:00 UTC Window"

    # 2. Reset Filters Callback: Zone
    @dash_app.callback(
        Output("filter-zone", "value"),
        [
            Input("btn-reset-filters", "n_clicks"),
            Input({"type": "btn-quick-zone", "index": ALL}, "n_clicks")
        ],
        State("filter-zone", "value"),
        prevent_initial_call=True
    )
    def change_zone_filter(reset_clicks, quick_zone_clicks, current_val):
        trig = ctx.triggered_id
        if trig == "btn-reset-filters":
            return "ALL"
        if isinstance(trig, dict) and trig.get("type") == "btn-quick-zone":
            return trig.get("index")
        return current_val

    # 3. Reset & Quick Parameter Selection: Parameter
    @dash_app.callback(
        Output("filter-parameter", "value"),
        [
            Input("btn-reset-filters", "n_clicks"),
            Input("pill-param-pm25", "n_clicks"),
            Input("pill-param-pm10", "n_clicks"),
            Input("pill-param-co2", "n_clicks"),
            Input("pill-param-noise", "n_clicks"),
            Input("pill-param-temperature", "n_clicks"),
            Input("pill-param-humidity", "n_clicks"),
            Input("pill-param-aqi", "n_clicks"),
        ],
        State("filter-parameter", "value"),
        prevent_initial_call=True
    )
    def change_parameter_filter(n_reset, n_pm25, n_pm10, n_co2, n_noise, n_temp, n_hum, n_aqi, current_val):
        trig = ctx.triggered_id
        mapping = {
            "btn-reset-filters": "pm25",
            "pill-param-pm25": "pm25",
            "pill-param-pm10": "pm10",
            "pill-param-co2": "co2",
            "pill-param-noise": "noise",
            "pill-param-temperature": "temperature",
            "pill-param-humidity": "humidity",
            "pill-param-aqi": "aqi"
        }
        return mapping.get(trig, current_val)

    # 4. Reset Filters Callback: Date & Time range
    @dash_app.callback(
        [
            Output("filter-date-range", "start_date"),
            Output("filter-date-range", "end_date"),
            Output("filter-time-range", "value")
        ],
        Input("btn-reset-filters", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_date_and_time(n_clicks):
        now = utc_now()
        start = (now - timedelta(days=7)).date()
        return start, now.date(), [0, 23]

    # 5. Live Telemetry Simulation Callback
    @dash_app.callback(
        Output("store-simulated-reading-trigger", "data"),
        Input("btn-simulate-reading", "n_clicks"),
        [
            State("store-simulated-reading-trigger", "data"),
            State("filter-zone", "value")
        ],
        prevent_initial_call=True
    )
    def trigger_simulated_ingestion(n_clicks, current_trigger, zone_val):
        if not n_clicks:
            return current_trigger

        zone_id = None if zone_val == "ALL" else int(zone_val)
        sensor = None
        if zone_id:
            sensor = Sensor.query.filter_by(zone_id=zone_id, status="online").first()
            if not sensor:
                sensor = Sensor.query.filter_by(zone_id=zone_id).first()

        if not sensor:
            sensor = Sensor.query.filter_by(status="online").first() or Sensor.query.first()

        if sensor:
            generate_single_reading(sensor_id=sensor.id, save=True)

        return (current_trigger or 0) + 1

    # 6. Alert Resolution Callback (Single or Resolve All)
    @dash_app.callback(
        Output("store-alert-resolved-trigger", "data"),
        [
            Input({"type": "btn-resolve-alert", "index": ALL}, "n_clicks"),
            Input("btn-resolve-all-alerts", "n_clicks")
        ],
        [
            State("store-alert-resolved-trigger", "data"),
            State("filter-zone", "value")
        ],
        prevent_initial_call=True
    )
    def handle_alert_resolution(n_clicks_list, resolve_all_clicks, current_trigger, zone_val):
        if not ctx.triggered:
            return current_trigger

        trig = ctx.triggered_id
        if trig == "btn-resolve-all-alerts":
            zone_id = None if zone_val == "ALL" else int(zone_val)
            resolve_all_alerts(zone_id=zone_id)
            return (current_trigger or 0) + 1

        if isinstance(trig, dict) and trig.get("type") == "btn-resolve-alert":
            alert_id = trig.get("index")
            if alert_id:
                resolve_alert(alert_id)
                return (current_trigger or 0) + 1

        return current_trigger

    # 7. Primary Dashboard Master Callback
    @dash_app.callback(
        [
            Output("container-metric-cards", "children"),
            Output("container-alerts-panel", "children"),
            Output("chart-trend-line", "figure"),
            Output("chart-gauge", "figure"),
            Output("chart-zone-bar", "figure"),
            Output("chart-distribution-box", "figure"),
            Output("chart-diurnal-heatmap", "figure"),
            Output("table-filtered-readings", "data"),
            Output("label-table-count", "children"),
            Output("label-last-refreshed", "children"),
            Output("container-zone-quick-list", "children")
        ],
        [
            Input("filter-zone", "value"),
            Input("filter-parameter", "value"),
            Input("filter-date-range", "start_date"),
            Input("filter-date-range", "end_date"),
            Input("filter-time-range", "value"),
            Input("btn-refresh-data", "n_clicks"),
            Input("interval-auto-refresh", "n_intervals"),
            Input("store-alert-resolved-trigger", "data"),
            Input("store-simulated-reading-trigger", "data")
        ]
    )
    def update_dashboard(zone_val, param_val, start_date_str, end_date_str, time_range, n_clicks, n_intervals, alert_trig, sim_trig):
        # Resolve zone filter
        zone_id = None if zone_val == "ALL" else int(zone_val)
        param = param_val or "pm25"
        meta = PARAMETERS_META.get(param, {"label": param.title(), "unit": "", "color": "#3B82F6"})

        # Parse date range boundaries
        start_dt = None
        end_dt = None
        if start_date_str:
            start_dt = datetime.strptime(start_date_str[:10], "%Y-%m-%d")
        if end_date_str:
            end_dt = datetime.strptime(end_date_str[:10], "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        # 1. Fetch filtered telemetry dataframe
        df = get_readings_dataframe(zone_id=zone_id, start_date=start_dt, end_date=end_dt, limit=5000)

        # Apply time-of-day slider filtering if specified
        if not df.empty and time_range and len(time_range) == 2:
            min_h, max_h = time_range
            df = df[(df["timestamp"].dt.hour >= min_h) & (df["timestamp"].dt.hour <= max_h)]

        # 2. Metric Cards Row
        metrics = get_dashboard_summary_metrics(zone_id=zone_id)
        metric_cards_row = create_metric_cards_row(metrics)

        # 3. Active Alerts Panel
        active_alerts = get_active_alerts(zone_id=zone_id, limit=20)
        alerts_panel = create_alerts_panel(active_alerts)

        # 4. Charts Generation
        fig_line = create_trend_line_chart(df, parameter=param, parameter_meta=meta)
        
        current_param_val = metrics.get(param, {}).get("current", 0.0)
        fig_gauge = create_gauge_chart(current_param_val, parameter=param, parameter_meta=meta)

        # For comparison bar and box plot
        if zone_id is not None:
            comparison_df = df
        else:
            comparison_df = df if not df.empty else get_readings_dataframe(start_date=start_dt, end_date=end_dt, limit=2000)

        fig_bar = create_zone_comparison_bar(comparison_df, parameter=param, parameter_meta=meta)
        fig_box = create_distribution_box_plot(comparison_df, parameter=param, parameter_meta=meta)

        # Diurnal Heatmap matrix
        heatmap_matrix = get_heatmap_matrix(parameter=param, days=7)
        fig_heatmap = create_heatmap_chart(heatmap_matrix)

        # 5. Data Table Rows
        if not df.empty:
            table_records = df.tail(100).sort_values("timestamp", ascending=False).to_dict("records")
            for r in table_records:
                if isinstance(r.get("timestamp"), pd.Timestamp):
                    r["timestamp_str"] = r["timestamp"].strftime("%Y-%m-%d %H:%M")
                else:
                    r["timestamp_str"] = str(r.get("timestamp", ""))
            total_count_label = f"Displaying {len(table_records)} of {len(df):,} matching readings"
        else:
            table_records = []
            total_count_label = "0 matching records found"

        # 6. Quick Zone Status List (Clickable!)
        latest_readings = get_latest_zone_readings()
        quick_list_items = []
        for l in latest_readings:
            zid = l.get("zone_id")
            zname = l.get("zone_name")
            bg_badge = "success" if l.get("aqi_category") == "Good" else ("warning" if l.get("aqi_category") == "Moderate" else "danger")
            quick_list_items.append(
                html.Div(
                    [
                        dbc.Button(
                            [html.I(className="bi bi-geo-alt-fill me-1 text-primary small"), zname],
                            id={"type": "btn-quick-zone", "index": zid},
                            color="link",
                            size="sm",
                            className="p-0 text-start text-dark fw-bold text-decoration-none small"
                        ),
                        html.Span(
                            f"AQI {l.get('aqi', 'N/A')} ({l.get('aqi_category', 'N/A')})",
                            className=f"badge bg-{bg_badge}-subtle text-{bg_badge} border border-{bg_badge}-subtle small"
                        )
                    ],
                    className="d-flex justify-content-between align-items-center py-2 border-bottom border-light"
                )
            )
        quick_list_container = html.Div(
            [
                html.Div(
                    [
                        html.H6("Campus Zones Status", className="small fw-bold text-uppercase text-muted mb-0"),
                        html.Small("Click zone to filter", className="text-muted fst-italic", style={"fontSize": "11px"})
                    ],
                    className="d-flex justify-content-between align-items-center mb-2"
                ),
                html.Div(quick_list_items)
            ]
        )

        refreshed_label = f"Refreshed: {utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')}"

        return (
            metric_cards_row,
            alerts_panel,
            fig_line,
            fig_gauge,
            fig_bar,
            fig_box,
            fig_heatmap,
            table_records,
            total_count_label,
            refreshed_label,
            quick_list_container
        )

    # 8. Report Period Selection Callback
    @dash_app.callback(
        Output("store-report-period", "data"),
        [
            Input("btn-report-daily", "n_clicks"),
            Input("btn-report-weekly", "n_clicks"),
            Input("btn-report-monthly", "n_clicks")
        ],
        prevent_initial_call=True
    )
    def toggle_report_period(n_daily, n_weekly, n_monthly):
        button_id = ctx.triggered_id
        if button_id == "btn-report-daily":
            return "daily"
        elif button_id == "btn-report-weekly":
            return "weekly"
        elif button_id == "btn-report-monthly":
            return "monthly"
        return "daily"

    # 9. Report Card Container Update Callback
    @dash_app.callback(
        Output("container-reports-card", "children"),
        [
            Input("store-report-period", "data"),
            Input("filter-zone", "value"),
            Input("btn-refresh-data", "n_clicks"),
            Input("store-simulated-reading-trigger", "data")
        ]
    )
    def update_report_card(period, zone_val, n_clicks, sim_trig):
        zone_id = None if zone_val == "ALL" else int(zone_val)
        report_data = generate_period_report(period=period or "daily", zone_id=zone_id)
        return create_reports_card(report_data)

    # 10. CSV Export Download Callback: Telemetry Records
    @dash_app.callback(
        Output("download-dataframe-csv", "data"),
        Input("btn-export-csv", "n_clicks"),
        [
            State("filter-zone", "value"),
            State("filter-date-range", "start_date"),
            State("filter-date-range", "end_date")
        ],
        prevent_initial_call=True
    )
    def export_csv_data(n_clicks, zone_val, start_date_str, end_date_str):
        if not n_clicks:
            return None

        zone_id = None if zone_val == "ALL" else int(zone_val)
        start_dt = datetime.strptime(start_date_str[:10], "%Y-%m-%d") if start_date_str else None
        end_dt = datetime.strptime(end_date_str[:10], "%Y-%m-%d").replace(hour=23, minute=59, second=59) if end_date_str else None

        df = get_readings_dataframe(zone_id=zone_id, start_date=start_dt, end_date=end_dt, limit=10000)
        
        filename = f"campus_telemetry_{utc_now().strftime('%Y%m%d_%H%M%S')}.csv"
        return dcc.send_data_frame(df.to_csv, filename, index=False)

    # 11. CSV Export Download Callback: Report Summary
    @dash_app.callback(
        Output("download-report-csv", "data"),
        Input("btn-export-report-csv", "n_clicks"),
        [
            State("store-report-period", "data"),
            State("filter-zone", "value")
        ],
        prevent_initial_call=True
    )
    def export_report_csv(n_clicks, period, zone_val):
        if not n_clicks:
            return None

        zone_id = None if zone_val == "ALL" else int(zone_val)
        report_data = generate_period_report(period=period or "daily", zone_id=zone_id)
        summaries = report_data.get("zone_summaries", [])
        df_rep = pd.DataFrame(summaries)
        filename = f"campus_summary_report_{period}_{utc_now().strftime('%Y%m%d_%H%M%S')}.csv"
        return dcc.send_data_frame(df_rep.to_csv, filename, index=False)

    # 12. Zone Multi-Dimensional Radar Chart Callback
    @dash_app.callback(
        Output("chart-zone-radar", "figure"),
        [
            Input("btn-refresh-data", "n_clicks"),
            Input("interval-auto-refresh", "n_intervals"),
            Input("store-simulated-reading-trigger", "data")
        ]
    )
    def update_zone_radar_chart(n_refresh, n_intervals, sim_trigger):
        radar_data = get_zone_radar_matrix()
        return create_zone_radar_chart(radar_data)

