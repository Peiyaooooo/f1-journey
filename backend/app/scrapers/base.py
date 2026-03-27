"""Base scraper class and data structures for ticket scraping."""

import asyncio
import random
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RawTicketListing:
    """A single ticket listing scraped from a source site."""
    source_site: str
    source_url: str
    source_section_name: str
    ticket_type: str
    price: float
    currency: str
    available_quantity: int | None = None
    includes: list[str] | None = None


class BaseScraper(ABC):
    """Abstract base class for all ticket scrapers."""

    source_site: str = ""

    @abstractmethod
    async def scrape_circuit(
        self, circuit_name: str, race_name: str, circuit_country: str
    ) -> list[RawTicketListing]:
        """Scrape all available tickets for a given circuit/race."""

    async def random_delay(self, min_s: float = 30, max_s: float = 120) -> None:
        """Sleep for a random duration to avoid rate limiting."""
        delay = random.uniform(min_s, max_s)
        logger.debug(f"[{self.source_site}] Sleeping {delay:.1f}s")
        await asyncio.sleep(delay)

    def get_user_agent(self) -> str:
        """Return a random user agent string."""
        agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        return random.choice(agents)
