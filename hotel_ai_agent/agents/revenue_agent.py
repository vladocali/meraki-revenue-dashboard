from __future__ import annotations

import json
import logging
from datetime import date, datetime
from time import perf_counter
from typing import Any

import pandas as pd
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from config import Settings
from services.competitor_service import CompetitorService
from services.occupancy_service import OccupancyService
from services.pricing_service import PricingService
from tools.db_tools import Database
from tools.pricing_tools import PriceDecisionInput, suggest_price
from tools.report_tools import write_json_report, write_txt_report

logger = logging.getLogger(__name__)


class RevenueSuggestionAgent:
    def __init__(
        self,
        db: Database,
        settings: Settings,
        occupancy_service: OccupancyService,
        pricing_service: PricingService,
        competitor_service: CompetitorService,
    ) -> None:
        self.db = db
        self.settings = settings
        self.occupancy_service = occupancy_service
        self.pricing_service = pricing_service
        self.competitor_service = competitor_service

    def run_daily_analysis(self) -> dict[str, Any]:
        started = perf_counter()
        logger.info("Inicio de análisis de revenue en modo sugerencia=%s", self.settings.suggestion_mode)

        self.db.ensure_agent_tables()

        occupancy_df = self.occupancy_service.get_7_day_occupancy()
        historical = self.occupancy_service.get_historical_booking_behavior()
        prices_df = self.pricing_service.get_current_room_prices()

        competitor_captured_df = self.competitor_service.scrape_and_store()
        competitor_avg = self.competitor_service.get_competitor_average_price()
        competitor_segmentation = self.competitor_service.get_competitor_segmentation_snapshot()

        events_df = self.db.get_special_dates(date.today(), date.today().fromordinal(date.today().toordinal() + 6))

        suggestions_df = self._build_suggestions(
            occupancy_df=occupancy_df,
            prices_df=prices_df,
            competitor_avg=competitor_avg,
            events_df=events_df,
        )

        self._persist_suggestions(suggestions_df)

        executive_summary = self._build_executive_summary_with_llm(
            occupancy_df=occupancy_df,
            suggestions_df=suggestions_df,
            competitor_avg=competitor_avg,
            historical=historical,
            events_df=events_df,
        )

        report_data: dict[str, Any] = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "mode": "SUGGESTION",
            "executive_summary": executive_summary,
            "occupancy": occupancy_df.to_dict(orient="records"),
            "current_prices": prices_df.to_dict(orient="records"),
            "historical_behavior": historical,
            "competitor_avg_price": competitor_avg,
            "competitor_segmentation": competitor_segmentation.to_dict(orient="records"),
            "captured_competitors": competitor_captured_df.to_dict(orient="records"),
            "events": events_df.to_dict(orient="records"),
            "suggestions": suggestions_df.to_dict(orient="records"),
            "note": "No se ejecutaron UPDATE de precios. Solo sugerencias.",
        }

        json_path = write_json_report(report_data, self.settings.reports_dir)
        txt_path = write_txt_report(report_data, self.settings.reports_dir)
        runtime_sec = round(perf_counter() - started, 2)

        logger.info("Análisis finalizado en %ss", runtime_sec)
        logger.info("Reportes generados: json=%s txt=%s", json_path, txt_path)

        report_data["runtime_seconds"] = runtime_sec
        report_data["output_files"] = {
            "json": str(json_path),
            "txt": str(txt_path),
        }
        return report_data

    def _build_suggestions(
        self,
        occupancy_df: pd.DataFrame,
        prices_df: pd.DataFrame,
        competitor_avg: float | None,
        events_df: pd.DataFrame,
    ) -> pd.DataFrame:
        if occupancy_df.empty or prices_df.empty:
            return pd.DataFrame(
                columns=[
                    "room_name",
                    "target_date",
                    "action",
                    "current_price",
                    "suggested_price",
                    "adjustment_pct",
                    "occupancy_pct",
                    "competitor_avg",
                    "reason",
                    "min_price",
                    "max_price",
                ]
            )

        event_dates = set(pd.to_datetime(events_df["fecha"]).dt.date.tolist()) if not events_df.empty else set()

        rows: list[dict[str, Any]] = []

        for _, occ in occupancy_df.iterrows():
            target_date = pd.to_datetime(occ["date"]).date()
            occupancy_pct = float(occ["occupancy_pct"])

            for _, price_row in prices_df.iterrows():
                room_name = str(price_row["room_name"])
                current_price = float(price_row["reference_price"])
                min_price, max_price = self.pricing_service.price_limits_for_room(current_price)

                is_aggressive_day = self.pricing_service.is_weekend(target_date) or target_date in event_dates

                decision = suggest_price(
                    PriceDecisionInput(
                        current_price=current_price,
                        occupancy_pct=occupancy_pct,
                        competitor_avg_price=competitor_avg,
                        is_weekend_or_event=is_aggressive_day,
                        min_price=min_price,
                        max_price=max_price,
                    )
                )

                rows.append(
                    {
                        "room_name": room_name,
                        "target_date": target_date.isoformat(),
                        "action": decision.action,
                        "current_price": round(current_price, 0),
                        "suggested_price": decision.suggested_price,
                        "adjustment_pct": round(decision.adjustment_pct * 100, 2),
                        "occupancy_pct": occupancy_pct,
                        "competitor_avg": competitor_avg,
                        "reason": decision.explanation,
                        "min_price": min_price,
                        "max_price": max_price,
                    }
                )

        return pd.DataFrame(rows)

    def _persist_suggestions(self, suggestions_df: pd.DataFrame) -> None:
        if suggestions_df.empty:
            return

        for _, row in suggestions_df.iterrows():
            sql = """
            INSERT INTO revenue_recommendations (
                room_name, target_date, current_price, suggested_price,
                action, reason, occupancy_pct, competitor_avg,
                min_price, max_price, suggestion_mode, status
            ) VALUES (
                :room_name, :target_date, :current_price, :suggested_price,
                :action, :reason, :occupancy_pct, :competitor_avg,
                :min_price, :max_price, :suggestion_mode, :status
            )
            """
            self.db.execute_non_query(
                sql,
                {
                    "room_name": row["room_name"],
                    "target_date": row["target_date"],
                    "current_price": float(row["current_price"]),
                    "suggested_price": float(row["suggested_price"]),
                    "action": row["action"],
                    "reason": row["reason"],
                    "occupancy_pct": float(row["occupancy_pct"]),
                    "competitor_avg": float(row["competitor_avg"]) if row["competitor_avg"] is not None else None,
                    "min_price": float(row["min_price"]),
                    "max_price": float(row["max_price"]),
                    "suggestion_mode": 1 if self.settings.suggestion_mode else 0,
                    "status": "SUGERIDA",
                },
            )

    def _build_executive_summary_with_llm(
        self,
        occupancy_df: pd.DataFrame,
        suggestions_df: pd.DataFrame,
        competitor_avg: float | None,
        historical: dict[str, float],
        events_df: pd.DataFrame,
    ) -> str:
        baseline = (
            f"Ocupación media 7 días: {occupancy_df['occupancy_pct'].mean():.2f}% | "
            f"Sugerencias: {len(suggestions_df)} | "
            f"Competencia promedio: {competitor_avg if competitor_avg is not None else 'N/A'}"
        )

        if not self.settings.openai_api_key:
            return baseline + " | Sin OPENAI_API_KEY, se usa resumen local."

        try:
            llm = ChatOpenAI(
                api_key=self.settings.openai_api_key,
                model=self.settings.openai_model,
                temperature=0.2,
            )
            prompt_payload = {
                "occupancy": occupancy_df.to_dict(orient="records"),
                "historical": historical,
                "competitor_avg": competitor_avg,
                "events": events_df.to_dict(orient="records"),
                "top_suggestions": suggestions_df.head(10).to_dict(orient="records"),
                "constraints": {
                    "mode": "SUGERENCIA_ONLY",
                    "do_not_update_prices": True,
                },
            }
            msg = HumanMessage(
                content=(
                    "Eres un analista senior de revenue para hotelería. "
                    "Genera un resumen ejecutivo de máximo 120 palabras en español, "
                    "explicando contexto de demanda y recomendaciones. "
                    "No sugieras ejecución automática, solo recomendación.\n\n"
                    f"DATA:\n{json.dumps(prompt_payload, ensure_ascii=False)}"
                )
            )
            response = llm.invoke([msg])
            text = str(response.content).strip()
            return text if text else baseline
        except Exception as exc:  # noqa: BLE001
            logger.warning("Fallo al generar resumen con LLM: %s", exc)
            return baseline + " | Error en LLM, se usa resumen local."
