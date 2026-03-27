from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.circuit import Circuit
from app.models.race_event import RaceEvent
from app.schemas.race_event import RaceEventRead, RaceEventWithCircuit

router = APIRouter(prefix="/api/race-events", tags=["race-events"])


@router.get("", response_model=list[RaceEventRead])
def list_race_events(
    season: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(RaceEvent)
    if season:
        query = query.filter(RaceEvent.season_year == season)
    if status:
        query = query.filter(RaceEvent.status == status)
    return query.order_by(RaceEvent.race_date).all()


@router.get("/{event_id}", response_model=RaceEventWithCircuit)
def get_race_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(RaceEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Race event not found")
    circuit = db.get(Circuit, event.circuit_id)
    return RaceEventWithCircuit(
        id=event.id,
        circuit_id=event.circuit_id,
        season_year=event.season_year,
        race_name=event.race_name,
        race_date=event.race_date,
        sprint_weekend=event.sprint_weekend,
        status=event.status,
        total_overtakes=event.total_overtakes,
        weather_actual=event.weather_actual,
        circuit_name=circuit.name,
        circuit_country=circuit.country,
        continent=circuit.continent,
    )
