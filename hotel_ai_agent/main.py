from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime

from config import get_settings, setup_logging
from services.competitor_service import CompetitorService
from services.occupancy_service import OccupancyService
from services.pricing_service import PricingService
from tools.db_tools import Database

logger = logging.getLogger(__name__)


def build_agent() -> RevenueSuggestionAgent:
    from agents.revenue_agent import RevenueSuggestionAgent

    settings, db, occupancy_service, pricing_service, competitor_service = build_services()
    return RevenueSuggestionAgent(
        db=db,
        settings=settings,
        occupancy_service=occupancy_service,
        pricing_service=pricing_service,
        competitor_service=competitor_service,
    )


def build_services():
    settings = get_settings()
    setup_logging(settings.log_level, settings.log_dir)

    db = Database(settings)
    occupancy_service = OccupancyService(db)
    pricing_service = PricingService(db, settings)
    competitor_service = CompetitorService(db, settings)

    return settings, db, occupancy_service, pricing_service, competitor_service



def build_competitor_service() -> tuple[object, Database, CompetitorService]:
    settings = get_settings()
    setup_logging(settings.log_level, settings.log_dir)

    db = Database(settings)
    competitor_service = CompetitorService(db, settings)
    return settings, db, competitor_service


def run_once() -> None:
    logger.info("Ejecución manual iniciada")
    agent = build_agent()
    result = agent.run_daily_analysis()
    logger.info("Ejecución manual finalizada: %s", result.get("output_files"))


def run_competitor_once() -> None:
    settings, db, competitor_service = build_competitor_service()
    logger.info(
        "Captura puntual de competencia iniciada (fuentes=%s)",
        len(settings.competitor_urls),
    )

    db.ensure_agent_tables()
    captured_df = competitor_service.scrape_and_store()
    logger.info("Captura puntual de competencia finalizada: %s registros", len(captured_df))


def run_scheduler() -> None:
    import schedule

    settings = get_settings()
    setup_logging(settings.log_level, settings.log_dir)

    def _job() -> None:
        start = datetime.now()
        logger.info("Job programado iniciado a las %s", start.isoformat(timespec="seconds"))
        try:
            agent = build_agent()
            result = agent.run_daily_analysis()
            logger.info("Job programado finalizado. Archivos: %s", result.get("output_files"))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error en job programado: %s", exc)

    schedule.every().day.at(settings.daily_run_time).do(_job)
    logger.info("Scheduler activo. Ejecutará todos los días a las %s", settings.daily_run_time)

    while True:
        schedule.run_pending()
        time.sleep(20)


def run_competitor_scheduler() -> None:
    import schedule

    settings, db, competitor_service = build_competitor_service()

    def _job() -> None:
        start = datetime.now()
        logger.info("Job de competencia iniciado a las %s", start.isoformat(timespec="seconds"))
        try:
            db.ensure_agent_tables()
            captured_df = competitor_service.scrape_and_store()
            logger.info("Job de competencia finalizado: %s registros", len(captured_df))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error en job de competencia: %s", exc)

    _job()
    schedule.every(settings.competitor_poll_minutes).minutes.do(_job)
    logger.info(
        "Scheduler de competencia activo. Ejecutará cada %s minutos",
        settings.competitor_poll_minutes,
    )

    while True:
        schedule.run_pending()
        time.sleep(20)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hotel AI Revenue Agent (modo sugerencia)")
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Ejecuta el análisis inmediatamente y termina.",
    )
    parser.add_argument(
        "--scheduler",
        action="store_true",
        help="Inicia scheduler diario (02:00 AM configurable).",
    )
    parser.add_argument(
        "--competitor-now",
        action="store_true",
        help="Captura competencia una sola vez y termina.",
    )
    parser.add_argument(
        "--competitor-scheduler",
        action="store_true",
        help="Inicia scheduler continuo de competencia.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.run_now:
        run_once()
    elif args.competitor_now:
        run_competitor_once()
    elif args.competitor_scheduler:
        run_competitor_scheduler()
    elif args.scheduler:
        run_scheduler()
    else:
        print("Usa --run-now, --competitor-now, --scheduler o --competitor-scheduler.")
