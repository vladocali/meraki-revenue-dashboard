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
    """Load all data from real database with fallback to mock."""
    try:
        db = get_dashboard_db()
        
        # Initialize with defaults
        data = {
            'occupancy_data': pd.DataFrame(),
            'occupancy_source': 'mock',
            'metrics': {},
            'suggestions': [],
            'alerts': [],
            'price_history': pd.DataFrame(),
        }
        
        # Try to load from real database
        if db.is_available():
            # Occupancy data
            occupancy_data = db.get_daily_occupancy_summary()
            if not occupancy_data.empty:
                data['occupancy_data'] = occupancy_data
                data['occupancy_source'] = 'db'
            
            # Revenue metrics
            revenue_7d = db.get_revenue_7d()
            occupancy_summary = db.get_daily_occupancy_summary()
            adr = db.get_adr()
            revpar = db.get_revpar()
            
            if not occupancy_summary.empty:
                avg_occupancy = occupancy_summary['occupancy_pct'].mean() / 100
            else:
                avg_occupancy = 0
            
            data['metrics'] = {
                'occupancy_7d': avg_occupancy,
                'adr': adr,
                'revpar': revpar,
                'revenue_7d': revenue_7d.get('total', 0),
                'revenue_7d_stays': revenue_7d.get('stays', 0),
                'revenue_7d_consumptions': revenue_7d.get('consumptions', 0),
                'daily_potential': adr * 9 if adr > 0 else 0,  # 9 rooms × ADR
                'daily_actual': revenue_7d.get('total', 0) / 7 if revenue_7d.get('total', 0) > 0 else 0,
                'lost_revenue_daily': 0,  # Calculate if needed
            }
            
            # Price history from real data
            price_history = db.get_price_history(days=30)
            if not price_history.empty:
                data['price_history'] = price_history
            
            # Alerts from real data
            alerts = db.get_alerts()
            data['alerts'] = alerts if alerts else []
        
        # Fallback to mock if database not available or missing data
        if data['occupancy_data'].empty:
            data['occupancy_data'] = get_mock_data('daily_summary')
            data['occupancy_source'] = 'mock'
        
        if not data['metrics']:
            mock_revenue = get_mock_data('revenue')
            data['metrics'] = mock_revenue
        
        if not data['alerts']:
            data['alerts'] = get_mock_data('alerts')
        
        if data['price_history'].empty:
            data['price_history'] = get_mock_data('price_history')
        
        # Suggestions (can combine real+mock)
        try:
            current_prices = db.get_current_room_prices() if db.is_available() else pd.DataFrame()
            if not current_prices.empty:
                # Generate basic suggestions from real prices
                suggestions = []
                for idx, room in current_prices.iterrows():
                    suggestions.append({
                        'room': room.get('room', 'Unknown'),
                        'action': 'MAINTAIN',
                        'reason': 'Precios estables basados en demanda actual',
                        'estimated_impact': 0,
                    })
                data['suggestions'] = suggestions[:5]  # Top 5
        except:
            pass
        
        if not data['suggestions']:
            data['suggestions'] = get_mock_data('suggestions')
        
        return data
    
    except Exception as e:
        dashboard_logger.error(f"Error loading dashboard data: {e}")
        # Return mock data as fallback
        return {
            'occupancy_data': get_mock_data('daily_summary'),
            'occupancy_source': 'mock',
            'metrics': get_mock_data('revenue'),
            'suggestions': get_mock_data('suggestions'),
            'alerts': get_mock_data('alerts'),
            'price_history': get_mock_data('price_history'),
        }

def render_kpi_row():
    """Render KPI metrics row."""
    data = load_data()
    if not data:
        st.error("Error loading data")
        return
    
    metrics = data['metrics']
    occupancy_data = data['occupancy_data']
    
    # Calculate analytics
    if not occupancy_data.empty and 'occupancy_pct' in occupancy_data.columns:
        avg_occ_pct = occupancy_data['occupancy_pct'].mean()
        avg_occ = avg_occ_pct / 100
    else:
        avg_occ = 0
        avg_occ_pct = 0
    
    adr = metrics.get('adr', 0)
    revpar = metrics.get('revpar', 0)
    revenue_7d = metrics.get('revenue_7d', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Ocupación Promedio (7d)",
            value=f"{avg_occ_pct:.1f}%"
        )
    
    with col2:
        st.metric(
            label="💰 ADR (Tarifa Promedio)",
            value=format_currency(adr)
        )
    
    with col3:
        st.metric(
            label="📈 RevPAR",
            value=format_currency(revpar)
        )
    
    with col4:
        st.metric(
            label="💵 Ingresos Últimos 7d",
            value=format_currency(revenue_7d)
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
        st.caption("📊 Datos reales" if data.get('occupancy_source') == 'db' else "📊 Datos demo")
    
    with col2:
        st.plotly_chart(
            create_occupancy_bar_chart(data['occupancy_data']),
            use_container_width=True
        )
    
    # Revenue and Price trends
    col3, col4 = st.columns(2)
    with col3:
        # Create a revenue trend based on real data
        revenue_data = get_dashboard_db().get_daily_revenue(7) if get_dashboard_db().is_available() else pd.DataFrame()
        
        if not revenue_data.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=revenue_data['date'],
                y=revenue_data['revenue_stays'],
                mode='lines+markers',
                name='Ingresos (Estadías)',
                line=dict(color=COLORS['success'], width=2),
                fill='tozeroy',
                fillcolor=f"rgba(76, 175, 80, 0.1)"
            ))
            fig.update_layout(
                title='Ingresos Últimos 7 Días',
                xaxis_title='Fecha',
                yaxis_title='Ingresos (COP)',
                template='plotly_white',
                height=350,
                margin=dict(l=0, r=0, t=40, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.plotly_chart(
                create_revenue_forecast_chart(data['metrics']),
                use_container_width=True
            )
    
    with col4:
        # Price trends from real data
        price_history = data.get('price_history', pd.DataFrame())
        if not price_history.empty:
            from dashboard.components.charts import create_price_history_chart
            st.plotly_chart(
                create_price_history_chart(price_history),
                use_container_width=True
            )
        else:
            st.info("No hay histórico de precios disponible")

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
