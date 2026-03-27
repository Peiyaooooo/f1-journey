# Subsystem 2b: Ticket Scraping Engine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a ticket scraping engine that pulls prices from 7 sources, fuzzy-matches them to seat sections, and displays them in the UI.

**Architecture:** TicketListing model stores scraped data. 7 per-source scrapers extend a BaseScraper class. A fuzzy matcher links scraped section names to our seat sections. An orchestrator runs all scrapers on a staggered schedule. Frontend shows prices in the section sidebar and a dedicated comparison page.

**Tech Stack:** Playwright, playwright-stealth, httpx, BeautifulSoup4, rapidfuzz (backend). Next.js client components (frontend).

---

## File Structure

### Backend (new/modified)
```
backend/app/
├── models/
│   ├── __init__.py                # Modify: add TicketListing export
│   └── ticket_listing.py         # Create: TicketListing model
├── schemas/
│   ├── __init__.py                # Modify: add TicketListing schema exports
│   └── ticket_listing.py         # Create: TicketListing Pydantic schemas
├── routers/
│   └── tickets.py                # Create: ticket listing endpoints
├── main.py                       # Modify: register tickets router
├── scrapers/
│   ├── __init__.py
│   ├── base.py                   # Create: BaseScraper + RawTicketListing
│   ├── matcher.py                # Create: fuzzy section name matcher
│   ├── orchestrator.py           # Create: scheduling orchestrator
│   ├── f1_official.py            # Create: F1.com scraper
│   ├── stubhub.py                # Create: StubHub scraper
│   ├── viagogo.py                # Create: Viagogo scraper
│   ├── seatgeek.py               # Create: SeatGeek scraper
│   ├── vivid_seats.py            # Create: Vivid Seats scraper
│   ├── ticketmaster.py           # Create: Ticketmaster scraper
│   └── gp_portal.py              # Create: GP portal scraper
backend/tests/
├── test_ticket_listing_model.py  # Create: model tests
├── test_tickets_api.py           # Create: API tests
├── test_matcher.py               # Create: fuzzy matcher tests
├── test_orchestrator.py          # Create: orchestrator tests
backend/pyproject.toml             # Modify: add scraping dependencies
```

### Frontend (new/modified)
```
frontend/src/
├── lib/
│   └── api.ts                    # Modify: add TicketListing types + fetch
├── components/
│   ├── SectionSidebar.tsx         # Modify: add ticket prices section
│   └── TicketTable.tsx            # Create: ticket comparison table
└── app/tracks/[id]/
    ├── page.tsx                   # Modify: fetch tickets, pass to sidebar
    ├── TrackDetailClient.tsx      # Modify: pass tickets to sidebar
    └── tickets/
        └── page.tsx              # Create: dedicated ticket comparison page
```

---

## Task 1: Add Scraping Dependencies

**Files:**
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: Add scraping dependencies to pyproject.toml**

Add to `dependencies` list:
```toml
    "playwright>=1.40.0",
    "playwright-stealth>=1.0.0",
    "httpx>=0.27.0",
    "beautifulsoup4>=4.12.0",
    "rapidfuzz>=3.0.0",
```

Note: `httpx` is already in dev dependencies — move it to main dependencies since scrapers need it in production.

- [ ] **Step 2: Install dependencies**

```bash
cd backend && .venv/bin/pip install -e ".[dev]"
```

- [ ] **Step 3: Install Playwright browsers**

```bash
cd backend && .venv/bin/playwright install chromium
```

- [ ] **Step 4: Commit**

```bash
git add backend/pyproject.toml
git commit -m "feat: add scraping dependencies (playwright, httpx, bs4, rapidfuzz)"
```

---

## Task 2: TicketListing Model

**Files:**
- Create: `backend/app/models/ticket_listing.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/tests/test_ticket_listing_model.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_ticket_listing_model.py
from datetime import date, datetime

from app.models.circuit import Circuit
from app.models.race_event import RaceEvent
from app.models.seat_section import SeatSection
from app.models.ticket_listing import TicketListing


def test_create_ticket_listing_matched(db):
    circuit = Circuit(
        name="Monza", country="Italy", continent="Europe", city="Monza",
        latitude=45.62, longitude=9.28, track_type="permanent",
        track_length_km=5.793, number_of_turns=11, drs_zones_count=2,
        overtake_difficulty=2, avg_overtakes_per_race=48.0,
        rain_probability_pct=20, nearest_airport="MXP",
    )
    db.add(circuit)
    db.commit()

    event = RaceEvent(
        circuit_id=circuit.id, season_year=2026, race_name="Italian GP",
        race_date=date(2026, 9, 6), sprint_weekend=False, status="upcoming",
    )
    db.add(event)
    db.commit()

    section = SeatSection(
        circuit_id=circuit.id, name="Central Grandstand",
        section_type="grandstand", has_roof=True, has_screen=True,
        pit_view=True, podium_view=True, latitude=45.618, longitude=9.281,
    )
    db.add(section)
    db.commit()

    listing = TicketListing(
        circuit_id=circuit.id,
        race_event_id=event.id,
        seat_section_id=section.id,
        source_site="stubhub",
        source_url="https://stubhub.com/listing/123",
        source_section_name="Central Grandstand",
        ticket_type="weekend",
        price=450.00,
        currency="EUR",
        available_quantity=5,
        last_scraped_at=datetime.utcnow(),
        is_available=True,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)

    assert listing.id is not None
    assert listing.price == 450.00
    assert listing.seat_section_id == section.id
    assert listing.source_site == "stubhub"


def test_create_ticket_listing_unmatched(db):
    circuit = Circuit(
        name="Spa", country="Belgium", continent="Europe", city="Spa",
        latitude=50.44, longitude=5.97, track_type="permanent",
        track_length_km=7.004, number_of_turns=19, drs_zones_count=2,
        overtake_difficulty=2, avg_overtakes_per_race=55.0,
        rain_probability_pct=60, nearest_airport="BRU",
    )
    db.add(circuit)
    db.commit()

    event = RaceEvent(
        circuit_id=circuit.id, season_year=2026, race_name="Belgian GP",
        race_date=date(2026, 7, 19), sprint_weekend=False, status="upcoming",
    )
    db.add(event)
    db.commit()

    listing = TicketListing(
        circuit_id=circuit.id,
        race_event_id=event.id,
        seat_section_id=None,
        source_site="viagogo",
        source_url="https://viagogo.com/listing/456",
        source_section_name="Unknown Zone XYZ",
        ticket_type="sunday",
        price=200.00,
        currency="EUR",
        available_quantity=None,
        last_scraped_at=datetime.utcnow(),
        is_available=True,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)

    assert listing.id is not None
    assert listing.seat_section_id is None
    assert listing.source_section_name == "Unknown Zone XYZ"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && .venv/bin/python -m pytest tests/test_ticket_listing_model.py -v`

- [ ] **Step 3: Implement TicketListing model**

```python
# backend/app/models/ticket_listing.py
from datetime import datetime

from sqlalchemy import String, Float, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TicketListing(Base):
    __tablename__ = "ticket_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"))
    race_event_id: Mapped[int] = mapped_column(ForeignKey("race_events.id"))
    seat_section_id: Mapped[int | None] = mapped_column(ForeignKey("seat_sections.id"), nullable=True)
    source_site: Mapped[str] = mapped_column(String(50))
    source_url: Mapped[str] = mapped_column(String(500))
    source_section_name: Mapped[str] = mapped_column(String(200))
    ticket_type: Mapped[str] = mapped_column(String(30))
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10))
    available_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    includes: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    last_scraped_at: Mapped[datetime] = mapped_column(DateTime)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    circuit: Mapped["Circuit"] = relationship()
    race_event: Mapped["RaceEvent"] = relationship()
    seat_section: Mapped["SeatSection | None"] = relationship()
```

- [ ] **Step 4: Update models __init__.py**

```python
from app.models.ticket_listing import TicketListing
```
Add `"TicketListing"` to `__all__`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && .venv/bin/python -m pytest tests/test_ticket_listing_model.py -v`
Expected: 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/ backend/tests/test_ticket_listing_model.py
git commit -m "feat: add TicketListing model with optional section matching"
```

---

## Task 3: Alembic Migration for TicketListing

**Files:**
- Create: `backend/alembic/versions/xxxx_add_ticket_listings.py`

- [ ] **Step 1: Hand-write the migration**

Look at `backend/alembic/versions/` for the previous revision ID (the seat_sections migration). Create a new migration file:

```python
"""add ticket_listings table"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'ticket_listings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('circuit_id', sa.Integer(), sa.ForeignKey('circuits.id'), nullable=False),
        sa.Column('race_event_id', sa.Integer(), sa.ForeignKey('race_events.id'), nullable=False),
        sa.Column('seat_section_id', sa.Integer(), sa.ForeignKey('seat_sections.id'), nullable=True),
        sa.Column('source_site', sa.String(50), nullable=False),
        sa.Column('source_url', sa.String(500), nullable=False),
        sa.Column('source_section_name', sa.String(200), nullable=False),
        sa.Column('ticket_type', sa.String(30), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('available_quantity', sa.Integer(), nullable=True),
        sa.Column('includes', sa.Text(), nullable=True),
        sa.Column('last_scraped_at', sa.DateTime(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default=sa.true()),
    )

def downgrade():
    op.drop_table('ticket_listings')
```

- [ ] **Step 2: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat: add Alembic migration for ticket_listings table"
```

---

## Task 4: Pydantic Schemas + API Endpoints for Tickets

**Files:**
- Create: `backend/app/schemas/ticket_listing.py`
- Modify: `backend/app/schemas/__init__.py`
- Create: `backend/app/routers/tickets.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_tickets_api.py`

- [ ] **Step 1: Create Pydantic schemas**

```python
# backend/app/schemas/ticket_listing.py
import json
from datetime import datetime
from pydantic import BaseModel, field_validator


class TicketListingRead(BaseModel):
    id: int
    circuit_id: int
    race_event_id: int
    seat_section_id: int | None = None
    source_site: str
    source_url: str
    source_section_name: str
    ticket_type: str
    price: float
    currency: str
    available_quantity: int | None = None
    includes: list[str] | None = None
    last_scraped_at: datetime
    is_available: bool

    model_config = {"from_attributes": True}

    @field_validator("includes", mode="before")
    @classmethod
    def parse_includes(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
```

Update `backend/app/schemas/__init__.py` to export `TicketListingRead`.

- [ ] **Step 2: Write API tests**

```python
# backend/tests/test_tickets_api.py
import json
from datetime import date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Circuit, RaceEvent, SeatSection
from app.models.ticket_listing import TicketListing

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
        rain_probability_pct=20, nearest_airport="MXP",
    )
    db.add(circuit)
    db.commit()

    event = RaceEvent(
        circuit_id=circuit.id, season_year=2026, race_name="Italian GP",
        race_date=date(2026, 9, 6), sprint_weekend=False, status="upcoming",
    )
    db.add(event)
    db.commit()

    section = SeatSection(
        circuit_id=circuit.id, name="Central Grandstand",
        section_type="grandstand", has_roof=True, has_screen=True,
        pit_view=True, podium_view=True, latitude=45.618, longitude=9.281,
    )
    db.add(section)
    db.commit()

    listings = [
        TicketListing(
            circuit_id=circuit.id, race_event_id=event.id,
            seat_section_id=section.id, source_site="stubhub",
            source_url="https://stubhub.com/1", source_section_name="Central Grandstand",
            ticket_type="weekend", price=450.0, currency="EUR",
            available_quantity=5, last_scraped_at=datetime.utcnow(), is_available=True,
        ),
        TicketListing(
            circuit_id=circuit.id, race_event_id=event.id,
            seat_section_id=section.id, source_site="seatgeek",
            source_url="https://seatgeek.com/1", source_section_name="Central Grandstand",
            ticket_type="weekend", price=420.0, currency="EUR",
            available_quantity=3, last_scraped_at=datetime.utcnow(), is_available=True,
        ),
        TicketListing(
            circuit_id=circuit.id, race_event_id=event.id,
            seat_section_id=None, source_site="viagogo",
            source_url="https://viagogo.com/1", source_section_name="Mystery Zone",
            ticket_type="sunday", price=200.0, currency="EUR",
            available_quantity=None, last_scraped_at=datetime.utcnow(), is_available=True,
        ),
    ]
    db.add_all(listings)
    db.commit()
    db.close()


def teardown_function():
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(engine)


def test_list_tickets_for_circuit():
    resp = client.get("/api/circuits/1/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3


def test_list_tickets_filter_by_source():
    resp = client.get("/api/circuits/1/tickets?source_site=stubhub")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["source_site"] == "stubhub"


def test_list_tickets_sort_by_price():
    resp = client.get("/api/circuits/1/tickets?sort=price_asc")
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["price"] <= data[1]["price"]


def test_list_tickets_for_section():
    resp = client.get("/api/sections/1/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(t["seat_section_id"] == 1 for t in data)


def test_list_unmatched_tickets():
    resp = client.get("/api/circuits/1/tickets/unmatched")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["seat_section_id"] is None
    assert data[0]["source_section_name"] == "Mystery Zone"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd backend && .venv/bin/python -m pytest tests/test_tickets_api.py -v`

- [ ] **Step 4: Implement tickets router**

```python
# backend/app/routers/tickets.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ticket_listing import TicketListing
from app.schemas.ticket_listing import TicketListingRead

router = APIRouter(tags=["tickets"])


@router.get("/api/circuits/{circuit_id}/tickets", response_model=list[TicketListingRead])
def list_circuit_tickets(
    circuit_id: int,
    source_site: str | None = None,
    ticket_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = "price_asc",
    db: Session = Depends(get_db),
):
    query = db.query(TicketListing).filter(
        TicketListing.circuit_id == circuit_id,
        TicketListing.is_available == True,
    )
    if source_site:
        query = query.filter(TicketListing.source_site == source_site)
    if ticket_type:
        query = query.filter(TicketListing.ticket_type == ticket_type)
    if min_price is not None:
        query = query.filter(TicketListing.price >= min_price)
    if max_price is not None:
        query = query.filter(TicketListing.price <= max_price)

    if sort == "price_desc":
        query = query.order_by(TicketListing.price.desc())
    else:
        query = query.order_by(TicketListing.price.asc())

    return query.all()


@router.get("/api/sections/{section_id}/tickets", response_model=list[TicketListingRead])
def list_section_tickets(
    section_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(TicketListing)
        .filter(TicketListing.seat_section_id == section_id, TicketListing.is_available == True)
        .order_by(TicketListing.price.asc())
        .all()
    )


@router.get("/api/circuits/{circuit_id}/tickets/unmatched", response_model=list[TicketListingRead])
def list_unmatched_tickets(
    circuit_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(TicketListing)
        .filter(
            TicketListing.circuit_id == circuit_id,
            TicketListing.seat_section_id == None,
            TicketListing.is_available == True,
        )
        .order_by(TicketListing.price.asc())
        .all()
    )
```

- [ ] **Step 5: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.routers.tickets import router as tickets_router
app.include_router(tickets_router)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && .venv/bin/python -m pytest tests/test_tickets_api.py -v`
Expected: 5 tests PASS.

- [ ] **Step 7: Run all tests**

Run: `cd backend && .venv/bin/python -m pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 8: Commit**

```bash
git add backend/app/schemas/ticket_listing.py backend/app/schemas/__init__.py backend/app/routers/tickets.py backend/app/main.py backend/tests/test_tickets_api.py
git commit -m "feat: add ticket listing schemas, API endpoints with filtering and sorting"
```

---

## Task 5: BaseScraper + RawTicketListing

**Files:**
- Create: `backend/app/scrapers/__init__.py`
- Create: `backend/app/scrapers/base.py`

- [ ] **Step 1: Create base scraper module**

```python
# backend/app/scrapers/__init__.py
```

```python
# backend/app/scrapers/base.py
"""Base scraper class and data structures for ticket scraping."""

import asyncio
import random
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RawTicketListing:
    """A single ticket listing scraped from a source site."""
    source_site: str
    source_url: str
    source_section_name: str
    ticket_type: str  # friday, saturday, sunday, weekend, 3_day
    price: float
    currency: str
    available_quantity: int | None = None
    includes: list[str] | None = None


class BaseScraper(ABC):
    """Abstract base class for all ticket scrapers."""

    source_site: str = ""

    @abstractmethod
    async def scrape_circuit(
        self, circuit_name: str, race_name: str, circuit_country: str
    ) -> list[RawTicketListing]:
        """Scrape all available tickets for a given circuit/race.

        Args:
            circuit_name: e.g. "Silverstone Circuit"
            race_name: e.g. "British Grand Prix"
            circuit_country: e.g. "Great Britain"

        Returns:
            List of raw ticket listings found.
        """

    async def random_delay(self, min_s: float = 30, max_s: float = 120) -> None:
        """Sleep for a random duration to avoid rate limiting."""
        delay = random.uniform(min_s, max_s)
        logger.debug(f"[{self.source_site}] Sleeping {delay:.1f}s")
        await asyncio.sleep(delay)

    def get_user_agent(self) -> str:
        """Return a random user agent string."""
        agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        return random.choice(agents)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/scrapers/
git commit -m "feat: add BaseScraper class and RawTicketListing dataclass"
```

---

## Task 6: Fuzzy Section Matcher

**Files:**
- Create: `backend/app/scrapers/matcher.py`
- Create: `backend/tests/test_matcher.py`

- [ ] **Step 1: Write matcher tests**

```python
# backend/tests/test_matcher.py
from app.scrapers.matcher import match_section_name


def test_exact_match():
    sections = {"Central Grandstand": 1, "GA Zone A": 2}
    result = match_section_name("Central Grandstand", sections)
    assert result == 1


def test_fuzzy_match():
    sections = {"Wellington Straight": 1, "Copse Grandstand": 2}
    result = match_section_name("Wellington Straight Grandstand", sections)
    assert result == 1


def test_case_insensitive():
    sections = {"Abbey Grandstand": 1}
    result = match_section_name("abbey grandstand", sections)
    assert result == 1


def test_no_match():
    sections = {"Wellington Straight": 1, "Copse Grandstand": 2}
    result = match_section_name("Completely Unknown Section XYZ", sections)
    assert result is None


def test_partial_match():
    sections = {"Copse A": 1, "Copse B": 2, "Copse C": 3}
    result = match_section_name("Copse A Grandstand", sections)
    assert result == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && .venv/bin/python -m pytest tests/test_matcher.py -v`

- [ ] **Step 3: Implement matcher**

```python
# backend/app/scrapers/matcher.py
"""Fuzzy matching engine for mapping scraped section names to seat_section IDs."""

import logging
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

MATCH_THRESHOLD = 70  # minimum similarity score (0-100)


def match_section_name(
    source_name: str,
    section_map: dict[str, int],  # {section_name: section_id}
) -> int | None:
    """Match a scraped section name to a known seat section.

    Args:
        source_name: The section name from the ticket source site.
        section_map: Dict mapping known section names to their IDs.

    Returns:
        The seat_section_id if a match is found, None otherwise.
    """
    if not section_map:
        return None

    # Try exact match first (case-insensitive)
    source_lower = source_name.lower().strip()
    for name, sid in section_map.items():
        if name.lower().strip() == source_lower:
            return sid

    # Fuzzy match
    result = process.extractOne(
        source_name,
        section_map.keys(),
        scorer=fuzz.token_sort_ratio,
        score_cutoff=MATCH_THRESHOLD,
    )

    if result is None:
        logger.debug(f"No match for '{source_name}' (threshold={MATCH_THRESHOLD})")
        return None

    matched_name, score, _ = result
    logger.debug(f"Matched '{source_name}' -> '{matched_name}' (score={score})")
    return section_map[matched_name]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && .venv/bin/python -m pytest tests/test_matcher.py -v`
Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/scrapers/matcher.py backend/tests/test_matcher.py
git commit -m "feat: add fuzzy section name matcher using rapidfuzz"
```

---

## Task 7: Individual Scrapers (7 files)

**Files:**
- Create: `backend/app/scrapers/f1_official.py`
- Create: `backend/app/scrapers/stubhub.py`
- Create: `backend/app/scrapers/viagogo.py`
- Create: `backend/app/scrapers/seatgeek.py`
- Create: `backend/app/scrapers/vivid_seats.py`
- Create: `backend/app/scrapers/ticketmaster.py`
- Create: `backend/app/scrapers/gp_portal.py`

Each scraper extends `BaseScraper` and implements `scrape_circuit()`. The implementation should:

1. Build a search URL for the circuit's race using the circuit name/race name
2. Fetch the page (Playwright for JS-heavy sites, httpx for API-based)
3. Parse ticket listings from the response
4. Return a list of `RawTicketListing` objects

Key implementation notes per scraper:

**SeatGeek** (`seatgeek.py`) — Uses their public API:
- Search endpoint: `https://api.seatgeek.com/2/events?q={race_name}&type=auto_racing`
- Parse event ID from results, then fetch listings
- No API key needed for basic search (rate-limited)

**StubHub** (`stubhub.py`) — Uses Playwright:
- Navigate to search page with race name
- Parse listing cards from DOM
- Extract price, section name, ticket type

**Viagogo** (`viagogo.py`) — Uses Playwright with stealth:
- Heavy anti-bot — use playwright-stealth
- Navigate to event page, parse listings
- May need to handle Cloudflare challenges

**F1 Official** (`f1_official.py`) — Uses Playwright:
- tickets.formula1.com has a queue system
- Navigate to circuit ticket page
- Parse available grandstand options and prices

**Ticketmaster** (`ticketmaster.py`) — Uses Playwright:
- Search for the F1 event
- Parse ticket listings from search results
- Handle potential CAPTCHA by returning empty list

**Vivid Seats** (`vivid_seats.py`) — Uses Playwright:
- Search for the F1 event
- Parse listing cards

**GP Portal** (`gp_portal.py`) — Uses httpx/Playwright:
- Uses the gpticketstore domains (same CDN as our map images)
- Per-circuit logic since each portal has different structure

Each scraper should:
- Use `try/except` around the main scraping logic
- Log errors but never crash — return empty list on failure
- Call `self.random_delay()` before making requests
- Use `self.get_user_agent()` for request headers

- [ ] **Step 1: Create all 7 scraper files**

Implement each scraper following the patterns above. Each file should be 50-100 lines. The scraper should make a real attempt to fetch data from the source site.

- [ ] **Step 2: Verify imports work**

```bash
cd backend && .venv/bin/python -c "
from app.scrapers.f1_official import F1OfficialScraper
from app.scrapers.stubhub import StubHubScraper
from app.scrapers.viagogo import ViagogoScraper
from app.scrapers.seatgeek import SeatGeekScraper
from app.scrapers.vivid_seats import VividSeatsScraper
from app.scrapers.ticketmaster import TicketmasterScraper
from app.scrapers.gp_portal import GPPortalScraper
print('All 7 scrapers imported successfully')
"
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/scrapers/
git commit -m "feat: add 7 ticket source scrapers (F1, StubHub, Viagogo, SeatGeek, Vivid Seats, Ticketmaster, GP Portal)"
```

---

## Task 8: Orchestrator

**Files:**
- Create: `backend/app/scrapers/orchestrator.py`
- Create: `backend/tests/test_orchestrator.py`

- [ ] **Step 1: Write orchestrator tests**

```python
# backend/tests/test_orchestrator.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.scrapers.orchestrator import ScrapingOrchestrator
from app.scrapers.base import RawTicketListing


@pytest.mark.asyncio
async def test_orchestrator_runs_all_scrapers():
    """Test that orchestrator calls each scraper for each circuit."""
    mock_listing = RawTicketListing(
        source_site="test",
        source_url="https://test.com/1",
        source_section_name="Test Stand",
        ticket_type="weekend",
        price=100.0,
        currency="EUR",
    )

    mock_scraper = AsyncMock()
    mock_scraper.scrape_circuit = AsyncMock(return_value=[mock_listing])
    mock_scraper.source_site = "test"

    orchestrator = ScrapingOrchestrator(scrapers=[mock_scraper])

    # Mock the DB session and circuit/event data
    with patch.object(orchestrator, '_get_circuits_and_events') as mock_get:
        mock_get.return_value = [
            {"circuit_id": 1, "circuit_name": "Test Circuit", "race_name": "Test GP", "country": "Test", "event_id": 1}
        ]
        with patch.object(orchestrator, '_save_listings') as mock_save:
            with patch.object(orchestrator, '_build_section_map', return_value={}):
                results = await orchestrator.run()

    assert mock_scraper.scrape_circuit.call_count == 1
    assert mock_save.call_count == 1


@pytest.mark.asyncio
async def test_orchestrator_handles_scraper_failure():
    """Test that orchestrator continues when a scraper fails."""
    mock_scraper = AsyncMock()
    mock_scraper.scrape_circuit = AsyncMock(side_effect=Exception("Connection failed"))
    mock_scraper.source_site = "failing_source"

    orchestrator = ScrapingOrchestrator(scrapers=[mock_scraper])

    with patch.object(orchestrator, '_get_circuits_and_events') as mock_get:
        mock_get.return_value = [
            {"circuit_id": 1, "circuit_name": "Test", "race_name": "Test GP", "country": "Test", "event_id": 1}
        ]
        with patch.object(orchestrator, '_save_listings'):
            with patch.object(orchestrator, '_build_section_map', return_value={}):
                results = await orchestrator.run()

    # Should not raise — failures are logged and skipped
    assert results is not None
```

- [ ] **Step 2: Implement orchestrator**

```python
# backend/app/scrapers/orchestrator.py
"""Scraping orchestrator — runs all scrapers across all circuits."""

import asyncio
import json
import logging
from datetime import datetime

from app.database import SessionLocal
from app.models.circuit import Circuit
from app.models.race_event import RaceEvent
from app.models.seat_section import SeatSection
from app.models.ticket_listing import TicketListing
from app.scrapers.base import BaseScraper, RawTicketListing
from app.scrapers.matcher import match_section_name

logger = logging.getLogger(__name__)


class ScrapingOrchestrator:
    """Runs all scrapers for all circuits with staggered delays."""

    def __init__(self, scrapers: list[BaseScraper] | None = None):
        if scrapers is None:
            from app.scrapers.seatgeek import SeatGeekScraper
            from app.scrapers.stubhub import StubHubScraper
            from app.scrapers.viagogo import ViagogoScraper
            from app.scrapers.f1_official import F1OfficialScraper
            from app.scrapers.vivid_seats import VividSeatsScraper
            from app.scrapers.ticketmaster import TicketmasterScraper
            from app.scrapers.gp_portal import GPPortalScraper

            scrapers = [
                SeatGeekScraper(),
                StubHubScraper(),
                ViagogoScraper(),
                F1OfficialScraper(),
                VividSeatsScraper(),
                TicketmasterScraper(),
                GPPortalScraper(),
            ]
        self.scrapers = scrapers
        self.failure_counts: dict[str, int] = {}  # source_site -> consecutive failures
        self.max_failures = 3  # circuit breaker threshold

    def _get_circuits_and_events(self) -> list[dict]:
        """Fetch all circuits with their upcoming race events."""
        db = SessionLocal()
        try:
            circuits = db.query(Circuit).all()
            result = []
            for c in circuits:
                event = (
                    db.query(RaceEvent)
                    .filter(RaceEvent.circuit_id == c.id, RaceEvent.status == "upcoming")
                    .first()
                )
                if event:
                    result.append({
                        "circuit_id": c.id,
                        "circuit_name": c.name,
                        "race_name": event.race_name,
                        "country": c.country,
                        "event_id": event.id,
                    })
            return result
        finally:
            db.close()

    def _build_section_map(self, circuit_id: int) -> dict[str, int]:
        """Build {section_name: section_id} map for fuzzy matching."""
        db = SessionLocal()
        try:
            sections = db.query(SeatSection).filter(SeatSection.circuit_id == circuit_id).all()
            return {s.name: s.id for s in sections}
        finally:
            db.close()

    def _save_listings(
        self,
        raw_listings: list[RawTicketListing],
        circuit_id: int,
        event_id: int,
        section_map: dict[str, int],
    ) -> tuple[int, int]:
        """Save raw listings to DB, matching to sections. Returns (matched, unmatched) counts."""
        db = SessionLocal()
        matched = 0
        unmatched = 0
        try:
            # Mark previous listings from this source for this circuit as unavailable
            source_site = raw_listings[0].source_site if raw_listings else None
            if source_site:
                db.query(TicketListing).filter(
                    TicketListing.circuit_id == circuit_id,
                    TicketListing.source_site == source_site,
                ).update({"is_available": False})

            for raw in raw_listings:
                section_id = match_section_name(raw.source_section_name, section_map)
                listing = TicketListing(
                    circuit_id=circuit_id,
                    race_event_id=event_id,
                    seat_section_id=section_id,
                    source_site=raw.source_site,
                    source_url=raw.source_url,
                    source_section_name=raw.source_section_name,
                    ticket_type=raw.ticket_type,
                    price=raw.price,
                    currency=raw.currency,
                    available_quantity=raw.available_quantity,
                    includes=json.dumps(raw.includes) if raw.includes else None,
                    last_scraped_at=datetime.utcnow(),
                    is_available=True,
                )
                db.add(listing)
                if section_id:
                    matched += 1
                else:
                    unmatched += 1
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        return matched, unmatched

    def _is_circuit_breaker_open(self, source_site: str) -> bool:
        return self.failure_counts.get(source_site, 0) >= self.max_failures

    async def run(self) -> dict:
        """Run all scrapers for all circuits. Returns summary stats."""
        circuits = self._get_circuits_and_events()
        stats = {"total_listings": 0, "matched": 0, "unmatched": 0, "errors": 0}

        for scraper in self.scrapers:
            if self._is_circuit_breaker_open(scraper.source_site):
                logger.warning(f"[{scraper.source_site}] Circuit breaker OPEN — skipping")
                continue

            for circuit_info in circuits:
                try:
                    logger.info(
                        f"[{scraper.source_site}] Scraping {circuit_info['circuit_name']}"
                    )
                    raw_listings = await scraper.scrape_circuit(
                        circuit_info["circuit_name"],
                        circuit_info["race_name"],
                        circuit_info["country"],
                    )

                    if raw_listings:
                        section_map = self._build_section_map(circuit_info["circuit_id"])
                        m, u = self._save_listings(
                            raw_listings,
                            circuit_info["circuit_id"],
                            circuit_info["event_id"],
                            section_map,
                        )
                        stats["total_listings"] += len(raw_listings)
                        stats["matched"] += m
                        stats["unmatched"] += u

                    # Reset failure count on success
                    self.failure_counts[scraper.source_site] = 0

                except Exception as e:
                    logger.error(
                        f"[{scraper.source_site}] Failed for {circuit_info['circuit_name']}: {e}"
                    )
                    stats["errors"] += 1
                    self.failure_counts[scraper.source_site] = (
                        self.failure_counts.get(scraper.source_site, 0) + 1
                    )
                    if self._is_circuit_breaker_open(scraper.source_site):
                        logger.warning(
                            f"[{scraper.source_site}] Circuit breaker TRIPPED after {self.max_failures} failures"
                        )
                        break

                # Stagger requests
                await scraper.random_delay(min_s=5, max_s=15)

        logger.info(f"Scraping complete: {stats}")
        return stats


async def main():
    """Entry point for running the orchestrator manually."""
    logging.basicConfig(level=logging.INFO)
    orchestrator = ScrapingOrchestrator()
    stats = await orchestrator.run()
    print(f"Scraping complete: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 3: Run tests**

Run: `cd backend && .venv/bin/python -m pytest tests/test_orchestrator.py -v`
Expected: 2 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/scrapers/orchestrator.py backend/tests/test_orchestrator.py
git commit -m "feat: add scraping orchestrator with circuit breaker and staggered delays"
```

---

## Task 9: Frontend — Ticket Types and Fetch Functions

**Files:**
- Modify: `frontend/src/lib/api.ts`

- [ ] **Step 1: Add TicketListing type and fetch functions**

Append to `frontend/src/lib/api.ts`:

```typescript
export interface TicketListing {
  id: number;
  circuit_id: number;
  race_event_id: number;
  seat_section_id: number | null;
  source_site: string;
  source_url: string;
  source_section_name: string;
  ticket_type: string;
  price: number;
  currency: string;
  available_quantity: number | null;
  includes: string[] | null;
  last_scraped_at: string;
  is_available: boolean;
}

export async function fetchCircuitTickets(
  circuitId: number,
  params?: { source_site?: string; ticket_type?: string; min_price?: number; max_price?: number; sort?: string }
): Promise<TicketListing[]> {
  const url = new URL(`${API_URL}/api/circuits/${circuitId}/tickets`);
  if (params?.source_site) url.searchParams.set("source_site", params.source_site);
  if (params?.ticket_type) url.searchParams.set("ticket_type", params.ticket_type);
  if (params?.min_price !== undefined) url.searchParams.set("min_price", String(params.min_price));
  if (params?.max_price !== undefined) url.searchParams.set("max_price", String(params.max_price));
  if (params?.sort) url.searchParams.set("sort", params.sort);
  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("Failed to fetch tickets");
  return res.json();
}

export async function fetchSectionTickets(sectionId: number): Promise<TicketListing[]> {
  const res = await fetch(`${API_URL}/api/sections/${sectionId}/tickets`, { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("Failed to fetch section tickets");
  return res.json();
}

export async function fetchUnmatchedTickets(circuitId: number): Promise<TicketListing[]> {
  const res = await fetch(`${API_URL}/api/circuits/${circuitId}/tickets/unmatched`, { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("Failed to fetch unmatched tickets");
  return res.json();
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: add TicketListing types and fetch functions"
```

---

## Task 10: Frontend — Ticket Prices in Section Sidebar

**Files:**
- Modify: `frontend/src/components/SectionSidebar.tsx`
- Modify: `frontend/src/app/tracks/[id]/TrackDetailClient.tsx`
- Modify: `frontend/src/app/tracks/[id]/page.tsx`

- [ ] **Step 1: Update SectionSidebar to accept and display tickets**

Add a `tickets` prop to `SectionSidebar`. After the existing content (before the "Ticket prices coming soon" placeholder), render ticket listings:

```tsx
// Add to SectionSidebarProps:
tickets: TicketListing[];

// Replace the "Ticket prices coming soon" placeholder with:
{tickets.length > 0 ? (
  <div>
    <div className="text-xs text-gray-500 mb-2 uppercase">Tickets Available</div>
    <div className="flex flex-col gap-2">
      {tickets.map((t) => (
        <a
          key={t.id}
          href={t.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="bg-gray-800 rounded-lg p-3 flex justify-between items-center hover:bg-gray-700 transition-colors"
        >
          <div>
            <div className="font-medium text-sm">{t.source_site.replace("_", " ")}</div>
            <div className="text-xs text-gray-400">{t.ticket_type.replace("_", " ")}</div>
          </div>
          <div className="text-right">
            <div className="font-bold text-green-400">{t.currency} {t.price.toFixed(0)}</div>
            {t.available_quantity && (
              <div className="text-xs text-gray-500">{t.available_quantity} left</div>
            )}
          </div>
        </a>
      ))}
    </div>
  </div>
) : (
  <div className="text-center text-gray-600 text-xs mt-4">
    No tickets found for this section
  </div>
)}
```

- [ ] **Step 2: Update TrackDetailClient to pass tickets to sidebar**

- Add `tickets` to `TrackDetailClientProps`
- Filter tickets by `selectedSection.id` when passing to `SectionSidebar`:

```tsx
const sectionTickets = selectedSection
  ? tickets.filter((t) => t.seat_section_id === selectedSection.id)
  : [];

// Pass to SectionSidebar:
<SectionSidebar
  section={selectedSection}
  tickets={sectionTickets}
  onClose={() => setSelectedSection(null)}
/>
```

- [ ] **Step 3: Update page.tsx to fetch tickets and pass down**

After fetching sections, fetch tickets:
```typescript
let tickets: TicketListing[] = [];
try {
  tickets = await fetchCircuitTickets(circuitId);
} catch {
  tickets = [];
}
```

Pass to `TrackDetailClient`:
```tsx
<TrackDetailClient
  circuitName={circuit.name}
  centerLat={circuit.latitude}
  centerLng={circuit.longitude}
  sections={sections}
  tickets={tickets}
/>
```

- [ ] **Step 4: Verify build**

```bash
cd frontend && npx next build
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/SectionSidebar.tsx frontend/src/app/tracks/[id]/
git commit -m "feat: show ticket prices in section sidebar from all sources"
```

---

## Task 11: Frontend — Ticket Comparison Page

**Files:**
- Create: `frontend/src/components/TicketTable.tsx`
- Create: `frontend/src/app/tracks/[id]/tickets/page.tsx`

- [ ] **Step 1: Create TicketTable component**

```tsx
// frontend/src/components/TicketTable.tsx
"use client";

import { useState } from "react";
import type { TicketListing } from "@/lib/api";

interface TicketTableProps {
  tickets: TicketListing[];
}

const SOURCE_LABELS: Record<string, string> = {
  f1_official: "F1.com",
  stubhub: "StubHub",
  viagogo: "Viagogo",
  seatgeek: "SeatGeek",
  vivid_seats: "Vivid Seats",
  ticketmaster: "Ticketmaster",
  gp_portal: "GP Portal",
};

export default function TicketTable({ tickets }: TicketTableProps) {
  const [sourceFilter, setSourceFilter] = useState<string>("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [sortBy, setSortBy] = useState<"price_asc" | "price_desc">("price_asc");

  const sources = [...new Set(tickets.map((t) => t.source_site))];
  const types = [...new Set(tickets.map((t) => t.ticket_type))];

  let filtered = tickets;
  if (sourceFilter) filtered = filtered.filter((t) => t.source_site === sourceFilter);
  if (typeFilter) filtered = filtered.filter((t) => t.ticket_type === typeFilter);
  filtered = [...filtered].sort((a, b) =>
    sortBy === "price_asc" ? a.price - b.price : b.price - a.price
  );

  return (
    <div>
      {/* Filters */}
      <div className="flex gap-3 mb-4 flex-wrap">
        <select
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value)}
          className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-1.5"
        >
          <option value="">All Sources</option>
          {sources.map((s) => (
            <option key={s} value={s}>{SOURCE_LABELS[s] || s}</option>
          ))}
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-1.5"
        >
          <option value="">All Types</option>
          {types.map((t) => (
            <option key={t} value={t}>{t.replace("_", " ")}</option>
          ))}
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as "price_asc" | "price_desc")}
          className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-1.5"
        >
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
        </select>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-gray-400 text-left">
              <th className="pb-2 pr-4">Source</th>
              <th className="pb-2 pr-4">Section</th>
              <th className="pb-2 pr-4">Type</th>
              <th className="pb-2 pr-4">Price</th>
              <th className="pb-2 pr-4">Available</th>
              <th className="pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((t) => (
              <tr key={t.id} className="border-b border-gray-800/50 hover:bg-gray-900">
                <td className="py-2 pr-4">{SOURCE_LABELS[t.source_site] || t.source_site}</td>
                <td className="py-2 pr-4 text-gray-400">{t.source_section_name}</td>
                <td className="py-2 pr-4 text-gray-400 capitalize">{t.ticket_type.replace("_", " ")}</td>
                <td className="py-2 pr-4 font-bold text-green-400">{t.currency} {t.price.toFixed(0)}</td>
                <td className="py-2 pr-4 text-gray-400">{t.available_quantity ?? "—"}</td>
                <td className="py-2">
                  <a
                    href={t.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
                  >
                    Buy
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center text-gray-500 py-8">No tickets found</div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create ticket comparison page**

```tsx
// frontend/src/app/tracks/[id]/tickets/page.tsx
import { fetchCircuit, fetchCircuitTickets, fetchUnmatchedTickets } from "@/lib/api";
import TicketTable from "@/components/TicketTable";
import Link from "next/link";
import { notFound } from "next/navigation";

export default async function TicketComparisonPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const circuitId = parseInt(id, 10);
  if (isNaN(circuitId)) notFound();

  let circuit;
  try {
    circuit = await fetchCircuit(circuitId);
  } catch {
    notFound();
  }

  const [tickets, unmatchedTickets] = await Promise.all([
    fetchCircuitTickets(circuitId).catch(() => []),
    fetchUnmatchedTickets(circuitId).catch(() => []),
  ]);

  return (
    <div>
      <div className="px-6 py-6 border-b border-gray-800">
        <Link href={`/tracks/${circuitId}`} className="text-sm text-gray-400 hover:text-white">
          &larr; Back to {circuit.name}
        </Link>
        <h1 className="text-2xl font-bold mt-2">Ticket Comparison — {circuit.name}</h1>
        <p className="text-gray-400 text-sm">
          Compare ticket prices across all sources
        </p>
      </div>

      <div className="px-6 py-6">
        <h2 className="text-lg font-bold mb-4">All Tickets ({tickets.length})</h2>
        <TicketTable tickets={tickets} />
      </div>

      {unmatchedTickets.length > 0 && (
        <div className="px-6 py-6 border-t border-gray-800">
          <h2 className="text-lg font-bold mb-4">Other Tickets ({unmatchedTickets.length})</h2>
          <p className="text-sm text-gray-400 mb-4">
            These tickets could not be matched to a specific seat section
          </p>
          <TicketTable tickets={unmatchedTickets} />
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Add link to ticket comparison page from track detail**

In `frontend/src/app/tracks/[id]/page.tsx`, add a link after the TrackDetailClient component:

```tsx
<div className="px-6 py-4">
  <Link
    href={`/tracks/${circuitId}/tickets`}
    className="text-sm text-blue-400 hover:underline"
  >
    View all ticket prices &rarr;
  </Link>
</div>
```

- [ ] **Step 4: Verify build**

```bash
cd frontend && npx next build
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/TicketTable.tsx frontend/src/app/tracks/
git commit -m "feat: add ticket comparison page and table with filters"
```

---

## Task 12: End-to-End Verification

- [ ] **Step 1: Re-seed database and create tables**

```bash
cd backend && rm -f f1journey.db && .venv/bin/python -m app.seed.seed_data
```

- [ ] **Step 2: Run all backend tests**

```bash
cd backend && .venv/bin/python -m pytest tests/ -v
```
Expected: All tests pass.

- [ ] **Step 3: Test a single scraper manually (SeatGeek — easiest)**

```bash
cd backend && .venv/bin/python -c "
import asyncio
from app.scrapers.seatgeek import SeatGeekScraper
scraper = SeatGeekScraper()
results = asyncio.run(scraper.scrape_circuit('Silverstone Circuit', 'British Grand Prix', 'Great Britain'))
print(f'Found {len(results)} listings')
for r in results[:3]:
    print(f'  {r.source_section_name}: {r.currency} {r.price} ({r.ticket_type})')
"
```

- [ ] **Step 4: Run the orchestrator for a quick test**

```bash
cd backend && .venv/bin/python -m app.scrapers.orchestrator
```

- [ ] **Step 5: Verify API returns scraped data**

```bash
curl -s http://localhost:8000/api/circuits/1/tickets | python3 -m json.tool | head -30
```

- [ ] **Step 6: Build and verify frontend**

```bash
cd frontend && npx next build
```

Start both servers and verify:
- Track detail page sidebar shows ticket prices when a section is selected
- `/tracks/{id}/tickets` page shows full ticket comparison table with filters
- "Buy" links open source site in new tab

- [ ] **Step 7: Final commit**

```bash
git add -A
git commit -m "feat: complete subsystem 2b — ticket scraping engine with 7 sources"
```
