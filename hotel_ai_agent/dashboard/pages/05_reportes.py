"""
REPORTS PAGE - Generate and Download Reports
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.data.mock_data import get_mock_data
from dashboard.services.analytics_service import AnalyticsService
from dashboard.services.ai_insights import get_ai_service
from dashboard.services.dashboard_db import get_dashboard_db
from dashboard.utils.logger import dashboard_logger

st.title("📑 Generación de Reportes")
st.markdown("---")


def _to_dataframe(value) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value
    if isinstance(value, list):
        return pd.DataFrame(value)
    if isinstance(value, dict):
        return pd.DataFrame([value])
    return pd.DataFrame()

# Tab structure
tab1, tab2, tab3 = st.tabs(["Reportes Listos", "Análisis IA Detallado", "Exportar Datos"])

with tab1:
    st.subheader("Reportes Disponibles")
    
    @st.cache_data(ttl=300)
    def load_report_data():
        try:
            db = get_dashboard_db()
            
            if db.is_available():
                occupancy = db.get_daily_occupancy_summary()
                if occupancy.empty:
                    occupancy = _to_dataframe(get_mock_data('daily_summary'))
            else:
                occupancy = _to_dataframe(get_mock_data('daily_summary'))
            
            # Get real metrics
            revenue_7d = db.get_revenue_7d() if db.is_available() else {}
            adr = db.get_adr() if db.is_available() else 0
            revpar = db.get_revpar() if db.is_available() else 0
            competitor_snapshots = db.get_competitor_prices(days=7) if db.is_available() else pd.DataFrame()
            
            metrics = {
                'adr': adr or get_mock_data('revenue')['adr'],
                'revpar': revpar or get_mock_data('revenue')['revpar'],
                'revenue_7d': revenue_7d.get('total', 0) or get_mock_data('revenue')['revenue_7d'],
            }
            
            suggestions = _to_dataframe(get_mock_data('suggestions'))
            if not competitor_snapshots.empty:
                suggestions = suggestions.copy()
                suggestions['competitor_price'] = competitor_snapshots['nightly_price'].mean()
            
            return occupancy, metrics, suggestions
        except Exception as e:
            dashboard_logger.error(f"Error loading report data: {e}")
            return _to_dataframe(get_mock_data('daily_summary')), get_mock_data('revenue'), _to_dataframe(get_mock_data('suggestions'))
    
    occupancy_data, metrics, suggestions = load_report_data()
    
    if occupancy_data is not None and not occupancy_data.empty:
        # Report 1: Executive Summary
        with st.container():
            st.markdown("#### 📊 Reporte Ejecutivo (7 Días)")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"""
                **Resumen Operativo**
                - Período: Últimos 7 días
                - Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                - Estado: ✅ Disponible
                """)
            
            with col2:
                avg_occ = occupancy_data['occupancy_pct'].mean() if 'occupancy_pct' in occupancy_data.columns else 0
                st.markdown(f"""
                **Métricas Clave**
                - Ocupación Promedio: {avg_occ:.1f}%
                - ADR: ${metrics.get('adr', 0):,.0f}
                - RevPAR: ${metrics.get('revpar', 0):,.0f}
                - Ingresos 7d: ${metrics.get('revenue_7d', 0):,.0f}
                """)
            
            with col3:
                if st.download_button(
                    label="📥 Descargar",
                    data=f"Reporte Ejecutivo\n{datetime.now()}\nOcupación: {avg_occ:.1f}%",
                    file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    key="download_exec"
                ):
                    st.success("Reporte descargado")
        
        st.divider()
        
        # Report 2: Occupancy Analysis
        with st.container():
            st.markdown("#### 📈 Análisis de Ocupación")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                rooms_count = occupancy_data['room'].nunique() if 'room' in occupancy_data.columns else len(occupancy_data)
                st.markdown(f"""
                **Análisis Detallado**
                - Período: Últimos 7 días
                - Habitaciones: {rooms_count}
                - Total registros: {len(occupancy_data)}
                """)
            
            with col2:
                if 'occupancy_pct' in occupancy_data.columns:
                    max_occ = occupancy_data['occupancy_pct'].max()
                    min_occ = occupancy_data['occupancy_pct'].min()
                else:
                    max_occ = 0
                    min_occ = 0
                
                st.markdown(f"""
                **Estadísticas**
                - Máxima ocupación: {max_occ:.1f}%
                - Mínima ocupación: {min_occ:.1f}%
                - Variación: {(max_occ - min_occ):.1f}%
                """)
            
            with col3:
                if st.download_button(
                    label="📥 Descargar",
                    data=occupancy_data.to_csv(index=False),
                    file_name=f"occupancy_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_occ"
                ):
                    st.success("Reporte descargado")
        
        st.divider()
        
        # Report 3: Pricing Recommendations
        with st.container():
            st.markdown("#### 💡 Reporte de Recomendaciones de Precio")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"""
                **Análisis de Precios**
                - Total sugerencias: {len(suggestions)}
                - Cambios recomendados: {len(suggestions[suggestions['action'] != 'MAINTAIN'])}
                - Impacto promedio: {suggestions['change_pct'].mean():+.1f}%
                """)
            
            with col2:
                increases = len(suggestions[suggestions['action'] == 'INCREASE'])
                decreases = len(suggestions[suggestions['action'] == 'DECREASE'])
                st.markdown(f"""
                **Recomendaciones por Acción**
                - Aumentos: {increases}
                - Reducciones: {decreases}
                - Mantener: {len(suggestions) - increases - decreases}
                """)
            
            with col3:
                if st.download_button(
                    label="📥 Descargar",
                    data=suggestions.to_csv(index=False),
                    file_name=f"pricing_recommendations_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_prices"
                ):
                    st.success("Reporte descargado")

with tab2:
    st.subheader("Análisis Inteligente Detallado")
    
    ai_service = get_ai_service()
    
    # Load data
    occupancy_data, metrics, suggestions = load_report_data()
    
    if occupancy_data is not None and not occupancy_data.empty:
        # Calculate analytics
        avg_occ = occupancy_data['occupancy_pct'].mean() / 100 if len(occupancy_data) > 0 else 0
        competitor_data = _to_dataframe(get_mock_data('competitor'))
        db_competitor = get_dashboard_db().get_competitor_prices(days=7) if get_dashboard_db().is_available() else pd.DataFrame()
        if not db_competitor.empty:
            competitor_data = db_competitor.copy()
            competitor_data['competitor'] = competitor_data['source'].astype(str).str.title()
            competitor_data['platform'] = competitor_data['source'].astype(str).str.title()
        comp_avg_price = competitor_data['nightly_price'].mean() if not competitor_data.empty else 0
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Análisis de Ocupación")
            with st.spinner("Generando análisis..."):
                occupancy_insight = ai_service.generate_occupancy_insight(
                    occupancy=avg_occ,
                    trend=0.05,
                    forecast_days=7
                )
                st.markdown(occupancy_insight)
        
        with col2:
            st.markdown("#### 💰 Análisis de Precios")
            if not suggestions.empty:
                first_room = suggestions.iloc[0]
                with st.spinner("Generando análisis..."):
                    pricing_insight = ai_service.generate_pricing_insight(
                        current_price=first_room['current_price'],
                        suggested_price=first_room['suggested_price'],
                        competitor_price=comp_avg_price,
                        occupancy=first_room['occupancy_forecast'] / 100,
                        room_type=first_room['room_type']
                    )
                    st.markdown(pricing_insight)
        
        st.divider()
        
        st.markdown("#### 📈 Resumen Ejecutivo Global")
        with st.spinner("Generando resumen..."):
            executive_summary = ai_service.generate_executive_summary(
                metrics=metrics,
                opportunities=get_mock_data('alerts'),
                alerts=[]
            )
            st.markdown(executive_summary)
        
        # Download option
        if st.button("📥 Descargar Análisis IA como PDF"):
            st.info("Función de exportación PDF disponible pronto")

with tab3:
    st.subheader("Exportar Datos")
    
    # Select data to export
    st.markdown("#### Seleccionar Datos a Exportar")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_occupancy = st.checkbox("Datos de Ocupación", value=True)
        export_prices = st.checkbox("Precios Actuales", value=True)
        export_suggestions = st.checkbox("Sugerencias IA", value=True)
    
    with col2:
        export_competitor = st.checkbox("Datos de Competencia", value=True)
        export_demographics = st.checkbox("Demografía de Huéspedes", value=True)
        export_history = st.checkbox("Historial de Precios", value=False)
    
    format_option = st.radio("Formato de Exportación", ["CSV", "JSON", "Excel"], horizontal=True)
    
    st.markdown("---")
    
    # Generate export
    if st.button("📦 Generar Paquete de Exportación"):
        export_data = {}
        
        try:
            if export_occupancy:
                export_data['occupancy'] = _to_dataframe(get_mock_data('daily_summary')).to_dict('records')
            
            if export_prices:
                export_data['prices'] = _to_dataframe(get_mock_data('current_prices')).to_dict('records')
            
            if export_suggestions:
                export_data['suggestions'] = _to_dataframe(get_mock_data('suggestions')).to_dict('records')
            
            if export_competitor:
                export_data['competitor'] = _to_dataframe(get_mock_data('competitor')).to_dict('records')
            
            if export_demographics:
                export_data['demographics'] = get_mock_data('demographics')
            
            if format_option == "JSON":
                json_data = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    label="📥 Descargar JSON",
                    data=json_data,
                    file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )
            
            elif format_option == "CSV":
                st.info("Exportación CSV disponible para cada sección por separado")
                
                for key, data in export_data.items():
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                        st.download_button(
                            label=f"📥 Descargar {key.upper()}",
                            data=df.to_csv(index=False),
                            file_name=f"{key}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
            
            elif format_option == "Excel":
                st.info("Función Excel disponible con opción de descarga JSON como alternativa")
            
            st.success("✅ Exportación generada correctamente")
        
        except Exception as e:
            st.error(f"Error generando exportación: {e}")
            dashboard_logger.error(f"Export error: {e}")
