from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.price_alert import PriceAlert
from app.schemas.price_alert import PriceAlertCreate, PriceAlertRead

router = APIRouter(prefix="/api/price-alerts", tags=["price-alerts"])


@router.get("", response_model=list[PriceAlertRead])
def list_price_alerts(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(PriceAlert).filter(PriceAlert.user_id == user.id).all()


@router.post("", response_model=PriceAlertRead, status_code=201)
def create_price_alert(
    req: PriceAlertCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = PriceAlert(
        user_id=user.id,
        circuit_id=req.circuit_id,
        seat_section_id=req.seat_section_id,
        target_price=req.target_price,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=204)
def delete_price_alert(
    alert_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = db.get(PriceAlert, alert_id)
    if not alert or alert.user_id != user.id:
        raise HTTPException(status_code=404, detail="Price alert not found")
    db.delete(alert)
    db.commit()
