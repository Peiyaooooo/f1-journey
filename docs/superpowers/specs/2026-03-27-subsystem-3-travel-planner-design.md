# Subsystem 3: Travel Planner + Cost Calculator — Design Spec

## Overview

Add travel cost estimation and a total trip cost calculator to the track detail page. Users enter their origin city and group size, and get flight/train/hotel estimates plus a total cost breakdown. Prices are shown in the user's preferred currency.

## Data Sources

### Flights — Kiwi.com Tequila API
- Free tier available
- Search by origin/destination airport codes
- Returns: price, duration, airline, number of stops
- Endpoint: `https://api.tequila.kiwi.com/v2/search`
- Requires API key (free registration)

### Trains / Local Transport — Rome2Rio API
- Free tier with limited calls
- Multi-modal route search (trains, buses, ferries, shuttles)
- Returns: price range, duration, transport types
- Endpoint: `https://api.rome2rio.com/api/1.4/json/Search`
- Requires API key (free registration)

### Hotels — Estimated
- Use a per-circuit hotel cost estimate stored in the database
- Based on average hotel prices near each circuit during race weekend
- Updated periodically (can be scraped or manually maintained)

### Exchange Rates — Free API
- frankfurter.app (free, no key needed) or exchangerate-api.com
- Fetched daily, cached in DB
- Base currency: USD

## Data Model

### TravelEstimate (new table)

- `id` (PK)
- `circuit_id` (FK → circuits.id)
- `origin_city` (string)
- `origin_country` (string)
- `origin_airport_code` (string, e.g. "LHR", "JFK")
- `flight_price_min` (float, USD)
- `flight_price_max` (float, USD)
- `flight_duration_hours` (float)
- `flight_stops` (int — minimum stops for cheapest option)
- `train_available` (bool)
- `train_price_min` (float, USD, nullable)
- `train_price_max` (float, USD, nullable)
- `train_duration_hours` (float, nullable)
- `local_transport_cost` (float, USD — estimate for airport/station to circuit)
- `hotel_avg_per_night` (float, USD)
- `last_fetched_at` (datetime)

All prices stored in USD.

### ExchangeRate (new table)

- `id` (PK)
- `currency_code` (string, e.g. "EUR", "GBP")
- `rate_to_usd` (float — 1 USD = X of this currency)
- `last_updated_at` (datetime)

### Relationships

- Circuit 1→N TravelEstimates (one per origin city)

## How It Works

1. User enters origin city on the Travel tab of the track detail page
2. Backend receives `GET /api/travel/estimate?circuit_id=X&origin=London`
3. Backend checks for cached estimate for this origin → circuit pair
4. If cached and fresh (< 24 hours old): return cached data
5. If stale or missing:
   - Look up origin airport code (maintain a mapping of major cities → airport codes)
   - Fetch flight data from Kiwi.com Tequila API
   - Fetch train/local transport data from Rome2Rio API
   - Compute hotel estimate from circuit's stored per-night cost
   - Save to DB as TravelEstimate
   - Return to frontend
6. Frontend calculates total trip cost:
   - `(ticket_price + flight_price + (hotel_per_night × num_nights) + local_transport) × group_size`
7. All prices converted to user's selected currency using cached exchange rates

## API Endpoints

### Get travel estimate

```
GET /api/travel/estimate?circuit_id=1&origin=London
```

Returns a TravelEstimate. Fetches live from APIs if no fresh cache exists. Query params:
- `circuit_id` (required)
- `origin` (required — city name)

### Get exchange rates

```
GET /api/travel/exchange-rates
```

Returns all cached exchange rates (USD-based). Refreshes from external API if stale (> 24h).

## Pydantic Schemas

### TravelEstimateRead

```python
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
    train_price_min: float | None
    train_price_max: float | None
    train_duration_hours: float | None
    local_transport_cost: float
    hotel_avg_per_night: float
    last_fetched_at: datetime
```

### ExchangeRateRead

```python
class ExchangeRateRead(BaseModel):
    currency_code: str
    rate_to_usd: float
    last_updated_at: datetime
```

## City-to-Airport Mapping

Maintain a dict of ~50 major cities to their primary airport IATA codes:
```python
CITY_AIRPORTS = {
    "london": "LHR",
    "new york": "JFK",
    "tokyo": "NRT",
    "sydney": "SYD",
    "paris": "CDG",
    # ... ~50 entries
}
```

Also use each circuit's `nearest_airport` field for the destination airport.

## Currency Handling

- All prices stored in USD internally
- User selects display currency:
  - Auto-detected from browser `navigator.language` locale
  - Overridable via dropdown in the UI
  - Stored in localStorage
- Frontend multiplies USD amounts by the exchange rate for display
- Exchange rates fetched from `GET /api/travel/exchange-rates`

## Frontend — Travel Tab

New tab on the track detail page alongside "Seat Map" and "Table View":

### Input Section
- Origin city text input (with autocomplete suggesting from the city-airport mapping)
- Group size selector (1-10)
- Number of nights (default 2, adjustable)

### Results Section (after search)
- **Flights**: price range (min-max), duration, stops, link to Kiwi.com for booking
- **Train** (if available): price range, duration
- **Local Transport**: estimated cost to get from airport/station to circuit
- **Hotel**: average per night × number of nights

### Total Cost Card
- Ticket cost (cheapest available from scraping, or "check ticket prices" link)
- Flight cost (using min price)
- Hotel cost (per night × nights)
- Local transport
- **Per person total**
- **Group total** (× group size)
- Currency selector dropdown

## Dependencies

- `httpx` (already installed) — for API calls to Kiwi, Rome2Rio, exchange rate APIs
- API keys needed: Kiwi.com Tequila (free), Rome2Rio (free)
- Store API keys as environment variables: `KIWI_API_KEY`, `ROME2RIO_API_KEY`

## Build Order

1. TravelEstimate + ExchangeRate models + migrations
2. City-to-airport mapping module
3. Kiwi.com flight fetcher
4. Rome2Rio transport fetcher
5. Exchange rate fetcher
6. Travel estimate API endpoint (with live fetch + caching)
7. Pydantic schemas + API tests
8. Frontend: Travel tab with origin input + results display
9. Frontend: Total cost calculator card + currency selector
10. End-to-end verification
