# F1 Journey Planner — Design Spec

## Overview

A web platform that helps users find the optimal Formula 1 race weekend by aggregating ticket availability, seat information, travel costs, and track intelligence across all Grand Prix events. Serves both hardcore fans (who know what they want) and newer fans (who need guidance choosing a GP).

Starts as a personal dashboard, then deploys publicly.

## Architecture

**Monolith API + React Frontend**

- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Leaflet/Mapbox (free tier) for interactive track maps. Deployed on Vercel (free).
- **Backend:** Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic. Deployed on Render (free).
- **Database:** PostgreSQL 16 on Render (free tier).
- **Scraping:** BeautifulSoup (static pages), Playwright with stealth plugin (JS-rendered pages). Scheduled via Render cron jobs.
- **CI:** GitHub Actions.

All infrastructure runs on free tiers. Total cost: $0.

## Data Model

### Circuit
- name, country, continent, city
- lat/lng, track_type (street/permanent)
- track_length_km, number_of_turns
- drs_zones_count, elevation_change
- overtake_difficulty (1-10 score)
- avg_overtakes_per_race (historical)
- rain_probability (% by month)
- nearest_airport, local_transport_notes
- atmosphere_rating, fan_reviews_summary

### Race Event
- circuit_id (FK)
- season_year, race_name
- race_date, sprint_weekend (bool)
- fp1/fp2/fp3/quali/race schedule
- status (upcoming/completed)
- total_overtakes (if completed)
- weather_actual (if completed)

### Seat Section
- circuit_id (FK)
- name (e.g., "Grandstand A", "GA Zone 3")
- section_type (grandstand/GA/hospitality/VIP)
- location_on_track (turn number/straight)
- has_roof (bool), has_screen (bool)
- pit_view (bool), podium_view (bool)
- capacity, view_description
- view_photos (URLs)
- map_coordinates (polygon for interactive map)

### Ticket Listing
- race_event_id (FK), seat_section_id (FK)
- source_site (F1.com, StubHub, etc.)
- source_url
- ticket_type (fri/sat/sun/weekend/3-day)
- price, currency
- available_quantity
- includes (list: food, drink, merch, etc.)
- last_scraped_at
- is_available (bool)

### Travel Option
- circuit_id (FK)
- origin_city, origin_country
- transport_type (flight/train/drive)
- provider (airline/rail company)
- estimated_cost_min, estimated_cost_max
- estimated_duration_hours
- local_transport_cost
- hotel_avg_cost_per_night
- last_scraped_at

### User
- email, hashed_password
- home_city, home_country
- preferred_continent (optional)
- budget_range (optional)
- group_size_default
- saved_searches (JSON)
- calendar_sync_token (optional)
- created_at, last_login

### Key Relationships
- Circuit 1→N Race Events
- Circuit 1→N Seat Sections
- Race Event + Seat Section → N Ticket Listings
- Circuit 1→N Travel Options (cached per origin city)
- User 1→N Saved Searches

## Features

### Core User Flow

1. **Landing/Dashboard** — Race calendar, quick filters (origin, continent, budget, group size, overtaking preference), "help me choose" recommendation quiz for newer fans.

2. **Explore Tracks** — World map view with all circuits. Filter by continent, overtaking score, rain risk, track type. Compare tracks side by side.

3. **Recommendation Quiz** — Guided flow: where are you based, budget, prefer overtaking, sun vs rain tolerance, group size. Outputs ranked GP recommendations.

4. **Track Detail Page** — Race stats, weather history, fan reviews. Two views:
   - **Interactive seat map:** Click grandstand/section on track map → sidebar shows view photos, amenities (roof, screen, pit view, podium view), what's included, and ticket prices from all sources with availability counts.
   - **Comparison table:** All seat options listed, filterable and sortable by price, type, amenities, source.

5. **Trip Planner** — Enter origin city + group size. Shows flight/train options with costs, local transport to circuit, hotel estimates. Full cost breakdown.

6. **Total Cost Summary** — Tickets + travel + local transport + hotel = total (per person and group total). Links out to ticket sites to purchase. Save search, add to calendar, share with group.

### Additional Features

- **Saved searches** — Persist filter combinations, get notified of changes.
- **Calendar integration** — Sync race schedule to personal calendar.
- **Comparison mode** — Side-by-side two GP weekends on cost, weather, overtaking, travel time, seats.
- **Weather intelligence** — Historical rain probability per track per month. Informs seat selection (covered vs uncovered sections). Not a live forecast — a historical estimate.
- **User accounts** — JWT auth, profile with home city and preferences.

## Scraping Strategy

### Ticket Sources
| Source | Type |
|--------|------|
| F1.com Official | Primary/official |
| Ticketmaster | Primary |
| StubHub | Resale |
| Viagogo | Resale |
| SeatGeek | Aggregator |
| Vivid Seats | Resale |
| GP-specific portals | Official (per-track) |

### Race & Track Data Sources
| Source | Data |
|--------|------|
| F1 Official Stats | Overtakes, results |
| Wikipedia | Track info, history |
| StatsF1 / F1Metrics | Deep race statistics |
| Reddit r/formula1 | Fan reviews, experiences |
| TripAdvisor | Venue/atmosphere reviews |
| OpenWeather API | Historical rain data |

### Travel Data Sources
| Source | Data |
|--------|------|
| Google Flights | Flight prices |
| Skyscanner | Flight comparison |
| Trainline / Rail Europe | Train prices |
| Rome2Rio | Multi-modal route planning |
| Booking.com | Hotel prices |
| Google Maps API | Local transport estimates |

### Scraping Schedule
| Data Type | Frequency | Method | Staleness Tolerance |
|-----------|-----------|--------|-------------------|
| Ticket prices & availability | Every 6 hours | Playwright | Up to 12h |
| Race stats & overtakes | After each race | BeautifulSoup | Indefinite |
| Fan reviews | Weekly | Reddit API + BeautifulSoup | 1 week |
| Travel costs (flights/trains) | Daily | Playwright + APIs | 24h |
| Hotel estimates | Daily | Playwright | 24h |
| Weather history | Monthly | OpenWeather API | Indefinite |

### Resilience
- Randomized delays between requests, rotating user agents, respect robots.txt.
- Playwright stealth plugin for headless browser fingerprint masking.
- Per-source circuit breakers: 3 consecutive failures → exponential backoff.
- Stale data displayed with "last updated" timestamp.
- Alerting on persistent scraper failures.

### Legal Model
Aggregator with attribution — display prices with clear source attribution and direct links to purchase. We don't sell tickets, we link to the source. Same model as Google Flights or Kayak.

## UI Design

### Layout Direction
- Dark theme (F1-inspired aesthetic)
- Interactive track maps with clickable seat sections
- Sidebar detail panel for selected sections
- Multi-source ticket price comparison within each section
- Responsive — works on mobile for on-the-go race weekend planning

### Key Pages
1. **Dashboard** — Hero with quick filters, upcoming race cards (showing overtaking score, rain risk, starting price), saved searches, recommendation quiz CTA.
2. **Explore / World Map** — Interactive map of all circuits, filter sidebar, click to drill in.
3. **Track Detail** — Tabbed: Seat Map | Table View | Race Stats | Weather | Reviews | Travel. Map + sidebar is the primary view.
4. **Comparison View** — Side-by-side two GP weekends across all dimensions.
5. **Trip Planner** — Origin input, transport options, cost grid (tickets + travel + transport + hotel), total per person and group.
6. **User Profile** — Home city, preferences, saved searches, calendar sync settings.

## Build Order (Subsystems)

This project decomposes into 5 independent subsystems, to be built sequentially:

1. **Core data model + seed data** — Database schema, seed circuits and race events with manually sourced initial data. Backend API for tracks and races. Basic frontend with track listing.

2. **Seat maps + ticket scraping** — Seat section data model, interactive track maps, ticket scraper for 2-3 sources initially (F1.com, StubHub, one aggregator). Seat detail sidebar with prices.

3. **Travel planner + cost calculator** — Travel data scraping, trip cost calculator, cost summary page. Group size multiplier.

4. **Discovery + recommendations** — Explore map, filters, recommendation quiz, comparison mode, weather intelligence.

5. **User accounts + extras** — Auth, saved searches, calendar sync, price alerts. Polish for public launch.

Each subsystem gets its own spec → plan → implementation cycle.
