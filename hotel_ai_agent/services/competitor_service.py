from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd

from config import Settings
from tools.competitor_tools import CompetitorListing, lightweight_scrape_price
from tools.db_tools import Database

logger = logging.getLogger(__name__)


class CompetitorService:
    def __init__(self, db: Database, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def scrape_and_store(self) -> pd.DataFrame:
        listings: list[CompetitorListing] = []

        for url in self.settings.competitor_urls:
            result = lightweight_scrape_price(url)
            if result:
                listings.append(result)

        if not listings:
            logger.info("No se capturaron datos de competencia en esta corrida")
            return pd.DataFrame(
                columns=[
                    "source",
                    "listing_title",
                    "listing_url",
                    "location",
                    "room_type",
                    "capacity",
                    "nightly_price",
                    "currency",
                    "captured_at",
                ]
            )

        for listing in listings:
            sql = """
            INSERT INTO competitor_price_snapshots (
                source, listing_title, listing_url, location, room_type,
                capacity, nightly_price, currency, captured_at
            ) VALUES (
                :source, :listing_title, :listing_url, :location, :room_type,
                :capacity, :nightly_price, :currency, :captured_at
            )
            """
            self.db.execute_non_query(
                sql,
                {
                    "source": listing.source,
                    "listing_title": listing.listing_title,
                    "listing_url": listing.listing_url,
                    "location": listing.location,
                    "room_type": listing.room_type,
                    "capacity": listing.capacity,
                    "nightly_price": listing.nightly_price,
                    "currency": listing.currency,
                    "captured_at": listing.captured_at,
                },
            )

        return pd.DataFrame([vars(item) for item in listings])

    def get_competitor_average_price(self, hours_back: int = 48) -> float | None:
        sql = """
        SELECT AVG(nightly_price) AS avg_price
        FROM competitor_price_snapshots
        WHERE captured_at >= DATE_SUB(NOW(), INTERVAL :hours_back HOUR)
        """
        df = self.db.execute_query(sql, {"hours_back": hours_back})
        if df.empty:
            return None
        value = df.iloc[0]["avg_price"]
        return round(float(value), 2) if value is not None else None

    def get_competitor_segmentation_snapshot(self, hours_back: int = 48) -> pd.DataFrame:
        sql = """
        SELECT
            source,
            COALESCE(location, 'N/A') AS location,
            COALESCE(room_type, 'N/A') AS room_type,
            COALESCE(capacity, 0) AS capacity,
            AVG(nightly_price) AS avg_price,
            COUNT(*) AS samples
        FROM competitor_price_snapshots
        WHERE captured_at >= DATE_SUB(NOW(), INTERVAL :hours_back HOUR)
        GROUP BY source, COALESCE(location, 'N/A'), COALESCE(room_type, 'N/A'), COALESCE(capacity, 0)
        ORDER BY source, avg_price
        """
        return self.db.execute_query(sql, {"hours_back": hours_back})
