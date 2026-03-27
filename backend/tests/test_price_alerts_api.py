from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.circuit import Circuit

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
    # Seed a circuit for FK constraint
    db = TestSession()
    circuit = Circuit(
        id=1,
        name="Monza",
        country="Italy",
        continent="Europe",
        city="Monza",
        latitude=45.6156,
        longitude=9.2811,
        track_type="permanent",
        track_length_km=5.793,
        number_of_turns=11,
        drs_zones_count=2,
        overtake_difficulty=3,
        avg_overtakes_per_race=30.0,
        rain_probability_pct=20,
        nearest_airport="Milan Malpensa",
    )
    db.add(circuit)
    db.commit()
    db.close()


def teardown_function():
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(engine)


def _register(email="test@example.com", password="secret123"):
    return client.post("/api/auth/register", json={"email": email, "password": password})


def _auth_header(email="test@example.com", password="secret123"):
    resp = _register(email, password)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_price_alert():
    headers = _auth_header()
    resp = client.post(
        "/api/price-alerts",
        json={"circuit_id": 1, "target_price": 250.0},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["circuit_id"] == 1
    assert data["target_price"] == 250.0
    assert data["is_active"] is True
    assert data["triggered_at"] is None
    assert data["seat_section_id"] is None
    assert "id" in data


def test_list_price_alerts():
    headers = _auth_header()
    client.post(
        "/api/price-alerts",
        json={"circuit_id": 1, "target_price": 200.0},
        headers=headers,
    )
    client.post(
        "/api/price-alerts",
        json={"circuit_id": 1, "target_price": 300.0},
        headers=headers,
    )
    resp = client.get("/api/price-alerts", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_delete_price_alert():
    headers = _auth_header()
    create_resp = client.post(
        "/api/price-alerts",
        json={"circuit_id": 1, "target_price": 250.0},
        headers=headers,
    )
    alert_id = create_resp.json()["id"]
    resp = client.delete(f"/api/price-alerts/{alert_id}", headers=headers)
    assert resp.status_code == 204

    # Verify it's gone
    list_resp = client.get("/api/price-alerts", headers=headers)
    assert len(list_resp.json()) == 0
