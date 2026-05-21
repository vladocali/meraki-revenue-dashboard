# Analytics Service for Dashboard
import pandas as pd
from datetime import datetime, timedelta
from dashboard.utils.logger import dashboard_logger
from dashboard.data.mock_data import get_mock_data

class AnalyticsService:
    """Analytics and metrics calculation service."""
    
    @staticmethod
    def calculate_revenue_metrics(occupancy: float, adr: float, rooms: int) -> dict:
        """Calculate revenue metrics."""
        try:
            revpar = adr * occupancy
            potential_revenue_day = adr * rooms
            actual_revenue_day = revpar * rooms
            lost_revenue = (potential_revenue_day - actual_revenue_day)
            
            return {
                'revpar': int(revpar),
                'potential_revenue_day': int(potential_revenue_day),
                'actual_revenue_day': int(actual_revenue_day),
                'lost_revenue': int(lost_revenue),
                'occupancy': occupancy,
                'adr': int(adr),
            }
        except Exception as e:
            dashboard_logger.error(f"Error calculating revenue metrics: {e}")
            return {}
    
    @staticmethod
    def calculate_occupancy_trend(occupancy_data: pd.DataFrame) -> dict:
        """Calculate occupancy trend."""
        try:
            if occupancy_data.empty:
                return {}
            
            trend_data = occupancy_data.sort_values('date')
            current_occ = trend_data.iloc[-1]['occupancy_pct'] / 100 if len(trend_data) > 0 else 0
            
            # Calculate average
            avg_occ = trend_data['occupancy_pct'].mean() / 100 if len(trend_data) > 0 else 0
            
            # Calculate trend
            if len(trend_data) >= 2:
                first_half_avg = trend_data.iloc[:len(trend_data)//2]['occupancy_pct'].mean()
                second_half_avg = trend_data.iloc[len(trend_data)//2:]['occupancy_pct'].mean()
                trend = second_half_avg - first_half_avg
            else:
                trend = 0
            
            return {
                'current_occupancy': current_occ,
                'average_occupancy': avg_occ,
                'trend': trend,
                'trend_direction': 'up' if trend > 0 else 'down' if trend < 0 else 'stable',
            }
        except Exception as e:
            dashboard_logger.error(f"Error calculating occupancy trend: {e}")
            return {}
    
    @staticmethod
    def analyze_price_suggestions(suggestions: pd.DataFrame) -> dict:
        """Analyze price suggestions."""
        try:
            if suggestions.empty:
                return {}
            
            total_suggestions = len(suggestions)
            increases = len(suggestions[suggestions['action'] == 'INCREASE'])
            decreases = len(suggestions[suggestions['action'] == 'DECREASE'])
            maintains = len(suggestions[suggestions['action'] == 'MAINTAIN'])
            
            avg_impact = suggestions['change_pct'].mean() if 'change_pct' in suggestions.columns else 0
            
            return {
                'total_suggestions': total_suggestions,
                'increases': increases,
                'decreases': decreases,
                'maintains': maintains,
                'average_impact_pct': avg_impact,
                'highest_impact': suggestions['change_pct'].max() if 'change_pct' in suggestions.columns else 0,
            }
        except Exception as e:
            dashboard_logger.error(f"Error analyzing suggestions: {e}")
            return {}
    
    @staticmethod
    def compare_with_competitor(my_price: float, competitor_data: pd.DataFrame) -> dict:
        """Compare prices with competitors."""
        try:
            if competitor_data.empty:
                return {}
            
            avg_competitor_price = competitor_data['nightly_price'].mean()
            min_competitor_price = competitor_data['nightly_price'].min()
            max_competitor_price = competitor_data['nightly_price'].max()
            
            price_diff = my_price - avg_competitor_price
            price_diff_pct = (price_diff / avg_competitor_price * 100) if avg_competitor_price > 0 else 0
            
            position = "SOBRE"
            if price_diff < 0:
                position = "BAJO"
            
            return {
                'my_price': my_price,
                'avg_competitor_price': int(avg_competitor_price),
                'min_competitor_price': int(min_competitor_price),
                'max_competitor_price': int(max_competitor_price),
                'price_difference': int(price_diff),
                'price_difference_pct': price_diff_pct,
                'position': position,
            }
        except Exception as e:
            dashboard_logger.error(f"Error comparing with competitors: {e}")
            return {}
    
    @staticmethod
    def identify_opportunities(occupancy: float, adr: float, competitor_data: dict) -> list:
        """Identify revenue opportunities."""
        opportunities = []
        
        try:
            # Occupancy opportunity
            if occupancy < 0.50:
                opportunities.append({
                    'type': 'OCCUPANCY',
                    'title': 'Baja ocupación detectada',
                    'description': f'Ocupación actual {occupancy*100:.0f}%. Considere estrategia de precios agresiva.',
                    'severity': 'HIGH',
                    'icon': '📉'
                })
            elif occupancy > 0.85:
                opportunities.append({
                    'type': 'PRICING',
                    'title': 'Oportunidad de incremento de precios',
                    'description': f'Ocupación {occupancy*100:.0f}%. Demanda fuerte sugiere subir tarifas.',
                    'severity': 'INFO',
                    'icon': '📈'
                })
            
            # Competitor opportunity
            if competitor_data.get('position') == 'BAJO':
                diff = abs(competitor_data.get('price_difference_pct', 0))
                opportunities.append({
                    'type': 'COMPETITOR',
                    'title': f'Precios {diff:.1f}% bajo competencia',
                    'description': 'Oportunidad para aumentar tarifa sin perder competitividad.',
                    'severity': 'INFO',
                    'icon': '💰'
                })
            
        except Exception as e:
            dashboard_logger.error(f"Error identifying opportunities: {e}")
        
        return opportunities
    
    @staticmethod
    def get_kpi_summary(occupancy: float, adr: float, rooms: int, revenue_7d: float) -> dict:
        """Get summary of all KPIs."""
        try:
            metrics = AnalyticsService.calculate_revenue_metrics(occupancy, adr, rooms)
            
            return {
                'occupancy': occupancy,
                'adr': int(adr),
                'revpar': metrics.get('revpar', 0),
                'rooms': rooms,
                'revenue_7d': int(revenue_7d),
                'daily_potential': metrics.get('potential_revenue_day', 0),
                'daily_actual': metrics.get('actual_revenue_day', 0),
                'lost_revenue_daily': metrics.get('lost_revenue', 0),
            }
        except Exception as e:
            dashboard_logger.error(f"Error getting KPI summary: {e}")
            return {}
