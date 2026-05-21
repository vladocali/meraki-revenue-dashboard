from __future__ import annotations

import logging
import re
from html import unescape
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

import requests

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

    html_text = response.text or ""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
    title = unescape(title_match.group(1)).strip() if title_match else None

    text_content = re.sub(r"<script[^>]*>.*?</script>", " ", html_text, flags=re.IGNORECASE | re.DOTALL)
    text_content = re.sub(r"<style[^>]*>.*?</style>", " ", text_content, flags=re.IGNORECASE | re.DOTALL)
    text_content = re.sub(r"<[^>]+>", " ", text_content)
    text_content = unescape(re.sub(r"\s+", " ", text_content)).strip()
    candidates = _extract_price_candidates(text_content)
    if not candidates:
        logger.info("No se detectaron precios en %s", url)
        return None

    parsed_url = urlparse(url)
    hostname = (parsed_url.netloc or "web").lower().replace("www.", "")
    if "airbnb" in hostname or "airbnb" in url.lower():
        source = "airbnb"
    elif "booking" in hostname or "booking" in url.lower():
        source = "booking"
    elif "hotels" in hostname or "hotel" in hostname:
        source = "google_hotel"
    else:
        source = hostname.split(":")[0].split(".")[0] or "web"

    nightly_price = min(candidates)

    room_type = None
    lower_text = text_content.lower()
    if "suite" in lower_text:
        room_type = "Suite"
    elif "deluxe" in lower_text:
        room_type = "Deluxe"
    elif "estándar" in lower_text or "estandar" in lower_text:
        room_type = "Estándar"

    return CompetitorListing(
        source=source,
        listing_title=title,
        listing_url=url,
        location=None,
        room_type=room_type,
        capacity=None,
        nightly_price=nightly_price,
        currency="COP",
        captured_at=datetime.now(),
    )
