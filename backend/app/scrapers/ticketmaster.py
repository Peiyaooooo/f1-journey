"""Ticketmaster ticket scraper for F1 events."""

import re
import logging
from urllib.parse import quote_plus

from playwright.async_api import async_playwright

from app.scrapers.base import BaseScraper, RawTicketListing

logger = logging.getLogger(__name__)


class TicketmasterScraper(BaseScraper):
    source_site = "ticketmaster"

    async def scrape_circuit(
        self, circuit_name: str, race_name: str, circuit_country: str
    ) -> list[RawTicketListing]:
        listings: list[RawTicketListing] = []
        try:
            await self.random_delay(min_s=2, max_s=5)

            search_query = quote_plus(f"{race_name} Formula 1")
            search_url = f"https://www.ticketmaster.com/search?q={search_query}"

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.get_user_agent(),
                    viewport={"width": 1920, "height": 1080},
                )
                page = await context.new_page()

                try:
                    await page.goto(search_url, timeout=30000)
                    await page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    logger.warning(
                        f"[{self.source_site}] Page load timeout for {race_name}"
                    )

                await self.random_delay(min_s=1, max_s=3)

                # Check for CAPTCHA or bot block
                page_content = await page.content()
                if "captcha" in page_content.lower() or "blocked" in page_content.lower():
                    logger.warning(
                        f"[{self.source_site}] Blocked by anti-bot for {race_name}"
                    )
                    await browser.close()
                    return listings

                # Find event links in search results
                event_links = await page.query_selector_all(
                    'a[href*="formula-1"], a[href*="grand-prix"], '
                    'a[href*="f1-"], a[href*="/event/"]'
                )

                event_url = None
                for link in event_links[:5]:
                    href = await link.get_attribute("href")
                    text = await link.inner_text()
                    if href and ("formula" in text.lower() or "grand prix" in text.lower() or "f1" in text.lower()):
                        event_url = href
                        if not event_url.startswith("http"):
                            event_url = f"https://www.ticketmaster.com{event_url}"
                        break

                if event_url:
                    await self.random_delay(min_s=1, max_s=3)
                    try:
                        await page.goto(event_url, timeout=30000)
                        await page.wait_for_load_state("networkidle", timeout=15000)
                    except Exception:
                        logger.warning(
                            f"[{self.source_site}] Event page load timeout"
                        )

                    # Parse ticket listings
                    ticket_cards = await page.query_selector_all(
                        '[class*="ticket"], [class*="listing"], '
                        '[data-testid*="ticket"], [class*="offer"]'
                    )

                    for card in ticket_cards[:30]:
                        try:
                            card_text = await card.inner_text()
                            price_match = re.search(
                                r"\$\s*([\d,]+(?:\.\d{2})?)", card_text
                            )
                            if not price_match:
                                continue
                            price = float(price_match.group(1).replace(",", ""))
                            if price < 10 or price > 50000:
                                continue

                            section_match = re.search(
                                r"(?:Section|Sec|Area)\s+([A-Za-z0-9\s\-]+)",
                                card_text,
                                re.IGNORECASE,
                            )
                            section = (
                                section_match.group(1).strip()
                                if section_match
                                else "General Admission"
                            )

                            qty_match = re.search(
                                r"(\d+)\s*ticket", card_text, re.IGNORECASE
                            )
                            quantity = int(qty_match.group(1)) if qty_match else None

                            listings.append(
                                RawTicketListing(
                                    source_site=self.source_site,
                                    source_url=event_url,
                                    source_section_name=section,
                                    ticket_type="race_weekend",
                                    price=price,
                                    currency="USD",
                                    available_quantity=quantity,
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
