# Dashboard Database Service
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from sqlalchemy import create_string_from_text
from dashboard.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from dashboard.utils.logger import dashboard_logger
from tools.db_tools import Database

class DashboardDatabase:
    """Database service for dashboard."""
    
    def __init__(self):
        """Initialize database connection."""
        try:
            connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            self.db = Database(connection_string)
            dashboard_logger.info("Dashboard database connected successfully")
        except Exception as e:
            dashboard_logger.error(f"Failed to connect to database: {e}")
            self.db = None
    
    def get_7day_occupancy(self) -> pd.DataFrame:
        """Get 7-day occupancy forecast from database."""
        try:
            query = """
            SELECT 
                DATE(d.CheckIn) as date,
                COUNT(DISTINCT h.id_habitacion) as total_rooms,
                COUNT(DISTINCT d.Habitacion) as occupied_rooms,
                ROUND(COUNT(DISTINCT d.Habitacion) / COUNT(DISTINCT h.id_habitacion) * 100, 2) as occupancy_pct
            FROM habitaciones h
            LEFT JOIN datos d ON h.id_habitacion = d.Habitacion 
                AND d.CheckIn <= CURDATE() + INTERVAL 7 DAY
                AND d.CheckOut > CURDATE()
            WHERE h.activa = 1
            GROUP BY DATE(d.CheckIn)
            ORDER BY date
            """
            
            result = self.db.execute_query(query)
            dashboard_logger.info(f"Retrieved 7-day occupancy data: {len(result)} rows")
            return result
        
        except Exception as e:
            dashboard_logger.error(f"Error fetching 7-day occupancy: {e}")
            return pd.DataFrame()
    
    def get_current_room_prices(self) -> pd.DataFrame:
        """Get current room prices from parametros table."""
        try:
            query = """
            SELECT 
                par.parametro as room_param,
                par.valor as price_value,
                h.nombre as room_name,
                h.id_habitacion as room_id
            FROM parametros par
            LEFT JOIN habitaciones h ON CAST(REPLACE(par.parametro, 'CotizacionHab', '') as DECIMAL) = h.id_habitacion
            WHERE par.parametro LIKE 'CotizacionHab%'
            AND h.activa = 1
            """
            
            result = self.db.execute_query(query)
            dashboard_logger.info(f"Retrieved current prices: {len(result)} rooms")
            return result
        
        except Exception as e:
            dashboard_logger.error(f"Error fetching current prices: {e}")
            return pd.DataFrame()
    
    def get_revenue_recommendations(self, limit: int = 100) -> pd.DataFrame:
        """Get AI revenue recommendations."""
        try:
            query = f"""
            SELECT 
                id,
                room_name,
                target_date,
                action,
                suggested_price,
                reason,
                occupancy_pct,
                status,
                created_at
            FROM revenue_recommendations
            ORDER BY created_at DESC
            LIMIT {limit}
            """
            
            result = self.db.execute_query(query)
            dashboard_logger.info(f"Retrieved revenue recommendations: {len(result)} records")
            return result
        
        except Exception as e:
            dashboard_logger.error(f"Error fetching revenue recommendations: {e}")
            return pd.DataFrame()
    
    def get_competitor_prices(self, days: int = 7) -> pd.DataFrame:
        """Get competitor price snapshots."""
        try:
            query = f"""
            SELECT 
                source,
                nightly_price,
                captured_at,
                room_type
            FROM competitor_price_snapshots
            WHERE captured_at >= DATE_SUB(NOW(), INTERVAL {days} DAY)
            ORDER BY captured_at DESC
            """
            
            result = self.db.execute_query(query)
            dashboard_logger.info(f"Retrieved competitor prices: {len(result)} records")
            return result
        
        except Exception as e:
            dashboard_logger.error(f"Error fetching competitor prices: {e}")
            return pd.DataFrame()
    
    def get_booking_statistics(self, days: int = 30) -> dict:
        """Get booking statistics."""
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_bookings,
                COUNT(DISTINCT Huesped) as unique_guests,
                AVG(DATEDIFF(CheckOut, CheckIn)) as avg_stay_nights,
                SUM(Valor) as total_revenue
            FROM datos
            WHERE CheckIn >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
            AND EstadoOperacion NOT IN ('Cancelada', 'No show')
            """
            
            result = self.db.execute_query(query)
            if not result.empty:
                dashboard_logger.info("Retrieved booking statistics")
                return result.iloc[0].to_dict()
            return {}
        
        except Exception as e:
            dashboard_logger.error(f"Error fetching booking statistics: {e}")
            return {}
    
    def log_user_action(self, action: str, details: str = "", user: str = "system"):
        """Log user action for audit trail."""
        try:
            query = f"""
            INSERT INTO dashboard_audit_log (user, action, details, timestamp)
            VALUES ('{user}', '{action}', '{details}', NOW())
            """
            
            self.db.execute_non_query(query)
            dashboard_logger.info(f"Logged action: {action} by {user}")
        
        except Exception as e:
            dashboard_logger.error(f"Error logging user action: {e}")
    
    def simulate_price_update(self, room_id: int, new_price: float) -> dict:
        """Simulate price update without executing."""
        try:
            # This is a simulation - no actual update
            dashboard_logger.info(f"SIMULATED: Price update for room {room_id} to {new_price}")
            
            return {
                'success': True,
                'message': f'Simulación: precio actualizado a ${new_price:,.0f}',
                'room_id': room_id,
                'new_price': new_price,
                'timestamp': pd.Timestamp.now()
            }
        
        except Exception as e:
            dashboard_logger.error(f"Error simulating price update: {e}")
            return {'success': False, 'message': str(e)}

# Singleton instance
_dashboard_db = None

def get_dashboard_db() -> DashboardDatabase:
    """Get or create dashboard database instance."""
    global _dashboard_db
    if _dashboard_db is None:
        _dashboard_db = DashboardDatabase()
    return _dashboard_db
