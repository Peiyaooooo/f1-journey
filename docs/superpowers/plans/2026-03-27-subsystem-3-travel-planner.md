# Subsystem 3: Travel Planner + Cost Calculator — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Travel tab to the track detail page where users enter their origin city and get flight/train/hotel estimates with a total trip cost breakdown.

**Architecture:** TravelEstimate and ExchangeRate models cached in DB. Live fetching from Kiwi.com (flights) and Rome2Rio (trains) APIs with 24h cache. Frontend Travel tab with origin input, results display, and total cost card with currency conversion.

**Tech Stack:** httpx for API calls, Kiwi.com Tequila API, Rome2Rio API, frankfurter.app for exchange rates. Next.js client components for the Travel tab.

---

## File Structure

### Backend (new/modified)
```
backend/app/
├── config.py                        # Modify: add KIWI_API_KEY, ROME2RIO_API_KEY
├── models/
│   ├── __init__.py                  # Modify: add TravelEstimate, ExchangeRate
│   ├── travel_estimate.py           # Create: TravelEstimate model
│   └── exchange_rate.py             # Create: ExchangeRate model
├── schemas/
│   ├── __init__.py                  # Modify: add new schema exports
│   └── travel.py                    # Create: TravelEstimateRead, ExchangeRateRead
├── routers/
│   └── travel.py                    # Create: travel estimate + exchange rate endpoints
├── main.py                          # Modify: register travel router
├── travel/
│   ├── __init__.py
│   ├── airports.py                  # Create: city-to-airport IATA mapping
│   ├── flights.py                   # Create: Kiwi.com flight fetcher
│   ├── transport.py                 # Create: Rome2Rio transport fetcher
│   └── exchange_rates.py            # Create: exchange rate fetcher
backend/alembic/versions/
│   └── xxxx_add_travel_tables.py    # Create: migration
backend/tests/
├── test_travel_models.py            # Create: model tests
├── test_travel_api.py               # Create: API tests
├── test_airports.py                 # Create: airport mapping tests
```

### Frontend (new/modified)
```
frontend/src/
├── lib/
│   ├── api.ts                       # Modify: add travel types + fetch functions
│   └── currency.ts                  # Create: currency detection + conversion utils
├── components/
│   ├── TravelTab.tsx                # Create: origin input + results + cost card
│   └── CurrencySelector.tsx         # Create: currency dropdown
└── app/tracks/[id]/
    ├── page.tsx                     # Modify: fetch exchange rates
    └── TrackDetailClient.tsx        # Modify: add Travel tab
```

---

## Task 1: TravelEstimate + ExchangeRate Models

**Files:**
- Create: `backend/app/models/travel_estimate.py`
- Create: `backend/app/models/exchange_rate.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/tests/test_travel_models.py`

- [ ] **Step 1: Write model tests**

```python
# backend/tests/test_travel_models.py
from datetime import date, datetime

from app.models.circuit import Circuit
from app.models.travel_estimate import TravelEstimate
from app.models.exchange_rate import ExchangeRate


def test_create_travel_estimate(db):
    circuit = Circuit(
        name="Monza", country="Italy", continent="Europe", city="Monza",
        latitude=45.62, longitude=9.28, track_type="permanent",
        track_length_km=5.793, number_of_turns=11, drs_zones_count=2,
        overtake_difficulty=2, avg_overtakes_per_race=48.0,
        rain_probability_pct=20, nearest_airport="Milan Malpensa (MXP)",
    )
    db.add(circuit)
    db.commit()

    estimate = TravelEstimate(
        circuit_id=circuit.id,
        origin_city="London",
        origin_country="United Kingdom",
        origin_airport_code="LHR",
        flight_price_min=85.0,
        flight_price_max=320.0,
        flight_duration_hours=2.0,
        flight_stops=0,
        train_available=True,
        train_price_min=120.0,
        train_price_max=250.0,
        train_duration_hours=8.5,
        local_transport_cost=25.0,
        hotel_avg_per_night=150.0,
        last_fetched_at=datetime.utcnow(),
    )
    db.add(estimate)
    db.commit()
    db.refresh(estimate)

    assert estimate.id is not None
    assert estimate.flight_price_min == 85.0
    assert estimate.train_available is True
    assert estimate.origin_airport_code == "LHR"


def test_create_travel_estimate_no_train(db):
    circuit = Circuit(
        name="Melbourne", country="Australia", continent="Oceania", city="Melbourne",
        latitude=-37.85, longitude=144.97, track_type="street",
        track_length_km=5.278, number_of_turns=14, drs_zones_count=4,
        overtake_difficulty=5, avg_overtakes_per_race=30.0,
        rain_probability_pct=25, nearest_airport="Melbourne Tullamarine (MEL)",
    )
    db.add(circuit)
    db.commit()

    estimate = TravelEstimate(
        circuit_id=circuit.id,
        origin_city="Tokyo",
        origin_country="Japan",
        origin_airport_code="NRT",
        flight_price_min=450.0,
        flight_price_max=1200.0,
        flight_duration_hours=10.5,
        flight_stops=1,
        train_available=False,
        train_price_min=None,
        train_price_max=None,
        train_duration_hours=None,
        local_transport_cost=40.0,
        hotel_avg_per_night=180.0,
        last_fetched_at=datetime.utcnow(),
    )
    db.add(estimate)
    db.commit()
    db.refresh(estimate)

    assert estimate.train_available is False
    assert estimate.train_price_min is None


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && .venv/bin/python -m pytest tests/test_travel_models.py -v`

- [ ] **Step 3: Implement TravelEstimate model**

```python
# backend/app/models/travel_estimate.py
from datetime import datetime

from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TravelEstimate(Base):
    __tablename__ = "travel_estimates"

    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"))
    origin_city: Mapped[str] = mapped_column(String(100))
    origin_country: Mapped[str] = mapped_column(String(100))
    origin_airport_code: Mapped[str] = mapped_column(String(10))
    flight_price_min: Mapped[float] = mapped_column(Float)
    flight_price_max: Mapped[float] = mapped_column(Float)
    flight_duration_hours: Mapped[float] = mapped_column(Float)
    flight_stops: Mapped[int] = mapped_column(Integer)
    train_available: Mapped[bool] = mapped_column(Boolean, default=False)
    train_price_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    train_price_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    train_duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    local_transport_cost: Mapped[float] = mapped_column(Float)
    hotel_avg_per_night: Mapped[float] = mapped_column(Float)
    last_fetched_at: Mapped[datetime] = mapped_column(DateTime)

    circuit: Mapped["Circuit"] = relationship()
```

- [ ] **Step 4: Implement ExchangeRate model**

```python
# backend/app/models/exchange_rate.py
from datetime import datetime

from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    currency_code: Mapped[str] = mapped_column(String(10), unique=True)
    rate_from_usd: Mapped[float] = mapped_column(Float)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime)
```

- [ ] **Step 5: Update models `__init__.py`**

Add imports for `TravelEstimate` and `ExchangeRate`, add to `__all__`.

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && .venv/bin/python -m pytest tests/test_travel_models.py -v`
Expected: 3 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/ backend/tests/test_travel_models.py
git commit -m "feat: add TravelEstimate and ExchangeRate models"
```

---

## Task 2: Alembic Migration

**Files:**
- Create: `backend/alembic/versions/xxxx_add_travel_tables.py`

- [ ] **Step 1: Hand-write migration**

Look at `backend/alembic/versions/` for the previous revision ID (ticket_listings migration). Create migration with two tables: `travel_estimates` and `exchange_rates`.

`travel_estimates`: id, circuit_id (FK), origin_city, origin_country, origin_airport_code, flight_price_min, flight_price_max, flight_duration_hours, flight_stops, train_available, train_price_min (nullable), train_price_max (nullable), train_duration_hours (nullable), local_transport_cost, hotel_avg_per_night, last_fetched_at.

`exchange_rates`: id, currency_code (unique), rate_from_usd, last_updated_at.

- [ ] **Step 2: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat: add Alembic migration for travel_estimates and exchange_rates tables"
```

---

## Task 3: Config + City-to-Airport Mapping

**Files:**
- Modify: `backend/app/config.py`
- Create: `backend/app/travel/__init__.py`
- Create: `backend/app/travel/airports.py`
- Create: `backend/tests/test_airports.py`

- [ ] **Step 1: Add API key settings to config**

Add to `backend/app/config.py` Settings class:

```python
    kiwi_api_key: str = ""
    rome2rio_api_key: str = ""
```

These will be read from env vars `F1_KIWI_API_KEY` and `F1_ROME2RIO_API_KEY`.

- [ ] **Step 2: Write airport mapping tests**

```python
# backend/tests/test_airports.py
from app.travel.airports import lookup_airport, get_city_suggestions


def test_lookup_known_city():
    code, country = lookup_airport("london")
    assert code == "LHR"
    assert country == "United Kingdom"


def test_lookup_case_insensitive():
    code, country = lookup_airport("NEW YORK")
    assert code == "JFK"


def test_lookup_unknown_city():
    result = lookup_airport("nonexistent_city_xyz")
    assert result is None


def test_get_suggestions():
    suggestions = get_city_suggestions()
    assert len(suggestions) >= 50
    assert "london" in suggestions
    assert "tokyo" in suggestions
```

- [ ] **Step 3: Implement airport mapping**

```python
# backend/app/travel/__init__.py
```

```python
# backend/app/travel/airports.py
"""City-to-airport IATA code mapping."""

# ~60 major cities worldwide covering all F1 circuit locations + common origins
CITY_AIRPORTS: dict[str, tuple[str, str]] = {
    # Europe
    "london": ("LHR", "United Kingdom"),
    "manchester": ("MAN", "United Kingdom"),
    "paris": ("CDG", "France"),
    "amsterdam": ("AMS", "Netherlands"),
    "berlin": ("BER", "Germany"),
    "munich": ("MUC", "Germany"),
    "frankfurt": ("FRA", "Germany"),
    "madrid": ("MAD", "Spain"),
    "barcelona": ("BCN", "Spain"),
    "rome": ("FCO", "Italy"),
    "milan": ("MXP", "Italy"),
    "zurich": ("ZRH", "Switzerland"),
    "vienna": ("VIE", "Austria"),
    "brussels": ("BRU", "Belgium"),
    "lisbon": ("LIS", "Portugal"),
    "dublin": ("DUB", "Ireland"),
    "copenhagen": ("CPH", "Denmark"),
    "stockholm": ("ARN", "Sweden"),
    "oslo": ("OSL", "Norway"),
    "helsinki": ("HEL", "Finland"),
    "warsaw": ("WAW", "Poland"),
    "prague": ("PRG", "Czech Republic"),
    "budapest": ("BUD", "Hungary"),
    "istanbul": ("IST", "Turkey"),
    "athens": ("ATH", "Greece"),
    "moscow": ("SVO", "Russia"),
    # Americas
    "new york": ("JFK", "United States"),
    "los angeles": ("LAX", "United States"),
    "chicago": ("ORD", "United States"),
    "miami": ("MIA", "United States"),
    "san francisco": ("SFO", "United States"),
    "dallas": ("DFW", "United States"),
    "houston": ("IAH", "United States"),
    "austin": ("AUS", "United States"),
    "las vegas": ("LAS", "United States"),
    "toronto": ("YYZ", "Canada"),
    "montreal": ("YUL", "Canada"),
    "mexico city": ("MEX", "Mexico"),
    "sao paulo": ("GRU", "Brazil"),
    "buenos aires": ("EZE", "Argentina"),
    "bogota": ("BOG", "Colombia"),
    # Asia
    "tokyo": ("NRT", "Japan"),
    "osaka": ("KIX", "Japan"),
    "shanghai": ("PVG", "China"),
    "beijing": ("PEK", "China"),
    "hong kong": ("HKG", "Hong Kong"),
    "singapore": ("SIN", "Singapore"),
    "bangkok": ("BKK", "Thailand"),
    "kuala lumpur": ("KUL", "Malaysia"),
    "seoul": ("ICN", "South Korea"),
    "mumbai": ("BOM", "India"),
    "delhi": ("DEL", "India"),
    "dubai": ("DXB", "United Arab Emirates"),
    "abu dhabi": ("AUH", "United Arab Emirates"),
    "doha": ("DOH", "Qatar"),
    "riyadh": ("RUH", "Saudi Arabia"),
    # Oceania
    "sydney": ("SYD", "Australia"),
    "melbourne": ("MEL", "Australia"),
    # Africa
    "johannesburg": ("JNB", "South Africa"),
    "cairo": ("CAI", "Egypt"),
    "nairobi": ("NBO", "Kenya"),
}


def lookup_airport(city: str) -> tuple[str, str] | None:
    """Look up airport IATA code and country for a city.

    Returns (airport_code, country) or None if city not found.
    """
    key = city.lower().strip()
    return CITY_AIRPORTS.get(key)


def get_city_suggestions() -> list[str]:
    """Return all known city names for autocomplete."""
    return sorted(CITY_AIRPORTS.keys())
```

- [ ] **Step 4: Run tests**

Run: `cd backend && .venv/bin/python -m pytest tests/test_airports.py -v`
Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/config.py backend/app/travel/ backend/tests/test_airports.py
git commit -m "feat: add city-to-airport mapping and API key config"
```

---

## Task 4: Flight Fetcher (Kiwi.com)

**Files:**
- Create: `backend/app/travel/flights.py`

- [ ] **Step 1: Implement flight fetcher**

```python
# backend/app/travel/flights.py
"""Fetch flight data from Kiwi.com Tequila API."""

import logging
from dataclasses import dataclass
from datetime import date, timedelta

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

KIWI_SEARCH_URL = "https://api.tequila.kiwi.com/v2/search"


@dataclass
class FlightResult:
    price_min: float  # USD
    price_max: float  # USD
    duration_hours: float
    stops: int


async def fetch_flights(
    origin_code: str,
    destination_code: str,
    race_date: date,
) -> FlightResult | None:
    """Fetch flight prices from Kiwi.com Tequila API.

    Searches for flights arriving 1-2 days before the race and
    departing 0-1 days after.

    Returns FlightResult or None if API fails.
    """
    if not settings.kiwi_api_key:
        logger.warning("KIWI_API_KEY not set — skipping flight fetch")
        return None

    # Search window: arrive 1-2 days before race, depart 0-1 day after
    date_from = (race_date - timedelta(days=3)).strftime("%d/%m/%Y")
    date_to = (race_date - timedelta(days=1)).strftime("%d/%m/%Y")
    return_from = race_date.strftime("%d/%m/%Y")
    return_to = (race_date + timedelta(days=1)).strftime("%d/%m/%Y")

    params = {
        "fly_from": origin_code,
        "fly_to": destination_code,
        "date_from": date_from,
        "date_to": date_to,
        "return_from": return_from,
        "return_to": return_to,
        "curr": "USD",
        "sort": "price",
        "limit": 10,
        "flight_type": "round",
    }

    headers = {"apikey": settings.kiwi_api_key}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(KIWI_SEARCH_URL, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

        flights = data.get("data", [])
        if not flights:
            logger.info(f"No flights found {origin_code} -> {destination_code}")
            return None

        prices = [f["price"] for f in flights]
        # Use cheapest flight for duration/stops
        cheapest = flights[0]
        duration_seconds = cheapest.get("duration", {}).get("total", 0)
        # Count route segments minus 1 for stops
        route = cheapest.get("route", [])
        outbound_stops = max(0, len([r for r in route if r.get("return") == 0]) - 1)

        return FlightResult(
            price_min=min(prices),
            price_max=max(prices),
            duration_hours=round(duration_seconds / 3600, 1),
            stops=outbound_stops,
        )

    except Exception as e:
        logger.error(f"Kiwi API error for {origin_code}->{destination_code}: {e}")
        return None
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/travel/flights.py
git commit -m "feat: add Kiwi.com flight fetcher"
```

---

## Task 5: Transport Fetcher (Rome2Rio) + Exchange Rate Fetcher

**Files:**
- Create: `backend/app/travel/transport.py`
- Create: `backend/app/travel/exchange_rates.py`

- [ ] **Step 1: Implement Rome2Rio transport fetcher**

```python
# backend/app/travel/transport.py
"""Fetch train/transport data from Rome2Rio API."""

import logging
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

ROME2RIO_URL = "https://free.rome2rio.com/api/1.4/json/Search"


@dataclass
class TransportResult:
    train_available: bool
    train_price_min: float | None  # USD
    train_price_max: float | None  # USD
    train_duration_hours: float | None
    local_transport_cost: float  # USD estimate


async def fetch_transport(
    origin_city: str,
    destination_city: str,
) -> TransportResult:
    """Fetch train/transport options from Rome2Rio.

    Returns TransportResult with train info if available,
    plus an estimate for local transport cost.
    """
    if not settings.rome2rio_api_key:
        logger.warning("ROME2RIO_API_KEY not set — returning defaults")
        return TransportResult(
            train_available=False,
            train_price_min=None,
            train_price_max=None,
            train_duration_hours=None,
            local_transport_cost=30.0,  # default estimate
        )

    params = {
        "key": settings.rome2rio_api_key,
        "oName": origin_city,
        "dName": destination_city,
        "currencyCode": "USD",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(ROME2RIO_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

        routes = data.get("routes", [])

        # Find train routes
        train_route = None
        for route in routes:
            name = route.get("name", "").lower()
            if "train" in name or "rail" in name:
                train_route = route
                break

        # Estimate local transport from cheapest short route
        local_cost = 30.0  # default
        for route in routes:
            duration = route.get("totalDuration", 999)
            if duration < 120:  # under 2 hours = local transport
                price = route.get("indicativePrice", {})
                low = price.get("priceLow", price.get("price", 0))
                if 5 <= low <= 100:
                    local_cost = low
                    break

        if train_route:
            price_info = train_route.get("indicativePrice", {})
            price_low = price_info.get("priceLow", price_info.get("price"))
            price_high = price_info.get("priceHigh", price_low)
            duration = train_route.get("totalDuration", 0)

            return TransportResult(
                train_available=True,
                train_price_min=price_low,
                train_price_max=price_high,
                train_duration_hours=round(duration / 60, 1) if duration else None,
                local_transport_cost=local_cost,
            )

        return TransportResult(
            train_available=False,
            train_price_min=None,
            train_price_max=None,
            train_duration_hours=None,
            local_transport_cost=local_cost,
        )

    except Exception as e:
        logger.error(f"Rome2Rio API error for {origin_city}->{destination_city}: {e}")
        return TransportResult(
            train_available=False,
            train_price_min=None,
            train_price_max=None,
            train_duration_hours=None,
            local_transport_cost=30.0,
        )
```

- [ ] **Step 2: Implement exchange rate fetcher**

```python
# backend/app/travel/exchange_rates.py
"""Fetch and cache exchange rates from frankfurter.app."""

import logging
from datetime import datetime, timedelta

import httpx

from app.database import SessionLocal
from app.models.exchange_rate import ExchangeRate

logger = logging.getLogger(__name__)

FRANKFURTER_URL = "https://api.frankfurter.app/latest?from=USD"
STALE_HOURS = 24


async def fetch_and_cache_rates() -> list[ExchangeRate]:
    """Fetch latest exchange rates and cache in DB.

    Returns list of ExchangeRate objects.
    """
    db = SessionLocal()
    try:
        # Check if rates are still fresh
        latest = db.query(ExchangeRate).first()
        if latest and latest.last_updated_at > datetime.utcnow() - timedelta(hours=STALE_HOURS):
            return db.query(ExchangeRate).all()

        # Fetch fresh rates
        async with httpx.AsyncClient() as client:
            resp = await client.get(FRANKFURTER_URL, timeout=15)
            resp.raise_for_status()
            data = resp.json()

        rates_data = data.get("rates", {})
        now = datetime.utcnow()

        for code, rate in rates_data.items():
            existing = db.query(ExchangeRate).filter(ExchangeRate.currency_code == code).first()
            if existing:
                existing.rate_from_usd = rate
                existing.last_updated_at = now
            else:
                db.add(ExchangeRate(currency_code=code, rate_from_usd=rate, last_updated_at=now))

        # Always ensure USD = 1.0
        usd = db.query(ExchangeRate).filter(ExchangeRate.currency_code == "USD").first()
        if usd:
            usd.rate_from_usd = 1.0
            usd.last_updated_at = now
        else:
            db.add(ExchangeRate(currency_code="USD", rate_from_usd=1.0, last_updated_at=now))

        db.commit()
        return db.query(ExchangeRate).all()

    except Exception as e:
        logger.error(f"Exchange rate fetch failed: {e}")
        db.rollback()
        # Return stale data if available
        return db.query(ExchangeRate).all()
    finally:
        db.close()


def get_cached_rates() -> list[ExchangeRate]:
    """Get cached exchange rates without fetching."""
    db = SessionLocal()
    try:
        return db.query(ExchangeRate).all()
    finally:
        db.close()
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/travel/transport.py backend/app/travel/exchange_rates.py
git commit -m "feat: add Rome2Rio transport fetcher and exchange rate fetcher"
```

---

## Task 6: Pydantic Schemas + API Endpoints + Tests

**Files:**
- Create: `backend/app/schemas/travel.py`
- Modify: `backend/app/schemas/__init__.py`
- Create: `backend/app/routers/travel.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_travel_api.py`

- [ ] **Step 1: Create Pydantic schemas**

```python
# backend/app/schemas/travel.py
from datetime import datetime
from pydantic import BaseModel


class TravelEstimateRead(BaseModel):
    id: int
    circuit_id: int
    origin_city: str
    origin_country: str
    origin_airport_code: str
    flight_price_min: float
    flight_price_max: float
    flight_duration_hours: float
    flight_stops: int
    train_available: bool
    train_price_min: float | None = None
    train_price_max: float | None = None
    train_duration_hours: float | None = None
    local_transport_cost: float
    hotel_avg_per_night: float
    last_fetched_at: datetime

    model_config = {"from_attributes": True}


class ExchangeRateRead(BaseModel):
    currency_code: str
    rate_from_usd: float
    last_updated_at: datetime

    model_config = {"from_attributes": True}
```

Update `backend/app/schemas/__init__.py` to export both.

- [ ] **Step 2: Write API tests**

```python
# backend/tests/test_travel_api.py
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
```

- [ ] **Step 3: Implement travel router**

```python
# backend/app/routers/travel.py
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

    # Check cache
    cached = (
        db.query(TravelEstimate)
        .filter(
            TravelEstimate.circuit_id == circuit_id,
            TravelEstimate.origin_city == origin.lower().strip(),
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
        "origin_city": origin.lower().strip(),
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
```

- [ ] **Step 4: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.routers.travel import router as travel_router
app.include_router(travel_router)
```

- [ ] **Step 5: Run tests**

Run: `cd backend && .venv/bin/python -m pytest tests/test_travel_api.py -v`
Expected: 4 tests PASS.

Run all: `cd backend && .venv/bin/python -m pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/travel.py backend/app/schemas/__init__.py backend/app/routers/travel.py backend/app/main.py backend/tests/test_travel_api.py
git commit -m "feat: add travel estimate and exchange rate API endpoints"
```

---

## Task 7: Frontend — API Types + Currency Utils

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/currency.ts`

- [ ] **Step 1: Add travel types and fetch functions to api.ts**

Append to `frontend/src/lib/api.ts`:

```typescript
export interface TravelEstimate {
  id: number;
  circuit_id: number;
  origin_city: string;
  origin_country: string;
  origin_airport_code: string;
  flight_price_min: number;
  flight_price_max: number;
  flight_duration_hours: number;
  flight_stops: number;
  train_available: boolean;
  train_price_min: number | null;
  train_price_max: number | null;
  train_duration_hours: number | null;
  local_transport_cost: number;
  hotel_avg_per_night: number;
  last_fetched_at: string;
}

export interface ExchangeRate {
  currency_code: string;
  rate_from_usd: number;
  last_updated_at: string;
}

export async function fetchTravelEstimate(circuitId: number, origin: string): Promise<TravelEstimate> {
  const url = new URL(`${API_URL}/api/travel/estimate`);
  url.searchParams.set("circuit_id", String(circuitId));
  url.searchParams.set("origin", origin);
  const res = await fetch(url.toString());
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to fetch travel estimate" }));
    throw new Error(err.detail || "Failed to fetch travel estimate");
  }
  return res.json();
}

export async function fetchExchangeRates(): Promise<ExchangeRate[]> {
  const res = await fetch(`${API_URL}/api/travel/exchange-rates`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch exchange rates");
  return res.json();
}

export async function fetchCitySuggestions(): Promise<string[]> {
  const res = await fetch(`${API_URL}/api/travel/cities`, { next: { revalidate: 86400 } });
  if (!res.ok) throw new Error("Failed to fetch cities");
  return res.json();
}
```

- [ ] **Step 2: Create currency utils**

```typescript
// frontend/src/lib/currency.ts

export function detectUserCurrency(): string {
  if (typeof navigator === "undefined") return "USD";
  const locale = navigator.language || "en-US";
  const regionCurrencies: Record<string, string> = {
    "en-US": "USD", "en-GB": "GBP", "en-AU": "AUD", "en-CA": "CAD",
    "de": "EUR", "fr": "EUR", "es": "EUR", "it": "EUR", "nl": "EUR",
    "pt-BR": "BRL", "ja": "JPY", "zh": "CNY", "ko": "KRW",
    "ar": "AED", "hi": "INR", "ru": "RUB", "tr": "TRY",
  };
  const lang = locale.split("-").slice(0, 2).join("-");
  return regionCurrencies[lang] || regionCurrencies[locale.split("-")[0]] || "USD";
}

export function convertCurrency(
  amountUsd: number,
  rates: Record<string, number>,
  targetCurrency: string
): number {
  const rate = rates[targetCurrency] || 1;
  return amountUsd * rate;
}

export function formatCurrency(amount: number, currency: string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/lib/api.ts frontend/src/lib/currency.ts
git commit -m "feat: add travel API types, fetch functions, and currency utils"
```

---

## Task 8: Frontend — TravelTab + CurrencySelector Components

**Files:**
- Create: `frontend/src/components/CurrencySelector.tsx`
- Create: `frontend/src/components/TravelTab.tsx`

- [ ] **Step 1: Create CurrencySelector**

```tsx
// frontend/src/components/CurrencySelector.tsx
"use client";

const CURRENCIES = [
  "USD", "EUR", "GBP", "AUD", "CAD", "JPY", "CNY", "BRL",
  "MXN", "SGD", "AED", "CHF", "SEK", "NOK", "DKK", "PLN",
  "HUF", "CZK", "TRY", "INR", "KRW", "THB", "MYR",
];

interface CurrencySelectorProps {
  value: string;
  onChange: (currency: string) => void;
}

export default function CurrencySelector({ value, onChange }: CurrencySelectorProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-2 py-1"
    >
      {CURRENCIES.map((c) => (
        <option key={c} value={c}>{c}</option>
      ))}
    </select>
  );
}
```

- [ ] **Step 2: Create TravelTab**

```tsx
// frontend/src/components/TravelTab.tsx
"use client";

import { useState, useEffect } from "react";
import { fetchTravelEstimate, fetchCitySuggestions } from "@/lib/api";
import type { TravelEstimate, ExchangeRate, TicketListing } from "@/lib/api";
import { detectUserCurrency, convertCurrency, formatCurrency } from "@/lib/currency";
import CurrencySelector from "@/components/CurrencySelector";

interface TravelTabProps {
  circuitId: number;
  exchangeRates: ExchangeRate[];
  tickets: TicketListing[];
}

export default function TravelTab({ circuitId, exchangeRates, tickets }: TravelTabProps) {
  const [origin, setOrigin] = useState("");
  const [groupSize, setGroupSize] = useState(2);
  const [nights, setNights] = useState(2);
  const [currency, setCurrency] = useState("USD");
  const [estimate, setEstimate] = useState<TravelEstimate | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Build rates lookup
  const rates: Record<string, number> = {};
  for (const r of exchangeRates) {
    rates[r.currency_code] = r.rate_from_usd;
  }

  useEffect(() => {
    setCurrency(detectUserCurrency());
    fetchCitySuggestions().then(setSuggestions).catch(() => {});
  }, []);

  function fmt(usd: number): string {
    return formatCurrency(convertCurrency(usd, rates, currency), currency);
  }

  async function handleSearch() {
    if (!origin.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchTravelEstimate(circuitId, origin.trim());
      setEstimate(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to fetch estimate");
      setEstimate(null);
    } finally {
      setLoading(false);
    }
  }

  // Convert ticket prices to USD for consistent total calculation
  // Tickets may be in different currencies — normalize using exchange rates
  const cheapestTicket = tickets.length > 0
    ? Math.min(...tickets.map((t) => {
        const ticketRate = rates[t.currency] || 1;
        return ticketRate > 0 ? t.price / ticketRate : t.price; // convert to USD
      }))
    : null;

  const filteredSuggestions = origin.length >= 2
    ? suggestions.filter((s) => s.startsWith(origin.toLowerCase())).slice(0, 8)
    : [];

  return (
    <div>
      {/* Input Section */}
      <div className="flex gap-3 flex-wrap items-end mb-6">
        <div className="relative">
          <label className="text-xs text-gray-500 block mb-1">From</label>
          <input
            type="text"
            value={origin}
            onChange={(e) => { setOrigin(e.target.value); setShowSuggestions(true); }}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Enter city..."
            className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-2 w-48"
          />
          {showSuggestions && filteredSuggestions.length > 0 && (
            <div className="absolute z-10 mt-1 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg max-h-40 overflow-y-auto">
              {filteredSuggestions.map((s) => (
                <button
                  key={s}
                  onMouseDown={() => { setOrigin(s); setShowSuggestions(false); }}
                  className="block w-full text-left px-3 py-1.5 text-sm text-gray-300 hover:bg-gray-700 capitalize"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Group Size</label>
          <select value={groupSize} onChange={(e) => setGroupSize(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-2">
            {[1,2,3,4,5,6,7,8,9,10].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Nights</label>
          <select value={nights} onChange={(e) => setNights(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-2">
            {[1,2,3,4,5].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Currency</label>
          <CurrencySelector value={currency} onChange={setCurrency} />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading || !origin.trim()}
          className="bg-red-500 hover:bg-red-600 disabled:bg-gray-700 text-white text-sm font-medium px-5 py-2 rounded-lg"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {error && <div className="text-red-400 text-sm mb-4">{error}</div>}

      {/* Results */}
      {estimate && (
        <div>
          {/* Travel Details */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-1">Flights</div>
              {estimate.flight_price_min > 0 ? (
                <>
                  <div className="text-lg font-bold text-blue-400">
                    {fmt(estimate.flight_price_min)} – {fmt(estimate.flight_price_max)}
                  </div>
                  <div className="text-xs text-gray-400">
                    {estimate.flight_duration_hours}h · {estimate.flight_stops === 0 ? "Direct" : `${estimate.flight_stops} stop${estimate.flight_stops > 1 ? "s" : ""}`}
                  </div>
                </>
              ) : (
                <div className="text-sm text-gray-500">No flight data</div>
              )}
            </div>

            {estimate.train_available && (
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-1">Train</div>
                <div className="text-lg font-bold text-green-400">
                  {estimate.train_price_min !== null ? fmt(estimate.train_price_min) : "—"}
                  {estimate.train_price_max !== null && estimate.train_price_max !== estimate.train_price_min
                    ? ` – ${fmt(estimate.train_price_max)}` : ""}
                </div>
                {estimate.train_duration_hours && (
                  <div className="text-xs text-gray-400">{estimate.train_duration_hours}h</div>
                )}
              </div>
            )}

            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-1">Local Transport</div>
              <div className="text-lg font-bold text-yellow-400">{fmt(estimate.local_transport_cost)}</div>
              <div className="text-xs text-gray-400">to circuit (each way)</div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-xs text-gray-500 mb-1">Hotel</div>
              <div className="text-lg font-bold text-purple-400">{fmt(estimate.hotel_avg_per_night)}</div>
              <div className="text-xs text-gray-400">per night avg</div>
            </div>
          </div>

          {/* Total Cost Card */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h3 className="font-bold text-lg mb-4">Total Trip Cost Estimate</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Tickets (cheapest)</span>
                <span>{cheapestTicket ? fmt(cheapestTicket) : "N/A"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Flights (min)</span>
                <span>{estimate.flight_price_min > 0 ? fmt(estimate.flight_price_min) : "N/A"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Hotel ({nights} night{nights > 1 ? "s" : ""})</span>
                <span>{fmt(estimate.hotel_avg_per_night * nights)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Local transport (return)</span>
                <span>{fmt(estimate.local_transport_cost * 2)}</span>
              </div>
              <div className="border-t border-gray-700 pt-2 mt-2">
                <div className="flex justify-between font-bold text-lg">
                  <span>Per person</span>
                  <span className="text-green-400">
                    {fmt(
                      (cheapestTicket || 0) +
                      estimate.flight_price_min +
                      estimate.hotel_avg_per_night * nights +
                      estimate.local_transport_cost * 2
                    )}
                  </span>
                </div>
                {groupSize > 1 && (
                  <div className="flex justify-between font-bold text-lg mt-1">
                    <span>Group total ({groupSize})</span>
                    <span className="text-green-400">
                      {fmt(
                        ((cheapestTicket || 0) +
                        estimate.flight_price_min +
                        estimate.hotel_avg_per_night * nights +
                        estimate.local_transport_cost * 2) * groupSize
                      )}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {!estimate && !loading && !error && (
        <div className="text-center text-gray-500 py-12">
          Enter your origin city to see travel cost estimates
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/CurrencySelector.tsx frontend/src/components/TravelTab.tsx
git commit -m "feat: add TravelTab and CurrencySelector components"
```

---

## Task 9: Frontend — Integrate Travel Tab into Track Detail Page

**Files:**
- Modify: `frontend/src/app/tracks/[id]/TrackDetailClient.tsx`
- Modify: `frontend/src/app/tracks/[id]/page.tsx`

- [ ] **Step 1: Update TrackDetailClient to include Travel tab**

Add to imports:
```tsx
import TravelTab from "@/components/TravelTab";
import type { ExchangeRate } from "@/lib/api";
```

Add `circuitId: number` and `exchangeRates: ExchangeRate[]` to `TrackDetailClientProps`.

Update `activeTab` state type to include `"travel"`:
```tsx
const [activeTab, setActiveTab] = useState<"map" | "table" | "travel">("map");
```

Add a Travel tab button in the tabs section:
```tsx
<button className={tabClass("travel")} onClick={() => setActiveTab("travel")}>
  Travel
</button>
```

Add a new branch in the content section for the travel tab:
```tsx
) : activeTab === "travel" ? (
  <TravelTab
    circuitId={circuitId}
    exchangeRates={exchangeRates}
    tickets={tickets}
  />
```

- [ ] **Step 2: Update page.tsx to fetch exchange rates and pass circuitId**

Add `fetchExchangeRates` import. Fetch exchange rates alongside other data:
```typescript
let exchangeRates: ExchangeRate[] = [];
try {
  exchangeRates = await fetchExchangeRates();
} catch {
  exchangeRates = [];
}
```

Pass to TrackDetailClient:
```tsx
<TrackDetailClient
  circuitId={circuitId}
  circuitName={circuit.name}
  centerLat={circuit.latitude}
  centerLng={circuit.longitude}
  sections={sections}
  tickets={tickets}
  exchangeRates={exchangeRates}
/>
```

- [ ] **Step 3: Verify build**

```bash
cd frontend && npx next build
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/tracks/[id]/
git commit -m "feat: integrate Travel tab into track detail page with cost calculator"
```

---

## Task 10: End-to-End Verification

- [ ] **Step 1: Re-seed database**

```bash
cd backend && rm -f f1journey.db && .venv/bin/python -m app.seed.seed_data
```

- [ ] **Step 2: Run all backend tests**

```bash
cd backend && .venv/bin/python -m pytest tests/ -v
```
Expected: All tests pass.

- [ ] **Step 3: Verify travel API**

```bash
# Test city suggestions
curl -s http://localhost:8000/api/travel/cities | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d)} cities')"

# Test exchange rates
curl -s http://localhost:8000/api/travel/exchange-rates | python3 -m json.tool | head -10

# Test travel estimate (will use cache or live fetch)
curl -s "http://localhost:8000/api/travel/estimate?circuit_id=9&origin=london" | python3 -m json.tool
```

- [ ] **Step 4: Verify frontend**

Start both servers, navigate to any track detail page, click the "Travel" tab:
- Enter origin city with autocomplete working
- See flight/train/hotel estimates (or "No flight data" if API keys not set)
- See total cost card with per-person and group totals
- Currency selector changes all displayed prices

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete subsystem 3 — travel planner with cost calculator"
```
