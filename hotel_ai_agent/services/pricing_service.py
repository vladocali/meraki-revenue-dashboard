from __future__ import annotations

import logging
from datetime import date

import pandas as pd

from config import Settings
from tools.db_tools import Database

logger = logging.getLogger(__name__)


class PricingService:
    def __init__(self, db: Database, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def get_current_room_prices(self) -> pd.DataFrame:
        sql_params = """
        SELECT clave, valor
        FROM parametros
        WHERE clave REGEXP '^CotizacionHab[0-9]+(Luvi|Finsemana|Alta)$'
        """
        df = self.db.execute_query(sql_params)

        if df.empty:
            logger.warning("No se encontraron tarifas en parametros. Se usará fallback histórico.")
            return self._fallback_prices_from_history()

        records: list[dict[str, float | str]] = []
        grouped: dict[str, dict[str, float]] = {}

        for _, row in df.iterrows():
            key = str(row["clave"])
            value = float(str(row["valor"]).replace(",", "."))

            room = key.replace("CotizacionHab", "")
            if room.endswith("Luvi"):
                room_name, ptype = room[:-4], "luvi"
            elif room.endswith("Finsemana"):
                room_name, ptype = room[:-9], "finsemana"
            elif room.endswith("Alta"):
                room_name, ptype = room[:-4], "alta"
            else:
                continue

            grouped.setdefault(room_name, {})[ptype] = value

        for room_name, prices in grouped.items():
            luvi = prices.get("luvi", 0.0)
            finsemana = prices.get("finsemana", luvi)
            alta = prices.get("alta", finsemana)
            avg_reference = round((luvi * 5 + finsemana * 2) / 7, 2)

            records.append(
                {
                    "room_name": room_name,
                    "price_luvi": luvi,
                    "price_weekend": finsemana,
                    "price_high": alta,
                    "reference_price": avg_reference,
                }
            )

        return pd.DataFrame(records).sort_values("room_name")

    def _fallback_prices_from_history(self, lookback_days: int = 120) -> pd.DataFrame:
        sql = """
        SELECT
            TRIM(Habitacion) AS room_name,
            AVG(
                CASE
                    WHEN DATEDIFF(CheckOut, CheckIn) > 0 THEN Valor / DATEDIFF(CheckOut, CheckIn)
                    ELSE NULL
                END
            ) AS reference_price
        FROM datos
        WHERE DATE(CheckIn) >= DATE_SUB(CURDATE(), INTERVAL :lookback DAY)
          AND TRIM(COALESCE(Habitacion, '')) <> ''
          AND TRIM(COALESCE(Habitacion, '')) <> '0'
          AND COALESCE(EstadoOperacion, 'RESERVA') <> 'CANCELADA'
        GROUP BY TRIM(Habitacion)
        """
        df = self.db.execute_query(sql, {"lookback": lookback_days})
        if df.empty:
            rooms = self.db.get_active_rooms()
            if rooms.empty:
                return pd.DataFrame(columns=["room_name", "price_luvi", "price_weekend", "price_high", "reference_price"])
            rooms["reference_price"] = float(self.settings.default_min_price)
            rooms["price_luvi"] = rooms["reference_price"]
            rooms["price_weekend"] = rooms["reference_price"]
            rooms["price_high"] = rooms["reference_price"]
            return rooms[["room_name", "price_luvi", "price_weekend", "price_high", "reference_price"]]

        df["reference_price"] = df["reference_price"].fillna(float(self.settings.default_min_price)).round(2)
        df["price_luvi"] = df["reference_price"]
        df["price_weekend"] = (df["reference_price"] * 1.1).round(2)
        df["price_high"] = (df["reference_price"] * 1.2).round(2)
        return df[["room_name", "price_luvi", "price_weekend", "price_high", "reference_price"]]

    def price_limits_for_room(self, reference_price: float) -> tuple[float, float]:
        min_price = max(self.settings.default_min_price, reference_price * self.settings.min_price_factor)
        max_price = max(min_price, min(self.settings.default_max_price, reference_price * self.settings.max_price_factor))
        return round(min_price, 0), round(max_price, 0)

    def is_weekend(self, target: date) -> bool:
        return target.weekday() >= 4
