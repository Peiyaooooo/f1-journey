"""Seed multi-source ticket listings from the comprehensive seat section data (v2).

For each seat section that has ticket data, generates 3-5 ticket listings from
different sources (F1 Official, GP Portal, StubHub, SeatGeek, Viagogo) with
realistic price variations.  Uses seeded randomness for reproducible output.
"""

import random
from datetime import datetime
from urllib.parse import quote_plus

from app.models.ticket_listing import TicketListing
from app.seed.seat_sections_data_v2 import SEAT_SECTIONS_V2

# ---------------------------------------------------------------------------
# GP Portal URL mapping (official ticket sites for each circuit)
# ---------------------------------------------------------------------------

GP_PORTAL_URLS: dict[str, str] = {
    "Albert Park Circuit": "https://www.f1-australia.com.au/en/tickets",
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
    "Albert Park Circuit": "https://tickets.formula1.com/en/f1-3159-australia",
    "Shanghai International Circuit": "https://tickets.formula1.com/en/f1-3307-china",
    "Suzuka International Racing Course": "https://tickets.formula1.com/en/f1-3309-japan",
    "Miami International Autodrome": "https://tickets.formula1.com/en/f1-54987-miami",
    "Circuit Gilles Villeneuve": "https://tickets.formula1.com/en/f1-3168-canada",
    "Circuit de Monaco": "https://tickets.formula1.com/en/f1-3202-monaco",
    "Circuit de Barcelona-Catalunya": "https://tickets.formula1.com/en/f1-3285-spain",
    "Red Bull Ring": "https://tickets.formula1.com/en/f1-3236-austria",
    "Silverstone Circuit": "https://tickets.formula1.com/en/f1-3226-great-britain",
    "Circuit de Spa-Francorchamps": "https://tickets.formula1.com/en/f1-3163-belgium",
    "Hungaroring": "https://tickets.formula1.com/en/f1-3184-hungary",
    "Circuit Zandvoort": "https://tickets.formula1.com/en/f1-3205-netherlands",
    "Autodromo Nazionale di Monza": "https://tickets.formula1.com/en/f1-3293-italy",
    "Madrid Street Circuit": "https://tickets.formula1.com/en/f1-3285-spain",
    "Baku City Circuit": "https://tickets.formula1.com/en/f1-3155-azerbaijan",
    "Marina Bay Street Circuit": "https://tickets.formula1.com/en/f1-3301-singapore",
    "Circuit of the Americas": "https://tickets.formula1.com/en/f1-3320-united-states",
    "Autodromo Hermanos Rodriguez": "https://tickets.formula1.com/en/f1-3200-mexico",
    "Interlagos": "https://tickets.formula1.com/en/f1-3167-brazil",
    "Las Vegas Street Circuit": "https://tickets.formula1.com/en/f1-55042-las-vegas",
    "Losail International Circuit": "https://tickets.formula1.com/en/f1-55041-qatar",
    "Yas Marina Circuit": "https://tickets.formula1.com/en/f1-3152-abu-dhabi",
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
# Resale site slugs (for StubHub and SeatGeek deep-link URLs)
# ---------------------------------------------------------------------------

CIRCUIT_RESALE_SLUG: dict[str, str] = {
    "Albert Park Circuit": "formula-1-australian-grand-prix",
    "Shanghai International Circuit": "formula-1-chinese-grand-prix",
    "Suzuka International Racing Course": "formula-1-japanese-grand-prix",
    "Miami International Autodrome": "formula-1-miami-grand-prix",
    "Circuit Gilles Villeneuve": "formula-1-canadian-grand-prix",
    "Circuit de Monaco": "formula-1-monaco-grand-prix",
    "Circuit de Barcelona-Catalunya": "formula-1-spanish-grand-prix",
    "Red Bull Ring": "formula-1-austrian-grand-prix",
    "Silverstone Circuit": "formula-1-british-grand-prix",
    "Circuit de Spa-Francorchamps": "formula-1-belgian-grand-prix",
    "Hungaroring": "formula-1-hungarian-grand-prix",
    "Circuit Zandvoort": "formula-1-dutch-grand-prix",
    "Autodromo Nazionale di Monza": "formula-1-italian-grand-prix",
    "Madrid Street Circuit": "formula-1-spanish-grand-prix",
    "Baku City Circuit": "formula-1-azerbaijan-grand-prix",
    "Marina Bay Street Circuit": "formula-1-singapore-grand-prix",
    "Circuit of the Americas": "formula-1-united-states-grand-prix",
    "Autodromo Hermanos Rodriguez": "formula-1-mexico-city-grand-prix",
    "Interlagos": "formula-1-sao-paulo-grand-prix",
    "Las Vegas Street Circuit": "formula-1-las-vegas-grand-prix",
    "Losail International Circuit": "formula-1-qatar-grand-prix",
    "Yas Marina Circuit": "formula-1-abu-dhabi-grand-prix",
}


def _build_source_url(source: str, circuit_name: str) -> str:
    """Build the source URL for a given source site and circuit."""
    race_name = CIRCUIT_RACE_NAME.get(circuit_name, "Formula 1")
    encoded_race = quote_plus(race_name)
    resale_slug = CIRCUIT_RESALE_SLUG.get(circuit_name, "")

    if source == "f1_official":
        return F1_TICKET_URLS.get(circuit_name, "https://tickets.formula1.com/en")
    elif source == "gp_portal":
        return GP_PORTAL_URLS.get(circuit_name, "")
    elif source == "stubhub":
        return f"https://www.stubhub.com/{resale_slug}-tickets/" if resale_slug else f"https://www.stubhub.com/search?q={encoded_race}"
    elif source == "seatgeek":
        return f"https://seatgeek.com/{resale_slug}-tickets" if resale_slug else f"https://seatgeek.com/search?search={encoded_race}"
    elif source == "viagogo":
        return f"https://www.viagogo.com/search?q={encoded_race}"
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
