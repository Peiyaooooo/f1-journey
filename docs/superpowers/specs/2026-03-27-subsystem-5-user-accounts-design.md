# Subsystem 5: User Accounts + Extras — Design Spec

## Overview

Add user authentication, saved searches, Google Calendar integration, and email price alerts. This is the final subsystem before public deployment.

## Auth

### Registration + Login
- Email + password (bcrypt hashed)
- JWT tokens: short-lived access token (15 min) + long-lived refresh token (7 days)
- Access token sent in `Authorization: Bearer <token>` header
- Refresh token sent as httpOnly cookie or in body

### User Model
- `id` (PK)
- `email` (unique)
- `hashed_password`
- `home_city` (nullable)
- `preferred_currency` (default "USD")
- `created_at`
- `last_login` (nullable)

### Dependencies
- `passlib[bcrypt]` for password hashing
- `python-jose[cryptography]` for JWT encoding/decoding

## Saved Searches

### SavedSearch Model
- `id` (PK)
- `user_id` (FK → users.id)
- `search_type` — "filters" or "trip"
- `name` (user-given label)
- `data` (JSON — stores the filter/trip config)
- `created_at`

### Filter search data format:
```json
{
  "continent": "Europe",
  "track_type": "permanent",
  "min_overtaking": 5,
  "max_rain": 40
}
```

### Trip search data format:
```json
{
  "circuit_id": 9,
  "circuit_name": "Silverstone Circuit",
  "origin_city": "london",
  "group_size": 2,
  "nights": 2
}
```

### API Endpoints
- `GET /api/saved-searches` — list user's saved searches (requires auth)
- `POST /api/saved-searches` — create a saved search
- `DELETE /api/saved-searches/{id}` — delete a saved search

## Google Calendar Integration

### How It Works
1. User clicks "Add to Google Calendar" on a race event
2. Frontend redirects to Google OAuth consent screen
3. After consent, Google returns an auth code to our callback URL
4. Backend exchanges code for access token
5. Backend creates a Google Calendar event using the Calendar API
6. Stores the Google OAuth token for future use (refresh token)

### GoogleCalendarToken Model
- `id` (PK)
- `user_id` (FK → users.id, unique)
- `access_token` (encrypted)
- `refresh_token` (encrypted)
- `token_expiry` (datetime)

### API Endpoints
- `GET /api/calendar/auth-url` — returns Google OAuth authorization URL
- `GET /api/calendar/callback?code=XXX` — OAuth callback, exchanges code for token
- `POST /api/calendar/add-event` — creates a calendar event for a race
  - Body: `{ "race_event_id": 1 }`
  - Uses stored Google token to create event

### Dependencies
- `google-auth` + `google-api-python-client` for Google Calendar API
- Google Cloud project with Calendar API enabled
- OAuth 2.0 credentials (client_id + client_secret)
- Config: `F1_GOOGLE_CLIENT_ID`, `F1_GOOGLE_CLIENT_SECRET`, `F1_GOOGLE_REDIRECT_URI`

## Price Alerts

### PriceAlert Model
- `id` (PK)
- `user_id` (FK → users.id)
- `circuit_id` (FK → circuits.id)
- `seat_section_id` (FK → seat_sections.id, nullable — null means any section)
- `target_price` (float, USD)
- `is_active` (bool, default True)
- `triggered_at` (datetime, nullable — set when alert fires)
- `created_at`

### How It Works
1. User sets a price alert: "Notify me when Silverstone Village A tickets drop below $400"
2. Background job runs after each scraping cycle
3. Checks all active alerts against current ticket prices
4. If a ticket price ≤ target_price: send email, set triggered_at, deactivate alert

### Email
- Use Resend (resend.com) — free tier: 3,000 emails/month, no SMTP setup
- Simple transactional email: "Price alert! {section} at {circuit} is now ${price} on {source}"
- Config: `F1_RESEND_API_KEY`

### API Endpoints
- `GET /api/price-alerts` — list user's active alerts (requires auth)
- `POST /api/price-alerts` — create an alert
  - Body: `{ "circuit_id": 9, "seat_section_id": 5, "target_price": 400 }`
- `DELETE /api/price-alerts/{id}` — delete an alert

## Frontend Pages

### `/login`
- Email + password form
- "Don't have an account? Register" link
- On success: store JWT in localStorage, redirect to dashboard

### `/register`
- Email + password + confirm password form
- Optional: home city, preferred currency
- On success: auto-login, redirect to dashboard

### `/dashboard`
- Requires auth (redirect to login if not authenticated)
- Three sections:
  1. **Saved Searches** — list with name, type badge, delete button, "Load" button that navigates to explore/track page with filters applied
  2. **Price Alerts** — list with circuit, section, target price, status (active/triggered), delete button, "Set new alert" button
  3. **Calendar** — "Connect Google Calendar" button if not connected, status if connected

### `/settings`
- Profile form: home city, preferred currency
- Change password
- Connected accounts (Google Calendar status)
- Delete account

### Existing Page Modifications
- **Navbar**: show "Login" or user email + "Dashboard" based on auth state
- **Explore page**: "Save this search" button when filters are applied (requires auth)
- **Track detail Travel tab**: "Save this trip" button (requires auth)
- **Section sidebar**: "Set price alert" button on ticket listings (requires auth)
- **Race event card**: "Add to Google Calendar" button (requires auth + Google connected)

## Auth State Management (Frontend)
- Store JWT access token in localStorage
- Create an auth context provider wrapping the app
- `useAuth()` hook returns: `user`, `isAuthenticated`, `login()`, `logout()`, `register()`
- Protected pages check auth state, redirect to login if needed

## Config Additions
```python
# backend/app/config.py
jwt_secret: str = "change-me-in-production"
jwt_algorithm: str = "HS256"
google_client_id: str = ""
google_client_secret: str = ""
google_redirect_uri: str = "http://localhost:3000/api/calendar/callback"
resend_api_key: str = ""
```

## Build Order

1. User model + auth endpoints (register, login, refresh) + JWT middleware
2. Auth context + login/register pages (frontend)
3. SavedSearch model + API endpoints
4. Dashboard page + saved search UI
5. Google Calendar OAuth + add event endpoint
6. Calendar UI on dashboard + "Add to Calendar" buttons
7. PriceAlert model + API endpoints + email sending
8. Price alert UI on dashboard + "Set alert" buttons
9. Navbar auth state + protected routes
10. Settings page
11. End-to-end verification
