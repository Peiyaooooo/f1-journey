from datetime import date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Circuit, RaceEvent, SeatSection, TicketListing

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


def setup_function():
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = override_get_db
    db = TestSession()

    circuit = Circuit(
        name="Silverstone", country="Great Britain", continent="Europe",
        city="Silverstone", latitude=52.07, longitude=-1.01,
        track_type="permanent", track_length_km=5.891, number_of_turns=18,
        drs_zones_count=2, overtake_difficulty=4, avg_overtakes_per_race=42.5,
        rain_probability_pct=55, nearest_airport="LTN",
    )
    db.add(circuit)
    db.commit()

    event = RaceEvent(
        circuit_id=circuit.id, season_year=2026, race_name="British Grand Prix",
        race_date=date(2026, 7, 5), sprint_weekend=False, status="upcoming",
    )
    db.add(event)
    db.commit()

    section = SeatSection(
        circuit_id=circuit.id, name="Wellington Straight", section_type="grandstand",
        location_on_track="Turn 1-3", has_roof=True, has_screen=True,
        pit_view=False, podium_view=False, latitude=52.0730, longitude=-1.0140,
    )
    db.add(section)
    db.commit()

    scraped_at = datetime(2026, 3, 1, 12, 0, 0)

    tickets = [
        # Matched ticket 1 — stubhub, cheaper
        TicketListing(
            circuit_id=circuit.id, race_event_id=event.id,
            seat_section_id=section.id,
            source_site="stubhub", source_url="https://stubhub.com/t/1",
            source_section_name="Wellington Straight GA",
            ticket_type="grandstand", price=150.0, currency="GBP",
            available_quantity=4, last_scraped_at=scraped_at, is_available=True,
        ),
        # Matched ticket 2 — viagogo, more expensive
        TicketListing(
            circuit_id=circuit.id, race_event_id=event.id,
            seat_section_id=section.id,
            source_site="viagogo", source_url="https://viagogo.com/t/2",
            source_section_name="Wellington Straight",
            ticket_type="grandstand", price=300.0, currency="GBP",
            available_quantity=2, last_scraped_at=scraped_at, is_available=True,
        ),
        # Unmatched ticket — no seat_section_id
        TicketListing(
            circuit_id=circuit.id, race_event_id=event.id,
            seat_section_id=None,
            source_site="stubhub", source_url="https://stubhub.com/t/3",
            source_section_name="Mystery Grandstand",
            ticket_type="grandstand", price=200.0, currency="GBP",
            available_quantity=1, last_scraped_at=scraped_at, is_available=True,
        ),
    ]
    db.add_all(tickets)
    db.commit()
    db.close()


def teardown_function():
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(engine)


def test_list_circuit_tickets():
    resp = client.get("/api/circuits/1/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3


def test_list_circuit_tickets_filter_by_source():
    resp = client.get("/api/circuits/1/tickets?source_site=stubhub")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(t["source_site"] == "stubhub" for t in data)


def test_list_circuit_tickets_sort_price_asc():
    resp = client.get("/api/circuits/1/tickets?sort=price_asc")
    assert resp.status_code == 200
    data = resp.json()
    prices = [t["price"] for t in data]
    assert prices == sorted(prices)


def test_list_circuit_tickets_sort_price_desc():
    resp = client.get("/api/circuits/1/tickets?sort=price_desc")
    assert resp.status_code == 200
    data = resp.json()
    prices = [t["price"] for t in data]
    assert prices == sorted(prices, reverse=True)


def test_list_section_tickets():
    resp = client.get("/api/sections/1/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(t["seat_section_id"] == 1 for t in data)


def test_list_unmatched_tickets():
    resp = client.get("/api/circuits/1/tickets/unmatched")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["seat_section_id"] is None
    assert data[0]["source_section_name"] == "Mystery Grandstand"


def test_list_circuit_tickets_nonexistent_circuit():
    resp = client.get("/api/circuits/999/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0


def test_list_section_tickets_nonexistent_section():
    resp = client.get("/api/sections/999/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0
