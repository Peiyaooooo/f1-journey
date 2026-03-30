"""Verified F1 Official and GP Portal ticket prices and availability.

Verified on 2026-03-27 by checking:
- F1 Official (tickets.formula1.com): HTTP status codes to confirm pages exist
- GP Portal sites: WebFetch to extract actual prices and availability

Currency conversion rates used:
  EUR=1.09, GBP=1.27, AUD=0.65, CAD=0.73, JPY=0.0067,
  SGD=0.75, BRL=0.18, MXN=0.05, AED=0.27, QAR=0.27, AZN=0.59
"""

VERIFIED_OFFICIAL_PRICES = {
    # =========================================================================
    # 1. Albert Park Circuit (Melbourne, Australia)
    # GP Portal: grandprix.com.au — 2026 event over, site shows "Register Interest" for 2027
    # F1 Official: No URL (not sold via F1 store)
    # =========================================================================
    "Albert Park Circuit": {
        "gp_portal_url": "https://www.grandprix.com.au",
        "gp_portal_status": "unavailable",  # 2026 race passed; site promoting 2027 registration
        "f1_store_status": "unavailable",
        "verified_date": "2026-03-27",
        "sections": {},
    },

    # =========================================================================
    # 2. Shanghai International Circuit (China)
    # GP Portal: formula1shanghai.com — All grandstands "Not Available", no prices shown (2027 page)
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Shanghai International Circuit": {
        "gp_portal_url": "https://www.formula1shanghai.com/en/tickets",
        "gp_portal_status": "unavailable",  # All "Not Available", no prices, showing 2027
        "f1_store_status": "available",  # 302 — page exists
        "verified_date": "2026-03-27",
        "sections": {
            "Grandstand A (Platinum)": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "Grandstand A (High Gold)": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "Grandstand A (Low Silver)": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "Grandstand B": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "Grandstand K": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "Grandstand H": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
        },
    },

    # =========================================================================
    # 3. Suzuka International Racing Course (Japan)
    # GP Portal: japan.gp — Unofficial reseller, all grandstands "Not Available", no prices
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Suzuka International Racing Course": {
        "gp_portal_url": "https://www.japan.gp/en/tickets",
        "gp_portal_status": "unavailable",  # Reseller site, all "Not Available"
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {},
    },

    # =========================================================================
    # 4. Miami International Autodrome (USA)
    # GP Portal: f1miamiusa.com — Multiple grandstands available with prices
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Miami International Autodrome": {
        "gp_portal_url": "https://www.f1miamiusa.com/en/tickets",
        "gp_portal_status": "available",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "South Beach Grandstand (Uncovered)": {"price_local": 829, "currency": "USD", "price_usd": 829, "status": "available"},
            "South Beach Grandstand (Covered)": {"price_local": 859, "currency": "USD", "price_usd": 859, "status": "available"},
            "North Beach Grandstand": {"price_local": 859, "currency": "USD", "price_usd": 859, "status": "available"},
            "Marina Grandstand": {"price_local": 929, "currency": "USD", "price_usd": 929, "status": "available"},
            "Start and Finish Grandstand (Uncovered)": {"price_local": 1409, "currency": "USD", "price_usd": 1409, "status": "available"},
            "Start and Finish Grandstand (Covered)": {"price_local": 1509, "currency": "USD", "price_usd": 1509, "status": "available"},
            "Turn 1 Grandstand (Uncovered)": {"price_local": 1259, "currency": "USD", "price_usd": 1259, "status": "available"},
            "Turn 1 Grandstand (Covered)": {"price_local": 1659, "currency": "USD", "price_usd": 1659, "status": "available"},
            "Turn 18 Grandstand": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "General Admission (Campus Pass)": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
        },
    },

    # =========================================================================
    # 5. Circuit Gilles Villeneuve (Canada)
    # GP Portal: canada.gp — Only GA available at $469, all grandstands sold out
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Circuit Gilles Villeneuve": {
        "gp_portal_url": "https://www.canada.gp/en/tickets",
        "gp_portal_status": "mostly_sold_out",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "General Admission": {"price_local": 469, "currency": "USD", "price_usd": 469, "status": "available"},
            "Grandstand 1": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Platine": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 11": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 12": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 15": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 21": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 24 (Lance Stroll)": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 31": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 33 (Family)": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 34": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 46": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 47": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 6. Circuit de Monaco
    # GP Portal: f1monaco.com — Mostly "Notify me" (waitlist), VIP from 7000 EUR
    # F1 Official: 200 OK (monaco-grandprix.com)
    # =========================================================================
    "Circuit de Monaco": {
        "gp_portal_url": "https://www.f1monaco.com/en/tickets",
        "gp_portal_status": "mostly_sold_out",  # All grandstands are "Notify me" or "Not available"
        "f1_store_status": "available",  # 200 OK
        "verified_date": "2026-03-27",
        "sections": {
            "VIP Caravelles Grand Terrace": {"price_local": 7000, "currency": "EUR", "price_usd": 7630, "status": "available"},
            "Grandstand B - Casino Square": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand K": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand K1-K2": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand K3-K6": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand L": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand N": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand O": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand P": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand T (high)": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "not_available"},
            "Grandstand T (low)": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "not_available"},
            "Grandstand V": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "not_available"},
            "General Admission (weekend)": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 7. Circuit de Barcelona-Catalunya (Spain)
    # GP Portal: barcelonaf1.com — GA 249 EUR, a few grandstands still available
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Circuit de Barcelona-Catalunya": {
        "gp_portal_url": "https://www.barcelonaf1.com/en/tickets",
        "gp_portal_status": "available",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "General Admission": {"price_local": 249, "currency": "EUR", "price_usd": 271, "status": "available"},
            "Grandstand A": {"price_local": 719, "currency": "EUR", "price_usd": 784, "status": "available"},  # 1 left
            "Grandstand I": {"price_local": 599, "currency": "EUR", "price_usd": 653, "status": "available"},  # 1 left
            "Grandstand M": {"price_local": 599, "currency": "EUR", "price_usd": 653, "status": "available"},
            "Grandstand C": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand E": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand F": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand G": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand H": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand J": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand K": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand L": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Main Grandstand": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 8. Red Bull Ring (Austria)
    # GP Portal: f1austria.com — 4 sections available, most sold out
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Red Bull Ring": {
        "gp_portal_url": "https://www.f1austria.com/en/tickets",
        "gp_portal_status": "available",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "T8": {"price_local": 549, "currency": "EUR", "price_usd": 598, "status": "available"},
            "T9": {"price_local": 649, "currency": "EUR", "price_usd": 707, "status": "available"},
            "Steiermark - First Row": {"price_local": 719, "currency": "EUR", "price_usd": 784, "status": "available"},
            "3 Corner Gold": {"price_local": 849, "currency": "EUR", "price_usd": 925, "status": "available"},  # 1 left
            "General Admission": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Start-Ziel": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Red Bull A": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Red Bull B": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Red Bull C,D,E": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Schönberg": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Steiermark Grandstand": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "T3": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "T10": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 9. Silverstone Circuit (UK)
    # GP Portal: british.gp — Only GA (579 EUR) and Farm Curve (719 EUR) available
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Silverstone Circuit": {
        "gp_portal_url": "https://www.british.gp/en/tickets",
        "gp_portal_status": "mostly_sold_out",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "General Admission": {"price_local": 579, "currency": "EUR", "price_usd": 631, "status": "available"},
            "Farm Curve": {"price_local": 719, "currency": "EUR", "price_usd": 784, "status": "available"},
            "Abbey A": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Abbey B": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Becketts": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Chapel": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Club Corner B & C": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Copse A/B/C/D": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Hamilton Straight A & B": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Luffield": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Stowe A/B/C": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Vale": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Village A & B": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Woodcote A & B": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Landostand": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 10. Circuit de Spa-Francorchamps (Belgium)
    # GP Portal: belgium.gp — Lots of availability with prices
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Circuit de Spa-Francorchamps": {
        "gp_portal_url": "https://www.belgium.gp/en/tickets",
        "gp_portal_status": "available",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "Bronze Area": {"price_local": 259, "currency": "EUR", "price_usd": 282, "status": "available"},
            "Blanchimont 17-27": {"price_local": 329, "currency": "EUR", "price_usd": 359, "status": "available"},
            "Bronze Area - Bruxelles": {"price_local": 359, "currency": "EUR", "price_usd": 391, "status": "available"},
            "Silver 5": {"price_local": 439, "currency": "EUR", "price_usd": 479, "status": "available"},  # 1 remaining
            "Speed Corner": {"price_local": 459, "currency": "EUR", "price_usd": 500, "status": "available"},
            "Combes 4": {"price_local": 499, "currency": "EUR", "price_usd": 544, "status": "available"},
            "Combes 2": {"price_local": 519, "currency": "EUR", "price_usd": 566, "status": "available"},
            "Silver 3": {"price_local": 579, "currency": "EUR", "price_usd": 631, "status": "available"},
            "Silver 4: Bruxelles": {"price_local": 589, "currency": "EUR", "price_usd": 642, "status": "available"},
            "Silver 2: Fan Zone": {"price_local": 639, "currency": "EUR", "price_usd": 697, "status": "available"},
            "Gold 7: Bis": {"price_local": 659, "currency": "EUR", "price_usd": 718, "status": "available"},
            "Gold 7 Ter: Endurance": {"price_local": 659, "currency": "EUR", "price_usd": 718, "status": "available"},
            "Gold 1: Pit": {"price_local": 879, "currency": "EUR", "price_usd": 958, "status": "available"},
            "Gold 2: GP2": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Gold 3: Eau-Rouge": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Gold 4: Eau Rouge": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Gold 6: Chicane": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Gold 7: La Source": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Gold 8: La Source": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Silver 1: Francorchamps": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Silver 6": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Combes 1": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Combes 3": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 11. Hungaroring (Hungary)
    # GP Portal: f1hungary.com — Only GA (279 EUR) and Fan 2 (349 EUR) available
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Hungaroring": {
        "gp_portal_url": "https://www.f1hungary.com/en/tickets",
        "gp_portal_status": "mostly_sold_out",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "General Admission": {"price_local": 279, "currency": "EUR", "price_usd": 304, "status": "available"},
            "Grandstand Fan 2": {"price_local": 349, "currency": "EUR", "price_usd": 380, "status": "available"},
            "Grandstand Chicane 1-4": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand Apex 1-2": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand Hungaroring": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand Pit Exit 1-2": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand T1": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand Grid 1-3": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand Grand Prix 1-2": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Podium Grandstand": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 12. Circuit Zandvoort (Netherlands)
    # GP Portal: dutchtickets.gp — Only Ben Pon 2 (799 EUR) and Eastside 3 (839 EUR) available
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Circuit Zandvoort": {
        "gp_portal_url": "https://www.dutchtickets.gp/en/tickets",
        "gp_portal_status": "mostly_sold_out",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "Ben Pon 2 (Silver)": {"price_local": 799, "currency": "EUR", "price_usd": 871, "status": "available"},
            "Eastside 3 (Gold)": {"price_local": 839, "currency": "EUR", "price_usd": 915, "status": "available"},
            "General Admission": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Ben Pon Gold": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Eastside 2A": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Eastside 2B": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Arena-In 1": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Arena-In 2": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Eastside 1": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Pit Grandstand": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Main Grandstand": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Tarzan-In 1": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "General Admission 2": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 13. Autodromo Nazionale di Monza (Italy)
    # GP Portal: f1italy.com — Many grandstands available with prices
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Autodromo Nazionale di Monza": {
        "gp_portal_url": "https://www.f1italy.com/en/tickets",
        "gp_portal_status": "available",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "General Admission (Settore 8)": {"price_local": 219, "currency": "EUR", "price_usd": 239, "status": "available"},
            "Grandstand 5 (Piscina)": {"price_local": 699, "currency": "EUR", "price_usd": 762, "status": "available"},
            "Grandstand 14": {"price_local": 699, "currency": "EUR", "price_usd": 762, "status": "available"},
            "Grandstand 21 A": {"price_local": 699, "currency": "EUR", "price_usd": 762, "status": "available"},
            "Grandstand 21 B": {"price_local": 699, "currency": "EUR", "price_usd": 762, "status": "available"},
            "Grandstand 18": {"price_local": 699, "currency": "EUR", "price_usd": 762, "status": "available"},
            "Grandstand 17A (Ascari)": {"price_local": 699, "currency": "EUR", "price_usd": 762, "status": "available"},
            "Grandstand 4": {"price_local": 789, "currency": "EUR", "price_usd": 860, "status": "available"},
            "Grandstand 8A": {"price_local": 789, "currency": "EUR", "price_usd": 860, "status": "available"},
            "Grandstand 8B": {"price_local": 789, "currency": "EUR", "price_usd": 860, "status": "available"},
            "Grandstand 22": {"price_local": 789, "currency": "EUR", "price_usd": 860, "status": "available"},
            "Grandstand 34": {"price_local": 789, "currency": "EUR", "price_usd": 860, "status": "available"},
            "Biassono 7": {"price_local": 789, "currency": "EUR", "price_usd": 860, "status": "available"},
            "Grandstand 16 (Ascari)": {"price_local": 899, "currency": "EUR", "price_usd": 980, "status": "available"},
            "Grandstand 9": {"price_local": 899, "currency": "EUR", "price_usd": 980, "status": "available"},
            "Grandstand 6 C": {"price_local": 1199, "currency": "EUR", "price_usd": 1307, "status": "available"},
            "Grandstand 1": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 2": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 3": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 6 A (3-day)": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 6 B": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 14. Madrid Street Circuit (Spain)
    # GP Portal: spainf1.com — All "Notify me", no prices displayed (widget-based)
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Madrid Street Circuit": {
        "gp_portal_url": "https://www.spainf1.com/en/tickets",
        "gp_portal_status": "unavailable",  # All "Notify me", no prices shown
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "General Admission (Pelouse)": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 1": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 2": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 3": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 4": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 5": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 6": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 7": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 8": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 9": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 10": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "not_available"},
            "Grandstand 11": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 12": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 13": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 14": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 15": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
            "Grandstand 16": {"price_local": None, "currency": "EUR", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 15. Baku City Circuit (Azerbaijan)
    # GP Portal: azerbaijanf1.com — Many grandstands available with discounted prices
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Baku City Circuit": {
        "gp_portal_url": "https://www.azerbaijanf1.com/en/tickets",
        "gp_portal_status": "available",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "Grandstand Zafar": {"price_local": 399, "currency": "USD", "price_usd": 399, "status": "available"},
            "Grandstand Filarmoniya": {"price_local": 439, "currency": "USD", "price_usd": 439, "status": "available"},
            "Grandstand Giz Galasi": {"price_local": 459, "currency": "USD", "price_usd": 459, "status": "available"},
            "Grandstand Bulvar": {"price_local": 459, "currency": "USD", "price_usd": 459, "status": "available"},
            "Grandstand Khazar": {"price_local": 459, "currency": "USD", "price_usd": 459, "status": "available"},
            "Grandstand Marine": {"price_local": 499, "currency": "USD", "price_usd": 499, "status": "available"},
            "Grandstand Mugham": {"price_local": 669, "currency": "USD", "price_usd": 669, "status": "available"},
            "Grandstand Icheri Sheher": {"price_local": 689, "currency": "USD", "price_usd": 689, "status": "available"},
            "Grandstand Azneft": {"price_local": 729, "currency": "USD", "price_usd": 729, "status": "available"},
            "Grandstand Champions": {"price_local": 879, "currency": "USD", "price_usd": 879, "status": "available"},
            "Grandstand Absheron A": {"price_local": 1149, "currency": "USD", "price_usd": 1149, "status": "available"},
            "Grandstand Absheron B": {"price_local": 1149, "currency": "USD", "price_usd": 1149, "status": "available"},
            "Grandstand Absheron C": {"price_local": 1219, "currency": "USD", "price_usd": 1219, "status": "available"},
            "Grandstand Absheron D": {"price_local": 1219, "currency": "USD", "price_usd": 1219, "status": "available"},
            "Grandstand Absheron E": {"price_local": 1149, "currency": "USD", "price_usd": 1149, "status": "available"},
            "Grandstand Sahil": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "General Admission (Roaming)": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
        },
    },

    # =========================================================================
    # 16. Marina Bay Street Circuit (Singapore)
    # GP Portal: f1-singapore.com — All "Notify me" or "Not available", no prices
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Marina Bay Street Circuit": {
        "gp_portal_url": "https://www.f1-singapore.com/en/tickets",
        "gp_portal_status": "unavailable",  # All "Notify me", no prices displayed
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "General Admission - Walkabout": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Republic": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Raffles": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Turn 1": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Pit": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Super Pit Grandstand": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Marina Bay Grandstand": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Bayfront": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Padang": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Connaught": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
        },
    },

    # =========================================================================
    # 17. Circuit of the Americas (USA)
    # GP Portal: austin.gp — 3 grandstands available with prices
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Circuit of the Americas": {
        "gp_portal_url": "https://www.austin.gp/en/tickets",
        "gp_portal_status": "available",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "Grandstand Turn 9": {"price_local": 759, "currency": "USD", "price_usd": 759, "status": "available"},
            "Grandstand Turn 12": {"price_local": 1009, "currency": "USD", "price_usd": 1009, "status": "available"},
            "Grandstand Turn 15": {"price_local": 1239, "currency": "USD", "price_usd": 1239, "status": "available"},
            "Grandstand Main": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Turn 1": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Turn 4": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Turn 13": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Turn 19": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "General Admission": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 18. Autodromo Hermanos Rodriguez (Mexico)
    # GP Portal: mexico.gp — 9 grandstands available with prices
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Autodromo Hermanos Rodriguez": {
        "gp_portal_url": "https://www.mexico.gp/en/tickets",
        "gp_portal_status": "available",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "Grandstand 2A": {"price_local": 509, "currency": "USD", "price_usd": 509, "status": "available"},
            "Grandstand 6A": {"price_local": 659, "currency": "USD", "price_usd": 659, "status": "available"},
            "Grandstand 15": {"price_local": 739, "currency": "USD", "price_usd": 739, "status": "available"},
            "Grandstand 14": {"price_local": 809, "currency": "USD", "price_usd": 809, "status": "available"},
            "Grandstand 3A": {"price_local": 859, "currency": "USD", "price_usd": 859, "status": "available"},
            "Grandstand 6": {"price_local": 1059, "currency": "USD", "price_usd": 1059, "status": "available"},
            "Grandstand 5A": {"price_local": 1129, "currency": "USD", "price_usd": 1129, "status": "available"},
            "Grandstand 4": {"price_local": 1149, "currency": "USD", "price_usd": 1149, "status": "available"},
            "Grandstand 5": {"price_local": 1149, "currency": "USD", "price_usd": 1149, "status": "available"},
            "Grandstand Main 1": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand Main 2": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 6B": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 7": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 8": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 9": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 10": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand 11": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 19. Interlagos (Brazil)
    # GP Portal: brasilf1.com — All grandstands "Not Available", no prices
    # F1 Official: 200 OK (page exists)
    # =========================================================================
    "Interlagos": {
        "gp_portal_url": "https://www.brasilf1.com/en/tickets",
        "gp_portal_status": "sold_out",  # All grandstands "Not Available"
        "f1_store_status": "available",  # 200
        "verified_date": "2026-03-27",
        "sections": {
            "Grandstand A": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand B": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand M": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand D": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand G": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand H": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand N": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand R": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand S": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
            "Grandstand V": {"price_local": None, "currency": "USD", "price_usd": None, "status": "sold_out"},
        },
    },

    # =========================================================================
    # 20. Las Vegas Street Circuit (USA)
    # GP Portal: lasvegas.gp — All "Not Available", no prices (reseller site)
    # F1 Official: 200 OK (page exists)
    # =========================================================================
    "Las Vegas Street Circuit": {
        "gp_portal_url": "https://www.lasvegas.gp/en/tickets",
        "gp_portal_status": "unavailable",  # All "Not Available", reseller site
        "f1_store_status": "available",  # 200
        "verified_date": "2026-03-27",
        "sections": {
            "Grandstand T-Mobile": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "Heineken Silver Main Grandstand": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "Grandstand West Harmon": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "Grandstand SG1 Sphere": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "Grandstand SG7 Sphere": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "General Admission: T-Mobile Zone": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "General Admission: Flamingo": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "General Admission: Caesar's Palace": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
        },
    },

    # =========================================================================
    # 21. Losail International Circuit (Qatar)
    # GP Portal: qatar.gp — 6 ticket options available with prices
    # F1 Official: 200 OK (page exists)
    # =========================================================================
    "Losail International Circuit": {
        "gp_portal_url": "https://www.qatar.gp/en/tickets",
        "gp_portal_status": "available",
        "f1_store_status": "available",  # 200
        "verified_date": "2026-03-27",
        "sections": {
            "General Admission": {"price_local": 229, "currency": "USD", "price_usd": 229, "status": "available"},
            "Grandstand T2": {"price_local": 349, "currency": "USD", "price_usd": 349, "status": "available"},
            "Grandstand T3": {"price_local": 349, "currency": "USD", "price_usd": 349, "status": "available"},
            "Grandstand T16": {"price_local": 349, "currency": "USD", "price_usd": 349, "status": "available"},
            "Grandstand Nord": {"price_local": 499, "currency": "USD", "price_usd": 499, "status": "available"},
            "Grandstand Main": {"price_local": 679, "currency": "USD", "price_usd": 679, "status": "available"},
        },
    },

    # =========================================================================
    # 22. Yas Marina Circuit (Abu Dhabi)
    # GP Portal: abudhabi.gp — Many grandstands available with prices (reseller site)
    # F1 Official: 302 redirect (page exists)
    # =========================================================================
    "Yas Marina Circuit": {
        "gp_portal_url": "https://www.abudhabi.gp/en/tickets",
        "gp_portal_status": "available",
        "f1_store_status": "available",  # 302
        "verified_date": "2026-03-27",
        "sections": {
            "Grandstand West Straight": {"price_local": 899, "currency": "USD", "price_usd": 899, "status": "available"},
            "Grandstand North Straight": {"price_local": 999, "currency": "USD", "price_usd": 999, "status": "available"},
            "Grandstand Marina": {"price_local": 1309, "currency": "USD", "price_usd": 1309, "status": "available"},
            "Grandstand South (Marina)": {"price_local": 1379, "currency": "USD", "price_usd": 1379, "status": "available"},
            "Grandstand Nord": {"price_local": 1469, "currency": "USD", "price_usd": 1469, "status": "available"},
            "Grandstand West": {"price_local": 1499, "currency": "USD", "price_usd": 1499, "status": "available"},
            "West Social Club": {"price_local": 1889, "currency": "USD", "price_usd": 1889, "status": "available"},
            "Grandstand Main": {"price_local": 2319, "currency": "USD", "price_usd": 2319, "status": "available"},
            "West Premium": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
            "General Admission - Abu Dhabi Hill": {"price_local": None, "currency": "USD", "price_usd": None, "status": "not_available"},
        },
    },
}
