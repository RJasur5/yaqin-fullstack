from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File, Body
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
import os
import shutil
import re

from database import get_db
from models import User, MasterProfile
from schemas import (
    UserRegister, UserLogin, TokenResponse,
    UserResponse, UserProfileUpdate, MessageResponse,
    MasterProfileCreate, SubscriptionResponse, FCMTokenUpdate
)
from models import Subscription
from config import settings


def normalize_phone_number(phone: str) -> str:
    """Always normalize to clean +998XXXXXXXXX format for DB storage and lookup."""
    if not phone:
        return phone
    digits = re.sub(r'\D', '', phone)
    # Handle 998XXXXXXXXX (12 digits with country code)
    if len(digits) >= 12 and digits.startswith('998'):
        return '+' + digits[:12]
    # Handle 9 digit subscriber number only
    elif len(digits) == 9:
        return '+998' + digits
    # Handle any other length - extract last 9 digits
    elif len(digits) > 9:
        return '+998' + digits[-9:]
    return phone  # fallback

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
TOKEN_EXPIRE_DAYS = settings.TOKEN_EXPIRE_DAYS


def create_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=TOKEN_EXPIRE_DAYS)
    data = {"sub": str(user_id), "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = "", db: Session = Depends(get_db)) -> User:
    """Decode token and return current user."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user_from_header(
    authorization: str = Header(""),
    db: Session = Depends(get_db)
) -> User:
    """Extract token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    token = authorization.replace("Bearer ", "")
    return get_current_user(token, db)


def get_current_admin(
    user: User = Depends(get_current_user_from_header)
) -> User:
    """Check if the current user is an admin."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    # Normalize phone to canonical format: +998XXXXXXXXX
    clean_phone = normalize_phone_number(data.phone)
    
    # Check if phone already exists (search by normalized form)
    existing = db.query(User).filter(User.phone == clean_phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")

    # Create user with normalized phone
    user = User(
        name=data.name,
        phone=clean_phone,
        password_hash=pwd_context.hash(data.password),
        role=data.role,
        city=data.city,
        lang=data.lang,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # --- GRANT 2-MINUTE TRIAL ---
    trial_expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=2)
    subscription = Subscription(
        user_id=user.id,
        user_role=user.role,
        plan_name="trial",
        ads_limit=10, # Give more ads for trial
        ads_used=0,
        expires_at=trial_expires,
        is_active=True
    )
    user.is_trial_used = True
    db.add(subscription)
    db.commit()
    # ----------------------------

    token = create_token(user.id)
    return TokenResponse(
        access_token=token,
        user=UserResponse.from_orm(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    # Normalize incoming phone to canonical +998XXXXXXXXX format before lookup
    clean_phone = normalize_phone_number(data.phone)
    
    # Try exact match first
    user = db.query(User).filter(User.phone == clean_phone).first()
    
    # Fallback: search all users and compare normalized phones
    # (handles legacy formatted phones like "+998 (99) 842-65-74" still in DB)
    if not user:
        all_users = db.query(User).all()
        for u in all_users:
            if normalize_phone_number(u.phone) == clean_phone:
                user = u
                # Fix phone format in DB while we're here
                u.phone = clean_phone
                db.commit()
                break
    
    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный номер телефона или пароль")

    token = create_token(user.id)
    return TokenResponse(
        access_token=token,
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    return UserResponse.from_orm(user)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UserProfileUpdate,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    if data.name is not None:
        user.name = data.name
    if data.city is not None:
        user.city = data.city
    if data.lang is not None:
        user.lang = data.lang
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)

@router.post("/me/avatar", response_model=UserResponse)
def upload_avatar(
    file: UploadFile = File(...),
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    os.makedirs("uploads", exist_ok=True)
    
    # Simple sanitization
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"avatar_{user.id}_{int(datetime.now().timestamp())}.{ext}"
    filepath = os.path.join("uploads", filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Set the URL path
    user.avatar = f"/uploads/{filename}"
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)


# ==================== ADMIN ACTIONS ====================

@router.put("/admin/users/{user_id}/password", response_model=MessageResponse)
def admin_change_user_password(
    user_id: int,
    new_password: str = Body(..., embed=True),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin can change any user's password."""
    user_to_update = db.query(User).filter(User.id == user_id).first()
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_to_update.password_hash = pwd_context.hash(new_password)
    db.commit()
    return MessageResponse(message=f"Пароль пользователя {user_to_update.name} успешно изменен")


@router.post("/fcm-token", response_model=MessageResponse)
def update_fcm_token(
    data: FCMTokenUpdate,
    user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """Update user's FCM token and APNs token for push notifications."""
    user.fcm_token = data.fcm_token
    if hasattr(data, 'apns_token') and data.apns_token:
        user.apns_token = data.apns_token
    db.commit()
    return MessageResponse(message="FCM token updated successfully")



