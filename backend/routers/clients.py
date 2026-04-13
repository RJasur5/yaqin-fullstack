from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import User, ClientReview, MasterProfile
from schemas import ClientDetailResponse, ClientReviewResponse

router = APIRouter(prefix="/api/clients", tags=["Clients"])

@router.get("/{client_id}", response_model=ClientDetailResponse)
def get_client_profile(
    client_id: int,
    db: Session = Depends(get_db)
):
    client = db.query(User).filter(User.id == client_id, User.role == "client").first()
    # Note: Masters can also act as clients, so maybe don't filter by role == "client" strictly, just get by ID
    client = db.query(User).filter(User.id == client_id).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    reviews = db.query(ClientReview).options(
        joinedload(ClientReview.master).joinedload(MasterProfile.user)
    ).filter(ClientReview.client_id == client_id).order_by(ClientReview.created_at.desc()).all()
    
    # We map to ClientReviewResponse manually
    review_responses = []
    for r in reviews:
        review_responses.append(ClientReviewResponse(
            id=r.id,
            client_id=r.client_id,
            master_id=r.master_id,
            master_name=r.master.user.name,
            master_avatar=r.master.user.avatar,
            rating=r.rating,
            comment=r.comment,
            created_at=r.created_at
        ))
        
    resp = ClientDetailResponse(
        id=client.id,
        name=client.name,
        phone=client.phone,
        role=client.role,
        avatar=client.avatar,
        city=client.city,
        lang=client.lang,
        client_rating=client.client_rating,
        client_reviews_count=client.client_reviews_count,
        is_blocked=client.is_blocked,
        created_at=client.created_at,
        reviews=review_responses
    )
    return resp
