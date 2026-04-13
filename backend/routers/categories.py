from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import Category, Subcategory
from schemas import CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = (
        db.query(Category)
        .options(joinedload(Category.subcategories))
        .order_by(Category.order_index)
        .all()
    )
    return [CategoryResponse.from_orm(c) for c in categories]
