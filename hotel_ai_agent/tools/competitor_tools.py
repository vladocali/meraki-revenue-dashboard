from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class CompetitorListing:
    source: str
    listing_title: str | None
    listing_url: str
    location: str | None
    room_type: str | None
    capacity: int | None
    nightly_price: float
    currency: str
    captured_at: datetime


def _extract_price_candidates(text: str) -> list[float]:
    patterns = [
        r"\$\s?([0-9][0-9\.,]{3,})",
        r"COP\s?([0-9][0-9\.,]{3,})",
        r"([0-9][0-9\.,]{4,})\s?COP",
    ]
    prices: list[float] = []
    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        for value in matches:
            normalized = value.replace(".", "").replace(",", "")
            if normalized.isdigit():
                price = float(normalized)
                if 20000 <= price <= 3000000:
                    prices.append(price)
    return prices


def lightweight_scrape_price(url: str, timeout: int = 12) -> CompetitorListing | None:
    headers = {
        "User-Agent": "MerakiHotelAgent/1.0 (suggestion-mode; respectful-scraping)",
        "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("No fue posible consultar competidor %s: %s", url, exc)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.text.strip() if soup.title and soup.title.text else None

    text_content = soup.get_text(" ", strip=True)
    candidates = _extract_price_candidates(text_content)
    if not candidates:
        logger.info("No se detectaron precios en %s", url)
        return None

    source = "airbnb" if "airbnb" in url.lower() else "booking" if "booking" in url.lower() else "web"
    nightly_price = min(candidates)

    return CompetitorListing(
        source=source,
        listing_title=title,
        listing_url=url,
        location=None,
        room_type=None,
        capacity=None,
        nightly_price=nightly_price,
        currency="COP",
        captured_at=datetime.now(),
    )
