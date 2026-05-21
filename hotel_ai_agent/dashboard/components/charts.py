# Interactive Chart Components
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from dashboard.config import COLORS, CHART_CONFIG

def create_occupancy_line_chart(data: pd.DataFrame):
    """Create occupancy trend line chart."""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['occupancy_pct'],
        mode='lines+markers',
        name='Ocupación %',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor=f"{COLORS['primary']}30",
    ))
    
    fig.update_layout(
        title='Ocupación: Próximos 7 Días',
        xaxis_title='Fecha',
        yaxis_title='Ocupación (%)',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        **CHART_CONFIG,
    )
    
    fig.update_yaxes(range=[0, 100])
    
    return fig

def create_occupancy_bar_chart(data: pd.DataFrame):
    """Create occupancy comparison bar chart."""
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data['date'],
        y=data['free_rooms'],
        name='Habitaciones Libres',
        marker_color=COLORS['secondary'],
    ))
    
    fig.add_trace(go.Bar(
        x=data['date'],
        y=data['occupied'].astype(int),
        name='Ocupadas',
        marker_color=COLORS['success'],
    ))
    
    fig.update_layout(
        title='Disponibilidad por Día',
        xaxis_title='Fecha',
        yaxis_title='Habitaciones',
        barmode='stack',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        **CHART_CONFIG,
    )
    
    return fig

def create_price_comparison_chart(current_prices: pd.DataFrame):
    """Create current prices comparison chart."""
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=current_prices['room'],
        x=current_prices['current_price'],
        orientation='h',
        marker=dict(
            color=current_prices['price_change_pct'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Cambio %")
        ),
        text=current_prices['current_price'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Precios Actuales por Habitación',
        xaxis_title='Precio (COP)',
        yaxis_title='',
        hovermode='y unified',
        template='plotly_white',
        height=350,
        margin=dict(l=150, r=0, t=40, b=0),
        **CHART_CONFIG,
    )
    
    return fig

def create_revenue_forecast_chart(data: dict):
    """Create revenue forecast chart."""
    
    dates = []
    revenues = []
    targets = []
    
    for i in range(7):
        date_str = f"Día {i+1}"
        dates.append(date_str)
        
        # Simulate daily revenue
        base_revenue = data['revenue_7d'] / 7
        revenue = base_revenue + np.random.randint(-50000, 150000)
        revenues.append(revenue)
        
        # Target line
        target = base_revenue
        targets.append(target)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=revenues,
        mode='lines+markers',
        name='Ingresos Reales',
        line=dict(color=COLORS['success'], width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor=f"{COLORS['success']}20",
    ))
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=targets,
        mode='lines',
        name='Objetivo',
        line=dict(color=COLORS['warning'], width=2, dash='dash'),
    ))
    
    fig.update_layout(
        title='Ingresos Proyectados vs Objetivo',
        xaxis_title='Período',
        yaxis_title='Ingresos (COP)',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        **CHART_CONFIG,
    )
    
    return fig

def create_competitor_comparison_chart(competitor_data: pd.DataFrame, my_price: float):
    """Create competitor price comparison."""
    
    # Get latest prices per competitor
    latest = competitor_data.groupby('competitor').agg({
        'nightly_price': 'mean'
    }).reset_index()
    
    # Add our price
    latest = pd.concat([
        latest,
        pd.DataFrame([{'competitor': 'Nuestro Precio', 'nightly_price': my_price}])
    ])
    
    # Determine colors
    colors = [COLORS['primary'] if comp == 'Nuestro Precio' else COLORS['secondary'] 
              for comp in latest['competitor']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=latest['competitor'],
        x=latest['nightly_price'],
        orientation='h',
        marker=dict(color=colors),
        text=latest['nightly_price'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Comparativa de Precios con Competencia',
        xaxis_title='Precio Noche (COP)',
        yaxis_title='',
        hovermode='y unified',
        template='plotly_white',
        height=400,
        margin=dict(l=150, r=0, t=40, b=0),
        **CHART_CONFIG,
    )
    
    return fig

def create_price_history_chart(history: pd.DataFrame):
    """Create price history line chart."""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=history['date'],
        y=history['price'],
        mode='lines+markers',
        name='Precio Histórico',
        line=dict(color=COLORS['accent'], width=2),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor=f"{COLORS['accent']}20",
    ))
    
    # Add average line
    avg_price = history['price'].mean()
    fig.add_hline(y=avg_price, line_dash="dash", line_color=COLORS['warning'],
                  annotation_text="Promedio", annotation_position="right")
    
    fig.update_layout(
        title='Historico de Precios (30 días)',
        xaxis_title='Fecha',
        yaxis_title='Precio (COP)',
        hovermode='x unified',
        template='plotly_white',
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        **CHART_CONFIG,
    )
    
    return fig

def create_occupancy_heatmap(occupancy_data: pd.DataFrame):
    """Create occupancy heatmap for rooms."""
    
    # Pivot data for heatmap
    pivot_data = occupancy_data.pivot_table(
        values='occupancy_pct',
        index='room',
        columns='date',
        aggfunc='first'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='RdYlGn',
        text=pivot_data.values,
        texttemplate='%{text:.0f}%',
        textfont={"size": 10},
        colorbar=dict(title="Ocupación %")
    ))
    
    fig.update_layout(
        title='Mapa de Ocupación por Habitación (7 días)',
        xaxis_title='Fecha',
        yaxis_title='Habitación',
        height=400,
        margin=dict(l=150, r=0, t=40, b=0),
        **CHART_CONFIG,
    )
    
    return fig

def create_revenue_breakdown_pie(demographics: dict):
    """Create revenue breakdown pie chart."""
    
    labels = list(demographics['sources'].keys())
    values = list(demographics['sources'].values())
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(
            colors=[COLORS['primary'], COLORS['secondary'], COLORS['accent']]
        ),
        textposition='auto',
        hoverinfo='label+percent+value'
    )])
    
    fig.update_layout(
        title='Ingresos por Fuente (7 días)',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        **CHART_CONFIG,
    )
    
    return fig

def create_adr_trend_chart(metric_history: list):
    """Create ADR (Average Daily Rate) trend chart."""
    
    dates = [f"Día {i+1}" for i in range(len(metric_history))]
    adrs = [m.get('adr', 0) for m in metric_history]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=adrs,
        mode='lines+markers+text',
        name='ADR',
        line=dict(color=COLORS['secondary'], width=3),
        marker=dict(size=10),
        text=adrs,
        textposition='top center',
        fill='tozeroy',
        fillcolor=f"{COLORS['secondary']}20",
    ))
    
    fig.update_layout(
        title='Tarifa Diaria Promedio (ADR)',
        xaxis_title='Período',
        yaxis_title='ADR (COP)',
        hovermode='x unified',
        template='plotly_white',
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        **CHART_CONFIG,
    )
    
    return fig

def create_suggestion_impact_chart(suggestions: pd.DataFrame):
    """Create chart showing estimated impact of suggestions."""
    
    # Only show top 5 by impact
    top_suggestions = suggestions.nlargest(5, 'estimated_impact')
    
    colors = [COLORS['success'] if x > 0 else COLORS['danger'] 
              for x in top_suggestions['estimated_impact']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_suggestions['room'],
        x=top_suggestions['estimated_impact'],
        orientation='h',
        marker=dict(color=colors),
        text=top_suggestions['estimated_impact'].apply(lambda x: f"{x:+.1f}%"),
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Impacto Estimado de Sugerencias (Top 5)',
        xaxis_title='Impacto Potencial (%)',
        yaxis_title='',
        hovermode='y unified',
        template='plotly_white',
        height=350,
        margin=dict(l=150, r=0, t=40, b=0),
        **CHART_CONFIG,
    )
    
    return fig
