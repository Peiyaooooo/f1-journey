# Subsystem 4: Discovery + Recommendations — Design Spec

## Overview

Add an Explore page, recommendation quiz, comparison mode, and weather intelligence. All frontend-only — no new backend models or APIs needed, just new pages consuming existing endpoints.

## Explore Page (`/explore`)

### Layout
- Grid of circuit cards (not a world map — simpler and more useful)
- Filter sidebar with:
  - Continent dropdown (All, Europe, Asia, North America, South America, Oceania)
  - Track type toggle (All, Permanent, Street)
  - Overtaking score range (slider 0-10)
  - Rain risk range (slider 0-100%)
- Sort by: name, overtaking score, rain risk, race date
- Each card shows: circuit name, country, track type badge, overtaking score, rain %, race date, cheapest ticket price (if available)
- Click card → navigates to track detail page

### Data
- Fetches `GET /api/circuits` and `GET /api/race-events?season=2026` and `GET /api/circuits/{id}/tickets` for pricing
- All filtering and sorting done client-side (22 circuits is small enough)

## Recommendation Quiz (`/quiz`)

### 5-Step Flow
1. **Where are you based?** — City input with autocomplete (reuses `/api/travel/cities` endpoint)
2. **Budget per person?** — Slider: $200 / $500 / $1000 / $2000 / $5000+
3. **What matters most?** — Multi-select: "Lots of overtaking" / "Great atmosphere" / "Low rain risk" / "Close to home" / "Cheapest overall"
4. **Rain tolerance?** — Single select: "Prefer sunshine" / "Don't mind rain" / "Love rain drama"
5. **Group size?** — Number selector 1-10

### Scoring Algorithm
After the quiz, score each circuit (0-100) based on:
- Overtaking preference: weight `10 - overtake_difficulty` if "lots of overtaking" selected
- Rain preference: weight low rain_probability_pct if "prefer sunshine", high if "love rain drama"
- Budget: penalize circuits where cheapest ticket exceeds budget
- Proximity: if origin city is known, penalize distant continents (rough heuristic)
- Atmosphere: bonus for circuits with high atmosphere_rating (if available)

### Results
- Ranked list of top 10 GPs with score breakdown
- Each result shows: circuit name, race date, score, key reasons (e.g. "High overtaking", "Low rain risk")
- "View details" button → track detail page

## Comparison Mode (`/compare`)

### Layout
- Two dropdown selectors at the top (pick circuit A and circuit B)
- Side-by-side stat cards:
  - Track stats: overtaking, rain %, length, turns, DRS zones, track type
  - Ticket prices: cheapest GA, cheapest grandstand (from seeded data)
  - Race info: date, sprint weekend
- Visual indicators: green highlight on the "better" value for each stat

### Data
- Fetches circuit data + tickets for both selected circuits
- All rendering client-side

## Weather Intelligence

### Track Detail Page Enhancement
- On circuits with rain_probability_pct > 40%:
  - Show a weather warning banner: "This circuit has X% chance of rain — consider a covered grandstand"
  - In the section chips/table, visually highlight sections with `has_roof=True` (e.g. rain icon or border)

## Frontend Pages & Components

### New Pages
- `/explore` — Explore page with filters
- `/quiz` — Recommendation quiz
- `/compare` — Comparison mode

### New Components
- `CircuitCard.tsx` — Card for explore grid (reusable)
- `ExploreFilters.tsx` — Filter sidebar for explore page
- `QuizFlow.tsx` — Multi-step quiz component
- `QuizResults.tsx` — Ranked results display
- `ComparisonView.tsx` — Side-by-side circuit comparison

### Modified Components
- `Navbar.tsx` — Add Explore, Quiz, Compare links
- `TrackDetailClient.tsx` — Add rain warning banner
- `CircuitMap.tsx` — Highlight covered sections when rain risk > 40%

## Build Order

1. CircuitCard component
2. Explore page with filters
3. Quiz flow component
4. Quiz results with scoring algorithm
5. Comparison view
6. Weather intelligence (rain warnings + covered section highlights)
7. Navbar updates
8. End-to-end verification
