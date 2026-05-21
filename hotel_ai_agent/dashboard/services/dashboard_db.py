# Dashboard Database Service
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import create_engine, text

from dashboard.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from dashboard.utils.logger import dashboard_logger

class DashboardDatabase:
    """Database service for dashboard."""
    
    def __init__(self):
        """Initialize database connection."""
        self.engine = None
        try:
            connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            self.engine = create_engine(connection_string, pool_pre_ping=True, future=True)
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            dashboard_logger.info("Dashboard database connected successfully")
        except Exception as e:
            dashboard_logger.error(f"Failed to connect to database: {e}")
            self.engine = None

    def is_available(self) -> bool:
        return self.engine is not None

    def execute_query(self, query: str, params: dict | None = None) -> pd.DataFrame:
        """Run SQL query and return a dataframe."""
        if self.engine is None:
            return pd.DataFrame()

        try:
            with self.engine.connect() as connection:
                return pd.read_sql(text(query), connection, params=params or {})
        except Exception as e:
            dashboard_logger.error(f"Database query failed: {e}")
            return pd.DataFrame()

    def get_active_rooms(self) -> pd.DataFrame:
        """Get list of active rooms from Meraki."""
        query = """
        SELECT nombre AS room
        FROM habitaciones
        WHERE activa = 1
        ORDER BY CAST(nombre AS UNSIGNED), nombre
        """
        return self.execute_query(query)

    def get_reservations_window(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Get reservations overlapping the requested window."""
        query = """
        SELECT DISTINCT
            TRIM(Habitacion) AS room,
            DATE(CheckIn) AS checkin,
            DATE(CheckOut) AS checkout
        FROM datos
        WHERE Habitacion IS NOT NULL
          AND TRIM(Habitacion) <> ''
          AND DATE(CheckIn) <= :end_date
          AND DATE(CheckOut) > :start_date
          AND UPPER(COALESCE(EstadoOperacion, 'RESERVA')) NOT IN ('CANCELADA', 'NO SHOW')
        """
        return self.execute_query(query, {
            'start_date': start_date,
            'end_date': end_date,
        })
    
    def get_7day_occupancy(self) -> pd.DataFrame:
        """Get real per-room occupancy for today and the next 6 days."""
        try:
            rooms_df = self.get_active_rooms()
            if rooms_df.empty:
                return pd.DataFrame()

            start_date = date.today()
            end_date = start_date + timedelta(days=6)
            reservations_df = self.get_reservations_window(start_date, end_date)

            if not reservations_df.empty:
                reservations_df['checkin'] = pd.to_datetime(reservations_df['checkin']).dt.date
                reservations_df['checkout'] = pd.to_datetime(reservations_df['checkout']).dt.date

            timeline = []
            for offset in range(7):
                current_date = start_date + timedelta(days=offset)
                for room in rooms_df['room'].astype(str):
                    room_reservations = reservations_df[reservations_df['room'].astype(str) == room] if not reservations_df.empty else pd.DataFrame()
                    occupied = False
                    if not room_reservations.empty:
                        occupied = ((room_reservations['checkin'] <= current_date) & (room_reservations['checkout'] > current_date)).any()

                    timeline.append({
                        'date': pd.Timestamp(current_date),
                        'day_of_week': pd.Timestamp(current_date).strftime('%A'),
                        'room': room,
                        'occupied': int(bool(occupied)),
                        'occupancy_pct': 100.0 if occupied else 0.0,
                    })

            result = pd.DataFrame(timeline)
            dashboard_logger.info(f"Retrieved real 7-day occupancy data: {len(result)} rows")
            return result
        
        except Exception as e:
            dashboard_logger.error(f"Error fetching 7-day occupancy: {e}")
            return pd.DataFrame()

    def get_daily_occupancy_summary(self) -> pd.DataFrame:
        """Aggregate real occupancy by day."""
        try:
            occupancy_data = self.get_7day_occupancy()
            if occupancy_data.empty:
                return pd.DataFrame()

            total_rooms = occupancy_data['room'].nunique()
            summary = occupancy_data.groupby('date', as_index=False).agg({
                'occupied': 'sum'
            })
            summary['total_rooms'] = int(total_rooms)
            summary['free_rooms'] = summary['total_rooms'] - summary['occupied']
            summary['occupancy_pct'] = ((summary['occupied'] / summary['total_rooms']) * 100).round(2)
            return summary[['date', 'occupied', 'occupancy_pct', 'total_rooms', 'free_rooms']]
        except Exception as e:
            dashboard_logger.error(f"Error building daily occupancy summary: {e}")
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
            
            result = self.execute_query(query)
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
            
            result = self.execute_query(query)
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
            
            result = self.execute_query(query)
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
            
            result = self.execute_query(query)
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
            
            if self.engine is not None:
                with self.engine.begin() as connection:
                    connection.execute(text(query))
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
