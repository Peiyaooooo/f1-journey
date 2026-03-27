from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch, AsyncMock

from app.database import Base, get_db
from app.main import app
from app.models import Circuit
from app.models.travel_estimate import TravelEstimate
from app.models.exchange_rate import ExchangeRate

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
        name="Monza", country="Italy", continent="Europe", city="Monza",
        latitude=45.62, longitude=9.28, track_type="permanent",
        track_length_km=5.793, number_of_turns=11, drs_zones_count=2,
        overtake_difficulty=2, avg_overtakes_per_race=48.0,
        rain_probability_pct=20, nearest_airport="Milan Malpensa (MXP)",
    )
    db.add(circuit)
    db.commit()

    # Pre-cache a travel estimate
    estimate = TravelEstimate(
        circuit_id=circuit.id, origin_city="London", origin_country="United Kingdom",
        origin_airport_code="LHR", flight_price_min=85.0, flight_price_max=320.0,
        flight_duration_hours=2.0, flight_stops=0, train_available=True,
        train_price_min=120.0, train_price_max=250.0, train_duration_hours=8.5,
        local_transport_cost=25.0, hotel_avg_per_night=150.0,
        last_fetched_at=datetime.utcnow(),
    )
    db.add(estimate)

    # Pre-cache exchange rates
    rates = [
        ExchangeRate(currency_code="USD", rate_from_usd=1.0, last_updated_at=datetime.utcnow()),
        ExchangeRate(currency_code="EUR", rate_from_usd=0.92, last_updated_at=datetime.utcnow()),
        ExchangeRate(currency_code="GBP", rate_from_usd=0.79, last_updated_at=datetime.utcnow()),
    ]
    db.add_all(rates)
    db.commit()
    db.close()


def teardown_function():
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(engine)


def test_get_cached_travel_estimate():
    resp = client.get("/api/travel/estimate?circuit_id=1&origin=London")
    assert resp.status_code == 200
    data = resp.json()
    assert data["origin_city"] == "London"
    assert data["flight_price_min"] == 85.0
    assert data["train_available"] is True


def test_get_exchange_rates():
    resp = client.get("/api/travel/exchange-rates")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    codes = [r["currency_code"] for r in data]
    assert "USD" in codes
    assert "EUR" in codes


def test_travel_estimate_unknown_city():
    resp = client.get("/api/travel/estimate?circuit_id=1&origin=nonexistent_xyz")
    assert resp.status_code == 400


def test_get_city_suggestions():
    resp = client.get("/api/travel/cities")
    assert resp.status_code == 200
    data = resp.json()
    assert "london" in data
    assert len(data) >= 50
