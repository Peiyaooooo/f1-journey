import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models.circuit import Circuit
from app.models.race_event import RaceEvent
from app.models.travel_estimate import TravelEstimate
from app.models.exchange_rate import ExchangeRate
from app.schemas.travel import TravelEstimateRead, ExchangeRateRead
from app.travel.airports import lookup_airport, get_city_suggestions
from app.travel.flights import fetch_flights
from app.travel.transport import fetch_transport
from app.travel.exchange_rates import fetch_and_cache_rates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/travel", tags=["travel"])

CACHE_HOURS = 24

# Per-circuit hotel estimates (USD per night during race weekend)
HOTEL_ESTIMATES: dict[str, float] = {
    "Albert Park Circuit": 200.0,
    "Shanghai International Circuit": 120.0,
    "Suzuka International Racing Course": 150.0,
    "Miami International Autodrome": 350.0,
    "Circuit Gilles Villeneuve": 250.0,
    "Circuit de Monaco": 500.0,
    "Circuit de Barcelona-Catalunya": 180.0,
    "Red Bull Ring": 150.0,
    "Silverstone Circuit": 200.0,
    "Circuit de Spa-Francorchamps": 160.0,
    "Hungaroring": 120.0,
    "Circuit Zandvoort": 200.0,
    "Autodromo Nazionale di Monza": 180.0,
    "Madrid Street Circuit": 200.0,
    "Baku City Circuit": 130.0,
    "Marina Bay Street Circuit": 300.0,
    "Circuit of the Americas": 280.0,
    "Autodromo Hermanos Rodriguez": 100.0,
    "Interlagos": 120.0,
    "Las Vegas Street Circuit": 400.0,
    "Losail International Circuit": 200.0,
    "Yas Marina Circuit": 250.0,
}


def _extract_airport_code(nearest_airport: str) -> str:
    """Extract IATA code from strings like 'Milan Malpensa (MXP)'."""
    if "(" in nearest_airport and ")" in nearest_airport:
        return nearest_airport.split("(")[1].split(")")[0].strip()
    return nearest_airport.strip()


@router.get("/estimate", response_model=TravelEstimateRead)
async def get_travel_estimate(
    circuit_id: int = Query(...),
    origin: str = Query(...),
    db: Session = Depends(get_db),
):
    # Look up origin airport
    airport_info = lookup_airport(origin)
    if not airport_info:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown city '{origin}'. Use /api/travel/cities for suggestions.",
        )

    origin_code, origin_country = airport_info

    # Check cache (case-insensitive city match)
    origin_normalized = origin.strip()
    cached = (
        db.query(TravelEstimate)
        .filter(
            TravelEstimate.circuit_id == circuit_id,
            TravelEstimate.origin_city.ilike(origin_normalized),
        )
        .first()
    )

    if cached and cached.last_fetched_at > datetime.utcnow() - timedelta(hours=CACHE_HOURS):
        return cached

    # Fetch fresh data
    circuit = db.get(Circuit, circuit_id)
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")

    dest_code = _extract_airport_code(circuit.nearest_airport)

    # Get race date for flight search window
    event = (
        db.query(RaceEvent)
        .filter(RaceEvent.circuit_id == circuit_id, RaceEvent.status == "upcoming")
        .first()
    )
    race_date = event.race_date if event else None

    # Fetch flights
    flight_result = None
    if race_date:
        flight_result = await fetch_flights(origin_code, dest_code, race_date)

    # Fetch transport
    transport_result = await fetch_transport(origin.title(), circuit.city)

    # Hotel estimate
    hotel_cost = HOTEL_ESTIMATES.get(circuit.name, 150.0)

    # Build estimate
    now = datetime.utcnow()
    estimate_data = {
        "circuit_id": circuit_id,
        "origin_city": origin.strip(),
        "origin_country": origin_country,
        "origin_airport_code": origin_code,
        "flight_price_min": flight_result.price_min if flight_result else 0.0,
        "flight_price_max": flight_result.price_max if flight_result else 0.0,
        "flight_duration_hours": flight_result.duration_hours if flight_result else 0.0,
        "flight_stops": flight_result.stops if flight_result else 0,
        "train_available": transport_result.train_available,
        "train_price_min": transport_result.train_price_min,
        "train_price_max": transport_result.train_price_max,
        "train_duration_hours": transport_result.train_duration_hours,
        "local_transport_cost": transport_result.local_transport_cost,
        "hotel_avg_per_night": hotel_cost,
        "last_fetched_at": now,
    }

    if cached:
        for key, value in estimate_data.items():
            setattr(cached, key, value)
        db.commit()
        db.refresh(cached)
        return cached
    else:
        estimate = TravelEstimate(**estimate_data)
        db.add(estimate)
        db.commit()
        db.refresh(estimate)
        return estimate


@router.get("/exchange-rates", response_model=list[ExchangeRateRead])
async def get_exchange_rates(db: Session = Depends(get_db)):
    rates = db.query(ExchangeRate).all()
    if not rates or rates[0].last_updated_at < datetime.utcnow() - timedelta(hours=CACHE_HOURS):
        rates = await fetch_and_cache_rates()
    return rates


@router.get("/cities", response_model=list[str])
def get_cities():
    return get_city_suggestions()
