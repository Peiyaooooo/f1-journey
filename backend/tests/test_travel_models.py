from datetime import datetime

from app.models.circuit import Circuit
from app.models.travel_estimate import TravelEstimate
from app.models.exchange_rate import ExchangeRate


def _make_circuit(db):
    circuit = Circuit(
        name="Silverstone", country="United Kingdom", continent="Europe",
        city="Silverstone", latitude=52.07, longitude=-1.02,
        track_type="permanent", track_length_km=5.891,
        number_of_turns=18, drs_zones_count=2,
        overtake_difficulty=3, avg_overtakes_per_race=35.0,
        rain_probability_pct=40, nearest_airport="BHX",
    )
    db.add(circuit)
    db.commit()
    return circuit


def test_create_travel_estimate(db):
    circuit = _make_circuit(db)

    estimate = TravelEstimate(
        circuit_id=circuit.id,
        origin_city="New York",
        origin_country="United States",
        origin_airport_code="JFK",
        flight_price_min=400.0,
        flight_price_max=900.0,
        flight_duration_hours=7.5,
        flight_stops=0,
        train_available=True,
        train_price_min=50.0,
        train_price_max=120.0,
        train_duration_hours=2.5,
        local_transport_cost=30.0,
        hotel_avg_per_night=200.0,
        last_fetched_at=datetime.utcnow(),
    )
    db.add(estimate)
    db.commit()
    db.refresh(estimate)

    assert estimate.id is not None
    assert estimate.origin_city == "New York"
    assert estimate.origin_airport_code == "JFK"
    assert estimate.train_available is True
    assert estimate.train_price_min == 50.0
    assert estimate.train_duration_hours == 2.5
    assert estimate.circuit_id == circuit.id


def test_create_travel_estimate_no_train(db):
    circuit = _make_circuit(db)

    estimate = TravelEstimate(
        circuit_id=circuit.id,
        origin_city="Tokyo",
        origin_country="Japan",
        origin_airport_code="HND",
        flight_price_min=800.0,
        flight_price_max=1800.0,
        flight_duration_hours=13.0,
        flight_stops=1,
        train_available=False,
        train_price_min=None,
        train_price_max=None,
        train_duration_hours=None,
        local_transport_cost=25.0,
        hotel_avg_per_night=180.0,
        last_fetched_at=datetime.utcnow(),
    )
    db.add(estimate)
    db.commit()
    db.refresh(estimate)

    assert estimate.id is not None
    assert estimate.origin_city == "Tokyo"
    assert estimate.train_available is False
    assert estimate.train_price_min is None
    assert estimate.train_price_max is None
    assert estimate.train_duration_hours is None
    assert estimate.flight_stops == 1


def test_create_exchange_rate(db):
    rate = ExchangeRate(
        currency_code="EUR",
        rate_from_usd=0.92,
        last_updated_at=datetime.utcnow(),
    )
    db.add(rate)
    db.commit()
    db.refresh(rate)

    assert rate.id is not None
    assert rate.currency_code == "EUR"
    assert rate.rate_from_usd == 0.92
    assert rate.last_updated_at is not None
