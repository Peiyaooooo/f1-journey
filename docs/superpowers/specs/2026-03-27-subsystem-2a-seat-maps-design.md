# Subsystem 2a: Seat Sections + Interactive Track Map — Design Spec

## Overview

Add seat section data and interactive track maps to the F1 Journey Planner. Each circuit gets a set of seat sections (grandstands, GA zones, hospitality/VIP areas) with amenities, locations, and view descriptions. The track detail page gets a Leaflet-based map with clickable section markers and a sidebar detail panel.

Data is sourced by scraping F1.com ticket pages and GP-specific portals.

## Data Model

### SeatSection (new table)

- `id` (PK)
- `circuit_id` (FK → circuits.id)
- `name` (e.g. "Wellington Straight", "Grandstand A", "GA Zone 3")
- `section_type` — enum: grandstand, general_admission, hospitality, vip
- `location_on_track` (e.g. "Turn 1", "Main Straight", "Pit Lane")
- `has_roof` (bool)
- `has_screen` (bool)
- `pit_view` (bool)
- `podium_view` (bool)
- `capacity` (int, nullable)
- `view_description` (text, nullable — what you can see from this section)
- `latitude` (float — marker position on real-world map)
- `longitude` (float — marker position on real-world map)
- `view_photos` (JSON array of URLs, nullable)

### Relationship

- Circuit 1→N SeatSections

## Scraping Strategy

### Sources

- F1.com ticket pages (per-GP ticket selection shows section names and types)
- GP-specific ticket portals (e.g. Silverstone.co.uk, monzanet.it)
- Track guide sites and fan resources for amenity details

### What to scrape

- Section names and types (grandstand vs GA vs hospitality)
- Amenities where listed (roof, screen, pit view, podium view)
- View descriptions from track guides
- Approximate lat/lng by mapping section descriptions ("Turn 1", "Main Straight") to known track coordinates

### Schedule

One-time scraping job — seat sections rarely change within a season. Can be re-run manually when needed. This is NOT a recurring background job.

### Implementation

- `backend/app/scrapers/seat_scraper.py` — scraper module
- Uses BeautifulSoup for static pages, Playwright for JS-rendered pages
- Per-circuit scraper functions (some circuits have unique page structures)
- Fallback: for circuits where scraping fails, populate with manually researched data
- Output: list of SeatSection dicts ready for DB insertion

## API Endpoints

### List sections for a circuit

```
GET /api/circuits/{circuit_id}/sections
```

Returns all seat sections for the given circuit. Response: `list[SeatSectionRead]`

Optional query params:
- `section_type` — filter by type (grandstand, general_admission, hospitality, vip)
- `has_roof` — filter by covered sections (bool)

### Get single section

```
GET /api/sections/{section_id}
```

Returns full detail for a single section. Response: `SeatSectionRead`

## Pydantic Schemas

### SeatSectionRead

```python
class SeatSectionRead(BaseModel):
    id: int
    circuit_id: int
    name: str
    section_type: str
    location_on_track: str | None
    has_roof: bool
    has_screen: bool
    pit_view: bool
    podium_view: bool
    capacity: int | None
    view_description: str | None
    latitude: float
    longitude: float
    view_photos: list[str] | None

    model_config = {"from_attributes": True}
```

## Frontend

### Track Detail Page Changes

The track detail page (`/tracks/[id]`) gets two new tabs:
- **Seat Map** (default) — interactive Leaflet map
- **Table View** — sortable table of all sections

### Seat Map Tab

- **Leaflet map** using free OpenStreetMap tiles, centered on circuit lat/lng, zoom level showing the full track
- **Colored markers** per section:
  - Blue = grandstand
  - Green = general admission
  - Gold = hospitality/VIP
- **Marker popups**: on click, show section name and type
- **Sidebar panel**: clicking a marker opens a detail sidebar showing:
  - Section name and type
  - Amenity badges (has roof, has screen, pit view, podium view)
  - View description
  - View photos (if available)
  - Location on track
  - Capacity (if known)
- Sidebar replaces the previous mockup's inline detail — it slides in from the right

### Table View Tab

- All sections listed in a table
- Columns: Name, Type, Location, Roof, Screen, Pit View, Podium View, Capacity
- Sortable by any column
- Click a row to see full section detail (same sidebar)

### Dependencies

- `leaflet` + `react-leaflet` npm packages (free, open source)
- OpenStreetMap tiles (free, no API key needed)

## Seed Data

For the initial version, seed data for all 22 circuits with:
- Section names, types, and amenities scraped from official sources
- Approximate lat/lng positions for each section
- View descriptions where available

The scraper produces a JSON file per circuit, which the seed script imports.

## Build Order

1. Backend: SeatSection model + migration
2. Backend: Pydantic schemas + API endpoints + tests
3. Backend: Seat scraper module (scrape + store)
4. Backend: Seed data from scraper output
5. Frontend: Leaflet map component with markers
6. Frontend: Section sidebar detail panel
7. Frontend: Table view tab
8. End-to-end verification
