# Subsystem 2b: Ticket Scraping Engine — Design Spec

## Overview

Build a ticket scraping engine that pulls ticket prices and availability from 7 source sites for all 22 circuits. Scraped listings are fuzzy-matched to seat sections and displayed in the section sidebar and a dedicated ticket comparison page.

## Data Model

### TicketListing (new table)

- `id` (PK)
- `circuit_id` (FK → circuits.id)
- `race_event_id` (FK → race_events.id)
- `seat_section_id` (FK → seat_sections.id, nullable — null if unmatched)
- `source_site` (string — one of: f1_official, stubhub, viagogo, seatgeek, vivid_seats, ticketmaster, gp_portal)
- `source_url` (string — direct link to the ticket listing)
- `source_section_name` (string — raw section name from the scraper, used for matching)
- `ticket_type` (string — friday, saturday, sunday, weekend, 3_day)
- `price` (float)
- `currency` (string — USD, EUR, GBP, etc.)
- `available_quantity` (int, nullable)
- `includes` (Text/JSON, nullable — list of inclusions like food, drink, merch, paddock access)
- `last_scraped_at` (datetime)
- `is_available` (bool)

### Relationships

- Circuit 1→N TicketListings
- RaceEvent 1→N TicketListings
- SeatSection 1→N TicketListings (nullable — unmatched listings have no section)

## Scraper Architecture

### Base Structure

```
backend/app/scrapers/
├── __init__.py
├── base.py              # BaseScraper abstract class + RawTicketListing dataclass
├── matcher.py           # Fuzzy matching engine (source_section_name → seat_section_id)
├── orchestrator.py      # Scheduling orchestrator — runs all scrapers, staggered
├── f1_official.py       # F1.com official ticket scraper
├── stubhub.py           # StubHub scraper
├── viagogo.py           # Viagogo scraper
├── seatgeek.py          # SeatGeek scraper (uses public API)
├── vivid_seats.py       # Vivid Seats scraper
├── ticketmaster.py      # Ticketmaster scraper
└── gp_portal.py         # GP-specific portal scraper (per-circuit logic)
```

### BaseScraper

Abstract class that all scrapers implement:

```python
class RawTicketListing:
    source_site: str
    source_url: str
    source_section_name: str
    ticket_type: str
    price: float
    currency: str
    available_quantity: int | None
    includes: list[str] | None

class BaseScraper(ABC):
    @abstractmethod
    async def scrape_circuit(self, circuit_name: str, race_name: str) -> list[RawTicketListing]:
        """Scrape all available tickets for a given circuit/race."""

    def get_browser(self) -> Playwright browser instance (stealth mode)
    def random_delay(self, min_s=30, max_s=120) -> None
```

### Fuzzy Matcher

Maps `source_section_name` to `seat_section_id`:
- Loads all seat section names for the circuit
- Uses `difflib.SequenceMatcher` or `rapidfuzz` library for string similarity
- Match threshold: 0.7 similarity score
- Below threshold → `seat_section_id = None` (unmatched)
- Logs all matches and non-matches for debugging

### Orchestrator

Single entry point that runs all scrapers:
- Iterates through all 7 sources × 22 circuits
- Random 30-120 second delay between requests
- Per-source circuit breaker: 3 consecutive failures → skip source for this run
- Logs results: source, circuit, tickets_found, matched, unmatched, errors
- Designed to be called by Render cron job every 6 hours
- Can also be run manually: `python -m app.scrapers.orchestrator`

### Per-Source Scraper Details

| Source | Method | Key Challenges |
|--------|--------|---------------|
| F1.com Official | Playwright | Queue/waiting room system, JS-heavy |
| StubHub | httpx + API | Rate limiting, API may need auth token |
| Viagogo | Playwright | Aggressive anti-bot, Cloudflare |
| SeatGeek | httpx + public API | Easiest — has documented API |
| Vivid Seats | Playwright | JS-rendered, anti-bot |
| Ticketmaster | Playwright | Heavy anti-bot, CAPTCHAs |
| GP Portal | Playwright/httpx | Varies per circuit, some use gpticketstore |

### Anti-Bot Measures

- `playwright-stealth` plugin for headless browser fingerprint masking
- Rotating user agent strings (pool of 20+ real browser UAs)
- Randomized delays between requests (30-120s)
- Per-domain rate limiting (max 1 request per 30s per domain)
- Respect robots.txt where feasible
- Exponential backoff on failures

## Scraping Schedule

- **Frequency**: Every 6 hours via Render cron job
- **Staggering**: 154 scrape tasks (7 sources × 22 circuits) spread across the 6-hour window
- **Staleness tolerance**: Data shown with "last updated X hours ago" timestamp
- **Circuit breaker**: Per-source, resets each run cycle

## API Endpoints

### List tickets for a circuit

```
GET /api/circuits/{circuit_id}/tickets
```

Returns all ticket listings for the circuit's upcoming race. Query params:
- `source_site` — filter by source
- `ticket_type` — filter by type (weekend, sunday, etc.)
- `min_price`, `max_price` — price range filter
- `sort` — price_asc (default), price_desc

### List tickets for a section

```
GET /api/sections/{section_id}/tickets
```

Returns ticket listings matched to this specific section.

### List unmatched tickets

```
GET /api/circuits/{circuit_id}/tickets/unmatched
```

Returns tickets that couldn't be matched to any seat section.

## Pydantic Schemas

### TicketListingRead

```python
class TicketListingRead(BaseModel):
    id: int
    circuit_id: int
    race_event_id: int
    seat_section_id: int | None
    source_site: str
    source_url: str
    source_section_name: str
    ticket_type: str
    price: float
    currency: str
    available_quantity: int | None
    includes: list[str] | None
    last_scraped_at: datetime
    is_available: bool
    section_name: str | None  # joined from seat_sections if matched
```

## Frontend

### Section Sidebar — Ticket Prices

When a seat section is selected, the sidebar shows a new "Tickets" section:
- List of available tickets from all sources, sorted by price
- Each row: source name, ticket type, price, availability count, direct link to buy
- "Last updated" timestamp

### Ticket Comparison Page (`/tracks/{id}/tickets`)

New dedicated page for deep ticket comparison:
- Full table of all tickets for the circuit
- Filters: source site, section, ticket type, price range
- Sort by: price, source, section name
- Unmatched tickets shown in a separate section at the bottom
- Direct "Buy" links to source sites

## Dependencies

- `playwright` — headless browser for JS-rendered sites
- `playwright-stealth` — anti-detection for Playwright
- `httpx` — async HTTP client for API-based scrapers
- `beautifulsoup4` — HTML parsing
- `rapidfuzz` — fast fuzzy string matching

## Build Order

1. TicketListing model + migration
2. Pydantic schemas + API endpoints + tests
3. BaseScraper + fuzzy matcher
4. Individual scrapers (7 files)
5. Orchestrator + cron integration
6. Seed with initial scrape run
7. Frontend: ticket prices in section sidebar
8. Frontend: ticket comparison page
9. End-to-end verification
