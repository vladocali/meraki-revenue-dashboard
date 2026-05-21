from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    db_dialect: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    openai_api_key: str
    openai_model: str

    log_level: str
    log_dir: Path
    reports_dir: Path

    suggestion_mode: bool
    daily_run_time: str
    competitor_poll_minutes: int

    min_price_factor: float
    max_price_factor: float
    default_min_price: int
    default_max_price: int

    db_echo_sql: bool
    competitor_urls: list[str]

    @property
    def database_url(self) -> str:
        return (
            f"{self.db_dialect}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, str(default)).strip().lower()
    return raw in {"1", "true", "yes", "y", "on"}


def get_settings() -> Settings:
    competitor_urls_raw = os.getenv("COMPETITOR_URLS", "").strip()
    competitor_urls = [u.strip() for u in competitor_urls_raw.split(",") if u.strip()]

    settings = Settings(
        db_dialect=os.getenv("DB_DIALECT", "mysql+pymysql"),
        db_host=os.getenv("DB_HOST", "127.0.0.1"),
        db_port=int(os.getenv("DB_PORT", "3306")),
        db_name=os.getenv("DB_NAME", "meraki"),
        db_user=os.getenv("DB_USER", "root"),
        db_password=os.getenv("DB_PASSWORD", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_dir=BASE_DIR / os.getenv("LOG_DIR", "logs"),
        reports_dir=BASE_DIR / os.getenv("REPORTS_DIR", "reports"),
        suggestion_mode=_get_bool("SUGGESTION_MODE", True),
        daily_run_time=os.getenv("DAILY_RUN_TIME", "02:00"),
        competitor_poll_minutes=int(os.getenv("COMPETITOR_POLL_MINUTES", "180")),
        min_price_factor=float(os.getenv("MIN_PRICE_FACTOR", "0.85")),
        max_price_factor=float(os.getenv("MAX_PRICE_FACTOR", "1.20")),
        default_min_price=int(os.getenv("DEFAULT_MIN_PRICE", "70000")),
        default_max_price=int(os.getenv("DEFAULT_MAX_PRICE", "300000")),
        db_echo_sql=_get_bool("DB_ECHO_SQL", False),
        competitor_urls=competitor_urls,
    )

    settings.log_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    return settings


def setup_logging(log_level: str, log_dir: Path) -> None:
    log_file = log_dir / "hotel_ai_agent.log"
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
