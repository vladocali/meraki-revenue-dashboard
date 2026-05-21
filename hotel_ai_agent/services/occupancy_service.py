from __future__ import annotations

import logging
from datetime import date, timedelta

import pandas as pd

from tools.db_tools import Database

logger = logging.getLogger(__name__)


class OccupancyService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_7_day_occupancy(self, start_date: date | None = None) -> pd.DataFrame:
        start = start_date or date.today()
        end = start + timedelta(days=6)

        total_rooms_df = self.db.execute_query("SELECT COUNT(*) AS total_rooms FROM habitaciones WHERE activa = 1")
        total_rooms = int(total_rooms_df.iloc[0]["total_rooms"]) if not total_rooms_df.empty else 0

        sql = """
        SELECT
            ds.dia AS target_date,
            COUNT(DISTINCT d.Habitacion) AS occupied_rooms
        FROM (
            SELECT :d0 AS dia UNION ALL
            SELECT :d1 UNION ALL SELECT :d2 UNION ALL SELECT :d3 UNION ALL
            SELECT :d4 UNION ALL SELECT :d5 UNION ALL SELECT :d6
        ) ds
        LEFT JOIN datos d
            ON d.Habitacion IS NOT NULL
           AND TRIM(d.Habitacion) <> ''
           AND TRIM(d.Habitacion) <> '0'
           AND ds.dia >= DATE(d.CheckIn)
           AND ds.dia < DATE(d.CheckOut)
           AND COALESCE(d.EstadoOperacion, 'RESERVA') <> 'CANCELADA'
        GROUP BY ds.dia
        ORDER BY ds.dia
        """

        params = {f"d{i}": start + timedelta(days=i) for i in range(7)}
        df = self.db.execute_query(sql, params)
        if df.empty:
            return pd.DataFrame(columns=["date", "occupied_rooms", "total_rooms", "occupancy_pct", "demand_flag"])

        df["total_rooms"] = total_rooms
        df["occupancy_pct"] = (df["occupied_rooms"] / total_rooms * 100).round(2) if total_rooms else 0.0

        def _flag(pct: float) -> str:
            if pct < 40:
                return "BAJA"
            if pct > 80:
                return "ALTA"
            return "MEDIA"

        df["demand_flag"] = df["occupancy_pct"].apply(_flag)
        df = df.rename(columns={"target_date": "date"})
        return df

    def get_historical_booking_behavior(self, lookback_days: int = 90) -> dict[str, float]:
        sql = """
        SELECT
            DATE(CheckIn) AS checkin_day,
            COUNT(*) AS bookings,
            AVG(GREATEST(DATEDIFF(CheckIn, DATE(FechaHora)), 0)) AS avg_lead_days,
            AVG(
                CASE
                    WHEN DATEDIFF(CheckOut, CheckIn) > 0 THEN Valor / DATEDIFF(CheckOut, CheckIn)
                    ELSE NULL
                END
            ) AS avg_nightly_price
        FROM datos
        WHERE DATE(CheckIn) >= DATE_SUB(CURDATE(), INTERVAL :lookback DAY)
          AND COALESCE(EstadoOperacion, 'RESERVA') <> 'CANCELADA'
          AND TRIM(COALESCE(Habitacion, '')) <> ''
          AND TRIM(COALESCE(Habitacion, '')) <> '0'
        GROUP BY DATE(CheckIn)
        """
        df = self.db.execute_query(sql, {"lookback": lookback_days})
        if df.empty:
            return {
                "avg_daily_bookings": 0.0,
                "avg_lead_days": 0.0,
                "avg_nightly_price": 0.0,
            }

        return {
            "avg_daily_bookings": round(float(df["bookings"].mean()), 2),
            "avg_lead_days": round(float(df["avg_lead_days"].mean()), 2),
            "avg_nightly_price": round(float(df["avg_nightly_price"].mean()), 2),
        }
