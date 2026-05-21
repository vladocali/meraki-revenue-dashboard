"""
HOME PAGE - Main Dashboard Overview
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.config import COLORS
from dashboard.components.metrics import display_metric_card, display_alert_box, display_status_indicator
from dashboard.components.charts import (
    create_occupancy_line_chart, create_revenue_forecast_chart, create_occupancy_bar_chart
)
from dashboard.data.mock_data import get_mock_data
from dashboard.services.dashboard_db import get_dashboard_db
from dashboard.services.analytics_service import AnalyticsService
from dashboard.services.ai_insights import get_ai_service
from dashboard.utils.formatters import format_currency, format_percentage, format_occupancy_status
from dashboard.utils.cache import cached_function
from dashboard.utils.logger import dashboard_logger

# Custom CSS
st.markdown("""
<style>
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
    .metric-card { padding: 20px; border-radius: 10px; background: linear-gradient(135deg, #f5f7fa, #ffffff); border: 1px solid #e5e7eb; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data():
    """Load all data with caching."""
    try:
        occupancy_source = 'mock'
        occupancy_data = pd.DataFrame()
        db = get_dashboard_db()
        if db.is_available():
            occupancy_data = db.get_daily_occupancy_summary()
            if not occupancy_data.empty:
                occupancy_source = 'db'

        if occupancy_data.empty:
            occupancy_data = get_mock_data('daily_summary')

        metrics = get_mock_data('revenue')
        suggestions = get_mock_data('suggestions')
        alerts = get_mock_data('alerts')
        competitor_data = get_mock_data('competitor')
        
        return {
            'occupancy_data': occupancy_data,
            'occupancy_source': occupancy_source,
            'metrics': metrics,
            'suggestions': suggestions,
            'alerts': alerts,
            'competitor_data': competitor_data,
        }
    except Exception as e:
        dashboard_logger.error(f"Error loading dashboard data: {e}")
        return None

def render_kpi_row():
    """Render KPI metrics row."""
    data = load_data()
    if not data:
        st.error("Error loading data")
        return
    
    metrics = data['metrics']
    occupancy_data = data['occupancy_data']
    competitor_data = data['competitor_data']
    
    # Calculate analytics
    avg_occ = occupancy_data['occupancy_pct'].mean() / 100 if not occupancy_data.empty else 0
    comp_avg_price = competitor_data['nightly_price'].mean() if not competitor_data.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Ocupación Promedio (7d)",
            value=format_percentage(avg_occ),
            delta=f"{avg_occ*100:.1f}%"
        )
    
    with col2:
        st.metric(
            label="💰 ADR (Tarifa Promedio)",
            value=format_currency(metrics['adr']),
            delta=f"${metrics['adr']:,.0f}"
        )
    
    with col3:
        st.metric(
            label="📈 RevPAR",
            value=format_currency(metrics['revpar']),
            delta=f"${metrics['revpar']:,.0f}"
        )
    
    with col4:
        st.metric(
            label="💵 Ingresos Proyectados (7d)",
            value=format_currency(metrics['revenue_7d']),
            delta=f"COP {metrics['revenue_7d']:,.0f}"
        )

def render_charts():
    """Render main charts."""
    data = load_data()
    if not data:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_occupancy_line_chart(data['occupancy_data']),
            use_container_width=True
        )
        st.caption("Datos reales" if data.get('occupancy_source') == 'db' else "Datos demo")
    
    with col2:
        st.plotly_chart(
            create_occupancy_bar_chart(data['occupancy_data']),
            use_container_width=True
        )
    
    # Revenue forecast
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(
            create_revenue_forecast_chart(data['metrics']),
            use_container_width=True
        )
    
    with col4:
        # Price trends
        price_history = get_mock_data('price_history')
        from dashboard.components.charts import create_price_history_chart
        st.plotly_chart(
            create_price_history_chart(price_history),
            use_container_width=True
        )

def render_alerts():
    """Render AI alerts."""
    data = load_data()
    if not data:
        return
    
    st.subheader("⚠️ Alertas y Recomendaciones IA")
    
    alerts = data['alerts']
    if alerts:
        for alert in alerts:
            display_alert_box(
                title=alert.get('title', 'Alert'),
                message=alert.get('message', ''),
                alert_type='info',
                icon=alert.get('icon', 'ℹ️')
            )
    else:
        st.info("No hay alertas críticas en este momento")

def render_top_suggestions():
    """Render top price suggestions."""
    data = load_data()
    if not data:
        return
    
    st.subheader("💡 Top Sugerencias de Precio")
    
    suggestions = data['suggestions']
    top_suggestions = suggestions.nlargest(5, 'estimated_impact')
    
    if not top_suggestions.empty:
        # Create display dataframe
        display_df = top_suggestions[[
            'room', 'action', 'current_price', 'suggested_price', 'change_pct', 'reason'
        ]].copy()
        
        display_df.columns = ['Habitación', 'Acción', 'Precio Actual', 'Precio Sugerido', '% Cambio', 'Razón']
        
        # Format numbers
        display_df['Precio Actual'] = display_df['Precio Actual'].apply(lambda x: f"${x:,.0f}")
        display_df['Precio Sugerido'] = display_df['Precio Sugerido'].apply(lambda x: f"${x:,.0f}")
        display_df['% Cambio'] = display_df['% Cambio'].apply(lambda x: f"{x:+.1f}%")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay sugerencias disponibles")

def render_ai_insights():
    """Render AI insights section."""
    st.subheader("🤖 Análisis Inteligente IA")
    
    data = load_data()
    if not data:
        return
    
    # Get AI service
    ai_service = get_ai_service()
    
    # Calculate metrics
    metrics = data['metrics']
    occupancy_data = data['occupancy_data']
    
    avg_occ = occupancy_data['occupancy_pct'].mean() / 100 if not occupancy_data.empty else 0
    
    # Generate insights
    with st.spinner("Generando análisis inteligente..."):
        occupancy_insight = ai_service.generate_occupancy_insight(
            occupancy=avg_occ,
            trend=0.05,  # Simulated trend
            forecast_days=7
        )
        
        executive_summary = ai_service.generate_executive_summary(
            metrics=metrics,
            opportunities=data['alerts'],
            alerts=[]
        )
    
    # Display insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Análisis de Ocupación")
        st.markdown(occupancy_insight)
    
    with col2:
        st.markdown("#### 📈 Resumen Ejecutivo")
        st.markdown(executive_summary)

def render_quick_actions():
    """Render quick action buttons."""
    st.subheader("⚡ Acciones Rápidas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶️ Ejecutar Análisis Ahora", key="run_analysis"):
            st.success("✅ Análisis ejecutado exitosamente")
            dashboard_logger.info("Manual analysis run triggered from dashboard")
    
    with col2:
        if st.button("📥 Descargar Reporte", key="download_report"):
            st.info("Reporte preparado para descargar")
    
    with col3:
        if st.button("🔄 Actualizar Competencia", key="refresh_competitor"):
            st.success("✅ Datos de competencia actualizados")
    
    with col4:
        if st.button("⚙️ Configuración", key="settings"):
            st.info("Ir a sección de configuración")

# Main page layout
def main():
    st.title("🏨 Revenue Management Dashboard")
    st.markdown("---")
    
    # Timestamp
    st.markdown(f"_Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}_")
    
    # KPI Row
    st.markdown("#### Métricas Clave (KPIs)")
    render_kpi_row()
    
    st.markdown("---")
    
    # Quick Actions
    render_quick_actions()
    
    st.markdown("---")
    
    # Charts Section
    st.markdown("#### Ocupación e Ingresos")
    render_charts()
    
    st.markdown("---")
    
    # Alerts
    render_alerts()
    
    st.markdown("---")
    
    # Suggestions
    render_top_suggestions()
    
    st.markdown("---")
    
    # AI Insights
    render_ai_insights()

if __name__ == "__main__":
    main()
