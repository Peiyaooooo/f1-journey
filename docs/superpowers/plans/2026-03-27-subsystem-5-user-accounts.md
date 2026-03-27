# Subsystem 5: User Accounts + Extras — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add user authentication, saved searches, Google Calendar integration, and email price alerts.

**Architecture:** JWT auth with bcrypt password hashing. User, SavedSearch, PriceAlert, GoogleCalendarToken models. Frontend auth context with protected routes. Google Calendar OAuth for event creation. Resend for transactional emails.

**Tech Stack:** PyJWT, passlib[bcrypt], google-auth, google-api-python-client, resend (backend). Next.js client components, React context for auth state (frontend).

---

## File Structure

### Backend
```
backend/app/
├── config.py                         # Modify: add JWT, Google, Resend config
├── models/
│   ├── __init__.py                   # Modify: add new model exports
│   ├── user.py                       # Create: User model
│   ├── saved_search.py               # Create: SavedSearch model
│   ├── price_alert.py                # Create: PriceAlert model
│   └── google_calendar_token.py      # Create: GoogleCalendarToken model
├── schemas/
│   ├── __init__.py                   # Modify: add new schema exports
│   ├── auth.py                       # Create: register/login/token schemas
│   ├── saved_search.py               # Create: SavedSearch schemas
│   └── price_alert.py                # Create: PriceAlert schemas
├── routers/
│   ├── auth.py                       # Create: register, login, refresh endpoints
│   ├── saved_searches.py             # Create: CRUD endpoints
│   ├── price_alerts.py               # Create: CRUD endpoints
│   └── calendar.py                   # Create: Google Calendar OAuth + add event
├── main.py                           # Modify: register new routers
├── auth/
│   ├── __init__.py
│   ├── jwt.py                        # Create: JWT create/verify helpers
│   ├── passwords.py                  # Create: hash/verify password helpers
│   └── dependencies.py               # Create: get_current_user dependency
└── alerts/
    ├── __init__.py
    └── checker.py                    # Create: price alert checker + email sender
backend/tests/
├── test_auth_api.py                  # Create
├── test_saved_searches_api.py        # Create
├── test_price_alerts_api.py          # Create
```

### Frontend
```
frontend/src/
├── lib/
│   ├── api.ts                        # Modify: add auth, saved search, alert types + functions
│   └── auth-context.tsx              # Create: React auth context provider
├── components/
│   ├── Navbar.tsx                    # Modify: show auth state
│   ├── ProtectedRoute.tsx            # Create: auth guard wrapper
│   ├── SavedSearchCard.tsx           # Create: saved search display card
│   └── PriceAlertCard.tsx            # Create: price alert display card
└── app/
    ├── login/page.tsx                # Create
    ├── register/page.tsx             # Create
    ├── dashboard/page.tsx            # Create
    ├── settings/page.tsx             # Create
    └── layout.tsx                    # Modify: wrap with AuthProvider
```

---

## Task 1: Dependencies + Config

**Files:**
- Modify: `backend/pyproject.toml`
- Modify: `backend/app/config.py`

- [ ] **Step 1: Add auth dependencies**

Add to `backend/pyproject.toml` dependencies:
```toml
    "PyJWT>=2.8.0",
    "passlib[bcrypt]>=1.7.0",
    "google-auth>=2.0.0",
    "google-api-python-client>=2.0.0",
    "resend>=2.0.0",
```

Install: `cd backend && .venv/bin/pip install -e ".[dev]"`

- [ ] **Step 2: Add config settings**

Add to `backend/app/config.py` Settings class:
```python
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_days: int = 7
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/calendar/callback"
    resend_api_key: str = ""
```

- [ ] **Step 3: Commit**

```bash
git add backend/pyproject.toml backend/app/config.py
git commit -m "feat: add auth, Google Calendar, and email dependencies + config"
```

---

## Task 2: User Model + Auth Helpers

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/auth/__init__.py`
- Create: `backend/app/auth/passwords.py`
- Create: `backend/app/auth/jwt.py`
- Create: `backend/app/auth/dependencies.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/tests/test_auth_api.py`

- [ ] **Step 1: Create User model**

```python
# backend/app/models/user.py
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    home_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_currency: Mapped[str] = mapped_column(String(10), default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
```

Update `backend/app/models/__init__.py` to export User.

- [ ] **Step 2: Create password helpers**

```python
# backend/app/auth/__init__.py
```

```python
# backend/app/auth/passwords.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

- [ ] **Step 3: Create JWT helpers**

```python
# backend/app/auth/jwt.py
from datetime import datetime, timedelta
import jwt
from app.config import settings

def create_access_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_access_expire_minutes),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def create_refresh_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(days=settings.jwt_refresh_expire_days),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

- [ ] **Step 4: Create auth dependency**

```python
# backend/app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.jwt import decode_token
from app.models.user import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = int(payload["sub"])
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/user.py backend/app/models/__init__.py backend/app/auth/
git commit -m "feat: add User model, password hashing, JWT helpers, and auth dependency"
```

---

## Task 3: Auth API Endpoints + Tests

**Files:**
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/routers/auth.py`
- Modify: `backend/app/schemas/__init__.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_auth_api.py`

- [ ] **Step 1: Create auth schemas**

```python
# backend/app/schemas/auth.py
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: str
    password: str
    home_city: str | None = None
    preferred_currency: str = "USD"

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserRead(BaseModel):
    id: int
    email: str
    home_city: str | None
    preferred_currency: str
    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Create auth router**

```python
# backend/app/routers/auth.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserRead
from app.auth.passwords import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        home_city=req.home_city,
        preferred_currency=req.preferred_currency,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(
        access_token=create_access_token(user.id, user.email),
        refresh_token=create_refresh_token(user.id),
    )

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user.last_login = datetime.utcnow()
    db.commit()
    return TokenResponse(
        access_token=create_access_token(user.id, user.email),
        refresh_token=create_refresh_token(user.id),
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = int(payload["sub"])
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return TokenResponse(
        access_token=create_access_token(user.id, user.email),
        refresh_token=create_refresh_token(user.id),
    )

@router.get("/me", response_model=UserRead)
def get_me(user: User = Depends(get_current_user)):
    return user
```

Register in main.py. Update schemas __init__.py.

- [ ] **Step 3: Write auth tests**

Test: register, login, login wrong password, duplicate email, get /me with token, refresh token. Use StaticPool pattern.

- [ ] **Step 4: Run tests, commit**

```bash
git add backend/app/schemas/auth.py backend/app/routers/auth.py backend/app/main.py backend/app/schemas/__init__.py backend/tests/test_auth_api.py
git commit -m "feat: add auth endpoints (register, login, refresh, me)"
```

---

## Task 4: SavedSearch + PriceAlert Models + Migration

**Files:**
- Create: `backend/app/models/saved_search.py`
- Create: `backend/app/models/price_alert.py`
- Create: `backend/app/models/google_calendar_token.py`
- Modify: `backend/app/models/__init__.py`
- Create: Alembic migration

- [ ] **Step 1: Create models**

SavedSearch: id, user_id (FK), search_type ("filters"/"trip"), name, data (Text/JSON), created_at.
PriceAlert: id, user_id (FK), circuit_id (FK), seat_section_id (FK, nullable), target_price (float), is_active (bool), triggered_at (datetime, nullable), created_at.
GoogleCalendarToken: id, user_id (FK, unique), access_token, refresh_token, token_expiry.

- [ ] **Step 2: Create migration**

Hand-write migration for: users, saved_searches, price_alerts, google_calendar_tokens tables.

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/ backend/alembic/
git commit -m "feat: add SavedSearch, PriceAlert, GoogleCalendarToken models + migration"
```

---

## Task 5: SavedSearch + PriceAlert API Endpoints

**Files:**
- Create: `backend/app/schemas/saved_search.py`
- Create: `backend/app/schemas/price_alert.py`
- Create: `backend/app/routers/saved_searches.py`
- Create: `backend/app/routers/price_alerts.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_saved_searches_api.py`
- Create: `backend/tests/test_price_alerts_api.py`

- [ ] **Step 1: Create schemas**

SavedSearch schemas: SavedSearchCreate (search_type, name, data as dict), SavedSearchRead.
PriceAlert schemas: PriceAlertCreate (circuit_id, seat_section_id, target_price), PriceAlertRead.

- [ ] **Step 2: Create routers**

saved_searches.py: GET /api/saved-searches (list, requires auth), POST (create), DELETE /{id}.
price_alerts.py: GET /api/price-alerts (list, requires auth), POST (create), DELETE /{id}.

Both use `get_current_user` dependency. Filter by current user.

- [ ] **Step 3: Write tests + register routers**

- [ ] **Step 4: Run all tests, commit**

```bash
git add backend/app/schemas/ backend/app/routers/ backend/app/main.py backend/tests/
git commit -m "feat: add saved searches and price alerts CRUD endpoints"
```

---

## Task 6: Google Calendar Integration

**Files:**
- Create: `backend/app/routers/calendar.py`

- [ ] **Step 1: Create calendar router**

```python
# Endpoints:
# GET /api/calendar/auth-url — returns Google OAuth URL
# GET /api/calendar/callback?code=XXX — exchanges code for token, stores it
# POST /api/calendar/add-event — creates calendar event for a race
```

Uses `google-auth` and `google-api-python-client`. Stores tokens in GoogleCalendarToken table.

The add-event endpoint:
- Takes `{ "race_event_id": 1 }`
- Fetches the race event + circuit info
- Creates a Google Calendar event with: summary (race name), location (circuit city, country), start/end datetime, description

- [ ] **Step 2: Register router, commit**

```bash
git add backend/app/routers/calendar.py backend/app/main.py
git commit -m "feat: add Google Calendar OAuth and event creation endpoints"
```

---

## Task 7: Price Alert Checker + Email

**Files:**
- Create: `backend/app/alerts/__init__.py`
- Create: `backend/app/alerts/checker.py`

- [ ] **Step 1: Create alert checker**

Function that:
1. Queries all active price alerts
2. For each alert, checks if any ticket listing for that circuit (and section if specified) has price <= target_price
3. If match found: send email via Resend, mark alert as triggered

Can be called after scraping runs, or manually via: `python -m app.alerts.checker`

Uses Resend API:
```python
import resend
resend.api_key = settings.resend_api_key
resend.Emails.send({
    "from": "F1 Journey <alerts@f1journey.com>",
    "to": [user.email],
    "subject": f"Price Alert: {section_name} at {circuit_name} is now ${price}",
    "text": f"...",
})
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/alerts/
git commit -m "feat: add price alert checker with Resend email notifications"
```

---

## Task 8: Frontend — Auth Context + Login/Register

**Files:**
- Create: `frontend/src/lib/auth-context.tsx`
- Create: `frontend/src/app/login/page.tsx`
- Create: `frontend/src/app/register/page.tsx`
- Modify: `frontend/src/app/layout.tsx`
- Modify: `frontend/src/lib/api.ts`

- [ ] **Step 1: Add auth types and functions to api.ts**

Add: User, TokenResponse types. Functions: register(), login(), refreshToken(), getMe(), createSavedSearch(), getSavedSearches(), deleteSavedSearch(), createPriceAlert(), getPriceAlerts(), deletePriceAlert(), getCalendarAuthUrl(), addCalendarEvent().

All authenticated requests include `Authorization: Bearer <token>` header.

- [ ] **Step 2: Create auth context**

React context providing: user, isAuthenticated, login(), logout(), register(). Stores token in localStorage. Checks token on mount. Wraps app in layout.tsx.

- [ ] **Step 3: Create login page**

Email + password form. On success: call login(), store token, redirect to dashboard.

- [ ] **Step 4: Create register page**

Email + password + confirm password + optional home city + currency. On success: auto-login, redirect to dashboard.

- [ ] **Step 5: Verify build, commit**

```bash
git add frontend/src/
git commit -m "feat: add auth context, login and register pages"
```

---

## Task 9: Frontend — Dashboard

**Files:**
- Create: `frontend/src/components/SavedSearchCard.tsx`
- Create: `frontend/src/components/PriceAlertCard.tsx`
- Create: `frontend/src/components/ProtectedRoute.tsx`
- Create: `frontend/src/app/dashboard/page.tsx`

- [ ] **Step 1: Create ProtectedRoute**

Client component that checks `useAuth()`. If not authenticated, redirect to /login. Otherwise render children.

- [ ] **Step 2: Create SavedSearchCard**

Shows: name, type badge (filters/trip), summary of saved data, delete button, "Load" button.

- [ ] **Step 3: Create PriceAlertCard**

Shows: circuit name, section name (or "Any section"), target price, status (active/triggered), delete button.

- [ ] **Step 4: Create dashboard page**

Three sections: Saved Searches, Price Alerts, Google Calendar connection. Protected route.

- [ ] **Step 5: Verify build, commit**

```bash
git add frontend/src/
git commit -m "feat: add dashboard with saved searches, price alerts, and calendar status"
```

---

## Task 10: Frontend — Navbar Auth + Save/Alert Buttons

**Files:**
- Modify: `frontend/src/components/Navbar.tsx`
- Modify: `frontend/src/components/SectionSidebar.tsx`
- Modify: `frontend/src/components/ExploreClient.tsx`
- Modify: `frontend/src/components/TravelTab.tsx`

- [ ] **Step 1: Update Navbar**

If authenticated: show user email + "Dashboard" link + "Logout" button.
If not: show "Login" link.

- [ ] **Step 2: Add "Save Search" to Explore page**

When filters are applied, show a "Save this search" button. On click: prompt for name, call createSavedSearch(). Requires auth.

- [ ] **Step 3: Add "Save Trip" to Travel tab**

After getting travel results, show "Save this trip" button. Same pattern.

- [ ] **Step 4: Add "Set Price Alert" to section sidebar**

On each ticket listing in the sidebar, add a small "Set alert" button. Opens a mini-form with target price input. Calls createPriceAlert().

- [ ] **Step 5: Add "Add to Calendar" on race events**

On the track detail page race event card, show "Add to Google Calendar" button if authenticated + Google connected.

- [ ] **Step 6: Verify build, commit**

```bash
git add frontend/src/
git commit -m "feat: add save search, price alert, and calendar buttons across UI"
```

---

## Task 11: Settings Page

**Files:**
- Create: `frontend/src/app/settings/page.tsx`

- [ ] **Step 1: Create settings page**

Protected route. Form with: home city, preferred currency, change password. Save button calls API.

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/settings/
git commit -m "feat: add user settings page"
```

---

## Task 12: End-to-End Verification

- [ ] **Step 1: Re-seed database**

```bash
cd backend && rm -f f1journey.db && .venv/bin/python -m app.seed.seed_data
```

- [ ] **Step 2: Run all backend tests**

```bash
cd backend && .venv/bin/python -m pytest tests/ -v
```

- [ ] **Step 3: Verify build**

```bash
cd frontend && npx next build
```

- [ ] **Step 4: Manual verification**

- Register a new account
- Login
- Save a search from Explore page
- Save a trip from Travel tab
- Set a price alert from section sidebar
- View everything on Dashboard
- Logout and verify protected routes redirect to login

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete subsystem 5 — user accounts, saved searches, calendar, price alerts"
```
