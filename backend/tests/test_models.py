from datetime import date

from app.models.circuit import Circuit
from app.models.race_event import RaceEvent
from app.models.seat_section import SeatSection
import json


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


def test_create_seat_section(db):
    circuit = Circuit(
        name="Monza", country="Italy", continent="Europe",
        city="Monza", latitude=45.62, longitude=9.28,
        track_type="permanent", track_length_km=5.793, number_of_turns=11,
        drs_zones_count=2, overtake_difficulty=2, avg_overtakes_per_race=48.0,
        rain_probability_pct=20, nearest_airport="MXP",
    )
    db.add(circuit)
    db.commit()

    section = SeatSection(
        circuit_id=circuit.id,
        name="Central Grandstand",
        section_type="grandstand",
        location_on_track="Main Straight",
        has_roof=True,
        has_screen=True,
        pit_view=True,
        podium_view=True,
        capacity=5000,
        view_description="View of pit lane entry and main straight.",
        latitude=45.6180,
        longitude=9.2815,
        view_photos=json.dumps(["https://example.com/photo1.jpg"]),
    )
    db.add(section)
    db.commit()
    db.refresh(section)

    assert section.id is not None
    assert section.name == "Central Grandstand"
    assert section.section_type == "grandstand"
    assert section.has_roof is True
    assert section.pit_view is True


def test_circuit_seat_sections_relationship(db):
    circuit = Circuit(
        name="Spa", country="Belgium", continent="Europe",
        city="Spa", latitude=50.44, longitude=5.97,
        track_type="permanent", track_length_km=7.004, number_of_turns=19,
        drs_zones_count=2, overtake_difficulty=2, avg_overtakes_per_race=55.0,
        rain_probability_pct=60, nearest_airport="BRU",
    )
    db.add(circuit)
    db.commit()

    s1 = SeatSection(
        circuit_id=circuit.id, name="Gold 1", section_type="grandstand",
        location_on_track="Eau Rouge", has_roof=False, has_screen=True,
        pit_view=False, podium_view=False, latitude=50.4371, longitude=5.9710,
    )
    s2 = SeatSection(
        circuit_id=circuit.id, name="GA Zone A", section_type="general_admission",
        location_on_track="Pouhon", has_roof=False, has_screen=False,
        pit_view=False, podium_view=False, latitude=50.4330, longitude=5.9680,
    )
    db.add_all([s1, s2])
    db.commit()
    db.refresh(circuit)

    assert len(circuit.seat_sections) == 2
