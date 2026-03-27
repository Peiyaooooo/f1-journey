"""Viagogo ticket scraper for F1 events."""

import logging
from urllib.parse import quote_plus

from playwright.async_api import async_playwright

from app.scrapers.base import BaseScraper, RawTicketListing

logger = logging.getLogger(__name__)


class ViagogoScraper(BaseScraper):
    source_site = "viagogo"

    async def scrape_circuit(
        self, circuit_name: str, race_name: str, circuit_country: str
    ) -> list[RawTicketListing]:
        listings: list[RawTicketListing] = []
        try:
            await self.random_delay(min_s=2, max_s=5)

            search_query = quote_plus(f"{race_name} Formula 1")
            search_url = f"https://www.viagogo.com/search?q={search_query}"

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.get_user_agent(),
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US",
                )
                page = await context.new_page()

                # Viagogo uses heavy Cloudflare protection
                try:
                    await page.goto(search_url, timeout=30000)
                    await page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    logger.warning(
                        f"[{self.source_site}] Page load timeout for {race_name}, "
                        "likely blocked by Cloudflare"
                    )
                    await browser.close()
                    return listings

                await self.random_delay(min_s=2, max_s=4)

                # Check if we got blocked by Cloudflare
                page_content = await page.content()
                if "challenge" in page_content.lower() or "captcha" in page_content.lower():
                    logger.warning(
                        f"[{self.source_site}] Blocked by anti-bot for {race_name}"
                    )
                    await browser.close()
                    return listings

                # Look for event links
                event_links = await page.query_selector_all(
                    'a[href*="formula"], a[href*="grand-prix"], a[href*="f1"]'
                )

                event_url = None
                if event_links:
                    event_url = await event_links[0].get_attribute("href")
                    if event_url and not event_url.startswith("http"):
                        event_url = f"https://www.viagogo.com{event_url}"

                if event_url:
                    await self.random_delay(min_s=1, max_s=3)
                    try:
                        await page.goto(event_url, timeout=30000)
                        await page.wait_for_load_state("networkidle", timeout=15000)
                    except Exception:
                        logger.warning(f"[{self.source_site}] Event page load timeout")
                        await browser.close()
                        return listings

                # Parse listing cards
                import re

                listing_cards = await page.query_selector_all(
                    '[class*="listing"], [class*="Listing"], '
                    '[data-testid*="listing"], [class*="ticket"]'
                )

                for card in listing_cards[:30]:
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

                        # Determine currency from symbol
                        currency_match = re.search(r"([\$\u20ac\u00a3])", card_text)
                        currency_map = {"$": "USD", "\u20ac": "EUR", "\u00a3": "GBP"}
                        currency = currency_map.get(
                            currency_match.group(1) if currency_match else "$", "USD"
                        )

                        section_match = re.search(
                            r"(?:Section|Category|Zone)\s+([A-Za-z0-9\s\-]+)",
                            card_text,
                            re.IGNORECASE,
                        )
                        section = (
                            section_match.group(1).strip()
                            if section_match
                            else "General Admission"
                        )

                        listings.append(
                            RawTicketListing(
                                source_site=self.source_site,
                                source_url=event_url or search_url,
                                source_section_name=section,
                                ticket_type="race_weekend",
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
