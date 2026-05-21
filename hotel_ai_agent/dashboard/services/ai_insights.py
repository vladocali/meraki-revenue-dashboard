# AI Insights Service with OpenAI
import json
import asyncio
from typing import Optional, Dict
from dashboard.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TIMEOUT
from dashboard.utils.logger import dashboard_logger

class AIInsightsService:
    """Service for generating AI insights using OpenAI."""
    
    def __init__(self):
        """Initialize AI service."""
        self.api_key = OPENAI_API_KEY
        self.model = OPENAI_MODEL
        self.available = bool(self.api_key)
        
        if self.available:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                dashboard_logger.info("OpenAI client initialized")
            except ImportError:
                self.available = False
                dashboard_logger.warning("OpenAI library not installed. AI insights disabled.")
            except Exception as e:
                self.available = False
                dashboard_logger.error(f"Failed to initialize OpenAI: {e}")
        else:
            dashboard_logger.warning("OPENAI_API_KEY not set. AI insights will use local analysis.")
    
    def generate_occupancy_insight(self, occupancy: float, trend: float, 
                                   forecast_days: int = 7) -> str:
        """Generate insight about occupancy."""
        
        if not self.available:
            return self._local_occupancy_insight(occupancy, trend, forecast_days)
        
        try:
            prompt = f"""
            Como experto en Revenue Management hotelero, analiza esta ocupación:
            
            - Ocupación actual: {occupancy*100:.1f}%
            - Tendencia (últimos días): {trend:+.1f}%
            - Horizonte de análisis: {forecast_days} días
            
            Proporciona un análisis breve (máx 200 palabras) que incluya:
            1. Evaluación del nivel de ocupación
            2. Indicadores de la tendencia
            3. Recomendación de estrategia de precios
            4. Riesgos potenciales
            
            Sé directo, profesional y actionable.
            """
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=OPENAI_TIMEOUT
            )
            
            insight = response.content[0].text
            dashboard_logger.info("Generated occupancy insight with AI")
            return insight
        
        except Exception as e:
            dashboard_logger.error(f"Error generating AI occupancy insight: {e}")
            return self._local_occupancy_insight(occupancy, trend, forecast_days)
    
    def generate_pricing_insight(self, current_price: float, suggested_price: float,
                                competitor_price: float, occupancy: float,
                                room_type: str) -> str:
        """Generate insight about pricing strategy."""
        
        if not self.available:
            return self._local_pricing_insight(current_price, suggested_price, 
                                              competitor_price, occupancy, room_type)
        
        try:
            price_change_pct = ((suggested_price - current_price) / current_price * 100) if current_price > 0 else 0
            
            prompt = f"""
            Como especialista en estrategia de precios de alojamiento, evalúa esta situación:
            
            HABITACIÓN: {room_type}
            - Precio actual: ${current_price:,.0f}
            - Precio sugerido: ${suggested_price:,.0f}
            - Cambio: {price_change_pct:+.1f}%
            - Ocupación actual: {occupancy*100:.1f}%
            - Competencia promedio: ${competitor_price:,.0f}
            
            Genera un análisis breve (máx 200 palabras) que incluya:
            1. Justificación del cambio propuesto
            2. Impacto potencial en demanda
            3. Posicionamiento vs competencia
            4. Riesgos y oportunidades
            5. Próximas acciones recomendadas
            
            Sé específico, datos-driven y profesional.
            """
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=OPENAI_TIMEOUT
            )
            
            insight = response.content[0].text
            dashboard_logger.info(f"Generated pricing insight for {room_type}")
            return insight
        
        except Exception as e:
            dashboard_logger.error(f"Error generating AI pricing insight: {e}")
            return self._local_pricing_insight(current_price, suggested_price, 
                                              competitor_price, occupancy, room_type)
    
    def generate_executive_summary(self, metrics: Dict, opportunities: list,
                                  alerts: list) -> str:
        """Generate executive summary."""
        
        if not self.available:
            return self._local_executive_summary(metrics, opportunities, alerts)
        
        try:
            # Prepare data for prompt
            metrics_json = json.dumps(metrics, indent=2, default=str)
            opportunities_text = "\n".join([f"- {o.get('title')}: {o.get('description')}" 
                                          for o in opportunities[:3]])
            alerts_text = "\n".join([f"- {a.get('title')}: {a.get('message')}" 
                                   for a in alerts[:3]])
            
            prompt = f"""
            Como Director de Revenue Management de un hotel, prepara un resumen ejecutivo conciso y profesional:
            
            MÉTRICAS ACTUALES:
            {metrics_json}
            
            OPORTUNIDADES IDENTIFICADAS:
            {opportunities_text or "Ninguna"}
            
            ALERTAS DEL SISTEMA:
            {alerts_text or "Ninguna"}
            
            Genera un resumen de máx 300 palabras que:
            1. Evalúe la situación actual
            2. Destaque los hallazgos principales
            3. Recomiende acciones inmediatas
            4. Proyecte el impacto esperado
            
            Usa lenguaje profesional, directo y accionable. Incluye solo datos relevantes.
            """
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=OPENAI_TIMEOUT
            )
            
            summary = response.content[0].text
            dashboard_logger.info("Generated executive summary with AI")
            return summary
        
        except Exception as e:
            dashboard_logger.error(f"Error generating AI executive summary: {e}")
            return self._local_executive_summary(metrics, opportunities, alerts)
    
    def _local_occupancy_insight(self, occupancy: float, trend: float, 
                                forecast_days: int) -> str:
        """Local fallback for occupancy insight."""
        status = "EXCELENTE" if occupancy > 0.85 else "BUENA" if occupancy > 0.70 else "MEDIA" if occupancy > 0.50 else "BAJA"
        trend_desc = "mejorando" if trend > 0 else "deteriorándose" if trend < 0 else "estable"
        
        return f"""
        **Análisis de Ocupación**
        
        Tu ocupación actual es **{occupancy*100:.1f}%** - nivel **{status}**.
        
        La tendencia está **{trend_desc}** (+{trend:.1f}% en últimos días).
        
        **Recomendación:** 
        {"Sube precios agresivamente para capitalizar demanda fuerte." if occupancy > 0.80 
         else "Mantén precios competitivos o baja ligeramente para atraer más reservas." if occupancy < 0.60
         else "Precios equilibrados, monitorea y ajusta según demanda."}
        
        Próximos {forecast_days} días: Continúa monitoreando ocupación diaria para identificar patrones.
        """
    
    def _local_pricing_insight(self, current_price: float, suggested_price: float,
                              competitor_price: float, occupancy: float,
                              room_type: str) -> str:
        """Local fallback for pricing insight."""
        change_pct = ((suggested_price - current_price) / current_price * 100) if current_price > 0 else 0
        relative_to_comp = ((suggested_price - competitor_price) / competitor_price * 100) if competitor_price > 0 else 0
        
        action = "SUBE" if change_pct > 0 else "BAJA" if change_pct < 0 else "MANTÉN"
        comp_pos = "SOBRE competencia" if relative_to_comp > 0 else "BAJO competencia" if relative_to_comp < 0 else "EN línea"
        
        return f"""
        **Estrategia de Pricing - {room_type}**
        
        Cambio recomendado: **{action}** {abs(change_pct):.1f}%
        (de ${current_price:,.0f} a ${suggested_price:,.0f})
        
        Posición: **{comp_pos}** (diferencia: {relative_to_comp:+.1f}%)
        
        Ocupación actual: {occupancy*100:.1f}% - {'Fuerte demanda' if occupancy > 0.75 else 'Demanda moderada' if occupancy > 0.50 else 'Bajo interés'}
        
        **Justificación:** {'Demanda fuerte y precios bajos - oportunidad de rentabilidad' if change_pct > 0 and occupancy > 0.7
                           else 'Ocupación baja - necesario mejorar competitividad' if change_pct < 0 and occupancy < 0.6
                           else 'Mantener equilibrio entre ocupación y precio'}.
        
        Monitorea impacto en reservas para próxi mos 3 días.
        """
    
    def _local_executive_summary(self, metrics: Dict, opportunities: list,
                                alerts: list) -> str:
        """Local fallback for executive summary."""
        occ = metrics.get('occupancy', 0)
        adr = metrics.get('adr', 0)
        revpar = metrics.get('revpar', 0)
        
        summary = f"""
        **📊 RESUMEN EJECUTIVO - REVENUE MANAGEMENT**
        
        **SITUACIÓN ACTUAL**
        - Ocupación: {occ*100:.1f}%
        - ADR (Tarifa Promedio): ${adr:,.0f}
        - RevPAR: ${revpar:,.0f}
        
        **HALLAZGOS PRINCIPALES**
        {f"✓ {len(opportunities)} oportunidades identificadas" if opportunities else ""}
        {f"⚠️ {len(alerts)} alertas activas" if alerts else ""}
        
        **OPORTUNIDADES**
        {"" + chr(10).join([f"• {o.get('title')}" for o in opportunities[:3]]) if opportunities else "• Ninguna crítica en este momento"}
        
        **ACCIONES RECOMENDADAS**
        {"1. Aumentar precios ante fuerte demanda" if occ > 0.80 
         else "1. Implementar estrategia de descuentos para impulsar ocupación" if occ < 0.50
         else "1. Mantener vigilancia activa sobre ocupación"}
        2. Monitorear precios de competencia diariamente
        3. Validar cambios recomendados antes de ejecutar
        
        Próxima revisión: Mañana a las 02:00 AM
        """
        
        return summary.strip()

# Singleton instance
_ai_service = None

def get_ai_service() -> AIInsightsService:
    """Get or create AI insights service."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIInsightsService()
    return _ai_service
