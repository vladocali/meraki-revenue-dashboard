"""
COMPETITORS PAGE - Competitor Price Analysis
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.config import COLORS
from dashboard.components.charts import create_competitor_comparison_chart
from dashboard.data.mock_data import get_mock_data
from dashboard.services.dashboard_db import get_dashboard_db
from dashboard.utils.formatters import format_currency
from dashboard.utils.logger import dashboard_logger

st.title("🎯 Análisis de Competencia")
st.markdown("---")


def _to_dataframe(value) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value
    if isinstance(value, list):
        return pd.DataFrame(value)
    if isinstance(value, dict):
        return pd.DataFrame([value])
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_competitor_data():
    try:
        db = get_dashboard_db()
        if db.is_available():
            real_data = db.get_competitor_prices(days=7)
            if not real_data.empty:
                real_data = real_data.copy()
                real_data['competitor'] = real_data['source'].astype(str).str.title()
                real_data['platform'] = real_data['source'].astype(str).str.title()
                real_data['date'] = pd.to_datetime(real_data['captured_at']).dt.date
                return real_data

        return _to_dataframe(get_mock_data('competitor'))
    except Exception as e:
        dashboard_logger.error(f"Error loading competitor data: {e}")
        return _to_dataframe(get_mock_data('competitor'))

competitor_data = load_competitor_data()
current_prices = pd.DataFrame()
try:
    db = get_dashboard_db()
    if db.is_available():
        current_prices = db.get_current_room_prices()
except Exception:
    current_prices = pd.DataFrame()

if current_prices.empty:
    current_prices = _to_dataframe(get_mock_data('current_prices'))

if competitor_data is not None and not competitor_data.empty:
    st.caption("📊 Datos reales" if 'source' in competitor_data.columns and not competitor_data.empty and 'captured_at' in competitor_data.columns else "📊 Datos demo")

    # Get average price
    my_avg_price = current_prices['current_price'].mean() if not current_prices.empty and 'current_price' in current_prices.columns else 200000
    
    # Comparison chart
    st.subheader("Comparativa de Precios")
    st.plotly_chart(
        create_competitor_comparison_chart(competitor_data, my_avg_price),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        comp_avg = competitor_data['nightly_price'].mean() if 'nightly_price' in competitor_data.columns else 0
        st.metric("Precio Promedio Competencia", format_currency(comp_avg))
    
    with col2:
        comp_min = competitor_data['nightly_price'].min() if 'nightly_price' in competitor_data.columns else 0
        st.metric("Precio Mínimo Competencia", format_currency(comp_min))
    
    with col3:
        comp_max = competitor_data['nightly_price'].max() if 'nightly_price' in competitor_data.columns else 0
        st.metric("Precio Máximo Competencia", format_currency(comp_max))
    
    with col4:
        my_avg = current_prices['current_price'].mean() if 'current_price' in current_prices.columns and not current_prices.empty else 0
        diff_pct = ((my_avg - comp_avg) / comp_avg * 100) if comp_avg > 0 else 0
        st.metric("Diferencia vs Promedio", f"{diff_pct:+.1f}%")
    
    st.markdown("---")
    
    # Filters
    st.subheader("Filtrar Competidores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_platform = st.multiselect(
            "Plataforma",
            options=competitor_data['platform'].unique().tolist(),
            default=competitor_data['platform'].unique().tolist()
        )
    
    with col2:
        date_range = st.date_input(
            "Rango de Fechas",
            value=(pd.to_datetime(competitor_data['date']).min(), pd.to_datetime(competitor_data['date']).max()),
            key="comp_date_range"
        )
    
    # Filter data
    filtered_data = competitor_data[
        (competitor_data['platform'].isin(selected_platform)) &
        (pd.to_datetime(competitor_data['date']) >= pd.to_datetime(date_range[0])) &
        (pd.to_datetime(competitor_data['date']) <= pd.to_datetime(date_range[1]))
    ]
    
    st.markdown("---")
    
    # Detailed table
    st.subheader("Detalles de Competencia")
    
    display_df = filtered_data.copy()
    display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%d/%m/%Y')
    display_df['nightly_price'] = display_df['nightly_price'].apply(lambda x: f"${x:,.0f}")
    display_df['captured_at'] = pd.to_datetime(display_df['captured_at']).dt.strftime('%H:%M') if 'captured_at' in display_df.columns else '-'
    
    display_df = display_df[[
        'date', 'competitor', 'platform', 'nightly_price', 'room_type', 'captured_at'
    ]]
    display_df.columns = ['Fecha', 'Competidor', 'Plataforma', 'Precio Noche', 'Tipo Habitación', 'Capturado a las']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Analytics
    st.subheader("Análisis por Competidor")
    
    competitor_summary = filtered_data.groupby('competitor').agg({
        'nightly_price': ['mean', 'min', 'max', 'std']
    }).reset_index()
    competitor_summary.columns = ['Competidor', 'Promedio', 'Mínimo', 'Máximo', 'Desv. Est']
    
    for col in ['Promedio', 'Mínimo', 'Máximo', 'Desv. Est']:
        competitor_summary[col] = competitor_summary[col].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(competitor_summary, use_container_width=True, hide_index=True)
    
else:
    st.warning("No hay datos de competencia disponibles")
