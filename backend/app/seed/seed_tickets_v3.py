"""Seed multi-source ticket listings from the comprehensive seat section data (v2).

For each seat section that has ticket data, generates 3-5 ticket listings from
different sources (F1 Official, GP Portal, StubHub, SeatGeek, Viagogo) with
realistic price variations.  Uses seeded randomness for reproducible output.
"""

import random
from datetime import datetime
from app.models.ticket_listing import TicketListing
from app.seed.seat_sections_data_v2 import SEAT_SECTIONS_V2

# ---------------------------------------------------------------------------
# GP Portal URL mapping (official ticket sites for each circuit)
# ---------------------------------------------------------------------------

GP_PORTAL_URLS: dict[str, str] = {
    "Albert Park Circuit": "https://www.grandprix.com.au",
    "Shanghai International Circuit": "https://www.formula1shanghai.com/en/tickets",
    "Suzuka International Racing Course": "https://www.japan.gp/en/tickets",
    "Miami International Autodrome": "https://www.f1miamiusa.com/en/tickets",
    "Circuit Gilles Villeneuve": "https://www.canada.gp/en/tickets",
    "Circuit de Monaco": "https://www.f1monaco.com/en/tickets",
    "Circuit de Barcelona-Catalunya": "https://www.barcelonaf1.com/en/tickets",
    "Red Bull Ring": "https://www.f1austria.com/en/tickets",
    "Silverstone Circuit": "https://www.british.gp/en/tickets",
    "Circuit de Spa-Francorchamps": "https://www.belgium.gp/en/tickets",
    "Hungaroring": "https://www.f1hungary.com/en/tickets",
    "Circuit Zandvoort": "https://www.dutchtickets.gp/en/tickets",
    "Autodromo Nazionale di Monza": "https://www.f1italy.com/en/tickets",
    "Madrid Street Circuit": "https://www.spainf1.com/en/tickets",
    "Baku City Circuit": "https://www.azerbaijanf1.com/en/tickets",
    "Marina Bay Street Circuit": "https://www.f1-singapore.com/en/tickets",
    "Circuit of the Americas": "https://www.austin.gp/en/tickets",
    "Autodromo Hermanos Rodriguez": "https://www.mexico.gp/en/tickets",
    "Interlagos": "https://www.brasilf1.com/en/tickets",
    "Las Vegas Street Circuit": "https://www.lasvegas.gp/en/tickets",
    "Losail International Circuit": "https://www.qatar.gp/en/tickets",
    "Yas Marina Circuit": "https://www.abudhabi.gp/en/tickets",
}

# ---------------------------------------------------------------------------
# F1 Official ticket URLs (real URLs with correct event IDs)
# ---------------------------------------------------------------------------

F1_TICKET_URLS: dict[str, str] = {
    "Albert Park Circuit": "https://www.formula1.com/en/racing/2026/australia",
    "Shanghai International Circuit": "https://www.formula1.com/en/racing/2026/china",
    "Suzuka International Racing Course": "https://www.formula1.com/en/racing/2026/japan",
    "Miami International Autodrome": "https://www.formula1.com/en/racing/2026/miami",
    "Circuit Gilles Villeneuve": "https://www.formula1.com/en/racing/2026/canada",
    "Circuit de Monaco": "https://www.formula1.com/en/racing/2026/monaco",
    "Circuit de Barcelona-Catalunya": "https://www.formula1.com/en/racing/2026/barcelona-catalunya",
    "Red Bull Ring": "https://www.formula1.com/en/racing/2026/austria",
    "Silverstone Circuit": "https://www.formula1.com/en/racing/2026/great-britain",
    "Circuit de Spa-Francorchamps": "https://www.formula1.com/en/racing/2026/belgium",
    "Hungaroring": "https://www.formula1.com/en/racing/2026/hungary",
    "Circuit Zandvoort": "https://www.formula1.com/en/racing/2026/netherlands",
    "Autodromo Nazionale di Monza": "https://www.formula1.com/en/racing/2026/italy",
    "Madrid Street Circuit": "https://www.formula1.com/en/racing/2026/spain",
    "Baku City Circuit": "https://www.formula1.com/en/racing/2026/azerbaijan",
    "Marina Bay Street Circuit": "https://www.formula1.com/en/racing/2026/singapore",
    "Circuit of the Americas": "https://www.formula1.com/en/racing/2026/united-states",
    "Autodromo Hermanos Rodriguez": "https://www.formula1.com/en/racing/2026/mexico",
    "Interlagos": "https://www.formula1.com/en/racing/2026/brazil",
    "Las Vegas Street Circuit": "https://www.formula1.com/en/racing/2026/las-vegas",
    "Losail International Circuit": "https://www.formula1.com/en/racing/2026/qatar",
    "Yas Marina Circuit": "https://www.formula1.com/en/racing/2026/united-arab-emirates",
}

# ---------------------------------------------------------------------------
# Circuit name -> race name (for resale site search queries)
# ---------------------------------------------------------------------------

CIRCUIT_RACE_NAME: dict[str, str] = {
    "Albert Park Circuit": "Australian Grand Prix",
    "Shanghai International Circuit": "Chinese Grand Prix",
    "Suzuka International Racing Course": "Japanese Grand Prix",
    "Miami International Autodrome": "Miami Grand Prix",
    "Circuit Gilles Villeneuve": "Canadian Grand Prix",
    "Circuit de Monaco": "Monaco Grand Prix",
    "Circuit de Barcelona-Catalunya": "Barcelona-Catalunya Grand Prix",
    "Red Bull Ring": "Austrian Grand Prix",
    "Silverstone Circuit": "British Grand Prix",
    "Circuit de Spa-Francorchamps": "Belgian Grand Prix",
    "Hungaroring": "Hungarian Grand Prix",
    "Circuit Zandvoort": "Dutch Grand Prix",
    "Autodromo Nazionale di Monza": "Italian Grand Prix",
    "Madrid Street Circuit": "Spanish Grand Prix",
    "Baku City Circuit": "Azerbaijan Grand Prix",
    "Marina Bay Street Circuit": "Singapore Grand Prix",
    "Circuit of the Americas": "United States Grand Prix",
    "Autodromo Hermanos Rodriguez": "Mexico City Grand Prix",
    "Interlagos": "Sao Paulo Grand Prix",
    "Las Vegas Street Circuit": "Las Vegas Grand Prix",
    "Losail International Circuit": "Qatar Grand Prix",
    "Yas Marina Circuit": "Abu Dhabi Grand Prix",
}

# ---------------------------------------------------------------------------
# StubHub URLs (verified working URL patterns)
# ---------------------------------------------------------------------------

STUBHUB_URLS: dict[str, str] = {
    "Albert Park Circuit": "https://www.stubhub.com/f1-australian-grand-prix-melbourne-tickets/performer/100477919",
    "Shanghai International Circuit": "https://www.stubhub.com/chinese-grand-prix-tickets",
    "Suzuka International Racing Course": "https://www.stubhub.com/japanese-grand-prix-tickets",
    "Miami International Autodrome": "https://www.stubhub.com/miami-grand-prix-tickets",
    "Circuit Gilles Villeneuve": "https://www.stubhub.com/canadian-grand-prix-tickets",
    "Circuit de Monaco": "https://www.stubhub.com/monaco-grand-prix-tickets",
    "Circuit de Barcelona-Catalunya": "https://www.stubhub.com/spanish-grand-prix-tickets",
    "Red Bull Ring": "https://www.stubhub.com/austria-grand-prix-tickets",
    "Silverstone Circuit": "https://www.stubhub.com/british-grand-prix-tickets",
    "Circuit de Spa-Francorchamps": "https://www.stubhub.com/belgian-grand-prix-tickets",
    "Hungaroring": "https://www.stubhub.com/hungarian-grand-prix-tickets",
    "Circuit Zandvoort": "https://www.stubhub.com/formula-1-dutch-grand-prix-tickets",
    "Autodromo Nazionale di Monza": "https://www.stubhub.com/italian-grand-prix-tickets",
    "Madrid Street Circuit": "https://www.stubhub.com/secure/search?q=Madrid+Grand+Prix+Formula+1",
    "Baku City Circuit": "https://www.stubhub.com/secure/search?q=Azerbaijan+Grand+Prix+Formula+1",
    "Marina Bay Street Circuit": "https://www.stubhub.com/singapore-grand-prix-tickets",
    "Circuit of the Americas": "https://www.stubhub.com/formula-1-united-states-grand-prix-tickets",
    "Autodromo Hermanos Rodriguez": "https://www.stubhub.com/secure/search?q=Mexico+City+Grand+Prix+Formula+1",
    "Interlagos": "https://www.stubhub.com/brazil-grand-prix-tickets",
    "Las Vegas Street Circuit": "https://www.stubhub.com/secure/search?q=Las+Vegas+Grand+Prix+Formula+1",
    "Losail International Circuit": "https://www.stubhub.com/secure/search?q=Qatar+Grand+Prix+Formula+1",
    "Yas Marina Circuit": "https://www.stubhub.com/secure/search?q=Abu+Dhabi+Grand+Prix+Formula+1",
}

# ---------------------------------------------------------------------------
# SeatGeek URLs (verified working URL patterns)
# ---------------------------------------------------------------------------

SEATGEEK_URLS: dict[str, str] = {
    "Albert Park Circuit": "https://seatgeek.com/australian-grand-prix-tickets",
    "Shanghai International Circuit": "https://seatgeek.com/chinese-grand-prix-tickets",
    "Suzuka International Racing Course": "https://seatgeek.com/japanese-grand-prix-tickets",
    "Miami International Autodrome": "https://seatgeek.com/miami-grand-prix-tickets",
    "Circuit Gilles Villeneuve": "https://seatgeek.com/canadian-grand-prix-tickets",
    "Circuit de Monaco": "https://seatgeek.com/monaco-grand-prix-tickets",
    "Circuit de Barcelona-Catalunya": "https://seatgeek.com/spanish-grand-prix-tickets",
    "Red Bull Ring": "https://seatgeek.com/austrian-grand-prix-tickets",
    "Silverstone Circuit": "https://seatgeek.com/british-grand-prix-tickets",
    "Circuit de Spa-Francorchamps": "https://seatgeek.com/belgian-grand-prix-tickets",
    "Hungaroring": "https://seatgeek.com/hungarian-grand-prix-tickets",
    "Circuit Zandvoort": "https://seatgeek.com/dutch-grand-prix-tickets",
    "Autodromo Nazionale di Monza": "https://seatgeek.com/italian-grand-prix-tickets",
    "Madrid Street Circuit": "https://seatgeek.com/madrid-grand-prix-tickets",
    "Baku City Circuit": "https://seatgeek.com/azerbaijan-grand-prix-tickets",
    "Marina Bay Street Circuit": "https://seatgeek.com/singapore-grand-prix-tickets",
    "Circuit of the Americas": "https://seatgeek.com/united-states-grand-prix-tickets",
    "Autodromo Hermanos Rodriguez": "https://seatgeek.com/mexican-grand-prix-tickets",
    "Interlagos": "https://seatgeek.com/sao-paulo-grand-prix-tickets",
    "Las Vegas Street Circuit": "https://seatgeek.com/las-vegas-grand-prix-tickets",
    "Losail International Circuit": "https://seatgeek.com/qatar-grand-prix-tickets",
    "Yas Marina Circuit": "https://seatgeek.com/abu-dhabi-grand-prix-tickets",
}

# ---------------------------------------------------------------------------
# Viagogo URL (single F1 category page for all circuits)
# ---------------------------------------------------------------------------

VIAGOGO_URL = "https://www.viagogo.com/Sports-Tickets/Motorsport/Formula-1"


def _build_source_url(source: str, circuit_name: str) -> str:
    """Build the source URL for a given source site and circuit."""
    if source == "f1_official":
        return F1_TICKET_URLS.get(circuit_name, "https://www.formula1.com/en/racing/2026")
    elif source == "gp_portal":
        return GP_PORTAL_URLS.get(circuit_name, "")
    elif source == "stubhub":
        return STUBHUB_URLS.get(circuit_name, "https://www.stubhub.com/f1-tickets")
    elif source == "seatgeek":
        return SEATGEEK_URLS.get(circuit_name, "https://seatgeek.com/f1-tickets")
    elif source == "viagogo":
        return VIAGOGO_URL
    return ""


# Source definitions: (source_site, price_low_mult, price_high_mult, is_resale)
SOURCE_CONFIGS = [
    ("f1_official", 1.00, 1.00, False),
    ("gp_portal", 0.95, 1.02, False),
    ("stubhub", 1.15, 1.30, True),
    ("seatgeek", 1.10, 1.25, True),
    ("viagogo", 1.20, 1.40, True),
]


def seed_tickets_v3(
    db,
    circuit_map: dict[str, int],
    event_map: dict[str, int],
    section_map: dict[int, dict[str, int]],
) -> int:
    """Seed multi-source ticket listings from the v2 seat section data.

    For each seat section with a ticket entry, generates 3-5 listings from
    different ticket sources with realistic price variations.

    Args:
        db: SQLAlchemy session
        circuit_map: {circuit_name: circuit_id}
        event_map: {circuit_name: race_event_id}
        section_map: {circuit_id: {section_name: section_id}}

    Returns:
        Number of ticket listings created.
    """
    random.seed(42)
    count = 0
    now = datetime.utcnow()

    for circuit_name, sections in SEAT_SECTIONS_V2.items():
        circuit_id = circuit_map.get(circuit_name)
        race_event_id = event_map.get(circuit_name)

        if circuit_id is None or race_event_id is None:
            print(f"Warning: no circuit/event for '{circuit_name}', skipping tickets")
            continue

        circuit_sections = section_map.get(circuit_id, {})

        for section in sections:
            tickets = section.get("tickets", [])
            if not tickets:
                continue

            # Use the first ticket entry as the base price reference
            base_ticket = tickets[0]
            base_price = base_ticket["price_usd"]
            ticket_type = base_ticket.get("ticket_type", "3-day")
            includes = base_ticket.get("includes", "")

            # Resolve the seat_section_id from the section name
            seat_section_id = circuit_sections.get(section["name"])

            # Pick 3-5 sources for this section
            num_sources = random.randint(3, 5)
            selected_sources = random.sample(SOURCE_CONFIGS, num_sources)

            # Always include f1_official if not already selected
            source_names = [s[0] for s in selected_sources]
            if "f1_official" not in source_names:
                # Replace a random resale source with f1_official
                for i, s in enumerate(selected_sources):
                    if s[3]:  # is_resale
                        selected_sources[i] = SOURCE_CONFIGS[0]  # f1_official
                        break

            for source_site, low_mult, high_mult, is_resale in selected_sources:
                # Compute price
                if low_mult == high_mult:
                    price = base_price
                else:
                    price = base_price * random.uniform(low_mult, high_mult)
                price = round(price)

                # Available quantity: random for resale, None for official
                available_quantity = random.randint(1, 50) if is_resale else None

                # Build includes text with source context
                if is_resale:
                    source_includes = f"{includes}\nResale marketplace — prices may vary. Verify section name matches before purchasing."
                else:
                    source_includes = includes

                source_url = _build_source_url(source_site, circuit_name)

                listing = TicketListing(
                    circuit_id=circuit_id,
                    race_event_id=race_event_id,
                    seat_section_id=seat_section_id,
                    source_site=source_site,
                    source_url=source_url,
                    source_section_name=section["name"],
                    ticket_type=ticket_type,
                    price=price,
                    currency="USD",
                    available_quantity=available_quantity,
                    includes=source_includes,
                    last_scraped_at=now,
                    is_available=True,
                )
                db.add(listing)
                count += 1

    return count
