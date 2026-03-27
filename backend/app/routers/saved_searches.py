import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.saved_search import SavedSearch
from app.schemas.saved_search import SavedSearchCreate, SavedSearchRead

router = APIRouter(prefix="/api/saved-searches", tags=["saved-searches"])


@router.get("", response_model=list[SavedSearchRead])
def list_saved_searches(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(SavedSearch).filter(SavedSearch.user_id == user.id).all()


@router.post("", response_model=SavedSearchRead, status_code=201)
def create_saved_search(
    req: SavedSearchCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search = SavedSearch(
        user_id=user.id,
        search_type=req.search_type,
        name=req.name,
        data=json.dumps(req.data),
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return search


@router.delete("/{search_id}", status_code=204)
def delete_saved_search(
    search_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search = db.get(SavedSearch, search_id)
    if not search or search.user_id != user.id:
        raise HTTPException(status_code=404, detail="Saved search not found")
    db.delete(search)
    db.commit()
