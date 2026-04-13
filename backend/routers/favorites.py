from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import Favorite, MasterProfile, User, Subcategory, Category
from schemas import MasterCardResponse, MessageResponse
from routers.auth import get_current_user_from_header
from routers.masters import build_master_card

router = APIRouter(prefix="/api/favorites", tags=["Favorites"])


@router.get("", response_model=List[MasterCardResponse])
def get_favorites(
    authorization: str = Header(""),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_header(authorization, db)
    favorites = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id)
        .all()
    )
    master_ids = [f.master_id for f in favorites]
    if not master_ids:
        return []

    profiles = (
        db.query(MasterProfile)
        .options(
            joinedload(MasterProfile.user),
            joinedload(MasterProfile.subcategory).joinedload(Subcategory.category),
        )
        .filter(MasterProfile.id.in_(master_ids))
        .all()
    )
    return [build_master_card(p) for p in profiles]


@router.post("/{master_id}", response_model=MessageResponse)
def toggle_favorite(
    master_id: int,
    authorization: str = Header(""),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_header(authorization, db)

    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.master_id == master_id)
        .first()
    )

    if existing:
        db.delete(existing)
        db.commit()
        return MessageResponse(message="Removed from favorites")
    else:
        profile = db.query(MasterProfile).filter(MasterProfile.id == master_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Master not found")
        fav = Favorite(user_id=user.id, master_id=master_id)
        db.add(fav)
        db.commit()
        return MessageResponse(message="Added to favorites")
