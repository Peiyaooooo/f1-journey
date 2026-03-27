"""Official F1 ticket site scraper."""

import re
import logging
from urllib.parse import quote_plus

from playwright.async_api import async_playwright

from app.scrapers.base import BaseScraper, RawTicketListing

logger = logging.getLogger(__name__)


class F1OfficialScraper(BaseScraper):
    source_site = "f1_official"

    # Mapping of common circuit names to their F1 ticket page slugs
    CIRCUIT_SLUGS = {
        "Bahrain": "bahrain",
        "Jeddah": "saudi-arabia",
        "Melbourne": "australia",
        "Suzuka": "japan",
        "Shanghai": "china",
        "Miami": "miami",
        "Imola": "emilia-romagna",
        "Monaco": "monaco",
        "Barcelona": "spain",
        "Montreal": "canada",
        "Silverstone": "great-britain",
        "Spielberg": "austria",
        "Budapest": "hungary",
        "Spa": "belgium",
        "Zandvoort": "netherlands",
        "Monza": "italy",
        "Baku": "azerbaijan",
        "Singapore": "singapore",
        "Austin": "united-states",
        "Mexico City": "mexico",
        "Sao Paulo": "brazil",
        "Las Vegas": "las-vegas",
        "Lusail": "qatar",
        "Yas Marina": "abu-dhabi",
    }

    async def scrape_circuit(
        self, circuit_name: str, race_name: str, circuit_country: str
    ) -> list[RawTicketListing]:
        listings: list[RawTicketListing] = []
        try:
            await self.random_delay(min_s=2, max_s=5)

            # Determine the GP page URL
            slug = None
            for key, val in self.CIRCUIT_SLUGS.items():
                if key.lower() in circuit_name.lower():
                    slug = val
                    break
            if not slug:
                slug = quote_plus(circuit_country.lower())

            base_url = "https://tickets.formula1.com/en"
            gp_url = f"{base_url}/race/{slug}"

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.get_user_agent(),
                    viewport={"width": 1920, "height": 1080},
                )
                page = await context.new_page()

                try:
                    await page.goto(gp_url, timeout=30000)
                    await page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    logger.warning(
                        f"[{self.source_site}] Page load timeout for {race_name}, "
                        "possibly in queue"
                    )

                # Check for waiting room / queue page
                page_content = await page.content()
                if "queue" in page_content.lower() or "waiting" in page_content.lower():
                    logger.info(
                        f"[{self.source_site}] Stuck in queue for {race_name}, skipping"
                    )
                    await browser.close()
                    return listings

                # Parse grandstand / ticket options
                ticket_cards = await page.query_selector_all(
                    '[class*="ticket"], [class*="Ticket"], '
                    '[class*="grandstand"], [class*="Grandstand"], '
                    '[class*="product"], [class*="Product"]'
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

                        # Extract grandstand name (usually the first line)
                        lines = [l.strip() for l in card_text.split("\n") if l.strip()]
                        section = lines[0] if lines else "General Admission"

                        # Determine ticket type from text
                        ticket_type = "race_weekend"
                        if "sunday" in card_text.lower() or "race day" in card_text.lower():
                            ticket_type = "race_day"
                        elif "3-day" in card_text.lower() or "3 day" in card_text.lower():
                            ticket_type = "3_day"

                        listings.append(
                            RawTicketListing(
                                source_site=self.source_site,
                                source_url=gp_url,
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
                    f"[{self.source_site}] Found {len(listings)} listings for {race_name}"
                )
                await browser.close()

        except Exception as e:
            logger.error(f"[{self.source_site}] Error scraping {circuit_name}: {e}")
        return listings
