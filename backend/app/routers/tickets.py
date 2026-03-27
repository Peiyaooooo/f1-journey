from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ticket_listing import TicketListing
from app.schemas.ticket_listing import TicketListingRead

router = APIRouter(tags=["tickets"])


@router.get("/api/circuits/{circuit_id}/tickets", response_model=list[TicketListingRead])
def list_circuit_tickets(
    circuit_id: int,
    source_site: str | None = None,
    ticket_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = "price_asc",
    db: Session = Depends(get_db),
):
    query = db.query(TicketListing).filter(
        TicketListing.circuit_id == circuit_id,
        TicketListing.is_available == True,
    )
    if source_site:
        query = query.filter(TicketListing.source_site == source_site)
    if ticket_type:
        query = query.filter(TicketListing.ticket_type == ticket_type)
    if min_price is not None:
        query = query.filter(TicketListing.price >= min_price)
    if max_price is not None:
        query = query.filter(TicketListing.price <= max_price)

    if sort == "price_desc":
        query = query.order_by(TicketListing.price.desc())
    else:
        query = query.order_by(TicketListing.price.asc())

    return query.all()


@router.get("/api/sections/{section_id}/tickets", response_model=list[TicketListingRead])
def list_section_tickets(section_id: int, db: Session = Depends(get_db)):
    return (
        db.query(TicketListing)
        .filter(TicketListing.seat_section_id == section_id, TicketListing.is_available == True)
        .order_by(TicketListing.price.asc())
        .all()
    )


@router.get("/api/circuits/{circuit_id}/tickets/unmatched", response_model=list[TicketListingRead])
def list_unmatched_tickets(circuit_id: int, db: Session = Depends(get_db)):
    return (
        db.query(TicketListing)
        .filter(
            TicketListing.circuit_id == circuit_id,
            TicketListing.seat_section_id == None,
            TicketListing.is_available == True,
        )
        .order_by(TicketListing.price.asc())
        .all()
    )
