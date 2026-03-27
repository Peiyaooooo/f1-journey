"""GP Portal scraper for official Grand Prix ticket sites."""

import re
import logging

import httpx
from playwright.async_api import async_playwright

from app.scrapers.base import BaseScraper, RawTicketListing

logger = logging.getLogger(__name__)


class GPPortalScraper(BaseScraper):
    source_site = "gp_portal"

    # Mapping of circuit names / countries to their official ticket site URLs
    GP_TICKET_SITES: dict[str, str] = {
        "Silverstone": "https://www.silverstone.co.uk/events/formula-1-british-grand-prix",
        "Spa": "https://www.spagrandprix.com/en/tickets",
        "Monaco": "https://www.formula1monaco.com/en/tickets",
        "Monza": "https://www.monzanet.it/en/tickets/",
        "Barcelona": "https://www.circuitcat.com/en/tickets/",
        "Spielberg": "https://www.redbullring.com/en/formula-1/tickets/",
        "Budapest": "https://hungaroring.hu/en/tickets/",
        "Zandvoort": "https://www.dutchgp.com/tickets",
        "Montreal": "https://www.gpcanada.ca/en/tickets/",
        "Melbourne": "https://www.grandprix.com.au/tickets",
        "Suzuka": "https://www.suzukacircuit.jp/en/f1/ticket/",
        "Singapore": "https://www.singaporegp.sg/en/tickets",
        "Austin": "https://www.circuitoftheamericas.com/f1/tickets",
        "Mexico City": "https://www.mexicogp.mx/en/tickets/",
        "Sao Paulo": "https://www.gpbrasil.com.br/en/tickets",
        "Jeddah": "https://www.saudiarabiangp.com/en/tickets",
        "Bahrain": "https://www.bahraingp.com/tickets/",
        "Yas Marina": "https://www.yasmarinacircuit.com/en/formula-1/tickets",
        "Las Vegas": "https://www.f1lasvegasgp.com/tickets",
        "Lusail": "https://www.qatargp.com/en/tickets",
        "Baku": "https://www.bakucitycircuit.com/en/tickets",
        "Shanghai": "https://www.f1shanghai.cn/en/tickets",
        "Miami": "https://f1miamigp.com/tickets/",
        "Imola": "https://www.autodromoimola.it/en/tickets/",
    }

    def _find_ticket_url(self, circuit_name: str, circuit_country: str) -> str | None:
        """Find the official ticket site URL for a given circuit."""
        for key, url in self.GP_TICKET_SITES.items():
            if key.lower() in circuit_name.lower():
                return url
        # Fallback: try matching by country
        for key, url in self.GP_TICKET_SITES.items():
            if key.lower() in circuit_country.lower():
                return url
        return None

    async def scrape_circuit(
        self, circuit_name: str, race_name: str, circuit_country: str
    ) -> list[RawTicketListing]:
        listings: list[RawTicketListing] = []
        try:
            ticket_url = self._find_ticket_url(circuit_name, circuit_country)
            if not ticket_url:
                logger.info(
                    f"[{self.source_site}] No known ticket site for {circuit_name}"
                )
                return listings

            await self.random_delay(min_s=2, max_s=5)

            # First try with httpx (faster, lighter)
            try:
                listings = await self._scrape_with_httpx(ticket_url, circuit_name)
                if listings:
                    return listings
            except Exception:
                pass

            # Fall back to Playwright for JS-rendered pages
            listings = await self._scrape_with_playwright(ticket_url, circuit_name)

        except Exception as e:
            logger.error(f"[{self.source_site}] Error scraping {circuit_name}: {e}")
        return listings

    async def _scrape_with_httpx(
        self, url: str, circuit_name: str
    ) -> list[RawTicketListing]:
        listings: list[RawTicketListing] = []
        async with httpx.AsyncClient(follow_redirects=True) as client:
            headers = {
                "User-Agent": self.get_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            resp = await client.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            html = resp.text

            # Parse grandstand / ticket listings from HTML
            # Many GP sites use similar structures with price and section info
            price_matches = re.findall(
                r"[\$\u20ac\u00a3]\s*([\d,]+(?:\.\d{2})?)", html
            )
            # Look for grandstand names near prices
            section_matches = re.findall(
                r"(?:grandstand|tribune|stand|zone|terrace)\s*[:\-]?\s*([A-Za-z0-9\s\-]+)",
                html,
                re.IGNORECASE,
            )

            for i, price_str in enumerate(price_matches[:20]):
                try:
                    price = float(price_str.replace(",", ""))
                    if price < 10 or price > 50000:
                        continue
                    section = (
                        section_matches[i].strip()
                        if i < len(section_matches)
                        else "General Admission"
                    )
                    # Detect currency from the page
                    currency = "EUR"
                    if "$" in html[:500] or "USD" in html[:500]:
                        currency = "USD"
                    elif "\u00a3" in html[:500] or "GBP" in html[:500]:
                        currency = "GBP"

                    listings.append(
                        RawTicketListing(
                            source_site=self.source_site,
                            source_url=url,
                            source_section_name=section,
                            ticket_type="race_weekend",
                            price=price,
                            currency=currency,
                            available_quantity=None,
                        )
                    )
                except ValueError:
                    continue

        logger.info(
            f"[{self.source_site}] Found {len(listings)} listings via httpx for {circuit_name}"
        )
        return listings

    async def _scrape_with_playwright(
        self, url: str, circuit_name: str
    ) -> list[RawTicketListing]:
        listings: list[RawTicketListing] = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.get_user_agent(),
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()

            try:
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                logger.warning(
                    f"[{self.source_site}] Page load timeout for {circuit_name}"
                )

            # Parse ticket/grandstand cards
            ticket_cards = await page.query_selector_all(
                '[class*="ticket"], [class*="grandstand"], '
                '[class*="product"], [class*="package"], '
                '[class*="Ticket"], [class*="Grandstand"]'
            )

            for card in ticket_cards[:30]:
                try:
                    card_text = await card.inner_text()
                    price_match = re.search(
                        r"[\$\u20ac\u00a3]\s*([\d,]+(?:\.\d{2})?)", card_text
                    )
                    if not price_match:
                        continue
                    price = float(price_match.group(1).replace(",", ""))
                    if price < 10 or price > 50000:
                        continue

                    currency_match = re.search(r"([\$\u20ac\u00a3])", card_text)
                    currency_map = {"$": "USD", "\u20ac": "EUR", "\u00a3": "GBP"}
                    currency = currency_map.get(
                        currency_match.group(1) if currency_match else "\u20ac", "EUR"
                    )

                    lines = [l.strip() for l in card_text.split("\n") if l.strip()]
                    section = lines[0] if lines else "General Admission"

                    ticket_type = "race_weekend"
                    lower_text = card_text.lower()
                    if "sunday" in lower_text or "race day" in lower_text:
                        ticket_type = "race_day"
                    elif "3-day" in lower_text or "3 day" in lower_text:
                        ticket_type = "3_day"

                    listings.append(
                        RawTicketListing(
                            source_site=self.source_site,
                            source_url=url,
                            source_section_name=section,
                            ticket_type=ticket_type,
                            price=price,
                            currency=currency,
                            available_quantity=None,
                        )
                    )
                except Exception:
                    continue

            logger.info(
                f"[{self.source_site}] Found {len(listings)} listings via Playwright for {circuit_name}"
            )
            await browser.close()

        return listings
