from datetime import date

from app.models.circuit import Circuit
from app.models.race_event import RaceEvent


def test_create_circuit(db):
    circuit = Circuit(
        name="Silverstone Circuit",
        country="United Kingdom",
        continent="Europe",
        city="Silverstone",
        latitude=52.0786,
        longitude=-1.0169,
        track_type="permanent",
        track_length_km=5.891,
        number_of_turns=18,
        drs_zones_count=2,
        overtake_difficulty=6,
        avg_overtakes_per_race=42.5,
        rain_probability_pct=55,
        nearest_airport="London Luton (LTN)",
    )
    db.add(circuit)
    db.commit()
    db.refresh(circuit)
    assert circuit.id is not None
    assert circuit.name == "Silverstone Circuit"
    assert circuit.continent == "Europe"
    assert circuit.track_type == "permanent"


def test_create_race_event_linked_to_circuit(db):
    circuit = Circuit(
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
        overtake_difficulty=7,
        avg_overtakes_per_race=48.0,
        rain_probability_pct=20,
        nearest_airport="Milan Malpensa (MXP)",
    )
    db.add(circuit)
    db.commit()

    event = RaceEvent(
        circuit_id=circuit.id,
        season_year=2026,
        race_name="Italian Grand Prix",
        race_date=date(2026, 9, 6),
        sprint_weekend=False,
        status="upcoming",
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    assert event.id is not None
    assert event.circuit_id == circuit.id
    assert event.race_name == "Italian Grand Prix"
    assert event.status == "upcoming"


def test_circuit_race_events_relationship(db):
    circuit = Circuit(
        name="Spa-Francorchamps",
        country="Belgium",
        continent="Europe",
        city="Stavelot",
        latitude=50.4372,
        longitude=5.9714,
        track_type="permanent",
        track_length_km=7.004,
        number_of_turns=19,
        drs_zones_count=2,
        overtake_difficulty=8,
        avg_overtakes_per_race=55.0,
        rain_probability_pct=60,
        nearest_airport="Brussels (BRU)",
    )
    db.add(circuit)
    db.commit()

    event1 = RaceEvent(
        circuit_id=circuit.id,
        season_year=2025,
        race_name="Belgian Grand Prix 2025",
        race_date=date(2025, 7, 27),
        sprint_weekend=False,
        status="completed",
        total_overtakes=62,
    )
    event2 = RaceEvent(
        circuit_id=circuit.id,
        season_year=2026,
        race_name="Belgian Grand Prix 2026",
        race_date=date(2026, 7, 26),
        sprint_weekend=False,
        status="upcoming",
    )
    db.add_all([event1, event2])
    db.commit()
    db.refresh(circuit)

    assert len(circuit.race_events) == 2
