"""
Main Streamlit Application - Revenue Management Dashboard
Run with: streamlit run app.py
"""
import streamlit as st
import sys
from pathlib import Path

# Add dashboard module to path
dashboard_path = Path(__file__).parent
sys.path.insert(0, str(dashboard_path.parent))

from dashboard.config import STREAMLIT_CONFIG, COLORS
from dashboard.utils.logger import dashboard_logger
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Revenue Management Dashboard | Hotel AI",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/yourusername/hotel_ai_agent",
        "Report a bug": "https://github.com/yourusername/hotel_ai_agent/issues",
        "About": "Revenue Management Dashboard v1.0 - Powered by AI"
    }
)

# Custom CSS
st.markdown(f"""
<style>
    :root {{
        --primary-color: {COLORS['primary']};
        --secondary-color: {COLORS['secondary']};
        --success-color: {COLORS['success']};
        --warning-color: {COLORS['warning']};
        --danger-color: {COLORS['danger']};
    }}
    
    /* Header styling */
    .stAppHeader {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']});
        padding: 20px;
        color: white;
        border-radius: 0;
    }}
    
    /* Sidebar styling */
    .stSidebar {{
        background: linear-gradient(180deg, #f8f9fa, #ffffff);
    }}
    
    .stSidebar .stButton > button {{
        width: 100%;
        background: {COLORS['primary']};
        border: none;
        border-radius: 5px;
        color: white;
    }}
    
    .stSidebar .stButton > button:hover {{
        background: {COLORS['secondary']};
    }}
    
    /* Metric cards */
    .streamlit-metric {{
        background: linear-gradient(135deg, #f5f7fa, #ffffff);
        border-radius: 10px;
        padding: 20px;
        border-left: 4px solid {COLORS['primary']};
    }}
    
    /* Dataframe styling */
    .stDataFrame {{
        border-radius: 10px;
        overflow: hidden;
    }}
    
    /* Button styling */
    .stButton > button {{
        background: {COLORS['primary']};
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        background: {COLORS['secondary']};
        transform: scale(1.02);
    }}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button {{
        border-radius: 5px;
        margin: 5px;
    }}
    
    /* Text styling */
    h1, h2, h3 {{
        color: {COLORS['dark']};
    }}
    
    /* Container styling */
    .stContainer {{
        border-radius: 10px;
        background: white;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_app():
    """Initialize app resources."""
    dashboard_logger.info("Dashboard application started")
    return {
        'start_time': datetime.now(),
        'version': '1.0.0'
    }

# Initialize
app_state = initialize_app()

PAGE_MAP = {
    "home": ("🏠 Home", "pages/01_home.py"),
    "ocupacion": ("📅 Ocupación", "pages/02_ocupacion.py"),
    "precios": ("💰 Precios", "pages/03_precios.py"),
    "competencia": ("🎯 Competencia", "pages/04_competencia.py"),
    "reportes": ("📑 Reportes", "pages/05_reportes.py"),
}

def _get_query_param(name: str, default: str = "") -> str:
    try:
        value = st.query_params.get(name, default)
    except Exception:
        legacy = st.experimental_get_query_params().get(name, [default])
        value = legacy[0] if isinstance(legacy, list) and legacy else default
    if isinstance(value, list):
        value = value[0] if value else default
    return str(value)

embed_value = _get_query_param("embed", "")
embed_mode = embed_value.lower() in {"1", "true", "yes"}

if embed_mode:
    st.markdown("""
    <style>
        section[data-testid="stSidebar"],
        div[data-testid="stSidebar"],
        aside[data-testid="stSidebar"] { display: none !important; width: 0 !important; min-width: 0 !important; }
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"],
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] { display: none !important; }
        #MainMenu { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

if embed_mode:
    selected_page_key = _get_query_param("page", "home").strip().lower()
    if selected_page_key not in PAGE_MAP:
        selected_page_key = "home"
    selected_page_label = PAGE_MAP[selected_page_key][0]
else:
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='font-size: 2.5em;'>🏨</h1>
            <h2>Revenue AI</h2>
            <p style='color: #666; font-size: 0.9em;'>Management Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("#### 🧭 Navegación")

        page_labels = [item[0] for item in PAGE_MAP.values()]
        selected_page = st.radio("Seleccionar página:", page_labels, label_visibility="collapsed")
        
        st.divider()
        
        st.markdown("#### ⚡ Acciones Rápidas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Actualizar", key="refresh_main"):
                st.rerun()
        
        with col2:
            if st.button("⚙️ Config", key="config_main"):
                st.info("Ir a configuración")
        
        st.divider()
        
        # Info section
        st.markdown("#### 📊 Estado del Sistema")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estado", "🟢 Activo")
        with col2:
            st.metric("Conexión BD", "✅ OK")
        
        st.divider()
        
        st.markdown("""
        <div style='font-size: 0.85em; color: #666; text-align: center;'>
            <p><strong>Hotel Revenue Management</strong></p>
            <p>v1.0.0 - Powered by AI</p>
            <p style='margin-top: 10px;'>
                <a href='#' style='color: {COLORS["primary"]}; text-decoration: none;'>📖 Docs</a> | 
                <a href='#' style='color: {COLORS["primary"]}; text-decoration: none;'>🐛 Report</a> | 
                <a href='#' style='color: {COLORS["primary"]}; text-decoration: none;'>💬 Support</a>
            </p>
        </div>
        """, unsafe_allow_html=True)

    selected_page_key = None
    for key, (label, _) in PAGE_MAP.items():
        if label == selected_page:
            selected_page_key = key
            break
    if selected_page_key is None:
        selected_page_key = "home"
    selected_page_label = PAGE_MAP[selected_page_key][0]

# Main content
selected_page_file = PAGE_MAP[selected_page_key][1]
exec(open(dashboard_path / selected_page_file).read())

if not embed_mode:
    st.divider()

    footer_col1, footer_col2, footer_col3 = st.columns(3)

    with footer_col1:
        st.markdown(f"**Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    with footer_col2:
        st.markdown("**Sistema:** Revenue Management AI")

    with footer_col3:
        st.markdown("**Versión:** 1.0.0 • Beta")

# Log dashboard access
dashboard_logger.info(f"Dashboard accessed - User viewed {selected_page_label}")
