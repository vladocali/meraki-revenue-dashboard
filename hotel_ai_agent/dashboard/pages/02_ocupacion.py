"""
OCCUPANCY PAGE - Occupancy Analysis and Calendar
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.config import COLORS
from dashboard.components.charts import create_occupancy_heatmap, create_occupancy_line_chart, create_occupancy_bar_chart
from dashboard.data.mock_data import get_mock_data
from dashboard.services.dashboard_db import get_dashboard_db
from dashboard.utils.formatters import format_percentage, format_occupancy_status
from dashboard.utils.logger import dashboard_logger

st.title("📅 Análisis de Ocupación")
st.markdown("---")

@st.cache_data(ttl=300)
def load_occupancy_data():
    try:
        source = 'db'
        occupancy_7d = pd.DataFrame()
        daily_summary = pd.DataFrame()

        db = get_dashboard_db()
        if db.is_available():
            occupancy_7d = db.get_7day_occupancy()
            daily_summary = db.get_daily_occupancy_summary()
            if not occupancy_7d.empty and not daily_summary.empty:
                source = 'db'

        return occupancy_7d, daily_summary, source
    except Exception as e:
        dashboard_logger.error(f"Error loading occupancy data: {e}")
        return pd.DataFrame(), pd.DataFrame(), 'unavailable'

occupancy_7d, daily_summary, occupancy_source = load_occupancy_data()

if occupancy_7d is not None and daily_summary is not None and not occupancy_7d.empty and not daily_summary.empty:
    st.caption("Datos reales" if occupancy_source == 'db' else "Datos demo")

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_occ = daily_summary['occupancy_pct'].mean() / 100
        st.metric("Ocupación Promedio (7d)", format_percentage(avg_occ))
    
    with col2:
        max_occ = daily_summary['occupancy_pct'].max() / 100
        st.metric("Ocupación Máxima", format_percentage(max_occ))
    
    with col3:
        min_occ = daily_summary['occupancy_pct'].min() / 100
        st.metric("Ocupación Mínima", format_percentage(min_occ))
    
    with col4:
        total_rooms = daily_summary['total_rooms'].iloc[0] if len(daily_summary) > 0 else 0
        st.metric("Total Habitaciones", int(total_rooms))
    
    st.markdown("---")
    
    # Heatmap
    st.subheader("🔥 Mapa de Calor - Ocupación por Habitación")
    st.plotly_chart(create_occupancy_heatmap(occupancy_7d), use_container_width=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Línea de Ocupación")
        st.plotly_chart(create_occupancy_line_chart(daily_summary), use_container_width=True)
    
    with col2:
        st.subheader("Disponibilidad Diaria")
        st.plotly_chart(create_occupancy_bar_chart(daily_summary), use_container_width=True)
    
    st.markdown("---")
    
    # Detailed Table
    st.subheader("📊 Detalles de Ocupación por Día")
    
    display_df = daily_summary.copy()
    display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%d/%m/%Y')
    display_df.columns = ['Fecha', 'Ocupadas', 'Ocupación %', 'Total', 'Libres']
    display_df = display_df[['Fecha', 'Ocupadas', 'Libres', 'Total', 'Ocupación %']]
    display_df['Ocupación %'] = display_df['Ocupación %'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Room occupancy detail
    st.subheader("📋 Detalle por Habitación")
    
    room_detail = occupancy_7d.groupby('room').agg({
        'occupancy_pct': 'mean',
        'occupied': 'sum'
    }).reset_index()
    room_detail.columns = ['Habitación', 'Ocupación %', 'Noches Ocupadas']
    room_detail['Ocupación %'] = room_detail['Ocupación %'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(room_detail, use_container_width=True, hide_index=True)
    
else:
    st.warning("No hay datos reales de ocupación disponibles en este momento")
