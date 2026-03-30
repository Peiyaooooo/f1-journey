"""Seed data for the 2026 F1 season — circuits and race calendar.

Source: https://www.formula1.com/en/racing/2026

Run: python -m app.seed.seed_data
"""

import json
from datetime import date

from app.database import Base, SessionLocal, engine
from app.models.circuit import Circuit
from app.models.race_event import RaceEvent
from app.models.seat_section import SeatSection
from app.models.ticket_listing import TicketListing
from app.seed.seat_sections_data_v2 import SEAT_SECTIONS_V2
from app.seed.seed_tickets_v3 import seed_tickets_v3

# ---------------------------------------------------------------------------
# Circuit definitions (22 circuits on the 2026 calendar)
# ---------------------------------------------------------------------------

CIRCUITS = [
    {
        "name": "Albert Park Circuit",
        "country": "Australia",
        "continent": "Oceania",
        "city": "Melbourne",
        "latitude": -37.8497,
        "longitude": 144.9680,
        "track_type": "street",
        "track_length_km": 5.278,
        "number_of_turns": 14,
        "drs_zones_count": 4,
        "overtake_difficulty": 5,
        "avg_overtakes_per_race": 30.0,
        "rain_probability_pct": 25,
        "nearest_airport": "Melbourne Tullamarine (MEL)",
    },
    {
        "name": "Shanghai International Circuit",
        "country": "China",
        "continent": "Asia",
        "city": "Shanghai",
        "latitude": 31.3389,
        "longitude": 121.2197,
        "track_type": "permanent",
        "track_length_km": 5.451,
        "number_of_turns": 16,
        "drs_zones_count": 2,
        "overtake_difficulty": 4,
        "avg_overtakes_per_race": 38.0,
        "rain_probability_pct": 30,
        "nearest_airport": "Shanghai Pudong (PVG)",
    },
    {
        "name": "Suzuka International Racing Course",
        "country": "Japan",
        "continent": "Asia",
        "city": "Suzuka",
        "latitude": 34.8431,
        "longitude": 136.5407,
        "track_type": "permanent",
        "track_length_km": 5.807,
        "number_of_turns": 18,
        "drs_zones_count": 1,
        "overtake_difficulty": 7,
        "avg_overtakes_per_race": 20.0,
        "rain_probability_pct": 35,
        "nearest_airport": "Chubu Centrair (NGO)",
    },
    {
        "name": "Miami International Autodrome",
        "country": "United States",
        "continent": "North America",
        "city": "Miami",
        "latitude": 25.9581,
        "longitude": -80.2389,
        "track_type": "street",
        "track_length_km": 5.412,
        "number_of_turns": 19,
        "drs_zones_count": 3,
        "overtake_difficulty": 5,
        "avg_overtakes_per_race": 32.0,
        "rain_probability_pct": 40,
        "nearest_airport": "Miami International (MIA)",
    },
    {
        "name": "Circuit Gilles Villeneuve",
        "country": "Canada",
        "continent": "North America",
        "city": "Montreal",
        "latitude": 45.5000,
        "longitude": -73.5228,
        "track_type": "street",
        "track_length_km": 4.361,
        "number_of_turns": 14,
        "drs_zones_count": 2,
        "overtake_difficulty": 5,
        "avg_overtakes_per_race": 35.0,
        "rain_probability_pct": 20,
        "nearest_airport": "Montreal Trudeau (YUL)",
    },
    {
        "name": "Circuit de Monaco",
        "country": "Monaco",
        "continent": "Europe",
        "city": "Monte Carlo",
        "latitude": 43.7347,
        "longitude": 7.4206,
        "track_type": "street",
        "track_length_km": 3.337,
        "number_of_turns": 19,
        "drs_zones_count": 1,
        "overtake_difficulty": 10,
        "avg_overtakes_per_race": 5.0,
        "rain_probability_pct": 15,
        "nearest_airport": "Nice Cote d'Azur (NCE)",
    },
    {
        "name": "Circuit de Barcelona-Catalunya",
        "country": "Spain",
        "continent": "Europe",
        "city": "Barcelona",
        "latitude": 41.5700,
        "longitude": 2.2611,
        "track_type": "permanent",
        "track_length_km": 4.657,
        "number_of_turns": 14,
        "drs_zones_count": 2,
        "overtake_difficulty": 6,
        "avg_overtakes_per_race": 25.0,
        "rain_probability_pct": 10,
        "nearest_airport": "Barcelona El Prat (BCN)",
    },
    {
        "name": "Red Bull Ring",
        "country": "Austria",
        "continent": "Europe",
        "city": "Spielberg",
        "latitude": 47.2197,
        "longitude": 14.7647,
        "track_type": "permanent",
        "track_length_km": 4.318,
        "number_of_turns": 10,
        "drs_zones_count": 3,
        "overtake_difficulty": 3,
        "avg_overtakes_per_race": 40.0,
        "rain_probability_pct": 30,
        "nearest_airport": "Graz (GRZ)",
    },
    {
        "name": "Silverstone Circuit",
        "country": "Great Britain",
        "continent": "Europe",
        "city": "Silverstone",
        "latitude": 52.0786,
        "longitude": -1.0169,
        "track_type": "permanent",
        "track_length_km": 5.891,
        "number_of_turns": 18,
        "drs_zones_count": 2,
        "overtake_difficulty": 4,
        "avg_overtakes_per_race": 42.5,
        "rain_probability_pct": 55,
        "nearest_airport": "London Luton (LTN)",
    },
    {
        "name": "Circuit de Spa-Francorchamps",
        "country": "Belgium",
        "continent": "Europe",
        "city": "Spa",
        "latitude": 50.4372,
        "longitude": 5.9714,
        "track_type": "permanent",
        "track_length_km": 7.004,
        "number_of_turns": 19,
        "drs_zones_count": 2,
        "overtake_difficulty": 2,
        "avg_overtakes_per_race": 55.0,
        "rain_probability_pct": 60,
        "nearest_airport": "Brussels (BRU)",
    },
    {
        "name": "Hungaroring",
        "country": "Hungary",
        "continent": "Europe",
        "city": "Budapest",
        "latitude": 47.5789,
        "longitude": 19.2486,
        "track_type": "permanent",
        "track_length_km": 4.381,
        "number_of_turns": 14,
        "drs_zones_count": 2,
        "overtake_difficulty": 9,
        "avg_overtakes_per_race": 15.0,
        "rain_probability_pct": 20,
        "nearest_airport": "Budapest Liszt Ferenc (BUD)",
    },
    {
        "name": "Circuit Zandvoort",
        "country": "Netherlands",
        "continent": "Europe",
        "city": "Zandvoort",
        "latitude": 52.3888,
        "longitude": 4.5409,
        "track_type": "permanent",
        "track_length_km": 4.259,
        "number_of_turns": 14,
        "drs_zones_count": 2,
        "overtake_difficulty": 9,
        "avg_overtakes_per_race": 12.0,
        "rain_probability_pct": 35,
        "nearest_airport": "Amsterdam Schiphol (AMS)",
    },
    {
        "name": "Autodromo Nazionale di Monza",
        "country": "Italy",
        "continent": "Europe",
        "city": "Monza",
        "latitude": 45.6156,
        "longitude": 9.2811,
        "track_type": "permanent",
        "track_length_km": 5.793,
        "number_of_turns": 11,
        "drs_zones_count": 2,
        "overtake_difficulty": 2,
        "avg_overtakes_per_race": 48.0,
        "rain_probability_pct": 20,
        "nearest_airport": "Milan Malpensa (MXP)",
    },
    {
        "name": "Madrid Street Circuit",
        "country": "Spain",
        "continent": "Europe",
        "city": "Madrid",
        "latitude": 40.4168,
        "longitude": -3.7038,
        "track_type": "street",
        "track_length_km": 5.473,
        "number_of_turns": 20,
        "drs_zones_count": 2,
        "overtake_difficulty": 6,
        "avg_overtakes_per_race": 25.0,
        "rain_probability_pct": 10,
        "nearest_airport": "Madrid Barajas (MAD)",
    },
    {
        "name": "Baku City Circuit",
        "country": "Azerbaijan",
        "continent": "Europe",
        "city": "Baku",
        "latitude": 40.3725,
        "longitude": 49.8533,
        "track_type": "street",
        "track_length_km": 6.003,
        "number_of_turns": 20,
        "drs_zones_count": 2,
        "overtake_difficulty": 3,
        "avg_overtakes_per_race": 40.0,
        "rain_probability_pct": 10,
        "nearest_airport": "Heydar Aliyev (GYD)",
    },
    {
        "name": "Marina Bay Street Circuit",
        "country": "Singapore",
        "continent": "Asia",
        "city": "Singapore",
        "latitude": 1.2914,
        "longitude": 103.8640,
        "track_type": "street",
        "track_length_km": 4.940,
        "number_of_turns": 19,
        "drs_zones_count": 3,
        "overtake_difficulty": 8,
        "avg_overtakes_per_race": 18.0,
        "rain_probability_pct": 40,
        "nearest_airport": "Changi (SIN)",
    },
    {
        "name": "Circuit of the Americas",
        "country": "United States",
        "continent": "North America",
        "city": "Austin",
        "latitude": 30.1328,
        "longitude": -97.6411,
        "track_type": "permanent",
        "track_length_km": 5.513,
        "number_of_turns": 20,
        "drs_zones_count": 2,
        "overtake_difficulty": 5,
        "avg_overtakes_per_race": 35.0,
        "rain_probability_pct": 20,
        "nearest_airport": "Austin-Bergstrom (AUS)",
    },
    {
        "name": "Autodromo Hermanos Rodriguez",
        "country": "Mexico",
        "continent": "North America",
        "city": "Mexico City",
        "latitude": 19.4042,
        "longitude": -99.0907,
        "track_type": "permanent",
        "track_length_km": 4.304,
        "number_of_turns": 17,
        "drs_zones_count": 3,
        "overtake_difficulty": 5,
        "avg_overtakes_per_race": 30.0,
        "rain_probability_pct": 25,
        "nearest_airport": "Mexico City (MEX)",
    },
    {
        "name": "Interlagos",
        "country": "Brazil",
        "continent": "South America",
        "city": "Sao Paulo",
        "latitude": -23.7036,
        "longitude": -46.6997,
        "track_type": "permanent",
        "track_length_km": 4.309,
        "number_of_turns": 15,
        "drs_zones_count": 2,
        "overtake_difficulty": 3,
        "avg_overtakes_per_race": 42.0,
        "rain_probability_pct": 45,
        "nearest_airport": "Sao Paulo Guarulhos (GRU)",
    },
    {
        "name": "Las Vegas Street Circuit",
        "country": "United States",
        "continent": "North America",
        "city": "Las Vegas",
        "latitude": 36.1147,
        "longitude": -115.1728,
        "track_type": "street",
        "track_length_km": 6.201,
        "number_of_turns": 17,
        "drs_zones_count": 2,
        "overtake_difficulty": 4,
        "avg_overtakes_per_race": 38.0,
        "rain_probability_pct": 5,
        "nearest_airport": "Harry Reid International (LAS)",
    },
    {
        "name": "Losail International Circuit",
        "country": "Qatar",
        "continent": "Asia",
        "city": "Doha",
        "latitude": 25.4900,
        "longitude": 51.4542,
        "track_type": "permanent",
        "track_length_km": 5.419,
        "number_of_turns": 16,
        "drs_zones_count": 2,
        "overtake_difficulty": 5,
        "avg_overtakes_per_race": 30.0,
        "rain_probability_pct": 1,
        "nearest_airport": "Hamad International (DOH)",
    },
    {
        "name": "Yas Marina Circuit",
        "country": "United Arab Emirates",
        "continent": "Asia",
        "city": "Abu Dhabi",
        "latitude": 24.4672,
        "longitude": 54.6031,
        "track_type": "permanent",
        "track_length_km": 5.281,
        "number_of_turns": 16,
        "drs_zones_count": 2,
        "overtake_difficulty": 5,
        "avg_overtakes_per_race": 35.0,
        "rain_probability_pct": 1,
        "nearest_airport": "Abu Dhabi (AUH)",
    },
]

# ---------------------------------------------------------------------------
# 2026 Race calendar (22 rounds)
# Source: https://www.formula1.com/en/racing/2026
# Sprint weekends: Shanghai, Miami, Montreal, Silverstone, Zandvoort, Singapore
# ---------------------------------------------------------------------------

RACES_2026 = [
    {
        "circuit_name": "Albert Park Circuit",
        "race_name": "Australian Grand Prix",
        "date": date(2026, 3, 8),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Shanghai International Circuit",
        "race_name": "Chinese Grand Prix",
        "date": date(2026, 3, 15),
        "sprint_weekend": True,
    },
    {
        "circuit_name": "Suzuka International Racing Course",
        "race_name": "Japanese Grand Prix",
        "date": date(2026, 3, 29),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Miami International Autodrome",
        "race_name": "Miami Grand Prix",
        "date": date(2026, 5, 3),
        "sprint_weekend": True,
    },
    {
        "circuit_name": "Circuit Gilles Villeneuve",
        "race_name": "Canadian Grand Prix",
        "date": date(2026, 5, 24),
        "sprint_weekend": True,
    },
    {
        "circuit_name": "Circuit de Monaco",
        "race_name": "Monaco Grand Prix",
        "date": date(2026, 6, 7),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Circuit de Barcelona-Catalunya",
        "race_name": "Barcelona-Catalunya Grand Prix",
        "date": date(2026, 6, 14),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Red Bull Ring",
        "race_name": "Austrian Grand Prix",
        "date": date(2026, 6, 28),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Silverstone Circuit",
        "race_name": "British Grand Prix",
        "date": date(2026, 7, 5),
        "sprint_weekend": True,
    },
    {
        "circuit_name": "Circuit de Spa-Francorchamps",
        "race_name": "Belgian Grand Prix",
        "date": date(2026, 7, 19),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Hungaroring",
        "race_name": "Hungarian Grand Prix",
        "date": date(2026, 7, 26),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Circuit Zandvoort",
        "race_name": "Dutch Grand Prix",
        "date": date(2026, 8, 23),
        "sprint_weekend": True,
    },
    {
        "circuit_name": "Autodromo Nazionale di Monza",
        "race_name": "Italian Grand Prix",
        "date": date(2026, 9, 6),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Madrid Street Circuit",
        "race_name": "Spanish Grand Prix",
        "date": date(2026, 9, 13),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Baku City Circuit",
        "race_name": "Azerbaijan Grand Prix",
        "date": date(2026, 9, 26),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Marina Bay Street Circuit",
        "race_name": "Singapore Grand Prix",
        "date": date(2026, 10, 11),
        "sprint_weekend": True,
    },
    {
        "circuit_name": "Circuit of the Americas",
        "race_name": "United States Grand Prix",
        "date": date(2026, 10, 25),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Autodromo Hermanos Rodriguez",
        "race_name": "Mexico City Grand Prix",
        "date": date(2026, 11, 1),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Interlagos",
        "race_name": "Sao Paulo Grand Prix",
        "date": date(2026, 11, 8),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Las Vegas Street Circuit",
        "race_name": "Las Vegas Grand Prix",
        "date": date(2026, 11, 21),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Losail International Circuit",
        "race_name": "Qatar Grand Prix",
        "date": date(2026, 11, 29),
        "sprint_weekend": False,
    },
    {
        "circuit_name": "Yas Marina Circuit",
        "race_name": "Abu Dhabi Grand Prix",
        "date": date(2026, 12, 6),
        "sprint_weekend": False,
    },
]


def seed() -> None:
    """Seed the database with 2026 F1 circuits and race events."""
    # Drop and recreate all tables to ensure schema is up to date
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Drop existing data and re-seed (ticket_listings first due to FK)
        db.query(TicketListing).delete()
        db.query(SeatSection).delete()
        db.query(RaceEvent).delete()
        db.query(Circuit).delete()
        db.commit()

        # Insert circuits
        circuit_objs = []
        for data in CIRCUITS:
            circuit = Circuit(**data)
            db.add(circuit)
            circuit_objs.append(circuit)

        db.flush()

        # Build name -> id map
        name_to_id: dict[str, int] = {c.name: c.id for c in circuit_objs}

        # Insert race events
        for race_data in RACES_2026:
            circuit_name = race_data["circuit_name"]
            circuit_id = name_to_id[circuit_name]
            race_event = RaceEvent(
                circuit_id=circuit_id,
                season_year=2026,
                race_name=race_data["race_name"],
                race_date=race_data["date"],
                sprint_weekend=race_data["sprint_weekend"],
                status="upcoming",
            )
            db.add(race_event)

        # Insert seat sections
        section_count = 0
        for circuit_name, sections in SEAT_SECTIONS_V2.items():
            cid = name_to_id.get(circuit_name)
            if cid is None:
                print(f"Warning: no circuit found for '{circuit_name}', skipping sections")
                continue
            for s in sections:
                seat = SeatSection(
                    circuit_id=cid,
                    name=s["name"],
                    section_type=s["section_type"],
                    location_on_track=s.get("location_on_track"),
                    has_roof=s.get("has_roof", False),
                    has_screen=s.get("has_screen", False),
                    pit_view=s.get("pit_view", False),
                    podium_view=s.get("podium_view", False),
                    capacity=s.get("capacity"),
                    view_description=s.get("view_description"),
                    seat_type=s.get("seat_type"),
                    latitude=s["latitude"],
                    longitude=s["longitude"],
                    view_photos=json.dumps(s["view_photos"]) if s.get("view_photos") else None,
                )
                db.add(seat)
                section_count += 1

        db.flush()

        # Build maps for ticket seeder
        # event_map: circuit_name -> race_event_id
        event_map: dict[str, int] = {}
        for race_data in RACES_2026:
            circuit_name = race_data["circuit_name"]
            cid = name_to_id[circuit_name]
            event = db.query(RaceEvent).filter_by(circuit_id=cid, season_year=2026).first()
            if event:
                event_map[circuit_name] = event.id

        # section_map: circuit_id -> {section_name: section_id}
        section_map: dict[int, dict[str, int]] = {}
        for section in db.query(SeatSection).all():
            section_map.setdefault(section.circuit_id, {})[section.name] = section.id

        # Seed ticket listings
        ticket_count = seed_tickets_v3(db, name_to_id, event_map, section_map)

        db.commit()
        circuit_count = db.query(Circuit).count()
        race_count = db.query(RaceEvent).count()
        print(f"Seeded {circuit_count} circuits, {race_count} race events, {section_count} seat sections, and {ticket_count} ticket listings.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
