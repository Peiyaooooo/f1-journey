from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Circuit

TEST_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(TEST_DATABASE_URL)
TestSession = sessionmaker(bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.create_all(engine)
    db = TestSession()
    circuits = [
        Circuit(
            name="Silverstone", country="United Kingdom", continent="Europe",
            city="Silverstone", latitude=52.07, longitude=-1.01,
            track_type="permanent", track_length_km=5.891, number_of_turns=18,
            drs_zones_count=2, overtake_difficulty=6, avg_overtakes_per_race=42.5,
            rain_probability_pct=55, nearest_airport="London Luton",
        ),
        Circuit(
            name="Monza", country="Italy", continent="Europe",
            city="Monza", latitude=45.62, longitude=9.28,
            track_type="permanent", track_length_km=5.793, number_of_turns=11,
            drs_zones_count=2, overtake_difficulty=7, avg_overtakes_per_race=48.0,
            rain_probability_pct=20, nearest_airport="Milan Malpensa",
        ),
        Circuit(
            name="Marina Bay", country="Singapore", continent="Asia",
            city="Singapore", latitude=1.29, longitude=103.86,
            track_type="street", track_length_km=4.940, number_of_turns=19,
            drs_zones_count=3, overtake_difficulty=3, avg_overtakes_per_race=18.0,
            rain_probability_pct=40, nearest_airport="Changi",
        ),
    ]
    db.add_all(circuits)
    db.commit()
    db.close()


def teardown_function():
    Base.metadata.drop_all(engine)


def test_list_circuits():
    resp = client.get("/api/circuits")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    # Results are ordered alphabetically by name: Marina Bay < Monza < Silverstone
    assert data[0]["name"] == "Marina Bay"


def test_list_circuits_filter_by_continent():
    resp = client.get("/api/circuits?continent=Asia")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Marina Bay"


def test_list_circuits_filter_by_track_type():
    resp = client.get("/api/circuits?track_type=street")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["track_type"] == "street"


def test_get_circuit_by_id():
    resp = client.get("/api/circuits/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Silverstone"
    assert data["overtake_difficulty"] == 6


def test_get_circuit_not_found():
    resp = client.get("/api/circuits/999")
    assert resp.status_code == 404
