from datetime import date, datetime

from app.models.circuit import Circuit
from app.models.race_event import RaceEvent
from app.models.seat_section import SeatSection
from app.models.ticket_listing import TicketListing


def test_create_ticket_listing_matched(db):
    circuit = Circuit(
        name="Monza", country="Italy", continent="Europe", city="Monza",
        latitude=45.62, longitude=9.28, track_type="permanent",
        track_length_km=5.793, number_of_turns=11, drs_zones_count=2,
        overtake_difficulty=2, avg_overtakes_per_race=48.0,
        rain_probability_pct=20, nearest_airport="MXP",
    )
    db.add(circuit)
    db.commit()

    event = RaceEvent(
        circuit_id=circuit.id, season_year=2026, race_name="Italian GP",
        race_date=date(2026, 9, 6), sprint_weekend=False, status="upcoming",
    )
    db.add(event)
    db.commit()

    section = SeatSection(
        circuit_id=circuit.id, name="Central Grandstand",
        section_type="grandstand", has_roof=True, has_screen=True,
        pit_view=True, podium_view=True, latitude=45.618, longitude=9.281,
    )
    db.add(section)
    db.commit()

    listing = TicketListing(
        circuit_id=circuit.id, race_event_id=event.id, seat_section_id=section.id,
        source_site="stubhub", source_url="https://stubhub.com/listing/123",
        source_section_name="Central Grandstand", ticket_type="weekend",
        price=450.00, currency="EUR", available_quantity=5,
        last_scraped_at=datetime.utcnow(), is_available=True,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)

    assert listing.id is not None
    assert listing.price == 450.00
    assert listing.seat_section_id == section.id


def test_create_ticket_listing_unmatched(db):
    circuit = Circuit(
        name="Spa", country="Belgium", continent="Europe", city="Spa",
        latitude=50.44, longitude=5.97, track_type="permanent",
        track_length_km=7.004, number_of_turns=19, drs_zones_count=2,
        overtake_difficulty=2, avg_overtakes_per_race=55.0,
        rain_probability_pct=60, nearest_airport="BRU",
    )
    db.add(circuit)
    db.commit()

    event = RaceEvent(
        circuit_id=circuit.id, season_year=2026, race_name="Belgian GP",
        race_date=date(2026, 7, 19), sprint_weekend=False, status="upcoming",
    )
    db.add(event)
    db.commit()

    listing = TicketListing(
        circuit_id=circuit.id, race_event_id=event.id, seat_section_id=None,
        source_site="viagogo", source_url="https://viagogo.com/listing/456",
        source_section_name="Unknown Zone XYZ", ticket_type="sunday",
        price=200.00, currency="EUR", available_quantity=None,
        last_scraped_at=datetime.utcnow(), is_available=True,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)

    assert listing.id is not None
    assert listing.seat_section_id is None
