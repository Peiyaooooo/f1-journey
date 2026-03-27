import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Circuit, SeatSection

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
    sections = [
        SeatSection(
            circuit_id=circuit.id, name="Wellington Straight", section_type="grandstand",
            location_on_track="Turn 1-3", has_roof=True, has_screen=True,
            pit_view=False, podium_view=False, latitude=52.0730, longitude=-1.0140,
            view_description="Great view of braking into Turn 1.",
            view_photos=json.dumps(["https://example.com/wellington.jpg"]),
        ),
        SeatSection(
            circuit_id=circuit.id, name="Copse", section_type="grandstand",
            location_on_track="Turn 9", has_roof=False, has_screen=True,
            pit_view=False, podium_view=False, latitude=52.0780, longitude=-1.0050,
        ),
        SeatSection(
            circuit_id=circuit.id, name="Inner GA", section_type="general_admission",
            location_on_track="Various", has_roof=False, has_screen=False,
            pit_view=False, podium_view=False, latitude=52.0750, longitude=-1.0100,
        ),
    ]
    db.add_all(sections)
    db.commit()
    db.close()


def teardown_function():
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(engine)


def test_list_sections_for_circuit():
    resp = client.get("/api/circuits/1/sections")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3


def test_list_sections_filter_by_type():
    resp = client.get("/api/circuits/1/sections?section_type=grandstand")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(s["section_type"] == "grandstand" for s in data)


def test_list_sections_filter_by_roof():
    resp = client.get("/api/circuits/1/sections?has_roof=true")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Wellington Straight"


def test_get_section_by_id():
    resp = client.get("/api/sections/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Wellington Straight"
    assert data["has_roof"] is True
    assert data["view_photos"] == ["https://example.com/wellington.jpg"]


def test_get_section_not_found():
    resp = client.get("/api/sections/999")
    assert resp.status_code == 404


def test_list_sections_for_nonexistent_circuit():
    resp = client.get("/api/circuits/999/sections")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0
