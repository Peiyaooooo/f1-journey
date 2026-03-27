"""SeatGeek ticket scraper using their public API.

Requires a free client_id from https://seatgeek.com/build
Set env var: F1_SEATGEEK_CLIENT_ID=your_client_id
"""

import httpx
import logging

from app.config import settings
from app.scrapers.base import BaseScraper, RawTicketListing

logger = logging.getLogger(__name__)

SEATGEEK_API = "https://api.seatgeek.com/2"


class SeatGeekScraper(BaseScraper):
    source_site = "seatgeek"

    async def scrape_circuit(
        self, circuit_name: str, race_name: str, circuit_country: str
    ) -> list[RawTicketListing]:
        listings: list[RawTicketListing] = []

        if not settings.seatgeek_client_id:
            logger.warning("[seatgeek] SEATGEEK_CLIENT_ID not set — skipping")
            return listings

        try:
            await self.random_delay(min_s=2, max_s=5)

            # Search for F1 events matching this race
            async with httpx.AsyncClient() as client:
                # First try taxonomy-based search for Formula 1
                params = {
                    "client_id": settings.seatgeek_client_id,
                    "q": race_name,
                    "per_page": 25,
                }
                resp = await client.get(
                    f"{SEATGEEK_API}/events", params=params, timeout=30
                )
                resp.raise_for_status()
                data = resp.json()

                events = data.get("events", [])

                # Filter for F1/Grand Prix events
                f1_events = []
                for event in events:
                    title = event.get("title", "").lower()
                    event_type = event.get("type", "").lower()
                    taxonomies = [
                        t.get("name", "").lower()
                        for t in event.get("taxonomies", [])
                    ]
                    if (
                        "formula" in title
                        or "grand prix" in title
                        or "f1" in title
                        or "formula_1" in taxonomies
                        or "auto_racing" in taxonomies
                    ):
                        f1_events.append(event)

                if not f1_events:
                    logger.info(f"[seatgeek] No F1 events found for {race_name}")
                    return listings

                for event in f1_events:
                    event_id = event.get("id")
                    event_title = event.get("title", "")
                    event_url = event.get("url", "")
                    stats = event.get("stats", {})

                    lowest_price = stats.get("lowest_price")
                    avg_price = stats.get("average_price")
                    highest_price = stats.get("highest_price")
                    listing_count = stats.get("listing_count", 0)

                    # The events endpoint gives price stats but not per-section breakdowns
                    # Create listings from the price stats we have
                    if lowest_price and lowest_price > 0:
                        listings.append(
                            RawTicketListing(
                                source_site=self.source_site,
                                source_url=event_url or f"https://seatgeek.com/e/{event_id}",
                                source_section_name=event_title,
                                ticket_type="race_weekend",
                                price=float(lowest_price),
                                currency="USD",
                                available_quantity=listing_count if listing_count > 0 else None,
                            )
                        )

                    if avg_price and avg_price > 0 and avg_price != lowest_price:
                        listings.append(
                            RawTicketListing(
                                source_site=self.source_site,
                                source_url=event_url or f"https://seatgeek.com/e/{event_id}",
                                source_section_name=event_title,
                                ticket_type="race_weekend",
                                price=float(avg_price),
                                currency="USD",
                                available_quantity=None,
                            )
                        )

                logger.info(
                    f"[seatgeek] Found {len(listings)} listings for {race_name}"
                )

        except Exception as e:
            logger.error(f"[seatgeek] Error scraping {circuit_name}: {e}")

        return listings
