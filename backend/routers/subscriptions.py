from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List

from database import get_db
from models import User, Subscription
from schemas import SubscriptionResponse, MessageResponse, PaymentRequest
from routers.auth import get_current_user_from_header, get_current_admin

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

@router.post("/pay-card", response_model=SubscriptionResponse)
def pay_by_card(
    data: PaymentRequest,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """
    SIMULATED PAYMENT PROCESS.
    In production, this would redirect to Payme/Click or initialize a transaction.
    """
    user = get_current_user_from_header(authorization, db)
    
    # Validation
    if len(data.card_number.replace(" ", "")) < 16:
        raise HTTPException(status_code=400, detail="Invalid card number")
    
    # 1. Start Transaction (Simulated)
    # transaction_id = str(uuid.uuid4())
    
    # 2. Complete Transaction (Simulated)
    plan_name = data.plan_name
    if plan_name not in ["day", "week", "month"]:
         raise HTTPException(status_code=400, detail="Invalid plan name")

    # Business Logic for subscription activation...
    # (Existing logic below remains the same but within this simulated context)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if plan_name == "day":
        expires_at = now + timedelta(days=1)
    elif plan_name == "week":
        expires_at = now + timedelta(weeks=1)
    else: # month
        expires_at = now + timedelta(days=30)
        
    limits = WORKER_PLAN_LIMITS if user.role == "master" else EMPLOYER_PLAN_LIMITS
    
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub:
        sub = Subscription(
            user_id=user.id,
            user_role=user.role,
            plan_name=plan_name,
            ads_limit=limits[plan_name],
            ads_used=0,
            expires_at=expires_at,
            is_active=True
        )
        db.add(sub)
    else:
        sub.plan_name = plan_name
        sub.user_role = user.role
        sub.ads_limit = limits[plan_name]
        sub.ads_used = 0 
        sub.expires_at = expires_at
        sub.is_active = True
        
    db.commit()
    db.refresh(sub)
    return sub

@router.post("/webhook/payme")
def payme_webhook(
    # This is where Payme sends its special JSON with their Merchant-ID and Keys
    data: dict,
    db: Session = Depends(get_db)
):
    """
    SKELETON FOR REAL PAYME INTEGRATION.
    This endpoint will be called by Payme server when a real payment is made.
    """
    # 1. Verify Payme Signature (Authentication)
    # 2. Locate the User/Order from data['params']['account']
    # 3. Activate subscription
    return {"result": {"success": True}}

@router.post("/webhook/click")
def click_webhook(
    data: dict,
    db: Session = Depends(get_db)
):
    """
    SKELETON FOR REAL CLICK INTEGRATION.
    """
    return {"result": "success"}
from routers.auth import get_current_user_from_header, get_current_admin

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

# Plan limits (Worker / Иш олувчи)
WORKER_PLAN_LIMITS = {
    "trial": 2,      # 3 minutes full access
    "day": 1,        
    "week": 10,      
    "month": 45      
}

# Plan limits (Employer / Иш берувчи)
EMPLOYER_PLAN_LIMITS = {
    "trial": 2,      
    "day": 1,        
    "week": 10,      
    "month": 30      
}

@router.get("/my", response_model=SubscriptionResponse)
def get_my_subscription(
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Check if expired
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if sub.is_active and sub.expires_at:
        expires_at = sub.expires_at
        if expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)
            
        if expires_at < now:
            sub.is_active = False
            db.commit()
            db.refresh(sub)
        
    return sub

@router.post("/activate", response_model=SubscriptionResponse)
def activate_subscription(
    user_id: int,
    plan_name: str, # "day", "week", "month"
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if plan_name not in ["day", "week", "month"]:
        raise HTTPException(status_code=400, detail="Invalid plan name")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate expiry
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if plan_name == "day":
        expires_at = now + timedelta(days=1)
    elif plan_name == "week":
        expires_at = now + timedelta(weeks=1)
    else: # month
        expires_at = now + timedelta(days=30)
        
    # Calculate limits based on role
    limits = WORKER_PLAN_LIMITS if user.role == "master" else EMPLOYER_PLAN_LIMITS
    
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not sub:
        sub = Subscription(
            user_id=user_id,
            user_role=user.role,
            plan_name=plan_name,
            ads_limit=limits[plan_name],
            ads_used=0,
            expires_at=expires_at,
            is_active=True
        )
        db.add(sub)
    else:
        sub.plan_name = plan_name
        sub.user_role = user.role
        sub.ads_limit = limits[plan_name]
        sub.ads_used = 0 
        sub.expires_at = expires_at
        sub.is_active = True
        
    db.commit()
    db.refresh(sub)
    return sub
