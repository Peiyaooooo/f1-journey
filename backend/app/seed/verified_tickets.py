"""Verified ticket prices scraped from StubHub and GP portal sites on 2026-03-27.

StubHub prices are from the listing/event pages (EUR, resale market).
GP portal prices are from official ticket seller websites.
Where both are available, both are stored for cross-reference.

Data quality notes:
- StubHub prices are "from" prices (cheapest available) and max prices seen on the page.
- GP portal prices are face-value official prices.
- Some circuits had no StubHub 2026 listings or were behind login walls.
- Some GP portal sites had all tickets sold out or showed no prices.
"""

VERIFIED_STUBHUB_TICKETS = {
    # =========================================================================
    # 1. Albert Park Circuit (Melbourne, Australia)
    # =========================================================================
    "Albert Park Circuit": {
        "stubhub_event_url": "",
        "stubhub_status": "unavailable",
        "stubhub_listings": [],
        "gp_portal_status": "site_404",
        "gp_portal_prices": [],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 2. Shanghai International Circuit (China)
    # =========================================================================
    "Shanghai International Circuit": {
        "stubhub_event_url": "",
        "stubhub_status": "unavailable",  # Scraper picked wrong event
        "stubhub_listings": [],
        "gp_portal_status": "no_prices",  # All "Not Available"
        "gp_portal_prices": [],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 3. Suzuka International Racing Course (Japan)
    # =========================================================================
    "Suzuka International Racing Course": {
        "stubhub_event_url": "",
        "stubhub_status": "unavailable",  # Scraper picked wrong event (football)
        "stubhub_listings": [],
        "gp_portal_status": "no_prices",  # All "Not Available" (reseller site)
        "gp_portal_prices": [],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 4. Miami International Autodrome (USA)
    # =========================================================================
    "Miami International Autodrome": {
        "stubhub_event_url": "https://www.stubhub.com/formula-1-miami-gardens-tickets-5-1-2026/event/158425349/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 618, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "General (most expensive)", "price": 2399, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "gp_portal_status": "available",
        "gp_portal_prices": [
            {"section": "South Beach Grandstand (Uncovered)", "price": 829, "currency": "USD", "ticket_type": "3-day"},
            {"section": "South Beach Grandstand (Covered)", "price": 859, "currency": "USD", "ticket_type": "3-day"},
            {"section": "North Beach Grandstand (Covered)", "price": 859, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Marina Grandstand", "price": 929, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Start and Finish Grandstand (Uncovered)", "price": 1409, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Start and Finish Grandstand (Covered)", "price": 1509, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Turn 1 Grandstand (Uncovered)", "price": 1259, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Turn 1 Grandstand (Covered)", "price": 1659, "currency": "USD", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 5. Circuit Gilles Villeneuve (Canada)
    # =========================================================================
    "Circuit Gilles Villeneuve": {
        "stubhub_event_url": "https://www.stubhub.com/canadian-f1-gp-montreal-tickets-5-21-2026/event/158704858/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 292, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "General (most expensive)", "price": 24365, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "gp_portal_status": "mostly_sold_out",
        "gp_portal_prices": [
            {"section": "General Admission", "price": 469, "currency": "USD", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 6. Circuit de Monaco
    # =========================================================================
    "Circuit de Monaco": {
        "stubhub_event_url": "https://www.stubhub.com/monaco-grand-prix-monte-carlo-tickets-4-25-2026/event/160594884/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 150, "currency": "EUR", "ticket_type": "weekend"},
            {"section": "General (most expensive)", "price": 1964, "currency": "EUR", "ticket_type": "weekend"},
        ],
        "gp_portal_status": "site_403",  # Official site blocked
        "gp_portal_prices": [],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 7. Circuit de Barcelona-Catalunya (Spain) / Madrid Street Circuit
    # Note: 2026 Spanish GP moved to Madrid
    # =========================================================================
    "Circuit de Barcelona-Catalunya": {
        "stubhub_event_url": "",
        "stubhub_status": "unavailable",  # No Barcelona event (moved to Madrid)
        "stubhub_listings": [],
        "gp_portal_status": "available",
        "gp_portal_prices": [
            {"section": "General Admission", "price": 249, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand M", "price": 599, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand I", "price": 599, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand A", "price": 719, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 8. Red Bull Ring (Austria)
    # =========================================================================
    "Red Bull Ring": {
        "stubhub_event_url": "https://www.stubhub.com/formula-1-spielberg-tickets-6-26-2026/event/158498605/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 220, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "General (most expensive)", "price": 2410, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "gp_portal_status": "available",
        "gp_portal_prices": [
            {"section": "T8", "price": 549, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "T9", "price": 649, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Steiermark - First Row", "price": 719, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "3 Corner Gold", "price": 849, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 9. Silverstone Circuit (UK)
    # =========================================================================
    "Silverstone Circuit": {
        "stubhub_event_url": "https://www.stubhub.com/formula-1-northamptonshire-tickets-7-3-2026/event/158498575/",
        "stubhub_status": "no_prices",  # Event page found but no price data extracted
        "stubhub_listings": [],
        "gp_portal_status": "mostly_sold_out",
        "gp_portal_prices": [
            {"section": "General Admission", "price": 579, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Farm Curve", "price": 719, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 10. Circuit de Spa-Francorchamps (Belgium)
    # =========================================================================
    "Circuit de Spa-Francorchamps": {
        "stubhub_event_url": "https://www.stubhub.com/formula-1-francorchamps-tickets-7-17-2026/event/158498632/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 225, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "General (most expensive)", "price": 1813, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "gp_portal_status": "available",
        "gp_portal_prices": [
            {"section": "General Admission (Bronze Area)", "price": 259, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Blanchimont 17-27", "price": 329, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Bronze Area - Bruxelles", "price": 359, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Silver 5", "price": 439, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Speed Corner", "price": 459, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Combes 4", "price": 499, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Combes 2", "price": 519, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Silver 3", "price": 579, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Silver 4: Bruxelles", "price": 589, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Silver 2: Fan Zone", "price": 639, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Gold 7: Bis", "price": 659, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Gold 7 Ter: Endurance", "price": 659, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Gold 1: Pit", "price": 879, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 11. Hungaroring (Hungary)
    # =========================================================================
    "Hungaroring": {
        "stubhub_event_url": "https://www.stubhub.com/formula-1-mogyorod-tickets-7-24-2026/event/158498648/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 188, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "General (most expensive)", "price": 1597, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "gp_portal_status": "mostly_sold_out",
        "gp_portal_prices": [
            {"section": "General Admission", "price": 279, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand Fan 2", "price": 349, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 12. Circuit Zandvoort (Netherlands)
    # =========================================================================
    "Circuit Zandvoort": {
        "stubhub_event_url": "https://www.stubhub.com/formula-1-zandvoort-tickets-8-21-2026/event/158498740/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 450, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "General (most expensive)", "price": 2100, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "gp_portal_status": "mostly_sold_out",
        "gp_portal_prices": [
            {"section": "Ben Pon 2 (Silver)", "price": 799, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Eastside 3 (Gold)", "price": 839, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 13. Autodromo Nazionale di Monza (Italy)
    # =========================================================================
    "Autodromo Nazionale di Monza": {
        "stubhub_event_url": "https://www.stubhub.com/formula-1-monza-tickets-9-4-2026/event/158498653/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 200, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "General (most expensive)", "price": 3198, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "gp_portal_status": "available",
        "gp_portal_prices": [
            {"section": "General Admission (Settore 8)", "price": 219, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand 5 (Piscina)", "price": 699, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand 14", "price": 699, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand 21 A & B", "price": 699, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand 4 / 8A / 8B / 22", "price": 789, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Biassono 7", "price": 789, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand 16 (Ascari)", "price": 899, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand 9", "price": 899, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "Grandstand 6 C", "price": 1199, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 14. Madrid Street Circuit (Spain)
    # =========================================================================
    "Madrid Street Circuit": {
        "stubhub_event_url": "https://www.stubhub.com/formula-1-madrid-tickets-9-11-2026/event/158510390/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 421, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "General (most expensive)", "price": 2314, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "gp_portal_status": "no_prices",  # Widget-based, prices not extractable
        "gp_portal_prices": [],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 15. Baku City Circuit (Azerbaijan)
    # =========================================================================
    "Baku City Circuit": {
        "stubhub_event_url": "",
        "stubhub_status": "unavailable",  # Login wall
        "stubhub_listings": [],
        "gp_portal_status": "available",
        "gp_portal_prices": [
            {"section": "Grandstand Zafar", "price": 399, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Filarmoniya", "price": 439, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Giz Galasi", "price": 459, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Bulvar", "price": 459, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Khazar", "price": 459, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Marine", "price": 499, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Mugham", "price": 669, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Icheri Sheher", "price": 689, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Azneft", "price": 729, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Champions", "price": 879, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Absheron A", "price": 1149, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Absheron B", "price": 1149, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Absheron C", "price": 1219, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Absheron D", "price": 1219, "currency": "USD", "ticket_type": "4-day"},
            {"section": "Grandstand Absheron E", "price": 1149, "currency": "USD", "ticket_type": "4-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 16. Marina Bay Street Circuit (Singapore)
    # =========================================================================
    "Marina Bay Street Circuit": {
        "stubhub_event_url": "https://www.stubhub.com/formula-1-singapore-tickets-10-9-2026/event/158498831/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 469, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "General (most expensive)", "price": 2482, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "gp_portal_status": "no_prices",  # Widget-based, no prices extracted
        "gp_portal_prices": [],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 17. Circuit of the Americas (USA)
    # =========================================================================
    "Circuit of the Americas": {
        "stubhub_event_url": "https://www.stubhub.com/formula-1-austin-tickets-10-23-2026/event/158487725/",
        "stubhub_status": "available",
        "stubhub_listings": [
            {"section": "General (cheapest)", "price": 470, "currency": "EUR", "ticket_type": "3-day"},
            {"section": "General (most expensive)", "price": 2477, "currency": "EUR", "ticket_type": "3-day"},
        ],
        "gp_portal_status": "available",
        "gp_portal_prices": [
            {"section": "Grandstand Turn 9", "price": 759, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand Turn 12", "price": 1009, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand Turn 15", "price": 1239, "currency": "USD", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 18. Autodromo Hermanos Rodriguez (Mexico)
    # =========================================================================
    "Autodromo Hermanos Rodriguez": {
        "stubhub_event_url": "",
        "stubhub_status": "unavailable",  # Login wall
        "stubhub_listings": [],
        "gp_portal_status": "available",
        "gp_portal_prices": [
            {"section": "Grandstand 2A", "price": 509, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand 6A", "price": 659, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand 15", "price": 739, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand 14", "price": 809, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand 3A", "price": 859, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand 6", "price": 1059, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand 5A", "price": 1129, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand 4", "price": 1149, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand 5", "price": 1149, "currency": "USD", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 19. Interlagos (Brazil)
    # =========================================================================
    "Interlagos": {
        "stubhub_event_url": "",
        "stubhub_status": "unavailable",  # Scraper picked wrong event
        "stubhub_listings": [],
        "gp_portal_status": "sold_out",  # All grandstands "Not Available"
        "gp_portal_prices": [],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 20. Las Vegas Street Circuit (USA)
    # =========================================================================
    "Las Vegas Street Circuit": {
        "stubhub_event_url": "",
        "stubhub_status": "unavailable",  # Login wall
        "stubhub_listings": [],
        "gp_portal_status": "no_prices",  # All "Not available" (reseller site)
        "gp_portal_prices": [],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 21. Losail International Circuit (Qatar)
    # =========================================================================
    "Losail International Circuit": {
        "stubhub_event_url": "",
        "stubhub_status": "unavailable",  # Login wall
        "stubhub_listings": [],
        "gp_portal_status": "available",
        "gp_portal_prices": [
            {"section": "General Admission", "price": 229, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand T2", "price": 349, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand T3", "price": 349, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand T16", "price": 349, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand Nord", "price": 499, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand Main", "price": 679, "currency": "USD", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },

    # =========================================================================
    # 22. Yas Marina Circuit (Abu Dhabi)
    # =========================================================================
    "Yas Marina Circuit": {
        "stubhub_event_url": "",
        "stubhub_status": "unavailable",  # Login wall
        "stubhub_listings": [],
        "gp_portal_status": "available",
        "gp_portal_prices": [
            {"section": "Grandstand West Straight", "price": 899, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand North Straight", "price": 999, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand Marina", "price": 1309, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand South (Marina)", "price": 1379, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand Nord", "price": 1469, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand West", "price": 1499, "currency": "USD", "ticket_type": "3-day"},
            {"section": "West Social Club", "price": 1889, "currency": "USD", "ticket_type": "3-day"},
            {"section": "Grandstand Main", "price": 2319, "currency": "USD", "ticket_type": "3-day"},
        ],
        "scraped_at": "2026-03-27",
    },
}

# ============================================================================
# Verified StubHub event URLs (for direct linking in ticket listings)
# Only includes confirmed correct 2026 F1 events
# ============================================================================
VERIFIED_STUBHUB_EVENT_URLS = {
    "Miami International Autodrome": "https://www.stubhub.com/formula-1-miami-gardens-tickets-5-1-2026/event/158425349/",
    "Circuit Gilles Villeneuve": "https://www.stubhub.com/canadian-f1-gp-montreal-tickets-5-21-2026/event/158704858/",
    "Circuit de Monaco": "https://www.stubhub.com/monaco-grand-prix-monte-carlo-tickets-4-25-2026/event/160594884/",
    "Red Bull Ring": "https://www.stubhub.com/formula-1-spielberg-tickets-6-26-2026/event/158498605/",
    "Silverstone Circuit": "https://www.stubhub.com/formula-1-northamptonshire-tickets-7-3-2026/event/158498575/",
    "Circuit de Spa-Francorchamps": "https://www.stubhub.com/formula-1-francorchamps-tickets-7-17-2026/event/158498632/",
    "Hungaroring": "https://www.stubhub.com/formula-1-mogyorod-tickets-7-24-2026/event/158498648/",
    "Circuit Zandvoort": "https://www.stubhub.com/formula-1-zandvoort-tickets-8-21-2026/event/158498740/",
    "Autodromo Nazionale di Monza": "https://www.stubhub.com/formula-1-monza-tickets-9-4-2026/event/158498653/",
    "Madrid Street Circuit": "https://www.stubhub.com/formula-1-madrid-tickets-9-11-2026/event/158510390/",
    "Marina Bay Street Circuit": "https://www.stubhub.com/formula-1-singapore-tickets-10-9-2026/event/158498831/",
    "Circuit of the Americas": "https://www.stubhub.com/formula-1-austin-tickets-10-23-2026/event/158487725/",
}
