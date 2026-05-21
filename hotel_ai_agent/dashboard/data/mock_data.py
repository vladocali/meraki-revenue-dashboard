# Mock Data Generator for Dashboard Demo
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import random

class MockDataGenerator:
    """Generate realistic mock data for dashboard demonstration."""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        self.rooms = {
            "Habitación 201": {"capacity": 2, "type": "Estándar"},
            "Habitación 202": {"capacity": 2, "type": "Estándar"},
            "Habitación 203": {"capacity": 2, "type": "Deluxe"},
            "Habitación 204": {"capacity": 2, "type": "Deluxe"},
            "Habitación 205": {"capacity": 3, "type": "Suite"},
            "Habitación 206": {"capacity": 3, "type": "Suite"},
            "Habitación 207": {"capacity": 4, "type": "Suite Presidencial"},
        }
    
    def get_7day_occupancy(self) -> pd.DataFrame:
        """Generate 7-day occupancy data."""
        today = datetime.now()
        data = []
        
        for i in range(7):
            date = today + timedelta(days=i)
            for room, info in self.rooms.items():
                # Simulate occupancy with patterns
                base_occupancy = np.random.rand()
                if date.weekday() >= 4:  # Weekend
                    occupancy = min(0.95, base_occupancy + 0.3)
                else:  # Weekday
                    occupancy = base_occupancy * 0.7
                
                data.append({
                    'date': date.date(),
                    'day_of_week': date.strftime('%A'),
                    'room': room,
                    'occupied': occupancy > 0.5,
                    'occupancy_pct': occupancy * 100,
                    'guest_name': f"Guest {random.randint(1000, 9999)}" if occupancy > 0.5 else None,
                })
        
        return pd.DataFrame(data)
    
    def get_daily_occupancy_summary(self) -> pd.DataFrame:
        """Get daily occupancy summary."""
        occupancy_data = self.get_7day_occupancy()
        summary = occupancy_data.groupby('date').agg({
            'occupied': 'sum',
            'occupancy_pct': 'mean'
        }).reset_index()
        summary['total_rooms'] = len(self.rooms)
        summary['free_rooms'] = summary['total_rooms'] - summary['occupied']
        summary['occupancy_pct'] = summary['occupancy_pct']
        summary['date'] = pd.to_datetime(summary['date'])
        return summary
    
    def get_current_prices(self) -> pd.DataFrame:
        """Get current room prices."""
        data = []
        base_prices = {
            "Habitación 201": 150000,
            "Habitación 202": 150000,
            "Habitación 203": 200000,
            "Habitación 204": 200000,
            "Habitación 205": 300000,
            "Habitación 206": 300000,
            "Habitación 207": 500000,
        }
        
        for room, base_price in base_prices.items():
            # Add some variation
            variation = np.random.randint(-10000, 20000)
            current_price = base_price + variation
            
            data.append({
                'room': room,
                'room_type': self.rooms[room]['type'],
                'base_price': base_price,
                'current_price': current_price,
                'price_change_pct': (variation / base_price) * 100,
                'last_updated': datetime.now() - timedelta(hours=random.randint(1, 48))
            })
        
        return pd.DataFrame(data)
    
    def get_price_suggestions(self) -> pd.DataFrame:
        """Get AI price suggestions."""
        current_prices = self.get_current_prices()
        suggestions = []
        
        for idx, row in current_prices.iterrows():
            # Simulate suggestions based on occupancy
            occupancy = np.random.rand() * 100
            
            if occupancy > 80:
                suggested_price = row['current_price'] * np.random.uniform(1.05, 1.15)
                action = "INCREASE"
                reason = "High occupancy forecast - demand strong"
            elif occupancy < 40:
                suggested_price = row['current_price'] * np.random.uniform(0.85, 0.95)
                action = "DECREASE"
                reason = "Low occupancy - boost demand with lower price"
            else:
                suggested_price = row['current_price']
                action = "MAINTAIN"
                reason = "Balanced occupancy - current price optimal"
            
            impact = (suggested_price - row['current_price']) / row['current_price'] * 100
            
            suggestions.append({
                'room': row['room'],
                'room_type': row['room_type'],
                'current_price': row['current_price'],
                'suggested_price': int(suggested_price),
                'change_pct': (suggested_price - row['current_price']) / row['current_price'] * 100,
                'action': action,
                'reason': reason,
                'occupancy_forecast': occupancy,
                'estimated_impact': impact,
                'status': 'PENDING',
                'generated_at': datetime.now() - timedelta(hours=random.randint(1, 6)),
            })
        
        return pd.DataFrame(suggestions)
    
    def get_competitor_data(self) -> pd.DataFrame:
        """Get competitor pricing data."""
        competitors = [
            {"name": "Airbnb - Similar Std", "platform": "Airbnb"},
            {"name": "Booking.com - Std", "platform": "Booking"},
            {"name": "Local Competitor A", "platform": "Direct"},
            {"name": "Local Competitor B", "platform": "Direct"},
        ]
        
        data = []
        base_price = 150000
        
        for comp in competitors:
            for i in range(7):
                date = datetime.now() + timedelta(days=i)
                # Simulate competitor prices
                price = base_price + np.random.randint(-50000, 100000)
                
                data.append({
                    'date': date.date(),
                    'competitor': comp['name'],
                    'platform': comp['platform'],
                    'nightly_price': price,
                    'room_type': 'Estándar',
                    'captured_at': datetime.now() - timedelta(hours=random.randint(1, 24))
                })
        
        return pd.DataFrame(data)
    
    def get_revenue_metrics(self) -> Dict:
        """Get revenue metrics."""
        rooms_count = len(self.rooms)
        avg_price = 220000  # COP
        occupancy_7d = np.random.uniform(0.65, 0.85)
        
        revenue_7d = rooms_count * avg_price * occupancy_7d * 7
        revenue_month = revenue_7d * 4.3  # Approximate for month
        
        # Calculate ADR and RevPAR
        adr = avg_price
        revpar = adr * occupancy_7d
        
        # Year over year comparison
        yoy_growth = np.random.uniform(-0.05, 0.20)
        
        return {
            'occupancy_7d': occupancy_7d,
            'adr': int(adr),
            'revpar': int(revpar),
            'revenue_7d': int(revenue_7d),
            'revenue_month': int(revenue_month),
            'yoy_growth': yoy_growth,
            'rooms_count': rooms_count,
        }
    
    def get_alerts(self) -> List[Dict]:
        """Get AI alerts."""
        alerts = []
        
        # Simulated alerts
        alert_types = [
            {
                'type': 'HIGH_OCCUPANCY',
                'title': 'Alta ocupación detectada',
                'message': 'Los próximos 3 días proyectan ocupación > 90%. Se recomienda aumentar precios.',
                'severity': 'info',
                'icon': '📈'
            },
            {
                'type': 'LOW_PRICE',
                'title': 'Precios bajos vs competencia',
                'message': 'Tus precios están 15% por debajo de competidores. Oportunidad para aumentar.',
                'severity': 'warning',
                'icon': '💰'
            },
            {
                'type': 'EVENT_DETECTED',
                'title': 'Evento próximo detectado',
                'message': 'Festival de música este fin de semana. Demanda esperada alta.',
                'severity': 'info',
                'icon': '🎉'
            },
        ]
        
        return random.sample(alert_types, k=min(3, len(alert_types)))
    
    def get_price_history(self, room: str = None, days: int = 30) -> pd.DataFrame:
        """Get historical price data."""
        if room is None:
            room = random.choice(list(self.rooms.keys()))
        
        data = []
        base_price = self.get_current_prices()
        base_price = base_price[base_price['room'] == room]['base_price'].values[0]
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            # Generate price trends
            trend = np.sin(i / 7) * 50000  # Weekly pattern
            noise = np.random.randint(-20000, 20000)
            price = base_price + trend + noise
            
            data.append({
                'date': date.date(),
                'room': room,
                'price': int(max(100000, price)),  # Minimum price floor
            })
        
        return pd.DataFrame(data)
    
    def get_demographic_data(self) -> Dict:
        """Get guest demographic data."""
        return {
            'total_guests_7d': np.random.randint(30, 60),
            'repeat_guests': np.random.randint(5, 15),
            'avg_stay_nights': np.random.uniform(2.5, 4.5),
            'nationalities': {
                'Colombiana': np.random.randint(20, 40),
                'Extranjera': np.random.randint(10, 30),
            },
            'sources': {
                'Airbnb': np.random.randint(15, 30),
                'Booking': np.random.randint(10, 25),
                'Direct': np.random.randint(5, 15),
            }
        }

# Singleton instance
mock_generator = MockDataGenerator()

def get_mock_data(data_type: str):
    """Get mock data by type."""
    methods = {
        'occupancy_7d': mock_generator.get_7day_occupancy,
        'daily_summary': mock_generator.get_daily_occupancy_summary,
        'current_prices': mock_generator.get_current_prices,
        'suggestions': mock_generator.get_price_suggestions,
        'competitor': mock_generator.get_competitor_data,
        'revenue': mock_generator.get_revenue_metrics,
        'alerts': mock_generator.get_alerts,
        'price_history': mock_generator.get_price_history,
        'demographics': mock_generator.get_demographic_data,
    }
    
    if data_type not in methods:
        raise ValueError(f"Unknown data type: {data_type}")
    
    return methods[data_type]()
