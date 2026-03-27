"""Seed ticket listings from the comprehensive seat section data (v2).

Reads ticket info embedded in SEAT_SECTIONS_V2 and creates TicketListing entries
linked to the correct circuit, race event, and seat section.
"""

from datetime import datetime

from app.models.ticket_listing import TicketListing
from app.seed.seat_sections_data_v2 import SEAT_SECTIONS_V2


def seed_tickets_v2(
    db,
    circuit_map: dict[str, int],
    event_map: dict[str, int],
    section_map: dict[int, dict[str, int]],
) -> int:
    """Seed ticket listings from the v2 seat section data.

    Each seat section in SEAT_SECTIONS_V2 may contain a ``tickets`` list with
    one or more ticket entries.  This function iterates over every section and
    creates a TicketListing for each ticket entry, linking it to the matching
    circuit, race event, and seat section.

    Args:
        db: SQLAlchemy session
        circuit_map: {circuit_name: circuit_id}
        event_map: {circuit_name: race_event_id}
        section_map: {circuit_id: {section_name: section_id}}

    Returns:
        Number of ticket listings created.
    """
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

            # Resolve the seat_section_id from the section name
            seat_section_id = circuit_sections.get(section["name"])

            for t in tickets:
                listing = TicketListing(
                    circuit_id=circuit_id,
                    race_event_id=race_event_id,
                    seat_section_id=seat_section_id,
                    source_site=t.get("source", "official"),
                    source_url=t.get("source_url", ""),
                    source_section_name=section["name"],
                    ticket_type=t.get("ticket_type", "3-day"),
                    price=t["price_usd"],
                    currency="USD",
                    available_quantity=None,
                    includes=t.get("includes"),
                    last_scraped_at=now,
                    is_available=True,
                )
                db.add(listing)
                count += 1

    return count
