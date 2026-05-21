# Dashboard Configuration
import os
from pathlib import Path
from dotenv import load_dotenv

def _get_config_value(name: str, default: str = "") -> str:
    """Read configuration from env vars first, then Streamlit secrets when available."""
    env_value = os.getenv(name)
    if env_value not in (None, ""):
        return str(env_value)

    try:
        import streamlit as st
        secret_value = st.secrets.get(name)
        if secret_value not in (None, ""):
            return str(secret_value)
    except Exception:
        pass

    return default

# Load environment variables
load_dotenv()

# Paths
DASHBOARD_DIR = Path(__file__).parent
PROJECT_DIR = DASHBOARD_DIR.parent
LOGS_DIR = PROJECT_DIR / "logs"
REPORTS_DIR = PROJECT_DIR / "reports"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "theme": {
        "primaryColor": "#00A86B",  # Professional green
        "backgroundColor": "#F8F9FA",  # Light gray
        "secondaryBackgroundColor": "#FFFFFF",
        "textColor": "#1F2937",  # Dark gray
        "font": "sans serif"
    },
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Color Palette
COLORS = {
    "primary": "#00A86B",        # Professional green
    "secondary": "#3B82F6",      # Blue
    "success": "#10B981",         # Green
    "warning": "#F59E0B",         # Amber
    "danger": "#EF4444",          # Red
    "light": "#F3F4F6",           # Light gray
    "dark": "#1F2937",            # Dark gray
    "accent": "#8B5CF6",          # Purple
}

# KPI Thresholds
KPI_THRESHOLDS = {
    "occupancy_excellent": 0.85,
    "occupancy_good": 0.70,
    "occupancy_medium": 0.50,
    "adr_growth_positive": 0.05,
    "revpar_target": 100000,
}

# Database
DB_HOST = _get_config_value("DB_HOST", "127.0.0.1")
DB_PORT = int(_get_config_value("DB_PORT", "3306"))
DB_NAME = _get_config_value("DB_NAME", "meraki")
DB_USER = _get_config_value("DB_USER", "root")
DB_PASSWORD = _get_config_value("DB_PASSWORD", "")

# OpenAI
OPENAI_API_KEY = _get_config_value("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"

# Dashboard Cache Settings
CACHE_TTL = 300  # 5 minutes in seconds
MOCK_DATA_TTL = 600  # 10 minutes for mock data

# Chart Configuration
CHART_CONFIG = {
    "responsive": True,
    "displayModeBar": False,
    "displaylogo": False,
}

# Report Generation
REPORT_FORMAT = ["txt", "csv", "json"]

# Logging
LOG_LEVEL = _get_config_value("LOG_LEVEL", "INFO")

# Currency
CURRENCY = "COP"
CURRENCY_SYMBOL = "$"

# Pagination
ITEMS_PER_PAGE = 20

# API Rate Limiting
OPENAI_TIMEOUT = 30
DB_QUERY_TIMEOUT = 30
