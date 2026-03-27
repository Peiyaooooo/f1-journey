from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.seat_section import SeatSection
from app.schemas.seat_section import SeatSectionRead, SeatSectionList

router = APIRouter(tags=["sections"])


@router.get("/api/circuits/{circuit_id}/sections", response_model=list[SeatSectionList])
def list_sections(
    circuit_id: int,
    section_type: str | None = None,
    has_roof: bool | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(SeatSection).filter(SeatSection.circuit_id == circuit_id)
    if section_type:
        query = query.filter(SeatSection.section_type == section_type)
    if has_roof is not None:
        query = query.filter(SeatSection.has_roof == has_roof)
    return query.order_by(SeatSection.name).all()


@router.get("/api/sections/{section_id}", response_model=SeatSectionRead)
def get_section(section_id: int, db: Session = Depends(get_db)):
    section = db.get(SeatSection, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section
