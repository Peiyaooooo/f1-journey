"""Fetch train/transport data from Rome2Rio API."""

import logging
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

ROME2RIO_URL = "https://free.rome2rio.com/api/1.4/json/Search"


@dataclass
class TransportResult:
    train_available: bool
    train_price_min: float | None  # USD
    train_price_max: float | None  # USD
    train_duration_hours: float | None
    local_transport_cost: float  # USD estimate


async def fetch_transport(
    origin_city: str,
    destination_city: str,
) -> TransportResult:
    """Fetch train/transport options from Rome2Rio.

    Returns TransportResult with train info if available,
    plus an estimate for local transport cost.
    """
    if not settings.rome2rio_api_key:
        logger.warning("ROME2RIO_API_KEY not set — returning defaults")
        return TransportResult(
            train_available=False,
            train_price_min=None,
            train_price_max=None,
            train_duration_hours=None,
            local_transport_cost=30.0,  # default estimate
        )

    params = {
        "key": settings.rome2rio_api_key,
        "oName": origin_city,
        "dName": destination_city,
        "currencyCode": "USD",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(ROME2RIO_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

        routes = data.get("routes", [])

        # Find train routes
        train_route = None
        for route in routes:
            name = route.get("name", "").lower()
            if "train" in name or "rail" in name:
                train_route = route
                break

        # Estimate local transport from cheapest short route
        local_cost = 30.0  # default
        for route in routes:
            duration = route.get("totalDuration", 999)
            if duration < 120:  # under 2 hours = local transport
                price = route.get("indicativePrice", {})
                low = price.get("priceLow", price.get("price", 0))
                if 5 <= low <= 100:
                    local_cost = low
                    break

        if train_route:
            price_info = train_route.get("indicativePrice", {})
            price_low = price_info.get("priceLow", price_info.get("price"))
            price_high = price_info.get("priceHigh", price_low)
            duration = train_route.get("totalDuration", 0)

            return TransportResult(
                train_available=True,
                train_price_min=price_low,
                train_price_max=price_high,
                train_duration_hours=round(duration / 60, 1) if duration else None,
                local_transport_cost=local_cost,
            )

        return TransportResult(
            train_available=False,
            train_price_min=None,
            train_price_max=None,
            train_duration_hours=None,
            local_transport_cost=local_cost,
        )

    except Exception as e:
        logger.error(f"Rome2Rio API error for {origin_city}->{destination_city}: {e}")
        return TransportResult(
            train_available=False,
            train_price_min=None,
            train_price_max=None,
            train_duration_hours=None,
            local_transport_cost=30.0,
        )
