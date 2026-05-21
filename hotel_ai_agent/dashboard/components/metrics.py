# Reusable Metric Components
import streamlit as st
from dashboard.utils.formatters import (
    format_currency, format_percentage, format_occupancy_status, get_status_color
)
from dashboard.config import COLORS

def display_kpi_metric(label: str, value: any, unit: str = "", icon: str = "📊", 
                       delta: float = None, delta_color: str = "normal", 
                       help_text: str = None, color: str = None):
    """Display a KPI metric card."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric(
            label=label,
            value=value,
            delta=delta,
            delta_color=delta_color,
            help=help_text
        )
    
    with col2:
        st.markdown(f"<div style='font-size: 2em'>{icon}</div>", unsafe_allow_html=True)

def display_metric_card(title: str, value: any, subtitle: str = "", icon: str = "📊", 
                       color: str = COLORS['primary'], help_text: str = None):
    """Display a metric in a card."""
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, {color}, {color}dd);
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    '>
        <div style='font-size: 2em; margin-bottom: 10px;'>{icon}</div>
        <div style='font-size: 0.9em; opacity: 0.9;'>{title}</div>
        <div style='font-size: 1.8em; font-weight: bold; margin: 10px 0;'>{value}</div>
        <div style='font-size: 0.8em; opacity: 0.85;'>{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def display_status_indicator(status: str, message: str = "", icon: str = "🟢"):
    """Display a status indicator."""
    status_colors = {
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'info': '#3B82F6',
    }
    
    color = status_colors.get(status, '#6B7280')
    
    st.markdown(f"""
    <div style='
        background: {color}15;
        border-left: 4px solid {color};
        padding: 12px;
        border-radius: 4px;
    '>
        <span style='font-size: 1.2em; margin-right: 10px;'>{icon}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)

def display_occupancy_badge(occupancy_pct: float):
    """Display occupancy status badge."""
    status, color_text = format_occupancy_status(occupancy_pct)
    
    # Determine background color
    if occupancy_pct >= 0.85:
        bg_color = "#D1FAE5"  # Light green
        text_color = "#065F46"  # Dark green
    elif occupancy_pct >= 0.70:
        bg_color = "#DBEAFE"  # Light blue
        text_color = "#1E40AF"  # Dark blue
    elif occupancy_pct >= 0.50:
        bg_color = "#FEF3C7"  # Light amber
        text_color = "#92400E"  # Dark amber
    else:
        bg_color = "#FEE2E2"  # Light red
        text_color = "#7F1D1D"  # Dark red
    
    st.markdown(f"""
    <div style='
        background: {bg_color};
        border-radius: 20px;
        padding: 8px 16px;
        text-align: center;
        font-weight: bold;
        color: {text_color};
    '>
        {format_percentage(occupancy_pct)} - {color_text}
    </div>
    """, unsafe_allow_html=True)

def display_alert_box(title: str, message: str, alert_type: str = "info", icon: str = "ℹ️"):
    """Display an alert box."""
    alert_colors = {
        'info': '#3B82F6',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
    }
    
    color = alert_colors.get(alert_type, '#3B82F6')
    
    st.markdown(f"""
    <div style='
        background: {color}15;
        border-left: 5px solid {color};
        border-radius: 4px;
        padding: 15px;
        margin: 10px 0;
    '>
        <div style='font-weight: bold; color: {color}; margin-bottom: 5px;'>
            <span style='font-size: 1.5em;'>{icon}</span> {title}
        </div>
        <div style='color: #374151; margin-left: 30px;'>{message}</div>
    </div>
    """, unsafe_allow_html=True)

def display_comparison_card(label: str, current: float, previous: float, 
                            unit: str = "", icon: str = "📊", format_func = None):
    """Display a comparison card showing current vs previous."""
    if format_func is None:
        format_func = lambda x: f"{x:,.0f}"
    
    delta = current - previous
    delta_pct = (delta / previous * 100) if previous != 0 else 0
    color = "#10B981" if delta >= 0 else "#EF4444"
    arrow = "📈" if delta >= 0 else "📉"
    
    st.markdown(f"""
    <div style='
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 20px;
    '>
        <div style='font-size: 0.9em; color: #6B7280; margin-bottom: 10px;'>
            {icon} {label}
        </div>
        <div style='font-size: 1.8em; font-weight: bold; margin-bottom: 10px;'>
            {format_func(current)}
        </div>
        <div style='color: {color}; font-weight: bold;'>
            {arrow} {delta_pct:+.1f}% vs período anterior
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_mini_stat(label: str, value: any, icon: str = "📊"):
    """Display a mini statistic."""
    st.markdown(f"""
    <div style='
        text-align: center;
        padding: 10px;
    '>
        <div style='font-size: 1.8em;'>{icon}</div>
        <div style='font-size: 0.85em; color: #6B7280; margin: 5px 0;'>{label}</div>
        <div style='font-size: 1.3em; font-weight: bold;'>{value}</div>
    </div>
    """, unsafe_allow_html=True)
