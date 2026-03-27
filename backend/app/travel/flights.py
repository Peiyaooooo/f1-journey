"""Fetch flight data from Kiwi.com Tequila API."""

import logging
from dataclasses import dataclass
from datetime import date, timedelta

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

KIWI_SEARCH_URL = "https://api.tequila.kiwi.com/v2/search"


@dataclass
class FlightResult:
    price_min: float  # USD
    price_max: float  # USD
    duration_hours: float
    stops: int


async def fetch_flights(
    origin_code: str,
    destination_code: str,
    race_date: date,
) -> FlightResult | None:
    """Fetch flight prices from Kiwi.com Tequila API.

    Searches for flights arriving 1-2 days before the race and
    departing 0-1 days after.

    Returns FlightResult or None if API fails.
    """
    if not settings.kiwi_api_key:
        logger.warning("KIWI_API_KEY not set — skipping flight fetch")
        return None

    # Search window: arrive 1-2 days before race, depart 0-1 day after
    date_from = (race_date - timedelta(days=3)).strftime("%d/%m/%Y")
    date_to = (race_date - timedelta(days=1)).strftime("%d/%m/%Y")
    return_from = race_date.strftime("%d/%m/%Y")
    return_to = (race_date + timedelta(days=1)).strftime("%d/%m/%Y")

    params = {
        "fly_from": origin_code,
        "fly_to": destination_code,
        "date_from": date_from,
        "date_to": date_to,
        "return_from": return_from,
        "return_to": return_to,
        "curr": "USD",
        "sort": "price",
        "limit": 10,
        "flight_type": "round",
    }

    headers = {"apikey": settings.kiwi_api_key}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(KIWI_SEARCH_URL, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

        flights = data.get("data", [])
        if not flights:
            logger.info(f"No flights found {origin_code} -> {destination_code}")
            return None

        prices = [f["price"] for f in flights]
        # Use cheapest flight for duration/stops
        cheapest = flights[0]
        duration_seconds = cheapest.get("duration", {}).get("total", 0)
        # Count route segments minus 1 for stops
        route = cheapest.get("route", [])
        outbound_stops = max(0, len([r for r in route if r.get("return") == 0]) - 1)

        return FlightResult(
            price_min=min(prices),
            price_max=max(prices),
            duration_hours=round(duration_seconds / 3600, 1),
            stops=outbound_stops,
        )

    except Exception as e:
        logger.error(f"Kiwi API error for {origin_code}->{destination_code}: {e}")
        return None
