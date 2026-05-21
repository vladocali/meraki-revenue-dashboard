# Formatters for Dashboard Display
from datetime import datetime
from typing import Any

def format_currency(value: float, currency: str = "$") -> str:
    """Format value as currency."""
    if value is None:
        return f"{currency}0"
    return f"{currency}{value:,.0f}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage."""
    if value is None:
        return "0%"
    return f"{value*100:.{decimals}f}%"

def format_number(value: float, decimals: int = 2) -> str:
    """Format number with decimals."""
    if value is None:
        return "0"
    return f"{value:,.{decimals}f}"

def format_date(date_obj: Any, format: str = "%d/%m/%Y") -> str:
    """Format date object."""
    if isinstance(date_obj, str):
        return date_obj
    if date_obj is None:
        return "-"
    return date_obj.strftime(format)

def format_datetime(dt: Any, format: str = "%d/%m/%Y %H:%M") -> str:
    """Format datetime object."""
    if isinstance(dt, str):
        return dt
    if dt is None:
        return "-"
    return dt.strftime(format)

def format_time_ago(seconds: int) -> str:
    """Format seconds as time ago."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds//60}m"
    elif seconds < 86400:
        return f"{seconds//3600}h"
    else:
        return f"{seconds//86400}d"

def format_occupancy_status(occupancy: float) -> tuple[str, str]:
    """Return status and badge color based on occupancy."""
    status = "BAJO"
    color = "🔴 BAJO"
    
    if occupancy >= 0.85:
        status = "EXCELENTE"
        color = "🟢 EXCELENTE"
    elif occupancy >= 0.70:
        status = "BUENO"
        color = "🟢 BUENO"
    elif occupancy >= 0.50:
        status = "MEDIO"
        color = "🟡 MEDIO"
    
    return status, color

def format_price_change(old_price: float, new_price: float) -> str:
    """Format price change as percentage."""
    if old_price == 0:
        return "N/A"
    change = ((new_price - old_price) / old_price) * 100
    arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
    return f"{arrow} {change:+.1f}%"

def get_status_color(value: float, thresholds: dict) -> str:
    """Get color based on value thresholds."""
    if value >= thresholds.get("excellent", 100):
        return "#10B981"  # Green
    elif value >= thresholds.get("good", 70):
        return "#3B82F6"  # Blue
    elif value >= thresholds.get("warning", 40):
        return "#F59E0B"  # Amber
    else:
        return "#EF4444"  # Red
