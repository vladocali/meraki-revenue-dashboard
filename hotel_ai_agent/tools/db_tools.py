from __future__ import annotations

import logging
from contextlib import contextmanager
from datetime import date
from typing import Any, Generator

import pandas as pd
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config import Settings

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.engine: Engine = create_engine(
            settings.database_url,
            echo=settings.db_echo_sql,
            pool_pre_ping=True,
            future=True,
        )
        self._session_factory = sessionmaker(bind=self.engine, class_=Session, expire_on_commit=False)
        self._attach_sql_logger()

    def _attach_sql_logger(self) -> None:
        @event.listens_for(self.engine, "before_cursor_execute")
        def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany) -> None:  # type: ignore[no-untyped-def]
            logger.debug("SQL: %s | params=%s", statement, parameters)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

    def execute_query(self, sql: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        logger.info("Ejecutando consulta SQL")
        with self.engine.connect() as conn:
            return pd.read_sql(text(sql), conn, params=params or {})

    def execute_non_query(self, sql: str, params: dict[str, Any] | None = None) -> None:
        with self.engine.begin() as conn:
            conn.execute(text(sql), params or {})

    def ensure_agent_tables(self) -> None:
        ddl_competitor = """
        CREATE TABLE IF NOT EXISTS competitor_price_snapshots (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            source VARCHAR(50) NOT NULL,
            listing_title VARCHAR(255) NULL,
            listing_url VARCHAR(500) NULL,
            location VARCHAR(120) NULL,
            room_type VARCHAR(100) NULL,
            capacity INT NULL,
            nightly_price DECIMAL(12,2) NOT NULL,
            currency VARCHAR(10) NOT NULL DEFAULT 'COP',
            captured_at DATETIME NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            KEY idx_source_date (source, captured_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        ddl_reco = """
        CREATE TABLE IF NOT EXISTS revenue_recommendations (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            room_name VARCHAR(20) NOT NULL,
            target_date DATE NOT NULL,
            current_price DECIMAL(12,2) NOT NULL,
            suggested_price DECIMAL(12,2) NOT NULL,
            action VARCHAR(20) NOT NULL,
            reason TEXT NOT NULL,
            occupancy_pct DECIMAL(5,2) NOT NULL,
            competitor_avg DECIMAL(12,2) NULL,
            min_price DECIMAL(12,2) NOT NULL,
            max_price DECIMAL(12,2) NOT NULL,
            suggestion_mode TINYINT(1) NOT NULL DEFAULT 1,
            status VARCHAR(20) NOT NULL DEFAULT 'SUGERIDA',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_room_date_created (room_name, target_date, created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        self.execute_non_query(ddl_competitor)
        self.execute_non_query(ddl_reco)
        logger.info("Tablas del agente verificadas/creadas")

    def get_active_rooms(self) -> pd.DataFrame:
        sql = """
        SELECT nombre AS room_name
        FROM habitaciones
        WHERE activa = 1
        ORDER BY nombre
        """
        return self.execute_query(sql)

    def get_special_dates(self, start_date: date, end_date: date) -> pd.DataFrame:
        sql = """
        SELECT fecha, tipo
        FROM cotizacion_fechas_especiales
        WHERE activo = 1
          AND fecha BETWEEN :start_date AND :end_date
        """
        return self.execute_query(sql, {"start_date": start_date, "end_date": end_date})
