# Subsystem 1: Core Data Model + Seed Data + Basic Frontend

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the database schema, backend API, and a basic frontend that lists all F1 circuits and race events with key stats.

**Architecture:** FastAPI monolith serving a REST API backed by PostgreSQL via SQLAlchemy. Next.js frontend consuming the API. Seed data manually sourced for all 2026 circuits and races.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic (migrations), Pydantic v2, pytest. Next.js 14 (App Router), TypeScript, Tailwind CSS. PostgreSQL 16.

---

## File Structure

### Backend (`backend/`)
```
backend/
├── pyproject.toml              # Project config, dependencies
├── alembic.ini                 # Alembic migration config
├── alembic/
│   ├── env.py                  # Migration environment
│   └── versions/               # Migration files
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory, CORS, routers
│   ├── config.py               # Settings via pydantic-settings
│   ├── database.py             # Engine, SessionLocal, Base
│   ├── models/
│   │   ├── __init__.py
│   │   ├── circuit.py          # Circuit model
│   │   └── race_event.py       # RaceEvent model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── circuit.py          # Circuit Pydantic schemas
│   │   └── race_event.py       # RaceEvent Pydantic schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── circuits.py         # /api/circuits endpoints
│   │   └── race_events.py      # /api/race-events endpoints
│   └── seed/
│       ├── __init__.py
│       └── seed_data.py        # Seed script with 2026 circuit + race data
└── tests/
    ├── conftest.py             # Test DB fixtures
    ├── test_models.py          # Model unit tests
    ├── test_circuits_api.py    # Circuit endpoint tests
    └── test_race_events_api.py # Race event endpoint tests
```

### Frontend (`frontend/`)
```
frontend/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
├── .env.local.example          # API_URL placeholder
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout, dark theme, nav
│   │   ├── page.tsx            # Dashboard — race calendar + track cards
│   │   └── tracks/
│   │       └── [id]/
│   │           └── page.tsx    # Track detail (basic for now — stats only)
│   ├── components/
│   │   ├── Navbar.tsx          # Top nav bar
│   │   ├── RaceCard.tsx        # Upcoming race card component
│   │   └── TrackStats.tsx      # Track statistics display
│   └── lib/
│       └── api.ts              # API client (fetch wrapper)
```

---

## Task 1: Backend Project Setup

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Initialize backend project with dependencies**

```toml
# backend/pyproject.toml
[project]
name = "f1-journey-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.0",
    "alembic>=1.13.0",
    "pydantic-settings>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",
    "pytest-asyncio>=0.23.0",
]
```

- [ ] **Step 2: Create config module**

```python
# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://localhost:5432/f1journey"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_prefix": "F1_"}

settings = Settings()
```

- [ ] **Step 3: Create database module**

```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: Create FastAPI app**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(title="F1 Journey API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Create empty `__init__.py` files**

Create `backend/app/__init__.py` (empty).

- [ ] **Step 6: Install dependencies and verify**

Run:
```bash
cd backend && pip install -e ".[dev]"
```
Expected: installs successfully.

Run:
```bash
cd backend && python -c "from app.main import app; print(app.title)"
```
Expected: `F1 Journey API`

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: scaffold backend project with FastAPI, config, and database setup"
```

---

## Task 2: Database Models — Circuit and RaceEvent

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/circuit.py`
- Create: `backend/app/models/race_event.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: Write model tests**

```python
# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def db():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()
```

```python
# backend/tests/test_models.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd backend && python -m pytest tests/test_models.py -v
```
Expected: FAIL — models don't exist yet.

- [ ] **Step 3: Implement Circuit model**

```python
# backend/app/models/circuit.py
from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Circuit(Base):
    __tablename__ = "circuits"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(100))
    continent: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(100))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    track_type: Mapped[str] = mapped_column(String(20))  # "street" or "permanent"
    track_length_km: Mapped[float] = mapped_column(Float)
    number_of_turns: Mapped[int] = mapped_column(Integer)
    drs_zones_count: Mapped[int] = mapped_column(Integer)
    overtake_difficulty: Mapped[int] = mapped_column(Integer)  # 1-10
    avg_overtakes_per_race: Mapped[float] = mapped_column(Float)
    rain_probability_pct: Mapped[int] = mapped_column(Integer)
    nearest_airport: Mapped[str] = mapped_column(String(200))
    local_transport_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    atmosphere_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    fan_reviews_summary: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    elevation_change: Mapped[float | None] = mapped_column(Float, nullable=True)

    race_events: Mapped[list["RaceEvent"]] = relationship(back_populates="circuit")
```

- [ ] **Step 4: Implement RaceEvent model**

```python
# backend/app/models/race_event.py
from datetime import date

from sqlalchemy import String, Integer, Float, ForeignKey, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RaceEvent(Base):
    __tablename__ = "race_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"))
    season_year: Mapped[int] = mapped_column(Integer)
    race_name: Mapped[str] = mapped_column(String(200))
    race_date: Mapped[date] = mapped_column(Date)
    sprint_weekend: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20))  # "upcoming" or "completed"
    total_overtakes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weather_actual: Mapped[str | None] = mapped_column(String(100), nullable=True)

    circuit: Mapped["Circuit"] = relationship(back_populates="race_events")
```

- [ ] **Step 5: Create models `__init__.py`**

```python
# backend/app/models/__init__.py
from app.models.circuit import Circuit
from app.models.race_event import RaceEvent

__all__ = ["Circuit", "RaceEvent"]
```

- [ ] **Step 6: Run tests to verify they pass**

Run:
```bash
cd backend && python -m pytest tests/test_models.py -v
```
Expected: 3 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/ backend/tests/
git commit -m "feat: add Circuit and RaceEvent SQLAlchemy models with tests"
```

---

## Task 3: Alembic Migrations

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/` (auto-generated)

- [ ] **Step 1: Initialize Alembic**

Run:
```bash
cd backend && alembic init alembic
```

- [ ] **Step 2: Configure `alembic/env.py`**

Replace the generated `env.py` target_metadata section:

```python
# At the top of alembic/env.py, add:
from app.database import Base
from app.models import Circuit, RaceEvent  # noqa: F401

# Replace target_metadata line:
target_metadata = Base.metadata
```

Also update `sqlalchemy.url` in `alembic.ini` to read from environment:
```ini
# In alembic.ini, set:
sqlalchemy.url = postgresql://localhost:5432/f1journey
```

- [ ] **Step 3: Generate initial migration**

Run:
```bash
cd backend && alembic revision --autogenerate -m "create circuits and race_events tables"
```
Expected: creates a migration file in `alembic/versions/`.

- [ ] **Step 4: Verify migration file looks correct**

Read the generated migration file. It should contain `create_table('circuits', ...)` and `create_table('race_events', ...)` with all columns and the foreign key.

- [ ] **Step 5: Commit**

```bash
git add backend/alembic.ini backend/alembic/
git commit -m "feat: add Alembic migrations for circuits and race_events"
```

---

## Task 4: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/circuit.py`
- Create: `backend/app/schemas/race_event.py`

- [ ] **Step 1: Create Circuit schemas**

```python
# backend/app/schemas/circuit.py
from pydantic import BaseModel


class CircuitBase(BaseModel):
    name: str
    country: str
    continent: str
    city: str
    latitude: float
    longitude: float
    track_type: str
    track_length_km: float
    number_of_turns: int
    drs_zones_count: int
    overtake_difficulty: int
    avg_overtakes_per_race: float
    rain_probability_pct: int
    nearest_airport: str
    local_transport_notes: str | None = None
    atmosphere_rating: float | None = None
    fan_reviews_summary: str | None = None
    elevation_change: float | None = None


class CircuitRead(CircuitBase):
    id: int

    model_config = {"from_attributes": True}


class CircuitList(BaseModel):
    id: int
    name: str
    country: str
    continent: str
    track_type: str
    overtake_difficulty: int
    avg_overtakes_per_race: float
    rain_probability_pct: int

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Create RaceEvent schemas**

```python
# backend/app/schemas/race_event.py
from datetime import date

from pydantic import BaseModel


class RaceEventBase(BaseModel):
    circuit_id: int
    season_year: int
    race_name: str
    race_date: date
    sprint_weekend: bool = False
    status: str
    total_overtakes: int | None = None
    weather_actual: str | None = None


class RaceEventRead(RaceEventBase):
    id: int

    model_config = {"from_attributes": True}


class RaceEventWithCircuit(RaceEventRead):
    circuit_name: str
    circuit_country: str
    continent: str
```

- [ ] **Step 3: Create schemas `__init__.py`**

```python
# backend/app/schemas/__init__.py
from app.schemas.circuit import CircuitBase, CircuitRead, CircuitList
from app.schemas.race_event import RaceEventBase, RaceEventRead, RaceEventWithCircuit

__all__ = [
    "CircuitBase", "CircuitRead", "CircuitList",
    "RaceEventBase", "RaceEventRead", "RaceEventWithCircuit",
]
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: add Pydantic schemas for circuits and race events"
```

---

## Task 5: API Endpoints — Circuits

**Files:**
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/circuits.py`
- Modify: `backend/app/main.py` (register router)
- Create: `backend/tests/test_circuits_api.py`

- [ ] **Step 1: Write API tests for circuits**

```python
# backend/tests/test_circuits_api.py
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
    assert data[0]["name"] == "Silverstone"


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd backend && python -m pytest tests/test_circuits_api.py -v
```
Expected: FAIL — router doesn't exist.

- [ ] **Step 3: Implement circuits router**

```python
# backend/app/routers/__init__.py
```

```python
# backend/app/routers/circuits.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.circuit import Circuit
from app.schemas.circuit import CircuitRead, CircuitList

router = APIRouter(prefix="/api/circuits", tags=["circuits"])


@router.get("", response_model=list[CircuitList])
def list_circuits(
    continent: str | None = None,
    track_type: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Circuit)
    if continent:
        query = query.filter(Circuit.continent == continent)
    if track_type:
        query = query.filter(Circuit.track_type == track_type)
    return query.order_by(Circuit.name).all()


@router.get("/{circuit_id}", response_model=CircuitRead)
def get_circuit(circuit_id: int, db: Session = Depends(get_db)):
    circuit = db.get(Circuit, circuit_id)
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    return circuit
```

- [ ] **Step 4: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.routers.circuits import router as circuits_router

app.include_router(circuits_router)
```

- [ ] **Step 5: Run tests to verify they pass**

Run:
```bash
cd backend && python -m pytest tests/test_circuits_api.py -v
```
Expected: 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/ backend/app/main.py backend/tests/test_circuits_api.py
git commit -m "feat: add circuits API endpoints with filtering"
```

---

## Task 6: API Endpoints — Race Events

**Files:**
- Create: `backend/app/routers/race_events.py`
- Modify: `backend/app/main.py` (register router)
- Create: `backend/tests/test_race_events_api.py`

- [ ] **Step 1: Write API tests for race events**

```python
# backend/tests/test_race_events_api.py
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Circuit, RaceEvent

TEST_DATABASE_URL = "sqlite:///./test_api_events.db"
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
    circuit = Circuit(
        name="Silverstone", country="United Kingdom", continent="Europe",
        city="Silverstone", latitude=52.07, longitude=-1.01,
        track_type="permanent", track_length_km=5.891, number_of_turns=18,
        drs_zones_count=2, overtake_difficulty=6, avg_overtakes_per_race=42.5,
        rain_probability_pct=55, nearest_airport="London Luton",
    )
    db.add(circuit)
    db.commit()
    events = [
        RaceEvent(
            circuit_id=circuit.id, season_year=2026, race_name="British Grand Prix",
            race_date=date(2026, 7, 5), sprint_weekend=False, status="upcoming",
        ),
        RaceEvent(
            circuit_id=circuit.id, season_year=2025, race_name="British Grand Prix 2025",
            race_date=date(2025, 7, 6), sprint_weekend=False, status="completed",
            total_overtakes=45,
        ),
    ]
    db.add_all(events)
    db.commit()
    db.close()


def teardown_function():
    Base.metadata.drop_all(engine)


def test_list_race_events():
    resp = client.get("/api/race-events")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_list_race_events_filter_by_season():
    resp = client.get("/api/race-events?season=2026")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["season_year"] == 2026


def test_list_race_events_filter_by_status():
    resp = client.get("/api/race-events?status=upcoming")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "upcoming"


def test_get_race_event_by_id():
    resp = client.get("/api/race-events/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["race_name"] == "British Grand Prix"
    assert data["circuit_name"] == "Silverstone"


def test_get_race_event_not_found():
    resp = client.get("/api/race-events/999")
    assert resp.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd backend && python -m pytest tests/test_race_events_api.py -v
```
Expected: FAIL — router doesn't exist.

- [ ] **Step 3: Implement race events router**

```python
# backend/app/routers/race_events.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.circuit import Circuit
from app.models.race_event import RaceEvent
from app.schemas.race_event import RaceEventRead, RaceEventWithCircuit

router = APIRouter(prefix="/api/race-events", tags=["race-events"])


@router.get("", response_model=list[RaceEventRead])
def list_race_events(
    season: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(RaceEvent)
    if season:
        query = query.filter(RaceEvent.season_year == season)
    if status:
        query = query.filter(RaceEvent.status == status)
    return query.order_by(RaceEvent.race_date).all()


@router.get("/{event_id}", response_model=RaceEventWithCircuit)
def get_race_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(RaceEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Race event not found")
    circuit = db.get(Circuit, event.circuit_id)
    return RaceEventWithCircuit(
        id=event.id,
        circuit_id=event.circuit_id,
        season_year=event.season_year,
        race_name=event.race_name,
        race_date=event.race_date,
        sprint_weekend=event.sprint_weekend,
        status=event.status,
        total_overtakes=event.total_overtakes,
        weather_actual=event.weather_actual,
        circuit_name=circuit.name,
        circuit_country=circuit.country,
        continent=circuit.continent,
    )
```

- [ ] **Step 4: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.routers.race_events import router as race_events_router

app.include_router(race_events_router)
```

- [ ] **Step 5: Run tests to verify they pass**

Run:
```bash
cd backend && python -m pytest tests/test_race_events_api.py -v
```
Expected: 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/race_events.py backend/app/main.py backend/tests/test_race_events_api.py
git commit -m "feat: add race events API endpoints with filtering"
```

---

## Task 7: Seed Data — 2026 F1 Calendar

**Files:**
- Create: `backend/app/seed/__init__.py`
- Create: `backend/app/seed/seed_data.py`

- [ ] **Step 1: Create seed script with all 2026 circuits and races**

```python
# backend/app/seed/__init__.py
```

```python
# backend/app/seed/seed_data.py
"""Seed the database with 2026 F1 calendar data.

Run: python -m app.seed.seed_data
"""
from datetime import date

from app.database import engine, SessionLocal, Base
from app.models import Circuit, RaceEvent

CIRCUITS = [
    {
        "name": "Bahrain International Circuit",
        "country": "Bahrain", "continent": "Asia", "city": "Sakhir",
        "latitude": 26.0325, "longitude": 50.5106,
        "track_type": "permanent", "track_length_km": 5.412,
        "number_of_turns": 15, "drs_zones_count": 3,
        "overtake_difficulty": 4, "avg_overtakes_per_race": 45.0,
        "rain_probability_pct": 2, "nearest_airport": "Bahrain International (BAH)",
    },
    {
        "name": "Jeddah Corniche Circuit",
        "country": "Saudi Arabia", "continent": "Asia", "city": "Jeddah",
        "latitude": 21.6319, "longitude": 39.1044,
        "track_type": "street", "track_length_km": 6.174,
        "number_of_turns": 27, "drs_zones_count": 3,
        "overtake_difficulty": 5, "avg_overtakes_per_race": 35.0,
        "rain_probability_pct": 1, "nearest_airport": "King Abdulaziz (JED)",
    },
    {
        "name": "Albert Park Circuit",
        "country": "Australia", "continent": "Oceania", "city": "Melbourne",
        "latitude": -37.8497, "longitude": 144.9680,
        "track_type": "street", "track_length_km": 5.278,
        "number_of_turns": 14, "drs_zones_count": 4,
        "overtake_difficulty": 5, "avg_overtakes_per_race": 30.0,
        "rain_probability_pct": 25, "nearest_airport": "Melbourne Tullamarine (MEL)",
    },
    {
        "name": "Suzuka International Racing Course",
        "country": "Japan", "continent": "Asia", "city": "Suzuka",
        "latitude": 34.8431, "longitude": 136.5407,
        "track_type": "permanent", "track_length_km": 5.807,
        "number_of_turns": 18, "drs_zones_count": 1,
        "overtake_difficulty": 7, "avg_overtakes_per_race": 20.0,
        "rain_probability_pct": 35, "nearest_airport": "Chubu Centrair (NGO)",
    },
    {
        "name": "Shanghai International Circuit",
        "country": "China", "continent": "Asia", "city": "Shanghai",
        "latitude": 31.3389, "longitude": 121.2197,
        "track_type": "permanent", "track_length_km": 5.451,
        "number_of_turns": 16, "drs_zones_count": 2,
        "overtake_difficulty": 5, "avg_overtakes_per_race": 38.0,
        "rain_probability_pct": 30, "nearest_airport": "Shanghai Pudong (PVG)",
    },
    {
        "name": "Miami International Autodrome",
        "country": "United States", "continent": "North America", "city": "Miami",
        "latitude": 25.9581, "longitude": -80.2389,
        "track_type": "street", "track_length_km": 5.412,
        "number_of_turns": 19, "drs_zones_count": 3,
        "overtake_difficulty": 5, "avg_overtakes_per_race": 32.0,
        "rain_probability_pct": 40, "nearest_airport": "Miami International (MIA)",
    },
    {
        "name": "Autodromo Enzo e Dino Ferrari",
        "country": "Italy", "continent": "Europe", "city": "Imola",
        "latitude": 44.3439, "longitude": 11.7167,
        "track_type": "permanent", "track_length_km": 4.909,
        "number_of_turns": 19, "drs_zones_count": 2,
        "overtake_difficulty": 7, "avg_overtakes_per_race": 22.0,
        "rain_probability_pct": 25, "nearest_airport": "Bologna (BLQ)",
    },
    {
        "name": "Circuit de Monaco",
        "country": "Monaco", "continent": "Europe", "city": "Monte Carlo",
        "latitude": 43.7347, "longitude": 7.4206,
        "track_type": "street", "track_length_km": 3.337,
        "number_of_turns": 19, "drs_zones_count": 1,
        "overtake_difficulty": 2, "avg_overtakes_per_race": 5.0,
        "rain_probability_pct": 15, "nearest_airport": "Nice Cote d'Azur (NCE)",
    },
    {
        "name": "Circuit de Barcelona-Catalunya",
        "country": "Spain", "continent": "Europe", "city": "Barcelona",
        "latitude": 41.5700, "longitude": 2.2611,
        "track_type": "permanent", "track_length_km": 4.657,
        "number_of_turns": 14, "drs_zones_count": 2,
        "overtake_difficulty": 6, "avg_overtakes_per_race": 25.0,
        "rain_probability_pct": 10, "nearest_airport": "Barcelona El Prat (BCN)",
    },
    {
        "name": "Circuit Gilles Villeneuve",
        "country": "Canada", "continent": "North America", "city": "Montreal",
        "latitude": 45.5000, "longitude": -73.5228,
        "track_type": "street", "track_length_km": 4.361,
        "number_of_turns": 14, "drs_zones_count": 2,
        "overtake_difficulty": 5, "avg_overtakes_per_race": 35.0,
        "rain_probability_pct": 20, "nearest_airport": "Montreal Trudeau (YUL)",
    },
    {
        "name": "Red Bull Ring",
        "country": "Austria", "continent": "Europe", "city": "Spielberg",
        "latitude": 47.2197, "longitude": 14.7647,
        "track_type": "permanent", "track_length_km": 4.318,
        "number_of_turns": 10, "drs_zones_count": 3,
        "overtake_difficulty": 4, "avg_overtakes_per_race": 40.0,
        "rain_probability_pct": 30, "nearest_airport": "Graz (GRZ)",
    },
    {
        "name": "Silverstone Circuit",
        "country": "United Kingdom", "continent": "Europe", "city": "Silverstone",
        "latitude": 52.0786, "longitude": -1.0169,
        "track_type": "permanent", "track_length_km": 5.891,
        "number_of_turns": 18, "drs_zones_count": 2,
        "overtake_difficulty": 6, "avg_overtakes_per_race": 42.5,
        "rain_probability_pct": 55, "nearest_airport": "London Luton (LTN)",
    },
    {
        "name": "Hungaroring",
        "country": "Hungary", "continent": "Europe", "city": "Budapest",
        "latitude": 47.5789, "longitude": 19.2486,
        "track_type": "permanent", "track_length_km": 4.381,
        "number_of_turns": 14, "drs_zones_count": 2,
        "overtake_difficulty": 8, "avg_overtakes_per_race": 15.0,
        "rain_probability_pct": 20, "nearest_airport": "Budapest Liszt Ferenc (BUD)",
    },
    {
        "name": "Circuit de Spa-Francorchamps",
        "country": "Belgium", "continent": "Europe", "city": "Stavelot",
        "latitude": 50.4372, "longitude": 5.9714,
        "track_type": "permanent", "track_length_km": 7.004,
        "number_of_turns": 19, "drs_zones_count": 2,
        "overtake_difficulty": 4, "avg_overtakes_per_race": 55.0,
        "rain_probability_pct": 60, "nearest_airport": "Brussels (BRU)",
    },
    {
        "name": "Circuit Zandvoort",
        "country": "Netherlands", "continent": "Europe", "city": "Zandvoort",
        "latitude": 52.3888, "longitude": 4.5409,
        "track_type": "permanent", "track_length_km": 4.259,
        "number_of_turns": 14, "drs_zones_count": 2,
        "overtake_difficulty": 8, "avg_overtakes_per_race": 12.0,
        "rain_probability_pct": 35, "nearest_airport": "Amsterdam Schiphol (AMS)",
    },
    {
        "name": "Autodromo Nazionale di Monza",
        "country": "Italy", "continent": "Europe", "city": "Monza",
        "latitude": 45.6156, "longitude": 9.2811,
        "track_type": "permanent", "track_length_km": 5.793,
        "number_of_turns": 11, "drs_zones_count": 2,
        "overtake_difficulty": 3, "avg_overtakes_per_race": 48.0,
        "rain_probability_pct": 20, "nearest_airport": "Milan Malpensa (MXP)",
    },
    {
        "name": "Baku City Circuit",
        "country": "Azerbaijan", "continent": "Europe", "city": "Baku",
        "latitude": 40.3725, "longitude": 49.8533,
        "track_type": "street", "track_length_km": 6.003,
        "number_of_turns": 20, "drs_zones_count": 2,
        "overtake_difficulty": 4, "avg_overtakes_per_race": 40.0,
        "rain_probability_pct": 10, "nearest_airport": "Heydar Aliyev (GYD)",
    },
    {
        "name": "Marina Bay Street Circuit",
        "country": "Singapore", "continent": "Asia", "city": "Singapore",
        "latitude": 1.2914, "longitude": 103.8640,
        "track_type": "street", "track_length_km": 4.940,
        "number_of_turns": 19, "drs_zones_count": 3,
        "overtake_difficulty": 7, "avg_overtakes_per_race": 18.0,
        "rain_probability_pct": 40, "nearest_airport": "Changi (SIN)",
    },
    {
        "name": "Circuit of the Americas",
        "country": "United States", "continent": "North America", "city": "Austin",
        "latitude": 30.1328, "longitude": -97.6411,
        "track_type": "permanent", "track_length_km": 5.513,
        "number_of_turns": 20, "drs_zones_count": 2,
        "overtake_difficulty": 5, "avg_overtakes_per_race": 35.0,
        "rain_probability_pct": 20, "nearest_airport": "Austin-Bergstrom (AUS)",
    },
    {
        "name": "Autodromo Hermanos Rodriguez",
        "country": "Mexico", "continent": "North America", "city": "Mexico City",
        "latitude": 19.4042, "longitude": -99.0907,
        "track_type": "permanent", "track_length_km": 4.304,
        "number_of_turns": 17, "drs_zones_count": 3,
        "overtake_difficulty": 5, "avg_overtakes_per_race": 30.0,
        "rain_probability_pct": 25, "nearest_airport": "Mexico City (MEX)",
    },
    {
        "name": "Interlagos",
        "country": "Brazil", "continent": "South America", "city": "Sao Paulo",
        "latitude": -23.7014, "longitude": -46.6969,
        "track_type": "permanent", "track_length_km": 4.309,
        "number_of_turns": 15, "drs_zones_count": 2,
        "overtake_difficulty": 4, "avg_overtakes_per_race": 42.0,
        "rain_probability_pct": 45, "nearest_airport": "Sao Paulo Guarulhos (GRU)",
    },
    {
        "name": "Las Vegas Street Circuit",
        "country": "United States", "continent": "North America", "city": "Las Vegas",
        "latitude": 36.1147, "longitude": -115.1728,
        "track_type": "street", "track_length_km": 6.201,
        "number_of_turns": 17, "drs_zones_count": 2,
        "overtake_difficulty": 4, "avg_overtakes_per_race": 38.0,
        "rain_probability_pct": 5, "nearest_airport": "Harry Reid International (LAS)",
    },
    {
        "name": "Losail International Circuit",
        "country": "Qatar", "continent": "Asia", "city": "Lusail",
        "latitude": 25.4900, "longitude": 51.4542,
        "track_type": "permanent", "track_length_km": 5.419,
        "number_of_turns": 16, "drs_zones_count": 2,
        "overtake_difficulty": 5, "avg_overtakes_per_race": 30.0,
        "rain_probability_pct": 1, "nearest_airport": "Hamad International (DOH)",
    },
    {
        "name": "Yas Marina Circuit",
        "country": "United Arab Emirates", "continent": "Asia", "city": "Abu Dhabi",
        "latitude": 24.4672, "longitude": 54.6031,
        "track_type": "permanent", "track_length_km": 5.281,
        "number_of_turns": 16, "drs_zones_count": 2,
        "overtake_difficulty": 5, "avg_overtakes_per_race": 35.0,
        "rain_probability_pct": 1, "nearest_airport": "Abu Dhabi (AUH)",
    },
]

# 2026 race calendar (approximate dates — adjust when official calendar is confirmed)
RACES_2026 = [
    ("Bahrain International Circuit", "Bahrain Grand Prix", date(2026, 3, 1), False),
    ("Jeddah Corniche Circuit", "Saudi Arabian Grand Prix", date(2026, 3, 15), False),
    ("Albert Park Circuit", "Australian Grand Prix", date(2026, 3, 29), False),
    ("Suzuka International Racing Course", "Japanese Grand Prix", date(2026, 4, 12), False),
    ("Shanghai International Circuit", "Chinese Grand Prix", date(2026, 4, 26), True),
    ("Miami International Autodrome", "Miami Grand Prix", date(2026, 5, 10), True),
    ("Autodromo Enzo e Dino Ferrari", "Emilia Romagna Grand Prix", date(2026, 5, 24), False),
    ("Circuit de Monaco", "Monaco Grand Prix", date(2026, 5, 31), False),
    ("Circuit de Barcelona-Catalunya", "Spanish Grand Prix", date(2026, 6, 14), False),
    ("Circuit Gilles Villeneuve", "Canadian Grand Prix", date(2026, 6, 28), False),
    ("Red Bull Ring", "Austrian Grand Prix", date(2026, 7, 12), True),
    ("Silverstone Circuit", "British Grand Prix", date(2026, 7, 5), False),
    ("Hungaroring", "Hungarian Grand Prix", date(2026, 7, 26), False),
    ("Circuit de Spa-Francorchamps", "Belgian Grand Prix", date(2026, 8, 2), False),
    ("Circuit Zandvoort", "Dutch Grand Prix", date(2026, 8, 30), False),
    ("Autodromo Nazionale di Monza", "Italian Grand Prix", date(2026, 9, 6), False),
    ("Baku City Circuit", "Azerbaijan Grand Prix", date(2026, 9, 20), True),
    ("Marina Bay Street Circuit", "Singapore Grand Prix", date(2026, 10, 4), False),
    ("Circuit of the Americas", "United States Grand Prix", date(2026, 10, 18), True),
    ("Autodromo Hermanos Rodriguez", "Mexico City Grand Prix", date(2026, 11, 1), False),
    ("Interlagos", "Sao Paulo Grand Prix", date(2026, 11, 8), True),
    ("Las Vegas Street Circuit", "Las Vegas Grand Prix", date(2026, 11, 22), False),
    ("Losail International Circuit", "Qatar Grand Prix", date(2026, 11, 29), False),
    ("Yas Marina Circuit", "Abu Dhabi Grand Prix", date(2026, 12, 6), False),
]


def seed():
    Base.metadata.create_all(engine)
    db = SessionLocal()

    if db.query(Circuit).count() > 0:
        print("Database already seeded. Skipping.")
        db.close()
        return

    circuit_map = {}
    for data in CIRCUITS:
        circuit = Circuit(**data)
        db.add(circuit)
        db.flush()
        circuit_map[circuit.name] = circuit.id

    for circuit_name, race_name, race_date, sprint in RACES_2026:
        event = RaceEvent(
            circuit_id=circuit_map[circuit_name],
            season_year=2026,
            race_name=race_name,
            race_date=race_date,
            sprint_weekend=sprint,
            status="upcoming",
        )
        db.add(event)

    db.commit()
    print(f"Seeded {len(CIRCUITS)} circuits and {len(RACES_2026)} race events.")
    db.close()


if __name__ == "__main__":
    seed()
```

- [ ] **Step 2: Test the seed script loads without errors**

Run:
```bash
cd backend && python -c "from app.seed.seed_data import CIRCUITS, RACES_2026; print(f'{len(CIRCUITS)} circuits, {len(RACES_2026)} races')"
```
Expected: `24 circuits, 24 races`

- [ ] **Step 3: Commit**

```bash
git add backend/app/seed/
git commit -m "feat: add seed data for all 2026 F1 circuits and race calendar"
```

---

## Task 8: Frontend Setup

**Files:**
- Create: `frontend/` (via create-next-app)
- Create: `frontend/.env.local.example`
- Create: `frontend/src/lib/api.ts`

- [ ] **Step 1: Scaffold Next.js project**

Run:
```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --no-import-alias
```

- [ ] **Step 2: Create environment example**

```
# frontend/.env.local.example
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Also create `frontend/.env.local` with same content for local dev.

- [ ] **Step 3: Create API client**

```typescript
// frontend/src/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface CircuitListItem {
  id: number;
  name: string;
  country: string;
  continent: string;
  track_type: string;
  overtake_difficulty: number;
  avg_overtakes_per_race: number;
  rain_probability_pct: number;
}

export interface Circuit extends CircuitListItem {
  city: string;
  latitude: number;
  longitude: number;
  track_length_km: number;
  number_of_turns: number;
  drs_zones_count: number;
  nearest_airport: string;
  local_transport_notes: string | null;
  atmosphere_rating: number | null;
  fan_reviews_summary: string | null;
  elevation_change: number | null;
}

export interface RaceEvent {
  id: number;
  circuit_id: number;
  season_year: number;
  race_name: string;
  race_date: string;
  sprint_weekend: boolean;
  status: string;
  total_overtakes: number | null;
  weather_actual: string | null;
}

export interface RaceEventWithCircuit extends RaceEvent {
  circuit_name: string;
  circuit_country: string;
  continent: string;
}

export async function fetchCircuits(params?: {
  continent?: string;
  track_type?: string;
}): Promise<CircuitListItem[]> {
  const url = new URL(`${API_URL}/api/circuits`);
  if (params?.continent) url.searchParams.set("continent", params.continent);
  if (params?.track_type) url.searchParams.set("track_type", params.track_type);
  const res = await fetch(url.toString(), { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch circuits");
  return res.json();
}

export async function fetchCircuit(id: number): Promise<Circuit> {
  const res = await fetch(`${API_URL}/api/circuits/${id}`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch circuit");
  return res.json();
}

export async function fetchRaceEvents(params?: {
  season?: number;
  status?: string;
}): Promise<RaceEvent[]> {
  const url = new URL(`${API_URL}/api/race-events`);
  if (params?.season) url.searchParams.set("season", String(params.season));
  if (params?.status) url.searchParams.set("status", params.status);
  const res = await fetch(url.toString(), { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch race events");
  return res.json();
}

export async function fetchRaceEvent(id: number): Promise<RaceEventWithCircuit> {
  const res = await fetch(`${API_URL}/api/race-events/${id}`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch race event");
  return res.json();
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Next.js frontend with API client and types"
```

---

## Task 9: Frontend — Navbar Component

**Files:**
- Create: `frontend/src/components/Navbar.tsx`
- Modify: `frontend/src/app/layout.tsx`

- [ ] **Step 1: Create Navbar component**

```tsx
// frontend/src/components/Navbar.tsx
import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-gray-950">
      <div className="flex items-center gap-8">
        <Link href="/" className="text-lg font-bold text-red-500">
          F1 Journey
        </Link>
        <Link href="/" className="text-sm text-gray-400 hover:text-white">
          Explore
        </Link>
      </div>
      <div className="flex items-center gap-3">
        <input
          type="text"
          placeholder="Search tracks..."
          className="bg-gray-800 text-sm text-gray-300 px-3 py-1.5 rounded-md w-48 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-600"
          readOnly
        />
      </div>
    </nav>
  );
}
```

- [ ] **Step 2: Update root layout with dark theme and Navbar**

Replace the content of `frontend/src/app/layout.tsx`:

```tsx
// frontend/src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "F1 Journey — Find Your Perfect Grand Prix Weekend",
  description: "Compare tracks, seats, and travel costs across every Formula 1 Grand Prix",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-gray-950 text-gray-100 min-h-screen`}>
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Verify it renders**

Run:
```bash
cd frontend && npm run dev
```
Open http://localhost:3000 — should see dark background with "F1 Journey" nav bar.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/Navbar.tsx frontend/src/app/layout.tsx
git commit -m "feat: add Navbar component and dark theme layout"
```

---

## Task 10: Frontend — RaceCard Component

**Files:**
- Create: `frontend/src/components/RaceCard.tsx`

- [ ] **Step 1: Create RaceCard component**

```tsx
// frontend/src/components/RaceCard.tsx
import Link from "next/link";

interface RaceCardProps {
  circuitId: number;
  raceName: string;
  circuitName: string;
  country: string;
  raceDate: string;
  trackType: string;
  overtakeDifficulty: number;
  rainProbabilityPct: number;
  sprintWeekend: boolean;
}

function overtakeColor(score: number): string {
  if (score >= 7) return "text-green-400";
  if (score >= 4) return "text-yellow-400";
  return "text-red-400";
}

function rainColor(pct: number): string {
  if (pct >= 40) return "text-red-400";
  if (pct >= 20) return "text-blue-400";
  return "text-green-400";
}

export default function RaceCard({
  circuitId,
  raceName,
  circuitName,
  country,
  raceDate,
  trackType,
  overtakeDifficulty,
  rainProbabilityPct,
  sprintWeekend,
}: RaceCardProps) {
  const dateStr = new Date(raceDate).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  const typeColor = trackType === "street" ? "bg-yellow-500/10 text-yellow-500" : "bg-green-500/10 text-green-500";

  return (
    <Link href={`/tracks/${circuitId}`}>
      <div className="min-w-[220px] bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-gray-500 transition-colors cursor-pointer">
        <div className="flex items-center justify-between mb-2">
          <span className="font-bold text-sm truncate">{circuitName}</span>
          <span className={`text-[10px] px-2 py-0.5 rounded ${typeColor}`}>
            {trackType === "street" ? "Street" : "Permanent"}
          </span>
        </div>
        <div className="text-xs text-gray-400 mb-1">{raceName}</div>
        <div className="text-xs text-gray-500 mb-2">{dateStr} &bull; {country}</div>
        <div className="flex gap-3 text-[11px] mb-2">
          <span className={overtakeColor(10 - overtakeDifficulty)}>
            Overtaking: {10 - overtakeDifficulty}/10
          </span>
          <span className={rainColor(rainProbabilityPct)}>
            Rain: {rainProbabilityPct}%
          </span>
        </div>
        {sprintWeekend && (
          <span className="text-[10px] bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded">
            Sprint
          </span>
        )}
      </div>
    </Link>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/RaceCard.tsx
git commit -m "feat: add RaceCard component for upcoming race display"
```

---

## Task 11: Frontend — Dashboard Page

**Files:**
- Modify: `frontend/src/app/page.tsx`

- [ ] **Step 1: Build the dashboard page**

```tsx
// frontend/src/app/page.tsx
import RaceCard from "@/components/RaceCard";
import { fetchCircuits, fetchRaceEvents } from "@/lib/api";

export default async function Home() {
  let circuits;
  let raceEvents;

  try {
    [circuits, raceEvents] = await Promise.all([
      fetchCircuits(),
      fetchRaceEvents({ season: 2026, status: "upcoming" }),
    ]);
  } catch {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <h2 className="text-xl font-bold mb-2">Unable to connect to API</h2>
          <p className="text-gray-400">Make sure the backend is running on port 8000</p>
        </div>
      </div>
    );
  }

  const circuitMap = Object.fromEntries(circuits.map((c) => [c.id, c]));

  return (
    <div>
      {/* Hero */}
      <div className="px-6 py-8 bg-gradient-to-br from-indigo-950 to-gray-950">
        <h1 className="text-2xl font-bold mb-1">Find your perfect F1 weekend</h1>
        <p className="text-gray-400 text-sm">
          Compare tracks, seats, and travel costs across every Grand Prix
        </p>
      </div>

      {/* Upcoming Races */}
      <div className="px-6 py-6">
        <h2 className="text-lg font-bold mb-4">Upcoming Races — 2026</h2>
        <div className="flex gap-3 overflow-x-auto pb-2">
          {raceEvents.map((event) => {
            const circuit = circuitMap[event.circuit_id];
            if (!circuit) return null;
            return (
              <RaceCard
                key={event.id}
                circuitId={circuit.id}
                raceName={event.race_name}
                circuitName={circuit.name}
                country={circuit.country}
                raceDate={event.race_date}
                trackType={circuit.track_type}
                overtakeDifficulty={circuit.overtake_difficulty}
                rainProbabilityPct={circuit.rain_probability_pct}
                sprintWeekend={event.sprint_weekend}
              />
            );
          })}
        </div>
      </div>

      {/* All Circuits Table */}
      <div className="px-6 py-6">
        <h2 className="text-lg font-bold mb-4">All Circuits</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-gray-400 text-left">
                <th className="pb-2 pr-4">Circuit</th>
                <th className="pb-2 pr-4">Country</th>
                <th className="pb-2 pr-4">Continent</th>
                <th className="pb-2 pr-4">Type</th>
                <th className="pb-2 pr-4">Overtaking</th>
                <th className="pb-2 pr-4">Avg Overtakes</th>
                <th className="pb-2">Rain %</th>
              </tr>
            </thead>
            <tbody>
              {circuits.map((circuit) => (
                <tr key={circuit.id} className="border-b border-gray-800/50 hover:bg-gray-900">
                  <td className="py-2 pr-4">
                    <a href={`/tracks/${circuit.id}`} className="text-blue-400 hover:underline">
                      {circuit.name}
                    </a>
                  </td>
                  <td className="py-2 pr-4 text-gray-400">{circuit.country}</td>
                  <td className="py-2 pr-4 text-gray-400">{circuit.continent}</td>
                  <td className="py-2 pr-4">
                    <span className={`text-xs px-2 py-0.5 rounded ${circuit.track_type === "street" ? "bg-yellow-500/10 text-yellow-500" : "bg-green-500/10 text-green-500"}`}>
                      {circuit.track_type}
                    </span>
                  </td>
                  <td className="py-2 pr-4">{10 - circuit.overtake_difficulty}/10</td>
                  <td className="py-2 pr-4">{circuit.avg_overtakes_per_race}</td>
                  <td className="py-2">{circuit.rain_probability_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify it renders with backend running**

Run backend:
```bash
cd backend && uvicorn app.main:app --reload
```

Run frontend (separate terminal):
```bash
cd frontend && npm run dev
```

Open http://localhost:3000 — should see hero, upcoming race cards (scrollable), and a full circuits table. If backend isn't seeded yet, run `cd backend && python -m app.seed.seed_data` first.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/page.tsx
git commit -m "feat: build dashboard page with race calendar and circuits table"
```

---

## Task 12: Frontend — Track Detail Page

**Files:**
- Create: `frontend/src/components/TrackStats.tsx`
- Create: `frontend/src/app/tracks/[id]/page.tsx`

- [ ] **Step 1: Create TrackStats component**

```tsx
// frontend/src/components/TrackStats.tsx
interface TrackStatsProps {
  overtakeDifficulty: number;
  avgOvertakes: number;
  rainProbabilityPct: number;
  trackLengthKm: number;
  numberOfTurns: number;
  drsZonesCount: number;
  atmosphereRating: number | null;
  trackType: string;
}

export default function TrackStats({
  overtakeDifficulty,
  avgOvertakes,
  rainProbabilityPct,
  trackLengthKm,
  numberOfTurns,
  drsZonesCount,
  atmosphereRating,
  trackType,
}: TrackStatsProps) {
  const stats = [
    { label: "Overtaking", value: `${10 - overtakeDifficulty}/10`, color: "text-yellow-400" },
    { label: "Avg Overtakes", value: String(avgOvertakes), color: "text-green-400" },
    { label: "Rain Risk", value: `${rainProbabilityPct}%`, color: rainProbabilityPct >= 40 ? "text-red-400" : "text-blue-400" },
    { label: "Length", value: `${trackLengthKm} km`, color: "text-blue-400" },
    { label: "Turns", value: String(numberOfTurns), color: "text-gray-300" },
    { label: "DRS Zones", value: String(drsZonesCount), color: "text-green-400" },
    { label: "Type", value: trackType === "street" ? "Street" : "Permanent", color: "text-gray-300" },
    ...(atmosphereRating ? [{ label: "Atmosphere", value: `${atmosphereRating}/5`, color: "text-yellow-400" }] : []),
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="bg-gray-800 rounded-lg p-3 text-center">
          <div className={`text-xl font-bold ${stat.color}`}>{stat.value}</div>
          <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Create track detail page**

```tsx
// frontend/src/app/tracks/[id]/page.tsx
import { fetchCircuit, fetchRaceEvents } from "@/lib/api";
import TrackStats from "@/components/TrackStats";
import { notFound } from "next/navigation";

export default async function TrackDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const circuitId = parseInt(id, 10);
  if (isNaN(circuitId)) notFound();

  let circuit;
  try {
    circuit = await fetchCircuit(circuitId);
  } catch {
    notFound();
  }

  let raceEvents;
  try {
    raceEvents = await fetchRaceEvents({ season: 2026 });
    raceEvents = raceEvents.filter((e) => e.circuit_id === circuitId);
  } catch {
    raceEvents = [];
  }

  return (
    <div>
      {/* Header */}
      <div className="px-6 py-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold">{circuit.name}</h1>
        <p className="text-gray-400 text-sm">
          {circuit.city}, {circuit.country} &bull; {circuit.continent}
        </p>
        {circuit.nearest_airport && (
          <p className="text-gray-500 text-xs mt-1">Nearest airport: {circuit.nearest_airport}</p>
        )}
      </div>

      {/* Stats */}
      <div className="px-6 py-6">
        <h2 className="text-lg font-bold mb-4">Track Statistics</h2>
        <TrackStats
          overtakeDifficulty={circuit.overtake_difficulty}
          avgOvertakes={circuit.avg_overtakes_per_race}
          rainProbabilityPct={circuit.rain_probability_pct}
          trackLengthKm={circuit.track_length_km}
          numberOfTurns={circuit.number_of_turns}
          drsZonesCount={circuit.drs_zones_count}
          atmosphereRating={circuit.atmosphere_rating}
          trackType={circuit.track_type}
        />
      </div>

      {/* Upcoming Races */}
      {raceEvents.length > 0 && (
        <div className="px-6 py-6">
          <h2 className="text-lg font-bold mb-4">2026 Race</h2>
          {raceEvents.map((event) => (
            <div key={event.id} className="bg-gray-800 rounded-lg p-4 flex items-center justify-between">
              <div>
                <div className="font-bold">{event.race_name}</div>
                <div className="text-sm text-gray-400">
                  {new Date(event.race_date).toLocaleDateString("en-US", {
                    weekday: "long",
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                  })}
                </div>
              </div>
              <div className="flex gap-2">
                {event.sprint_weekend && (
                  <span className="text-xs bg-purple-500/10 text-purple-400 px-2 py-1 rounded">
                    Sprint Weekend
                  </span>
                )}
                <span className="text-xs bg-blue-500/10 text-blue-400 px-2 py-1 rounded">
                  {event.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Placeholder for future subsystems */}
      <div className="px-6 py-6 text-center text-gray-600 text-sm">
        Seat map, ticket prices, and travel planning coming in future updates.
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Verify track detail page renders**

Navigate to http://localhost:3000/tracks/1 — should show circuit name, stats grid, and upcoming race info.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/TrackStats.tsx frontend/src/app/tracks/
git commit -m "feat: add track detail page with stats display"
```

---

## Task 13: End-to-End Verification

- [ ] **Step 1: Create the database and run migrations**

```bash
createdb f1journey
cd backend && alembic upgrade head
```

- [ ] **Step 2: Seed the database**

```bash
cd backend && python -m app.seed.seed_data
```
Expected: `Seeded 24 circuits and 24 race events.`

- [ ] **Step 3: Start backend and verify API**

```bash
cd backend && uvicorn app.main:app --reload
```

Test endpoints:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/circuits | python -m json.tool | head -20
curl http://localhost:8000/api/circuits?continent=Europe | python -m json.tool | head -5
curl http://localhost:8000/api/race-events?season=2026 | python -m json.tool | head -20
```

- [ ] **Step 4: Start frontend and verify full flow**

```bash
cd frontend && npm run dev
```

Verify:
- http://localhost:3000 — Dashboard shows race cards and circuits table
- Click a circuit name — navigates to track detail with stats
- http://localhost:3000/tracks/1 — Shows track details for first circuit

- [ ] **Step 5: Run all backend tests**

```bash
cd backend && python -m pytest tests/ -v
```
Expected: All tests pass.

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "feat: complete subsystem 1 — core data model, API, and basic frontend"
```
