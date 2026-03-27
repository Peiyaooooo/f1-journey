"""Google Calendar OAuth and event creation endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.models.google_calendar_token import GoogleCalendarToken
from app.models.race_event import RaceEvent
from app.models.user import User

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def _make_flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri,
    )


@router.get("/auth-url")
def get_auth_url(user: User = Depends(get_current_user)):
    """Return the Google OAuth authorization URL for the current user."""
    if not settings.google_client_id:
        raise HTTPException(status_code=400, detail="Google Calendar not configured")
    flow = _make_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", state=str(user.id))
    return {"auth_url": auth_url}


@router.get("/callback")
def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    """Exchange the OAuth authorization code for tokens and store them."""
    try:
        user_id = int(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    flow = _make_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    token_expiry = creds.expiry or datetime.now(timezone.utc)

    existing = db.query(GoogleCalendarToken).filter(
        GoogleCalendarToken.user_id == user_id
    ).first()

    if existing:
        existing.access_token = creds.token
        existing.refresh_token = creds.refresh_token or existing.refresh_token
        existing.token_expiry = token_expiry
    else:
        db_token = GoogleCalendarToken(
            user_id=user_id,
            access_token=creds.token,
            refresh_token=creds.refresh_token or "",
            token_expiry=token_expiry,
        )
        db.add(db_token)

    db.commit()
    return {"message": "Google Calendar connected successfully"}


class AddEventRequest(BaseModel):
    race_event_id: int


@router.post("/add-event")
def add_event(
    req: AddEventRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Google Calendar event for a race event."""
    # Get the stored Google token for the user
    token_row = db.query(GoogleCalendarToken).filter(
        GoogleCalendarToken.user_id == user.id
    ).first()
    if not token_row:
        raise HTTPException(
            status_code=400,
            detail="Google Calendar not connected. Please authorize via /api/calendar/auth-url",
        )

    # Fetch the race event (with circuit loaded via relationship)
    race_event = db.get(RaceEvent, req.race_event_id)
    if not race_event:
        raise HTTPException(status_code=404, detail="Race event not found")

    circuit = race_event.circuit

    # Build Google credentials
    creds = Credentials(
        token=token_row.access_token,
        refresh_token=token_row.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES,
    )

    # Build the calendar event body
    race_date = race_event.race_date
    start_datetime = f"{race_date}T13:00:00"
    end_datetime = f"{race_date}T16:00:00"
    location = f"{circuit.city}, {circuit.country}"

    event_body = {
        "summary": race_event.race_name,
        "location": location,
        "description": (
            f"F1 Race: {race_event.race_name}\n"
            f"Circuit: {circuit.name}\n"
            f"Season: {race_event.season_year}\n"
            f"Track length: {circuit.track_length_km} km\n"
        ),
        "start": {
            "dateTime": start_datetime,
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": "UTC",
        },
    }

    try:
        service = build("calendar", "v3", credentials=creds)
        created_event = service.events().insert(
            calendarId="primary", body=event_body
        ).execute()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to create Google Calendar event: {e}",
        )

    # Update stored token in case it was refreshed
    if creds.token != token_row.access_token:
        token_row.access_token = creds.token
        if creds.expiry:
            token_row.token_expiry = creds.expiry
        db.commit()

    return {
        "message": "Event added to Google Calendar",
        "event_id": created_event.get("id"),
        "event_link": created_event.get("htmlLink"),
    }
