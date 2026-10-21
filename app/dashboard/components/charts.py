"""
Plotly visualization charts generator.
Generates line charts, bar comparisons, gauge indicators, box distributions, and heatmaps.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from app.services.analytics import PARAMETERS_META


CHART_LAYOUT_DEFAULTS = dict(
    template="plotly_white",
    margin=dict(l=40, r=40, t=55, b=45),
    font=dict(family="'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", size=12, color="#334155"),
    plot_bgcolor="rgba(248, 250, 252, 0.4)",
    paper_bgcolor="rgba(255, 255, 255, 1)",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.03,
        xanchor="right",
        x=1,
        font=dict(size=11),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="rgba(226,232,240,0.8)",
        borderwidth=1
    ),
    hoverlabel=dict(
        bgcolor="#0F172A",
        bordercolor="#334155",
        font_size=12,
        font_color="#FFFFFF",
        font_family="'Plus Jakarta Sans', 'Inter', sans-serif"
    )
)


def create_trend_line_chart(
    df: pd.DataFrame,
    parameter: str = "pm25",
    parameter_meta: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """Create interactive multi-zone or single-zone time series trend chart."""
    fig = go.Figure()
    meta = parameter_meta or PARAMETERS_META.get(parameter, {"label": parameter.title(), "unit": "", "color": "#3B82F6"})

    if df.empty or parameter not in df.columns:
        fig.add_annotation(
            text="No telemetry data available for selected filter range.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, title=f"{meta['label']} Telemetry Trend")
        return fig

    # Group by zone if multiple zones exist
    zones = df["zone_name"].unique()
    colors = ["#2563EB", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#06B6D4", "#F97316", "#64748B"]

    for idx, zone in enumerate(zones):
        zone_df = df[df["zone_name"] == zone].sort_values("timestamp")
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Scatter(
                x=zone_df["timestamp"],
                y=zone_df[parameter],
                mode="lines",
                name=zone,
                line=dict(shape="spline", smoothing=1.2, width=2.5, color=color),
                hovertemplate=f"<b>{zone}</b><br>Time: %{{x|%Y-%m-%d %H:%M}}<br>{meta['label']}: <b>%{{y:.1f}}</b> {meta['unit']}<extra></extra>"
            )
        )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text=f"<b>{meta['label']} Real-Time Telemetry Trend</b> <span style='font-size:12px; color:#64748B;'>({meta['unit']})</span>",
            x=0.02
        ),
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0",
            rangeselector=dict(
                buttons=list([
                    dict(count=24, label="24 Hours", step="hour", stepmode="backward"),
                    dict(count=7, label="7 Days", step="day", stepmode="backward"),
                    dict(step="all", label="All Data")
                ]),
                bgcolor="#F8FAFC",
                activecolor="#E2E8F0",
                bordercolor="#CBD5E1",
                borderwidth=1,
                font=dict(size=11, color="#334155")
            )
        ),
        yaxis=dict(
            title=f"{meta['label']} ({meta['unit']})",
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0"
        ),
        hovermode="x unified"
    )
    return fig


def create_zone_comparison_bar(
    df: pd.DataFrame,
    parameter: str = "pm25",
    parameter_meta: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """Create bar chart comparing parameter averages across campus zones."""
    fig = go.Figure()
    meta = parameter_meta or PARAMETERS_META.get(parameter, {"label": parameter.title(), "unit": "", "color": "#3B82F6"})

    if df.empty or parameter not in df.columns:
        fig.add_annotation(
            text="No comparison data available.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, title=f"Zone Comparison: {meta['label']}")
        return fig

    # Aggregate average by zone
    grouped = df.groupby("zone_name")[parameter].mean().reset_index()
    grouped = grouped.sort_values(parameter, ascending=True)

    fig.add_trace(
        go.Bar(
            y=grouped["zone_name"],
            x=grouped[parameter],
            orientation="h",
            marker=dict(
                color=grouped[parameter],
                colorscale="Tealgrn" if parameter in ["temperature", "humidity"] else "Blues",
                cornerradius=6,
                showscale=False,
                line=dict(color="rgba(255,255,255,0.6)", width=1)
            ),
            text=[f"<b>{v:.1f}</b> {meta['unit']}" for v in grouped[parameter]],
            textposition="auto",
            hovertemplate=f"<b>%{{y}}</b><br>Average {meta['label']}: <b>%{{x:.1f}}</b> {meta['unit']}<extra></extra>"
        )
    )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text=f"<b>Campus Zone Spatial Comparison</b> <span style='font-size:12px; color:#64748B;'>Mean {meta['label']}</span>",
            x=0.02
        ),
        xaxis=dict(title=f"Average {meta['label']} ({meta['unit']})", showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="", automargin=True)
    )
    return fig


def create_gauge_chart(
    current_value: float,
    parameter: str = "pm25",
    parameter_meta: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """Create an aesthetic gauge indicator for real-time readings."""
    meta = parameter_meta or PARAMETERS_META.get(parameter, {"label": parameter.title(), "unit": ""})
    
    # Establish realistic bounds based on parameter
    bounds = {
        "pm25": {"max": 150, "steps": [(0, 35, "#10B981"), (35, 55, "#F59E0B"), (55, 150, "#EF4444")]},
        "pm10": {"max": 250, "steps": [(0, 50, "#10B981"), (50, 150, "#F59E0B"), (150, 250, "#EF4444")]},
        "co2": {"max": 2500, "steps": [(0, 1000, "#10B981"), (1000, 2000, "#F59E0B"), (2000, 2500, "#EF4444")]},
        "noise": {"max": 100, "steps": [(0, 65, "#10B981"), (65, 80, "#F59E0B"), (80, 100, "#EF4444")]},
        "temperature": {"max": 45, "steps": [(0, 18, "#3B82F6"), (18, 30, "#10B981"), (30, 45, "#EF4444")]},
        "humidity": {"max": 100, "steps": [(0, 30, "#F59E0B"), (30, 70, "#10B981"), (70, 100, "#EF4444")]},
        "aqi": {"max": 300, "steps": [(0, 50, "#10B981"), (50, 100, "#F59E0B"), (100, 150, "#F97316"), (150, 300, "#EF4444")]}
    }
    cfg = bounds.get(parameter, {"max": 100, "steps": [(0, 50, "#10B981"), (50, 100, "#EF4444")]})

    gauge_steps = [{"range": [s[0], s[1]], "color": s[2]} for s in cfg["steps"]]

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=current_value,
            number={"suffix": f" {meta['unit']}", "font": {"size": 24, "family": "'Plus Jakarta Sans', sans-serif"}},
            title={"text": f"<b>{meta['label']} Current Level</b>", "font": {"size": 14, "color": "#1E293B"}},
            gauge={
                "axis": {"range": [0, cfg["max"]], "tickwidth": 1, "tickcolor": "#94A3B8"},
                "bar": {"color": "#0F172A", "thickness": 0.22},
                "bgcolor": "white",
                "borderwidth": 1,
                "bordercolor": "#E2E8F0",
                "steps": gauge_steps
            }
        )
    )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=25, r=25, t=35, b=15),
        height=260,
        paper_bgcolor="rgba(255, 255, 255, 1)",
        font=dict(family="'Plus Jakarta Sans', sans-serif")
    )
    return fig


def create_distribution_box_plot(
    df: pd.DataFrame,
    parameter: str = "pm25",
    parameter_meta: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """Create box plot showing parameter distribution and variance across campus zones."""
    fig = go.Figure()
    meta = parameter_meta or PARAMETERS_META.get(parameter, {"label": parameter.title(), "unit": "", "color": "#3B82F6"})

    if df.empty or parameter not in df.columns:
        fig.add_annotation(
            text="No data for distribution plot.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, title=f"Distribution: {meta['label']}")
        return fig

    zones = df["zone_name"].unique()
    colors = ["#2563EB", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#06B6D4", "#F97316", "#64748B"]

    for idx, zone in enumerate(zones):
        zone_df = df[df["zone_name"] == zone]
        fig.add_trace(
            go.Box(
                y=zone_df[parameter],
                name=zone,
                marker_color=colors[idx % len(colors)],
                boxmean="sd",
                hovertemplate=f"<b>{zone}</b><br>{meta['label']}: <b>%{{y:.1f}}</b> {meta['unit']}<extra></extra>"
            )
        )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text=f"<b>Statistical Variance & Dispersion</b> <span style='font-size:12px; color:#64748B;'>Across Campus Zones</span>",
            x=0.02
        ),
        yaxis=dict(title=f"{meta['label']} ({meta['unit']})", showgrid=True, gridcolor="#F1F5F9"),
        xaxis=dict(title="", tickangle=-25),
        showlegend=False
    )
    return fig


def create_heatmap_chart(heatmap_matrix: Dict[str, Any]) -> go.Figure:
    """Create diurnal hourly heatmap across all campus zones."""
    fig = go.Figure()

    zones = heatmap_matrix.get("zones", [])
    hours = heatmap_matrix.get("hours", [])
    z_data = heatmap_matrix.get("z", [])
    label = heatmap_matrix.get("parameter_label", "Parameter")
    unit = heatmap_matrix.get("unit", "")

    if not zones or not z_data:
        fig.add_annotation(
            text="Insufficient data for heatmap analysis.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, title="Diurnal Heatmap")
        return fig

    fig.add_trace(
        go.Heatmap(
            z=z_data,
            x=hours,
            y=zones,
            colorscale="Viridis",
            colorbar=dict(
                title=dict(text=f"<b>{unit}</b>", side="top"),
                thickness=12,
                len=0.9
            ),
            hovertemplate="Zone: <b>%{y}</b><br>Hour: <b>%{x}</b><br>Mean Intensity: <b>%{z:.1f}</b> " + unit + "<extra></extra>"
        )
    )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text=f"<b>Diurnal Pattern Heatmap: {label}</b> <span style='font-size:12px; color:#64748B;'>(Hour of Day vs Zones)</span>",
            x=0.02
        ),
        xaxis=dict(title="Hour of Day (UTC)", tickangle=0, showgrid=False),
        yaxis=dict(title="", automargin=True, showgrid=False)
    )
    return fig


def create_zone_radar_chart(radar_data: Optional[Dict[str, Any]] = None) -> go.Figure:
    """Create multi-dimensional radar spider chart comparing environmental health across campus zones."""
    fig = go.Figure()
    if not radar_data or not radar_data.get("zones"):
        fig.add_annotation(
            text="Insufficient data for radar comparison.",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, title="Campus Zone Radar Comparison")
        return fig

    categories = radar_data.get("categories", ["Air Cleanliness", "Acoustic Quietness", "IAQ Ventilation", "Thermal Comfort", "Particle Safety"])
    closed_categories = categories + [categories[0]]
    colors = ["#2563EB", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#06B6D4", "#F97316", "#64748B"]

    for idx, zone in enumerate(radar_data["zones"]):
        values = zone["values"] + [zone["values"][0]]
        color = colors[idx % len(colors)]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=closed_categories,
                fill="toself",
                name=zone["zone_name"],
                line=dict(color=color, width=2),
                fillcolor=color + "1A",
                hovertemplate=f"<b>{zone['zone_name']}</b><br>%{{theta}}: <b>%{{r:.1f}}/100</b><extra></extra>"
            )
        )

    layout_args = {k: v for k, v in CHART_LAYOUT_DEFAULTS.items() if k != "legend"}
    fig.update_layout(
        **layout_args,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showline=False,
                gridcolor="#E2E8F0",
                tickfont=dict(size=10, color="#64748B")
            ),
            angularaxis=dict(
                gridcolor="#E2E8F0",
                tickfont=dict(size=11, color="#334155", family="'Plus Jakarta Sans', sans-serif")
            ),
            bgcolor="rgba(248, 250, 252, 0.4)"
        ),
        title=dict(
            text="<b>Multi-Dimensional Environmental Radar Matrix</b> <span style='font-size:12px; color:#64748B;'>(Score 0-100 per dimension)</span>",
            x=0.02
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5
        )
    )
    return fig

