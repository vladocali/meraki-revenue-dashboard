"""
PRICING PAGE - Price Analysis and Approval
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.config import COLORS
from dashboard.components.charts import create_price_comparison_chart, create_suggestion_impact_chart
from dashboard.data.mock_data import get_mock_data
from dashboard.services.dashboard_db import get_dashboard_db
from dashboard.utils.formatters import format_currency, format_percentage
from dashboard.utils.logger import dashboard_logger

st.title("💰 Gestión de Precios")
st.markdown("---")


def _to_dataframe(value) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value
    if isinstance(value, list):
        return pd.DataFrame(value)
    if isinstance(value, dict):
        return pd.DataFrame([value])
    return pd.DataFrame()

# Tabs
tab1, tab2, tab3 = st.tabs(["Precios Actual", "Sugerencias IA", "Historial"])

with tab1:
    st.subheader("Precios Actuales por Habitación")
    
    @st.cache_data(ttl=300)
    def load_current_prices():
        try:
            db = get_dashboard_db()
            if db.is_available():
                prices = db.get_current_room_prices()
                if not prices.empty:
                    # Format for display
                    prices = prices.rename(columns={
                        'room': 'room',
                        'room_type': 'room_type',
                        'current_price': 'current_price',
                        'min_price': 'base_price',
                        'last_booking': 'last_updated',
                    })
                    prices['price_change_pct'] = 0  # Not calculated yet
                    return prices
            
            # Fallback to mock
            return _to_dataframe(get_mock_data('current_prices'))
        except Exception as e:
            dashboard_logger.error(f"Error loading current prices: {e}")
            return _to_dataframe(get_mock_data('current_prices'))
    
    current_prices = load_current_prices()
    
    if current_prices is not None and not current_prices.empty:
        # Display chart
        st.plotly_chart(create_price_comparison_chart(current_prices), use_container_width=True)
        
        st.markdown("---")
        
        # Table
        display_df = current_prices.copy()
        if 'current_price' in display_df.columns:
            display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:,.0f}" if x and x > 0 else "N/A")
        if 'base_price' in display_df.columns or 'min_price' in display_df.columns:
            col_name = 'base_price' if 'base_price' in display_df.columns else 'min_price'
            display_df[col_name] = display_df[col_name].apply(lambda x: f"${x:,.0f}" if x and x > 0 else "N/A")
        if 'price_change_pct' in display_df.columns:
            display_df['price_change_pct'] = display_df['price_change_pct'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
        
        cols = [c for c in ['room', 'room_type', 'base_price', 'current_price', 'price_change_pct', 'last_updated'] if c in display_df.columns]
        display_df = display_df[cols]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No hay datos de precios disponibles")

with tab2:
    st.subheader("Sugerencias de Precio (IA)")
    
    @st.cache_data(ttl=300)
    def load_suggestions():
        try:
            db = get_dashboard_db()
            if db.is_available():
                # Generate basic suggestions from current prices
                prices = db.get_current_room_prices()
                if not prices.empty:
                    suggestions = []
                    for idx, room in prices.iterrows():
                        suggestions.append({
                            'room': room.get('room', 'Unknown'),
                            'room_type': room.get('room_type', 'Unknown'),
                            'current_price': room.get('current_price', 0),
                            'suggested_price': room.get('current_price', 0),
                            'change_pct': 0,
                            'action': 'MAINTAIN',
                            'reason': 'Precios estables basados en ocupación actual',
                            'occupancy_forecast': 0.5,
                            'estimated_impact': 0,
                        })
                    return pd.DataFrame(suggestions)
            
            # Fallback to mock
            return _to_dataframe(get_mock_data('suggestions'))
        except Exception as e:
            dashboard_logger.error(f"Error loading suggestions: {e}")
            return _to_dataframe(get_mock_data('suggestions'))
    
    suggestions = load_suggestions()
    
    if suggestions is not None and not suggestions.empty:
        # Display impact chart
        st.plotly_chart(create_suggestion_impact_chart(suggestions), use_container_width=True)
        
        st.markdown("---")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sugerencias", len(suggestions))
        
        with col2:
            if 'action' in suggestions.columns:
                increases = len(suggestions[suggestions['action'] == 'INCREASE'])
                st.metric("Aumentos Recomendados", increases, delta=f"+{increases}" if increases > 0 else "")
            else:
                st.metric("Aumentos Recomendados", 0)
        
        with col3:
            if 'action' in suggestions.columns:
                decreases = len(suggestions[suggestions['action'] == 'DECREASE'])
                st.metric("Reducciones Recomendadas", decreases, delta=f"-{decreases}" if decreases > 0 else "")
            else:
                st.metric("Reducciones Recomendadas", 0)
        
        with col4:
            if 'change_pct' in suggestions.columns:
                avg_impact = suggestions['change_pct'].mean()
                st.metric("Impacto Promedio", f"{avg_impact:+.1f}%")
            else:
                st.metric("Impacto Promedio", "0.0%")
        
        st.markdown("---")
        
        # Suggestions table with approval buttons
        st.subheader("Revisar y Aprobar Sugerencias")
        
        for idx, row in suggestions.iterrows():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create container for suggestion
                with st.container():
                    st.markdown(f"""
                    **{row['room']}** ({row['room_type']})
                    
                    Acción: **{row['action']}** | Ocupación: {row['occupancy_forecast']:.1f}%
                    
                    ${row['current_price']:,.0f} → ${row['suggested_price']:,.0f} ({row['change_pct']:+.1f}%)
                    
                    **Razón:** {row['reason']}
                    """)
            
            with col2:
                button_cols = st.columns(2)
                with button_cols[0]:
                    if st.button("✅", key=f"approve_{idx}", help="Aprobar"):
                        st.success("Sugerencia aprobada (simulada)")
                        dashboard_logger.info(f"Price change approved for {row['room']}")
                
                with button_cols[1]:
                    if st.button("❌", key=f"reject_{idx}", help="Rechazar"):
                        st.info("Sugerencia rechazada")
                        dashboard_logger.info(f"Price change rejected for {row['room']}")
            
            st.divider()
    
    else:
        st.info("No hay sugerencias disponibles")

with tab3:
    st.subheader("Histórico de Precios")
    
    # Select room
    @st.cache_data(ttl=300)
    def load_rooms():
        try:
            current_prices = _to_dataframe(get_mock_data('current_prices'))
            return current_prices['room'].tolist()
        except:
            return []
    
    rooms = load_rooms()
    selected_room = st.selectbox("Seleccionar Habitación", rooms, index=0 if rooms else None)
    
    if selected_room:
        @st.cache_data(ttl=300)
        def load_price_history(room):
            try:
                history = _to_dataframe(get_mock_data('price_history'))
                return history[history['room'] == room] if isinstance(history, pd.DataFrame) else None
            except:
                return None
        
        history = load_price_history(selected_room)
        
        if history is not None and not history.empty:
            from dashboard.components.charts import create_price_history_chart
            st.plotly_chart(create_price_history_chart(history), use_container_width=True)
            
            st.markdown("---")
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_price = history['price'].mean()
                st.metric("Precio Promedio", f"${avg_price:,.0f}")
            
            with col2:
                max_price = history['price'].max()
                st.metric("Precio Máximo", f"${max_price:,.0f}")
            
            with col3:
                min_price = history['price'].min()
                st.metric("Precio Mínimo", f"${min_price:,.0f}")
            
            with col4:
                volatility = history['price'].std()
                st.metric("Volatilidad", f"${volatility:,.0f}")
        else:
            st.warning("No hay datos de historial para esta habitación")
