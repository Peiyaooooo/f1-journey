from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.circuit import Circuit
from app.schemas.circuit import CircuitRead, CircuitList

router = APIRouter(prefix="/api/circuits", tags=["circuits"])


@router.get("", response_model=list[CircuitList])
def list_circuits(
    continent: str | None = None,
    track_type: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Circuit)
    if continent:
        query = query.filter(Circuit.continent == continent)
    if track_type:
        query = query.filter(Circuit.track_type == track_type)
    return query.order_by(Circuit.name).all()


@router.get("/{circuit_id}", response_model=CircuitRead)
def get_circuit(circuit_id: int, db: Session = Depends(get_db)):
    circuit = db.get(Circuit, circuit_id)
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    return circuit
