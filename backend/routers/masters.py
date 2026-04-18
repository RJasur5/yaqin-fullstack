from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import timezone

from database import get_db
from models import User, MasterProfile, Subcategory, Category, Review
from schemas import (
    MasterCardResponse, MasterDetailResponse, MasterProfileCreate,
    MasterProfileUpdate, ReviewCreate, ReviewResponse, MessageResponse
)
from routers.auth import get_current_user_from_header
from routers.orders import check_subscription
from utils.security import mask_phone

router = APIRouter(prefix="/api/masters", tags=["Masters"])


def build_master_card(profile: MasterProfile, is_subscribed: bool = True) -> MasterCardResponse:
    res = MasterCardResponse(
        id=profile.id,
        user_id=profile.user_id,
        user_name=profile.user.name,
        user_avatar=profile.user.avatar,
        subcategory_id=profile.subcategory_id,
        subcategory_name_ru=profile.subcategory.name_ru,
        subcategory_name_uz=profile.subcategory.name_uz,
        category_name_ru=profile.subcategory.category.name_ru,
        category_name_uz=profile.subcategory.category.name_uz,
        description=profile.description,
        experience_years=profile.experience_years,
        hourly_rate=profile.hourly_rate,
        city=profile.city,
        district=profile.district,
        address=profile.address,
        skills=profile.skills,
        rating=profile.rating,
        reviews_count=profile.reviews_count,
        is_available=profile.is_available,
        is_blocked=profile.is_blocked,
        portfolio_images=profile.portfolio_images,
        can_contact=is_subscribed
    )
    if not is_subscribed:
        from utils.security import filter_description
        res.description = filter_description(res.description or "")
        
    return res


@router.get("", response_model=List[MasterCardResponse])
def get_masters(
    category_id: Optional[int] = Query(None),
    subcategory_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None),
    sort_by: Optional[str] = Query("rating"),  # "rating", "experience", "price"
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    authorization: str = Header(""),
    db: Session = Depends(get_db),
):
    try:
        user = get_current_user_from_header(authorization, db)
        is_subscribed = check_subscription(user.id, db)
    except:
        is_subscribed = False

    query = (
        db.query(MasterProfile)
        .join(User)
        .join(Subcategory)
        .join(Category)
        .options(
            joinedload(MasterProfile.user),
            joinedload(MasterProfile.subcategory).joinedload(Subcategory.category),
        )
        .filter(MasterProfile.is_blocked == False)
    )

    if category_id:
        query = query.filter(Subcategory.category_id == category_id)
    if subcategory_id:
        query = query.filter(MasterProfile.subcategory_id == subcategory_id)
    if city:
        query = query.filter(MasterProfile.city.ilike(f"%{city}%"))
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (MasterProfile.description.ilike(f"%{search}%"))
        )
    if min_rating:
        query = query.filter(MasterProfile.rating >= min_rating)

    if sort_by == "rating":
        query = query.order_by(MasterProfile.rating.desc())
    elif sort_by == "experience":
        query = query.order_by(MasterProfile.experience_years.desc())
    elif sort_by == "price":
        query = query.order_by(MasterProfile.hourly_rate.asc())

    profiles = query.offset(offset).limit(limit).all()
    return [build_master_card(p, is_subscribed=is_subscribed) for p in profiles]


@router.get("/{master_id}", response_model=MasterDetailResponse)
def get_master_detail(
    master_id: int, 
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    try:
        user = get_current_user_from_header(authorization, db)
        is_subscribed = check_subscription(user.id, db)
    except:
        is_subscribed = False
    profile = (
        db.query(MasterProfile)
        .options(
            joinedload(MasterProfile.user),
            joinedload(MasterProfile.subcategory).joinedload(Subcategory.category),
            joinedload(MasterProfile.reviews).joinedload(Review.client),
        )
        .filter(MasterProfile.id == master_id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Master not found")

    card = build_master_card(profile, is_subscribed=is_subscribed)
    reviews = []
    for r in profile.reviews:
        created_at = r.created_at
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
            
        reviews.append(ReviewResponse(
            id=r.id,
            master_id=r.master_id,
            client_id=r.client_id,
            client_name=r.client.name,
            client_avatar=r.client.avatar,
            rating=r.rating,
            comment=r.comment,
            created_at=created_at,
        ))

    
    phone = profile.user.phone
    if not is_subscribed:
        phone = mask_phone(phone)

    return MasterDetailResponse(
        **card.dict(),
        reviews=reviews,
        phone=phone,
    )


@router.post("/profile", response_model=MasterCardResponse)
def create_master_profile(
    data: MasterProfileCreate,
    authorization: str = Header(""),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_header(authorization, db)

    existing = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    user.role = "master"
    profile = MasterProfile(
        user_id=user.id,
        subcategory_id=data.subcategory_id,
        description=data.description,
        experience_years=data.experience_years,
        hourly_rate=data.hourly_rate,
        city=data.city or user.city,
        district=data.district,
        address=data.address,
        skills=data.skills,
        is_available=data.is_available,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # Reload with relationships
    profile = (
        db.query(MasterProfile)
        .options(
            joinedload(MasterProfile.user),
            joinedload(MasterProfile.subcategory).joinedload(Subcategory.category),
        )
        .filter(MasterProfile.id == profile.id)
        .first()
    )
    return build_master_card(profile)


@router.get("/profile/me", response_model=MasterCardResponse)
def get_my_master_profile(
    authorization: str = Header(""),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_header(authorization, db)
    profile = (
        db.query(MasterProfile)
        .options(
            joinedload(MasterProfile.user),
            joinedload(MasterProfile.subcategory).joinedload(Subcategory.category),
        )
        .filter(MasterProfile.user_id == user.id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Master profile not found")
    
    return build_master_card(profile)

@router.put("/profile", response_model=MasterCardResponse)
def update_master_profile(
    data: MasterProfileUpdate,
    authorization: str = Header(""),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_header(authorization, db)
    profile = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    print(f"DEBUG: Master {user.id} (username: {user.name}) is updating profile. NEW DISTRICT: {data.district}")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    profile = (
        db.query(MasterProfile)
        .options(
            joinedload(MasterProfile.user),
            joinedload(MasterProfile.subcategory).joinedload(Subcategory.category),
        )
        .filter(MasterProfile.id == profile.id)
        .first()
    )
    return build_master_card(profile)


@router.post("/{master_id}/review", response_model=ReviewResponse)
def create_review(
    master_id: int,
    data: ReviewCreate,
    authorization: str = Header(""),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_header(authorization, db)
    profile = db.query(MasterProfile).filter(MasterProfile.id == master_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Master not found")

    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")

    review = Review(
        master_id=master_id,
        client_id=user.id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    db.commit()

    # Update master rating and check for auto-block
    all_reviews = db.query(Review).filter(Review.master_id == master_id).all()
    avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    profile.rating = round(avg_rating, 1)
    profile.reviews_count = len(all_reviews)
    
    # Auto-block logic: 3 reviews with rating 1 or 2
    bad_reviews_count = sum(1 for r in all_reviews if r.rating <= 2)
    if bad_reviews_count >= 3:
        profile.is_blocked = True

    db.commit()
    db.refresh(review)

    created_at = review.created_at
    if created_at and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return ReviewResponse(
        id=review.id,
        master_id=review.master_id,
        client_id=review.client_id,
        client_name=user.name,
        client_avatar=user.avatar,
        rating=review.rating,
        comment=review.comment,
        created_at=created_at,
    )
