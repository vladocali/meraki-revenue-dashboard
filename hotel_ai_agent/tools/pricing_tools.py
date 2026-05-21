from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PriceDecisionInput:
    current_price: float
    occupancy_pct: float
    competitor_avg_price: float | None
    is_weekend_or_event: bool
    min_price: float
    max_price: float


@dataclass
class PriceDecision:
    action: str
    suggested_price: float
    adjustment_pct: float
    explanation: str


def clamp_price(price: float, min_price: float, max_price: float) -> float:
    return max(min_price, min(max_price, price))


def suggest_price(input_data: PriceDecisionInput) -> PriceDecision:
    current = input_data.current_price
    occupancy = input_data.occupancy_pct
    competitor = input_data.competitor_avg_price
    aggressive = input_data.is_weekend_or_event

    adjustment_pct = 0.0
    action = "MANTENER"

    if occupancy < 40 and competitor is not None and competitor < current:
        action = "BAJAR"
        adjustment_pct = 0.10 if aggressive else 0.07
    elif occupancy > 80:
        action = "SUBIR"
        adjustment_pct = 0.18 if aggressive else 0.10

    if action == "BAJAR":
        suggested = current * (1 - adjustment_pct)
    elif action == "SUBIR":
        suggested = current * (1 + adjustment_pct)
    else:
        suggested = current

    suggested = clamp_price(suggested, input_data.min_price, input_data.max_price)

    explanation = (
        f"Acción={action}. Ocupación={occupancy:.2f}% | "
        f"Competencia promedio={'N/A' if competitor is None else f'{competitor:,.0f}'} | "
        f"Ajuste={adjustment_pct * 100:.1f}% | "
        f"Límites [{input_data.min_price:,.0f}, {input_data.max_price:,.0f}]"
    )

    return PriceDecision(
        action=action,
        suggested_price=round(suggested, 0),
        adjustment_pct=adjustment_pct,
        explanation=explanation,
    )


def suggest_price_update(*args, **kwargs) -> None:  # type: ignore[no-untyped-def]
    logger.warning(
        "suggest_price_update() está deshabilitada en MODO SUGERENCIA. "
        "No se ejecutan UPDATEs automáticos."
    )
