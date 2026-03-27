# backend/app/scrapers/orchestrator.py
"""Scraping orchestrator — runs all scrapers across all circuits."""

import asyncio
import json
import logging
from datetime import datetime

from app.database import SessionLocal
from app.models.circuit import Circuit
from app.models.race_event import RaceEvent
from app.models.seat_section import SeatSection
from app.models.ticket_listing import TicketListing
from app.scrapers.base import BaseScraper, RawTicketListing
from app.scrapers.matcher import match_section_name

logger = logging.getLogger(__name__)


class ScrapingOrchestrator:
    def __init__(self, scrapers: list[BaseScraper] | None = None):
        if scrapers is None:
            from app.scrapers.seatgeek import SeatGeekScraper
            from app.scrapers.stubhub import StubHubScraper
            from app.scrapers.viagogo import ViagogoScraper
            from app.scrapers.f1_official import F1OfficialScraper
            from app.scrapers.vivid_seats import VividSeatsScraper
            from app.scrapers.ticketmaster import TicketmasterScraper
            from app.scrapers.gp_portal import GPPortalScraper
            scrapers = [
                SeatGeekScraper(), StubHubScraper(), ViagogoScraper(),
                F1OfficialScraper(), VividSeatsScraper(),
                TicketmasterScraper(), GPPortalScraper(),
            ]
        self.scrapers = scrapers
        self.failure_counts: dict[str, int] = {}
        self.max_failures = 3

    def _get_circuits_and_events(self) -> list[dict]:
        db = SessionLocal()
        try:
            circuits = db.query(Circuit).all()
            result = []
            for c in circuits:
                event = (
                    db.query(RaceEvent)
                    .filter(RaceEvent.circuit_id == c.id, RaceEvent.status == "upcoming")
                    .first()
                )
                if event:
                    result.append({
                        "circuit_id": c.id, "circuit_name": c.name,
                        "race_name": event.race_name, "country": c.country,
                        "event_id": event.id,
                    })
            return result
        finally:
            db.close()

    def _build_section_map(self, circuit_id: int) -> dict[str, int]:
        db = SessionLocal()
        try:
            sections = db.query(SeatSection).filter(SeatSection.circuit_id == circuit_id).all()
            return {s.name: s.id for s in sections}
        finally:
            db.close()

    def _save_listings(self, raw_listings: list[RawTicketListing], circuit_id: int, event_id: int, section_map: dict[str, int]) -> tuple[int, int]:
        db = SessionLocal()
        matched = 0
        unmatched = 0
        try:
            # Mark previous listings from this source as unavailable
            source_site = raw_listings[0].source_site if raw_listings else None
            if source_site:
                db.query(TicketListing).filter(
                    TicketListing.circuit_id == circuit_id,
                    TicketListing.source_site == source_site,
                ).update({"is_available": False})

            for raw in raw_listings:
                section_id = match_section_name(raw.source_section_name, section_map)
                listing = TicketListing(
                    circuit_id=circuit_id, race_event_id=event_id,
                    seat_section_id=section_id, source_site=raw.source_site,
                    source_url=raw.source_url, source_section_name=raw.source_section_name,
                    ticket_type=raw.ticket_type, price=raw.price, currency=raw.currency,
                    available_quantity=raw.available_quantity,
                    includes=json.dumps(raw.includes) if raw.includes else None,
                    last_scraped_at=datetime.utcnow(), is_available=True,
                )
                db.add(listing)
                if section_id:
                    matched += 1
                else:
                    unmatched += 1
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        return matched, unmatched

    def _is_circuit_breaker_open(self, source_site: str) -> bool:
        return self.failure_counts.get(source_site, 0) >= self.max_failures

    async def run(self) -> dict:
        circuits = self._get_circuits_and_events()
        stats = {"total_listings": 0, "matched": 0, "unmatched": 0, "errors": 0}

        for scraper in self.scrapers:
            if self._is_circuit_breaker_open(scraper.source_site):
                logger.warning(f"[{scraper.source_site}] Circuit breaker OPEN — skipping")
                continue

            for circuit_info in circuits:
                try:
                    logger.info(f"[{scraper.source_site}] Scraping {circuit_info['circuit_name']}")
                    raw_listings = await scraper.scrape_circuit(
                        circuit_info["circuit_name"], circuit_info["race_name"], circuit_info["country"],
                    )
                    if raw_listings:
                        section_map = self._build_section_map(circuit_info["circuit_id"])
                        m, u = self._save_listings(raw_listings, circuit_info["circuit_id"], circuit_info["event_id"], section_map)
                        stats["total_listings"] += len(raw_listings)
                        stats["matched"] += m
                        stats["unmatched"] += u
                    self.failure_counts[scraper.source_site] = 0
                except Exception as e:
                    logger.error(f"[{scraper.source_site}] Failed for {circuit_info['circuit_name']}: {e}")
                    stats["errors"] += 1
                    self.failure_counts[scraper.source_site] = self.failure_counts.get(scraper.source_site, 0) + 1
                    if self._is_circuit_breaker_open(scraper.source_site):
                        logger.warning(f"[{scraper.source_site}] Circuit breaker TRIPPED")
                        break

                await scraper.random_delay(min_s=5, max_s=15)

        logger.info(f"Scraping complete: {stats}")
        return stats


async def main():
    logging.basicConfig(level=logging.INFO)
    orchestrator = ScrapingOrchestrator()
    stats = await orchestrator.run()
    print(f"Scraping complete: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
