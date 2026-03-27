from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Circuit, RaceEvent

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
        name="Silverstone", country="United Kingdom", continent="Europe",
        city="Silverstone", latitude=52.07, longitude=-1.01,
        track_type="permanent", track_length_km=5.891, number_of_turns=18,
        drs_zones_count=2, overtake_difficulty=6, avg_overtakes_per_race=42.5,
        rain_probability_pct=55, nearest_airport="London Luton",
    )
    db.add(circuit)
    db.commit()
    events = [
        RaceEvent(
            circuit_id=circuit.id, season_year=2026, race_name="British Grand Prix",
            race_date=date(2026, 7, 5), sprint_weekend=False, status="upcoming",
        ),
        RaceEvent(
            circuit_id=circuit.id, season_year=2025, race_name="British Grand Prix 2025",
            race_date=date(2025, 7, 6), sprint_weekend=False, status="completed",
            total_overtakes=45,
        ),
    ]
    db.add_all(events)
    db.commit()
    db.close()


def teardown_function():
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(engine)


def test_list_race_events():
    resp = client.get("/api/race-events")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_list_race_events_filter_by_season():
    resp = client.get("/api/race-events?season=2026")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["season_year"] == 2026


def test_list_race_events_filter_by_status():
    resp = client.get("/api/race-events?status=upcoming")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "upcoming"


def test_get_race_event_by_id():
    resp = client.get("/api/race-events/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["race_name"] == "British Grand Prix"
    assert data["circuit_name"] == "Silverstone"


def test_get_race_event_not_found():
    resp = client.get("/api/race-events/999")
    assert resp.status_code == 404
