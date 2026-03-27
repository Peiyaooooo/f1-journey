"""Fetch and cache exchange rates from frankfurter.app."""

import logging
from datetime import datetime, timedelta

import httpx

from app.database import SessionLocal
from app.models.exchange_rate import ExchangeRate

logger = logging.getLogger(__name__)

FRANKFURTER_URL = "https://api.frankfurter.app/latest?from=USD"
STALE_HOURS = 24


async def fetch_and_cache_rates() -> list[ExchangeRate]:
    """Fetch latest exchange rates and cache in DB.

    Returns list of ExchangeRate objects.
    """
    db = SessionLocal()
    try:
        # Check if rates are still fresh
        latest = db.query(ExchangeRate).first()
        if latest and latest.last_updated_at > datetime.utcnow() - timedelta(hours=STALE_HOURS):
            return db.query(ExchangeRate).all()

        # Fetch fresh rates
        async with httpx.AsyncClient() as client:
            resp = await client.get(FRANKFURTER_URL, timeout=15)
            resp.raise_for_status()
            data = resp.json()

        rates_data = data.get("rates", {})
        now = datetime.utcnow()

        for code, rate in rates_data.items():
            existing = db.query(ExchangeRate).filter(ExchangeRate.currency_code == code).first()
            if existing:
                existing.rate_from_usd = rate
                existing.last_updated_at = now
            else:
                db.add(ExchangeRate(currency_code=code, rate_from_usd=rate, last_updated_at=now))

        # Always ensure USD = 1.0
        usd = db.query(ExchangeRate).filter(ExchangeRate.currency_code == "USD").first()
        if usd:
            usd.rate_from_usd = 1.0
            usd.last_updated_at = now
        else:
            db.add(ExchangeRate(currency_code="USD", rate_from_usd=1.0, last_updated_at=now))

        db.commit()
        return db.query(ExchangeRate).all()

    except Exception as e:
        logger.error(f"Exchange rate fetch failed: {e}")
        db.rollback()
        # Return stale data if available
        return db.query(ExchangeRate).all()
    finally:
        db.close()


def get_cached_rates() -> list[ExchangeRate]:
    """Get cached exchange rates without fetching."""
    db = SessionLocal()
    try:
        return db.query(ExchangeRate).all()
    finally:
        db.close()
