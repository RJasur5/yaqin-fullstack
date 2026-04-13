from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, AppReview
from schemas import AppReviewCreate, AppReviewResponse, MessageResponse
from routers.auth import get_current_user_from_header

router = APIRouter(prefix="/api/app-reviews", tags=["App Reviews"])

@router.get("/", response_model=List[AppReviewResponse])
def get_app_reviews(db: Session = Depends(get_db)):
    """Get all app reviews, sorted by newest first."""
    return db.query(AppReview).order_by(AppReview.created_at.desc()).all()

@router.post("/")
def create_app_review(
    data: AppReviewCreate,
    user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """Leave a review for the app."""
    try:
        review = AppReview(
            user_id=user.id,
            rating=data.rating,
            comment=data.comment
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return {"status": "ok", "message": "Review added"}
    except Exception as e:
        import traceback
        error_msg = f"ERROR creating app review: {e}\n{traceback.format_exc()}"
        print(error_msg)
        with open("error_log.txt", "a") as f:
            f.write(error_msg + "\n")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
