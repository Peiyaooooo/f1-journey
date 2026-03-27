# Subsystem 2a: Seat Sections + Interactive Track Map — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add seat section data for all 22 circuits with an interactive Leaflet map and sidebar detail panel on the track detail page.

**Architecture:** New SeatSection model with API endpoints, seat data scraped/seeded for all circuits, Leaflet map with clickable markers, sidebar showing section details. Follows existing FastAPI + Next.js patterns.

**Tech Stack:** SQLAlchemy, FastAPI, Pydantic (backend). Leaflet, react-leaflet, Next.js client components (frontend).

---

## File Structure

### Backend (new/modified)
```
backend/app/
├── models/
│   ├── __init__.py              # Modify: add SeatSection export
│   └── seat_section.py          # Create: SeatSection model
├── schemas/
│   ├── __init__.py              # Modify: add SeatSection schema exports
│   └── seat_section.py          # Create: SeatSection Pydantic schemas
├── routers/
│   └── sections.py              # Create: seat section endpoints
├── main.py                      # Modify: register sections router
└── seed/
    ├── seat_sections_data.py    # Create: seed data for all 22 circuits
    └── seed_data.py             # Modify: call seat section seeder
backend/tests/
├── test_models.py               # Modify: add SeatSection model tests
├── test_sections_api.py         # Create: seat section API tests
backend/alembic/versions/
└── xxxx_add_seat_sections.py    # Create: migration (auto-generated)
```

### Frontend (new/modified)
```
frontend/src/
├── lib/
│   └── api.ts                   # Modify: add SeatSection types + fetch functions
├── components/
│   ├── TrackMap.tsx              # Create: Leaflet map with section markers (client component)
│   ├── SectionSidebar.tsx        # Create: section detail sidebar panel
│   └── SectionTable.tsx          # Create: sortable table of all sections
└── app/tracks/[id]/
    └── page.tsx                  # Modify: add tabbed view with map/table
```

---

## Task 1: SeatSection Model

**Files:**
- Create: `backend/app/models/seat_section.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/tests/test_models.py`

- [ ] **Step 1: Write failing tests**

Add to `backend/tests/test_models.py`:

```python
from app.models.seat_section import SeatSection
import json


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && .venv/bin/python -m pytest tests/test_models.py -v`
Expected: FAIL — `seat_section` module doesn't exist.

- [ ] **Step 3: Implement SeatSection model**

```python
# backend/app/models/seat_section.py
from sqlalchemy import String, Float, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SeatSection(Base):
    __tablename__ = "seat_sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"))
    name: Mapped[str] = mapped_column(String(200))
    section_type: Mapped[str] = mapped_column(String(30))  # grandstand, general_admission, hospitality, vip
    location_on_track: Mapped[str | None] = mapped_column(String(200), nullable=True)
    has_roof: Mapped[bool] = mapped_column(Boolean, default=False)
    has_screen: Mapped[bool] = mapped_column(Boolean, default=False)
    pit_view: Mapped[bool] = mapped_column(Boolean, default=False)
    podium_view: Mapped[bool] = mapped_column(Boolean, default=False)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    view_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    view_photos: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of URLs

    circuit: Mapped["Circuit"] = relationship(back_populates="seat_sections")
```

- [ ] **Step 4: Add relationship to Circuit model**

In `backend/app/models/circuit.py`, add after the `race_events` relationship:

```python
seat_sections: Mapped[list["SeatSection"]] = relationship(back_populates="circuit")
```

- [ ] **Step 5: Update models `__init__.py`**

```python
# backend/app/models/__init__.py
from app.models.circuit import Circuit
from app.models.race_event import RaceEvent
from app.models.seat_section import SeatSection

__all__ = ["Circuit", "RaceEvent", "SeatSection"]
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && .venv/bin/python -m pytest tests/test_models.py -v`
Expected: 5 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/ backend/tests/test_models.py
git commit -m "feat: add SeatSection model with circuit relationship"
```

---

## Task 2: Alembic Migration for SeatSection

**Files:**
- Create: `backend/alembic/versions/xxxx_add_seat_sections.py` (auto-generated or manual)

- [ ] **Step 1: Generate or hand-write the migration**

Since PostgreSQL isn't available locally, hand-write the migration:

```python
# backend/alembic/versions/xxxx_add_seat_sections_table.py
"""add seat_sections table

Revision ID: <generate>
Revises: <previous revision>
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '<generate>'
down_revision = '<previous>'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'seat_sections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('circuit_id', sa.Integer(), sa.ForeignKey('circuits.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('section_type', sa.String(30), nullable=False),
        sa.Column('location_on_track', sa.String(200), nullable=True),
        sa.Column('has_roof', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_screen', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('pit_view', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('podium_view', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('view_description', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('view_photos', sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_table('seat_sections')
```

Look at `backend/alembic/versions/` for the previous migration's revision ID to set as `down_revision`.

- [ ] **Step 2: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat: add Alembic migration for seat_sections table"
```

---

## Task 3: Pydantic Schemas for SeatSection

**Files:**
- Create: `backend/app/schemas/seat_section.py`
- Modify: `backend/app/schemas/__init__.py`

- [ ] **Step 1: Create SeatSection schemas**

```python
# backend/app/schemas/seat_section.py
import json
from pydantic import BaseModel, field_validator


class SeatSectionRead(BaseModel):
    id: int
    circuit_id: int
    name: str
    section_type: str
    location_on_track: str | None = None
    has_roof: bool
    has_screen: bool
    pit_view: bool
    podium_view: bool
    capacity: int | None = None
    view_description: str | None = None
    latitude: float
    longitude: float
    view_photos: list[str] | None = None

    model_config = {"from_attributes": True}

    @field_validator("view_photos", mode="before")
    @classmethod
    def parse_view_photos(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class SeatSectionList(BaseModel):
    id: int
    circuit_id: int
    name: str
    section_type: str
    location_on_track: str | None = None
    has_roof: bool
    has_screen: bool
    pit_view: bool
    podium_view: bool
    latitude: float
    longitude: float

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Update schemas `__init__.py`**

Add to `backend/app/schemas/__init__.py`:

```python
from app.schemas.seat_section import SeatSectionRead, SeatSectionList
```

And add to `__all__`:

```python
"SeatSectionRead", "SeatSectionList",
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: add Pydantic schemas for seat sections"
```

---

## Task 4: Seat Section API Endpoints

**Files:**
- Create: `backend/app/routers/sections.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_sections_api.py`

- [ ] **Step 1: Write API tests**

```python
# backend/tests/test_sections_api.py
import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Circuit, SeatSection

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
        name="Silverstone", country="Great Britain", continent="Europe",
        city="Silverstone", latitude=52.07, longitude=-1.01,
        track_type="permanent", track_length_km=5.891, number_of_turns=18,
        drs_zones_count=2, overtake_difficulty=4, avg_overtakes_per_race=42.5,
        rain_probability_pct=55, nearest_airport="LTN",
    )
    db.add(circuit)
    db.commit()
    sections = [
        SeatSection(
            circuit_id=circuit.id, name="Wellington Straight", section_type="grandstand",
            location_on_track="Turn 1-3", has_roof=True, has_screen=True,
            pit_view=False, podium_view=False, latitude=52.0730, longitude=-1.0140,
            view_description="Great view of braking into Turn 1.",
            view_photos=json.dumps(["https://example.com/wellington.jpg"]),
        ),
        SeatSection(
            circuit_id=circuit.id, name="Copse", section_type="grandstand",
            location_on_track="Turn 9", has_roof=False, has_screen=True,
            pit_view=False, podium_view=False, latitude=52.0780, longitude=-1.0050,
        ),
        SeatSection(
            circuit_id=circuit.id, name="Inner GA", section_type="general_admission",
            location_on_track="Various", has_roof=False, has_screen=False,
            pit_view=False, podium_view=False, latitude=52.0750, longitude=-1.0100,
        ),
    ]
    db.add_all(sections)
    db.commit()
    db.close()


def teardown_function():
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(engine)


def test_list_sections_for_circuit():
    resp = client.get("/api/circuits/1/sections")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3


def test_list_sections_filter_by_type():
    resp = client.get("/api/circuits/1/sections?section_type=grandstand")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(s["section_type"] == "grandstand" for s in data)


def test_list_sections_filter_by_roof():
    resp = client.get("/api/circuits/1/sections?has_roof=true")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Wellington Straight"


def test_get_section_by_id():
    resp = client.get("/api/sections/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Wellington Straight"
    assert data["has_roof"] is True
    assert data["view_photos"] == ["https://example.com/wellington.jpg"]


def test_get_section_not_found():
    resp = client.get("/api/sections/999")
    assert resp.status_code == 404


def test_list_sections_for_nonexistent_circuit():
    resp = client.get("/api/circuits/999/sections")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && .venv/bin/python -m pytest tests/test_sections_api.py -v`
Expected: FAIL — router doesn't exist.

- [ ] **Step 3: Implement sections router**

```python
# backend/app/routers/sections.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.seat_section import SeatSection
from app.schemas.seat_section import SeatSectionRead, SeatSectionList

router = APIRouter(tags=["sections"])


@router.get("/api/circuits/{circuit_id}/sections", response_model=list[SeatSectionList])
def list_sections(
    circuit_id: int,
    section_type: str | None = None,
    has_roof: bool | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(SeatSection).filter(SeatSection.circuit_id == circuit_id)
    if section_type:
        query = query.filter(SeatSection.section_type == section_type)
    if has_roof is not None:
        query = query.filter(SeatSection.has_roof == has_roof)
    return query.order_by(SeatSection.name).all()


@router.get("/api/sections/{section_id}", response_model=SeatSectionRead)
def get_section(section_id: int, db: Session = Depends(get_db)):
    section = db.get(SeatSection, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section
```

- [ ] **Step 4: Register router in main.py**

Add to `backend/app/main.py`:

```python
from app.routers.sections import router as sections_router

app.include_router(sections_router)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && .venv/bin/python -m pytest tests/test_sections_api.py -v`
Expected: 6 tests PASS.

- [ ] **Step 6: Run all tests**

Run: `cd backend && .venv/bin/python -m pytest tests/ -v`
Expected: All tests PASS (model tests + circuits API + race events API + sections API).

- [ ] **Step 7: Commit**

```bash
git add backend/app/routers/sections.py backend/app/main.py backend/tests/test_sections_api.py
git commit -m "feat: add seat section API endpoints with filtering"
```

---

## Task 5: Seat Section Seed Data

**Files:**
- Create: `backend/app/seed/seat_sections_data.py`
- Modify: `backend/app/seed/seed_data.py`

- [ ] **Step 1: Create seat sections data file**

Create `backend/app/seed/seat_sections_data.py` containing a `SEAT_SECTIONS` dict mapping circuit names to lists of section dicts. Each section has: `name`, `section_type`, `location_on_track`, `has_roof`, `has_screen`, `pit_view`, `podium_view`, `latitude`, `longitude`, and optionally `capacity`, `view_description`.

Research real seat sections for all 22 circuits. For each circuit, include the major grandstands and GA zones listed on the official ticket sales pages. Use approximate lat/lng coordinates by placing sections near the relevant turns/straights on the track.

Example format for one circuit:

```python
SEAT_SECTIONS = {
    "Silverstone Circuit": [
        {
            "name": "Wellington Straight",
            "section_type": "grandstand",
            "location_on_track": "Turns 1-3",
            "has_roof": True,
            "has_screen": True,
            "pit_view": False,
            "podium_view": False,
            "capacity": 9000,
            "view_description": "Covered grandstand with view of heavy braking into Turn 1. One of the most popular sections.",
            "latitude": 52.0735,
            "longitude": -1.0155,
        },
        {
            "name": "Village",
            "section_type": "grandstand",
            "location_on_track": "The Loop (Turns 8-10)",
            "has_roof": False,
            "has_screen": True,
            "pit_view": False,
            "podium_view": False,
            "latitude": 52.0695,
            "longitude": -1.0175,
        },
        # ... more sections
    ],
    # ... all 22 circuits
}
```

This is the largest single file in the project. Target 8-15 sections per circuit. For section positions, use the track's real-world coordinates and offset markers to approximate grandstand locations near turns.

- [ ] **Step 2: Update seed_data.py to seed seat sections**

Add at the end of the `seed()` function in `backend/app/seed/seed_data.py`, after race events are inserted:

```python
from app.seed.seat_sections_data import SEAT_SECTIONS
from app.models.seat_section import SeatSection
import json

# Insert seat sections
section_count = 0
for circuit_name, sections in SEAT_SECTIONS.items():
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
            latitude=s["latitude"],
            longitude=s["longitude"],
            view_photos=json.dumps(s["view_photos"]) if s.get("view_photos") else None,
        )
        db.add(seat)
        section_count += 1
```

Also update the delete section at the top of `seed()` to clear seat sections before re-seeding:

```python
from app.models.seat_section import SeatSection

db.query(SeatSection).delete()
db.query(RaceEvent).delete()
db.query(Circuit).delete()
```

And update the final print:

```python
print(f"Seeded {circuit_count} circuits, {race_count} race events, and {section_count} seat sections.")
```

- [ ] **Step 3: Verify seed loads**

Run:
```bash
cd backend && .venv/bin/python -c "from app.seed.seat_sections_data import SEAT_SECTIONS; total = sum(len(v) for v in SEAT_SECTIONS.values()); print(f'{len(SEAT_SECTIONS)} circuits, {total} total sections')"
```
Expected: `22 circuits, ~200+ total sections`

- [ ] **Step 4: Re-seed the database**

```bash
cd backend && rm -f f1journey.db && .venv/bin/python -m app.seed.seed_data
```
Expected: `Seeded 22 circuits, 22 race events, and XXX seat sections.`

- [ ] **Step 5: Verify API returns sections**

```bash
curl -s http://localhost:8000/api/circuits/1/sections | python3 -m json.tool | head -20
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/seed/
git commit -m "feat: add seat section seed data for all 22 circuits"
```

---

## Task 6: Frontend — API Types and Fetch Functions

**Files:**
- Modify: `frontend/src/lib/api.ts`

- [ ] **Step 1: Add SeatSection types and fetch functions**

Add to `frontend/src/lib/api.ts`:

```typescript
export interface SeatSection {
  id: number;
  circuit_id: number;
  name: string;
  section_type: string;
  location_on_track: string | null;
  has_roof: boolean;
  has_screen: boolean;
  pit_view: boolean;
  podium_view: boolean;
  capacity: number | null;
  view_description: string | null;
  latitude: number;
  longitude: number;
  view_photos: string[] | null;
}

export async function fetchSections(
  circuitId: number,
  params?: { section_type?: string; has_roof?: boolean }
): Promise<SeatSection[]> {
  const url = new URL(`${API_URL}/api/circuits/${circuitId}/sections`);
  if (params?.section_type) url.searchParams.set("section_type", params.section_type);
  if (params?.has_roof !== undefined) url.searchParams.set("has_roof", String(params.has_roof));
  const res = await fetch(url.toString(), { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch sections");
  return res.json();
}

export async function fetchSection(id: number): Promise<SeatSection> {
  const res = await fetch(`${API_URL}/api/sections/${id}`, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error("Failed to fetch section");
  return res.json();
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: add SeatSection types and fetch functions"
```

---

## Task 7: Frontend — TrackMap Component

**Files:**
- Create: `frontend/src/components/TrackMap.tsx`

- [ ] **Step 1: Install Leaflet dependencies**

```bash
cd frontend && npm install leaflet react-leaflet && npm install -D @types/leaflet
```

- [ ] **Step 2: Create TrackMap client component**

```tsx
// frontend/src/components/TrackMap.tsx
"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { SeatSection } from "@/lib/api";

interface TrackMapProps {
  centerLat: number;
  centerLng: number;
  sections: SeatSection[];
  onSectionClick: (section: SeatSection) => void;
  selectedSectionId: number | null;
}

const SECTION_COLORS: Record<string, string> = {
  grandstand: "#3b82f6",       // blue
  general_admission: "#22c55e", // green
  hospitality: "#eab308",       // gold
  vip: "#eab308",               // gold
};

function FitBounds({ sections, centerLat, centerLng }: { sections: SeatSection[]; centerLat: number; centerLng: number }) {
  const map = useMap();
  useEffect(() => {
    if (sections.length === 0) {
      map.setView([centerLat, centerLng], 15);
      return;
    }
    const lats = sections.map((s) => s.latitude);
    const lngs = sections.map((s) => s.longitude);
    const bounds: [[number, number], [number, number]] = [
      [Math.min(...lats) - 0.002, Math.min(...lngs) - 0.004],
      [Math.max(...lats) + 0.002, Math.max(...lngs) + 0.004],
    ];
    map.fitBounds(bounds);
  }, [sections, centerLat, centerLng, map]);
  return null;
}

export default function TrackMap({
  centerLat,
  centerLng,
  sections,
  onSectionClick,
  selectedSectionId,
}: TrackMapProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-[500px] bg-gray-800 rounded-lg flex items-center justify-center">
        <span className="text-gray-500">Loading map...</span>
      </div>
    );
  }

  return (
    <MapContainer
      center={[centerLat, centerLng]}
      zoom={15}
      className="w-full h-[500px] rounded-lg"
      style={{ background: "#1e293b" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitBounds sections={sections} centerLat={centerLat} centerLng={centerLng} />
      {sections.map((section) => (
        <CircleMarker
          key={section.id}
          center={[section.latitude, section.longitude]}
          radius={selectedSectionId === section.id ? 10 : 7}
          pathOptions={{
            color: selectedSectionId === section.id ? "#ffffff" : SECTION_COLORS[section.section_type] || "#3b82f6",
            fillColor: SECTION_COLORS[section.section_type] || "#3b82f6",
            fillOpacity: 0.8,
            weight: selectedSectionId === section.id ? 3 : 1,
          }}
          eventHandlers={{
            click: () => onSectionClick(section),
          }}
        >
          <Popup>
            <div className="text-sm">
              <strong>{section.name}</strong>
              <br />
              {section.section_type.replace("_", " ")}
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/TrackMap.tsx
git commit -m "feat: add TrackMap component with Leaflet and section markers"
```

---

## Task 8: Frontend — SectionSidebar Component

**Files:**
- Create: `frontend/src/components/SectionSidebar.tsx`

- [ ] **Step 1: Create SectionSidebar component**

```tsx
// frontend/src/components/SectionSidebar.tsx
"use client";

import type { SeatSection } from "@/lib/api";

interface SectionSidebarProps {
  section: SeatSection | null;
  onClose: () => void;
}

const TYPE_LABELS: Record<string, string> = {
  grandstand: "Grandstand",
  general_admission: "General Admission",
  hospitality: "Hospitality",
  vip: "VIP",
};

export default function SectionSidebar({ section, onClose }: SectionSidebarProps) {
  if (!section) return null;

  const badges = [
    section.has_roof && { label: "Has Roof", color: "bg-green-500/10 text-green-400" },
    section.has_screen && { label: "Screen", color: "bg-blue-500/10 text-blue-400" },
    section.pit_view && { label: "Pit View", color: "bg-yellow-500/10 text-yellow-400" },
    section.podium_view && { label: "Podium View", color: "bg-purple-500/10 text-purple-400" },
  ].filter(Boolean) as { label: string; color: string }[];

  return (
    <div className="bg-gray-900 border-l border-gray-700 p-4 w-80 overflow-y-auto">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-bold text-lg">{section.name}</h3>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-white text-xl leading-none"
        >
          &times;
        </button>
      </div>

      <div className="text-sm text-gray-400 mb-3">
        {TYPE_LABELS[section.section_type] || section.section_type}
        {section.location_on_track && <> &bull; {section.location_on_track}</>}
      </div>

      {badges.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {badges.map((badge) => (
            <span
              key={badge.label}
              className={`text-xs px-2 py-1 rounded ${badge.color}`}
            >
              {badge.label}
            </span>
          ))}
        </div>
      )}

      {section.view_description && (
        <div className="bg-gray-800 rounded-lg p-3 mb-4 text-sm text-gray-300">
          <div className="text-xs text-gray-500 mb-1 uppercase">View Description</div>
          {section.view_description}
        </div>
      )}

      {section.capacity && (
        <div className="text-sm text-gray-400 mb-4">
          Capacity: {section.capacity.toLocaleString()}
        </div>
      )}

      {section.view_photos && section.view_photos.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-gray-500 mb-2 uppercase">View Photos</div>
          <div className="flex flex-col gap-2">
            {section.view_photos.map((url, i) => (
              <img
                key={i}
                src={url}
                alt={`${section.name} view ${i + 1}`}
                className="rounded-lg w-full object-cover h-40"
              />
            ))}
          </div>
        </div>
      )}

      {/* Placeholder for ticket prices (Subsystem 2b) */}
      <div className="text-center text-gray-600 text-xs mt-4">
        Ticket prices coming soon
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/SectionSidebar.tsx
git commit -m "feat: add SectionSidebar component for seat section details"
```

---

## Task 9: Frontend — SectionTable Component

**Files:**
- Create: `frontend/src/components/SectionTable.tsx`

- [ ] **Step 1: Create SectionTable component**

```tsx
// frontend/src/components/SectionTable.tsx
"use client";

import { useState } from "react";
import type { SeatSection } from "@/lib/api";

interface SectionTableProps {
  sections: SeatSection[];
  onSectionClick: (section: SeatSection) => void;
}

type SortKey = "name" | "section_type" | "location_on_track" | "has_roof" | "has_screen";

export default function SectionTable({ sections, onSectionClick }: SectionTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("name");
  const [sortAsc, setSortAsc] = useState(true);

  const sorted = [...sections].sort((a, b) => {
    const aVal = a[sortKey];
    const bVal = b[sortKey];
    if (aVal === null || aVal === undefined) return 1;
    if (bVal === null || bVal === undefined) return -1;
    if (typeof aVal === "boolean") return (aVal === bVal ? 0 : aVal ? -1 : 1) * (sortAsc ? 1 : -1);
    if (typeof aVal === "string") return aVal.localeCompare(String(bVal)) * (sortAsc ? 1 : -1);
    return 0;
  });

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  }

  const thClass = "pb-2 pr-4 cursor-pointer hover:text-gray-200";

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800 text-gray-400 text-left">
            <th className={thClass} onClick={() => handleSort("name")}>Name {sortKey === "name" ? (sortAsc ? "↑" : "↓") : ""}</th>
            <th className={thClass} onClick={() => handleSort("section_type")}>Type {sortKey === "section_type" ? (sortAsc ? "↑" : "↓") : ""}</th>
            <th className={thClass} onClick={() => handleSort("location_on_track")}>Location {sortKey === "location_on_track" ? (sortAsc ? "↑" : "↓") : ""}</th>
            <th className={thClass} onClick={() => handleSort("has_roof")}>Roof {sortKey === "has_roof" ? (sortAsc ? "↑" : "↓") : ""}</th>
            <th className={thClass} onClick={() => handleSort("has_screen")}>Screen {sortKey === "has_screen" ? (sortAsc ? "↑" : "↓") : ""}</th>
            <th className="pb-2 pr-4">Pit View</th>
            <th className="pb-2 pr-4">Podium View</th>
            <th className="pb-2">Capacity</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((section) => (
            <tr
              key={section.id}
              className="border-b border-gray-800/50 hover:bg-gray-900 cursor-pointer"
              onClick={() => onSectionClick(section)}
            >
              <td className="py-2 pr-4 text-blue-400">{section.name}</td>
              <td className="py-2 pr-4 text-gray-400 capitalize">{section.section_type.replace("_", " ")}</td>
              <td className="py-2 pr-4 text-gray-400">{section.location_on_track || "—"}</td>
              <td className="py-2 pr-4">{section.has_roof ? "✓" : "—"}</td>
              <td className="py-2 pr-4">{section.has_screen ? "✓" : "—"}</td>
              <td className="py-2 pr-4">{section.pit_view ? "✓" : "—"}</td>
              <td className="py-2 pr-4">{section.podium_view ? "✓" : "—"}</td>
              <td className="py-2">{section.capacity ? section.capacity.toLocaleString() : "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/SectionTable.tsx
git commit -m "feat: add SectionTable component with sortable columns"
```

---

## Task 10: Frontend — Update Track Detail Page with Tabs

**Files:**
- Create: `frontend/src/app/tracks/[id]/TrackDetailClient.tsx`
- Modify: `frontend/src/app/tracks/[id]/page.tsx`

- [ ] **Step 1: Create client wrapper for interactive sections**

The track detail page is currently a server component. The map and sidebar need client-side interactivity. Create a client component that wraps the interactive parts:

```tsx
// frontend/src/app/tracks/[id]/TrackDetailClient.tsx
"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import type { SeatSection } from "@/lib/api";
import SectionSidebar from "@/components/SectionSidebar";
import SectionTable from "@/components/SectionTable";

const TrackMap = dynamic(() => import("@/components/TrackMap"), { ssr: false });

interface TrackDetailClientProps {
  centerLat: number;
  centerLng: number;
  sections: SeatSection[];
}

export default function TrackDetailClient({ centerLat, centerLng, sections }: TrackDetailClientProps) {
  const [activeTab, setActiveTab] = useState<"map" | "table">("map");
  const [selectedSection, setSelectedSection] = useState<SeatSection | null>(null);

  function handleSectionClick(section: SeatSection) {
    setSelectedSection(section);
  }

  const tabClass = (tab: string) =>
    `px-4 py-2 text-sm font-medium cursor-pointer ${
      activeTab === tab
        ? "border-b-2 border-blue-500 text-blue-400"
        : "text-gray-400 hover:text-white"
    }`;

  return (
    <div>
      {/* Tabs */}
      <div className="flex border-b border-gray-800 px-6">
        <button className={tabClass("map")} onClick={() => setActiveTab("map")}>
          Seat Map
        </button>
        <button className={tabClass("table")} onClick={() => setActiveTab("table")}>
          Table View
        </button>
      </div>

      {/* Legend */}
      <div className="px-6 pt-3 flex gap-4 text-xs text-gray-400">
        <span><span className="inline-block w-3 h-3 rounded-full bg-blue-500 mr-1"></span> Grandstand</span>
        <span><span className="inline-block w-3 h-3 rounded-full bg-green-500 mr-1"></span> General Admission</span>
        <span><span className="inline-block w-3 h-3 rounded-full bg-yellow-500 mr-1"></span> Hospitality / VIP</span>
      </div>

      {/* Content */}
      <div className="px-6 py-4">
        {activeTab === "map" ? (
          <div className="flex gap-0">
            <div className={selectedSection ? "flex-1" : "w-full"}>
              <TrackMap
                centerLat={centerLat}
                centerLng={centerLng}
                sections={sections}
                onSectionClick={handleSectionClick}
                selectedSectionId={selectedSection?.id ?? null}
              />
            </div>
            <SectionSidebar
              section={selectedSection}
              onClose={() => setSelectedSection(null)}
            />
          </div>
        ) : (
          <div className="flex gap-0">
            <div className={selectedSection ? "flex-1" : "w-full"}>
              <SectionTable sections={sections} onSectionClick={handleSectionClick} />
            </div>
            <SectionSidebar
              section={selectedSection}
              onClose={() => setSelectedSection(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Update track detail page**

Modify `frontend/src/app/tracks/[id]/page.tsx`:

1. Add import for `fetchSections` and `TrackDetailClient`
2. Fetch sections in the server component
3. Replace the placeholder text with `<TrackDetailClient />`

The updated page should:
- Import `fetchSections` from `@/lib/api`
- Import `TrackDetailClient` from `./TrackDetailClient`
- After fetching circuit and race events, also fetch sections:
  ```typescript
  let sections: SeatSection[] = [];
  try {
    sections = await fetchSections(circuitId);
  } catch {
    sections = [];
  }
  ```
- Replace the placeholder div (`Seat map, ticket prices...`) with:
  ```tsx
  {/* Seat Sections */}
  <div className="py-6">
    <TrackDetailClient
      centerLat={circuit.latitude}
      centerLng={circuit.longitude}
      sections={sections}
    />
  </div>
  ```

- [ ] **Step 3: Verify it builds**

Run:
```bash
cd frontend && npx next build
```
Expected: Build succeeds with no TypeScript errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/tracks/[id]/ frontend/src/components/
git commit -m "feat: add seat map and table view to track detail page"
```

---

## Task 11: End-to-End Verification

- [ ] **Step 1: Re-seed the database**

```bash
cd backend && rm -f f1journey.db && .venv/bin/python -m app.seed.seed_data
```

- [ ] **Step 2: Start backend**

```bash
cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000
```

- [ ] **Step 3: Verify API**

```bash
curl -s http://localhost:8000/api/circuits/1/sections | python3 -m json.tool | head -30
curl -s http://localhost:8000/api/sections/1 | python3 -m json.tool
```

- [ ] **Step 4: Start frontend and verify**

```bash
cd frontend && npm run dev -- -p 3001
```

Verify at http://localhost:3001/tracks/1:
- Map tab shows Leaflet map with colored markers at section positions
- Clicking a marker opens the sidebar with section details and amenity badges
- Table tab shows sortable table of all sections
- Clicking a table row opens the sidebar

- [ ] **Step 5: Run all backend tests**

```bash
cd backend && .venv/bin/python -m pytest tests/ -v
```
Expected: All tests pass.

- [ ] **Step 6: Commit any final fixes**

```bash
git add -A
git commit -m "feat: complete subsystem 2a — seat sections with interactive track map"
```
