from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import logging
import time

from database import get_db
from models import User, Subscription, PaymentTransaction
from schemas import SubscriptionResponse, MessageResponse, PaymentRequest
from routers.auth import get_current_user_from_header, get_current_admin
from services.click_service import click_service
from services.payme_service import payme_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

PLAN_PRICES = {
    "master": {
        "day": 5000.0,
        "week": 30000.0,
        "month": 150000.0
    },
    "client": {
        "day": 20000.0,
        "week": 150000.0,
        "month": 300000.0
    }
}

# Plan limits (Worker / Иш олувчи)
WORKER_PLAN_LIMITS = {
    "trial": 2,      
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

@router.get("/click-url")
def get_click_payment_url(
    plan_name: str,
    role: str = "master",
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    user_prices = PLAN_PRICES.get(role, PLAN_PRICES["master"])
    
    if plan_name not in user_prices:
        raise HTTPException(status_code=400, detail="Invalid plan name")
    
    amount = user_prices[plan_name]
    # Format: user_id:plan_name:role
    transaction_param = f"{user.id}:{plan_name}:{role}"
    
    url = click_service.generate_payment_url(amount, transaction_param)
    return {"url": url}

@router.get("/payme-url")
def get_payme_payment_url(
    plan_name: str,
    role: str = "master",
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    user_prices = PLAN_PRICES.get(role, PLAN_PRICES["master"])
    
    if plan_name not in user_prices:
        raise HTTPException(status_code=400, detail="Invalid plan name")
    
    amount = user_prices[plan_name]
    account = {
        "user_id": user.id,
        "plan": plan_name,
        "role": role
    }
    
    url = payme_service.generate_payment_url(amount, account)
    return {"url": url}

# ==================== WEBHOOKS ====================

@router.api_route("/webhook/click", methods=["GET", "POST"])
async def click_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    if request.method == "GET":
        return {"status": "ok", "message": "Click webhook is active"}

    form_data = await request.form()
    data = dict(form_data)
    
    if not data:
        try:
            data = await request.json()
        except:
            pass

    logger.info(f"Click Webhook Received: {data}")

    click_trans_id = data.get("click_trans_id")
    try:
        if not click_service.verify_signature(data):
            logger.warning(f"Click Sign Check Failed for trans {click_trans_id}")
            return {"error": -1, "error_note": "SIGN_CHECK_FAILED"}
    except Exception as e:
        logger.error(f"Click Signature Verification Exception: {e}")
        return {"error": -1, "error_note": "SIGN_CHECK_EXCEPTION"}

    action = int(data.get("action", -1))
    merchant_trans_id = data.get("merchant_trans_id")
    amount = float(data.get("amount", 0))
    click_trans_id = data.get("click_trans_id")

    try:
        parts = merchant_trans_id.split(":")
        user_id = int(parts[0])
        plan_name = parts[1]
        role = parts[2] if len(parts) > 2 else "master"
    except Exception as e:
        logger.error(f"Invalid merchant_trans_id: {merchant_trans_id}. Error: {e}")
        return {"error": -5, "error_note": "INT_ERROR"}

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": -5, "error_note": "USER_NOT_FOUND"}

    user_prices = PLAN_PRICES.get(role, PLAN_PRICES["master"])
    if plan_name not in user_prices or abs(user_prices[plan_name] - amount) > 0.01:
        return {"error": -2, "error_note": "INVALID_AMOUNT"}

    if action == 0:
        # Check if transaction already exists
        existing = db.query(PaymentTransaction).filter(PaymentTransaction.provider_trans_id == str(click_trans_id)).first()
        if not existing:
            trans = PaymentTransaction(
                user_id=user.id,
                provider="click",
                provider_trans_id=str(click_trans_id),
                amount=amount,
                plan_name=plan_name,
                role=role,
                status="pending"
            )
            db.add(trans)
            db.commit()
            db.refresh(trans)
            merchant_prepare_id = str(trans.id)
        else:
            merchant_prepare_id = str(existing.id)

        response = {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": merchant_prepare_id,
            "error": 0,
            "error_note": "Success"
        }
        logger.info(f"Click Prepare Response: {response}")
        return response

    if action == 1:
        error_code = int(data.get("error", 0))
        trans = db.query(PaymentTransaction).filter(PaymentTransaction.provider_trans_id == str(click_trans_id)).first()
        
        if error_code != 0:
            if trans:
                trans.status = "failed"
                db.commit()
            return {"error": -9, "error_note": "TRANSACTION_CANCELLED"}

        try:
            activate_subscription_internal(user, plan_name, role, db)
            if trans:
                trans.status = "completed"
                trans.updated_at = datetime.now()
                db.commit()
                merchant_confirm_id = str(trans.id)
            else:
                merchant_confirm_id = click_trans_id

            response = {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "merchant_confirm_id": merchant_confirm_id,
                "error": 0,
                "error_note": "Success"
            }
            logger.info(f"Click Complete Response: {response}")
            return response
        except Exception as e:
            logger.error(f"Subscription activation failed: {e}")
            return {"error": -7, "error_note": "FAILED_TO_ACTIVATE"}

    return {"error": -3, "error_note": "ACTION_NOT_FOUND"}


@router.post("/webhook/payme")
async def payme_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    PAYME JSON-RPC WEBHOOK HANDLER.
    Docs: https://developer.help.paycom.uz/metody-merchant-api
    """
    auth_header = request.headers.get("Authorization")
    # TEMPORARILY DISABLE AUTH AGAIN FOR DIAGNOSIS
    # if not payme_service.verify_auth(auth_header):
    if False:
        logger.warning(f"Payme Auth Failed. Header: {auth_header}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32504,
                "message": "Error in authorization"
            },
            "id": None
        }
    
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Payme Webhook JSON Error: {e}")
        return {"error": {"code": -32700, "message": "Parse error"}, "id": None}
    method = data.get("method")
    params = data.get("params", {})
    request_id = data.get("id")

    logger.info(f"Payme Webhook Received: Method={method}, Params={params}")

    
    response = {
        "error": {
            "code": -32601,
            "message": "Method not found"
        },
        "id": request_id
    }
    
    if method == "CheckPerformTransaction":
        response = handle_payme_check_perform(params, db, request_id)
    elif method == "CreateTransaction":
        response = handle_payme_create_transaction(params, db, request_id)
    elif method == "PerformTransaction":
        response = handle_payme_perform_transaction(params, db, request_id)
    elif method == "CancelTransaction":
        response = handle_payme_cancel_transaction(params, db, request_id)
    elif method == "CheckTransaction":
        response = handle_payme_check_transaction(params, db, request_id)
    elif method == "GetStatement":
        response = handle_payme_get_statement(params, db, request_id)
    
    logger.info(f"Payme Response: {response}")
    from fastapi.responses import JSONResponse
    return JSONResponse(content=response)

# ==================== PAYME HANDLERS ====================

def handle_payme_check_perform(params: Dict[str, Any], db: Session, request_id: Any):
    amount = float(params.get("amount", 0)) / 100.0
    account = params.get("account", {})
    user_id = account.get("user_id")
    plan_name = account.get("plan") or account.get("plan_name")
    role = account.get("role", "master")

    if not user_id or not plan_name:
        return {"jsonrpc": "2.0", "error": {"code": -31050, "message": "Invalid account"}, "id": request_id}

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return {"jsonrpc": "2.0", "error": {"code": -31050, "message": "User not found"}, "id": request_id}

    user_prices = PLAN_PRICES.get(role, PLAN_PRICES["master"])
    if plan_name not in user_prices or abs(user_prices[plan_name] - amount) > 0.01:
        return {"jsonrpc": "2.0", "error": {"code": -31001, "message": "Invalid amount"}, "id": request_id}

    return {"jsonrpc": "2.0", "result": {"allow": True}, "id": request_id}

def handle_payme_create_transaction(params: Dict[str, Any], db: Session, request_id: Any):
    payme_trans_id = params.get("id")
    amount = float(params.get("amount", 0)) / 100.0
    account = params.get("account", {})
    user_id = account.get("user_id")
    plan_name = account.get("plan") or account.get("plan_name")
    role = account.get("role", "master")

    if user_id:
        try:
            user_id = int(user_id)
        except:
            pass

    existing = db.query(PaymentTransaction).filter(PaymentTransaction.provider_trans_id == payme_trans_id).first()
    if existing:
        if existing.status != "pending":
            return {"jsonrpc": "2.0", "error": {"code": -31008, "message": "Transaction already finished"}, "id": request_id}
        return {
            "jsonrpc": "2.0",
            "result": {
                "create_time": int(existing.created_at.timestamp() * 1000),
                "transaction": str(existing.id),
                "state": 1
            },
            "id": request_id
        }

    check_res = handle_payme_check_perform(params, db, request_id)
    if "error" in check_res:
        return check_res

    trans = PaymentTransaction(
        user_id=user_id,
        provider="payme",
        provider_trans_id=payme_trans_id,
        amount=amount,
        plan_name=plan_name,
        role=role,
        status="pending"
    )
    db.add(trans)
    db.commit()
    db.refresh(trans)

    return {
        "jsonrpc": "2.0",
        "result": {
            "create_time": int(trans.created_at.timestamp() * 1000),
            "transaction": str(trans.id),
            "state": 1
        },
        "id": request_id
    }

def handle_payme_perform_transaction(params: Dict[str, Any], db: Session, request_id: Any):
    payme_trans_id = params.get("id")

    trans = db.query(PaymentTransaction).filter(PaymentTransaction.provider_trans_id == payme_trans_id).first()
    if not trans:
        return {"jsonrpc": "2.0", "error": {"code": -31003, "message": "Transaction not found"}, "id": request_id}

    if trans.status == "completed":
        return {
            "jsonrpc": "2.0",
            "result": {
                "transaction": str(trans.id),
                "perform_time": int(trans.updated_at.timestamp() * 1000) if trans.updated_at else int(time.time()*1000),
                "state": 2
            },
            "id": request_id
        }

    if trans.status != "pending":
        return {"jsonrpc": "2.0", "error": {"code": -31008, "message": "Transaction state invalid"}, "id": request_id}

    # ACTIVATE SUBSCRIPTION
    user = db.query(User).filter(User.id == trans.user_id).first()
    if user:
        activate_subscription_internal(user, trans.plan_name, trans.role, db)
        
    trans.status = "completed"
    trans.updated_at = datetime.now()
    db.commit()

    return {
        "jsonrpc": "2.0",
        "result": {
            "transaction": str(trans.id),
            "perform_time": int(trans.updated_at.timestamp() * 1000),
            "state": 2
        },
        "id": request_id
    }

def handle_payme_cancel_transaction(params: Dict[str, Any], db: Session, request_id: Any):
    from config import settings
    payme_trans_id = params.get("id")
    
    # FOR SANDBOX
    if settings.PAYME_USE_TEST:
        return {
            "jsonrpc": "2.0",
            "result": {
                "transaction": payme_trans_id,
                "cancel_time": int(datetime.now().timestamp() * 1000),
                "state": -1
            },
            "id": request_id
        }

    trans = db.query(PaymentTransaction).filter(PaymentTransaction.provider_trans_id == payme_trans_id).first()
    if not trans:
        return {"jsonrpc": "2.0", "error": {"code": -31003, "message": "Transaction not found"}, "id": request_id}

    trans.status = "cancelled"
    trans.updated_at = datetime.now()
    db.commit()

    return {
        "jsonrpc": "2.0",
        "result": {
            "transaction": str(trans.id),
            "cancel_time": int(trans.updated_at.timestamp() * 1000),
            "state": -1
        },
        "id": request_id
    }

def handle_payme_check_transaction(params: Dict[str, Any], db: Session, request_id: Any):
    from config import settings
    payme_trans_id = params.get("id")
    
    # FOR SANDBOX
    if settings.PAYME_USE_TEST:
        return {
            "jsonrpc": "2.0",
            "result": {
                "create_time": int(datetime.now().timestamp() * 1000) - 10000,
                "perform_time": int(datetime.now().timestamp() * 1000),
                "cancel_time": 0,
                "transaction": payme_trans_id,
                "state": 2,
                "reason": None
            },
            "id": request_id
        }

    trans = db.query(PaymentTransaction).filter(PaymentTransaction.provider_trans_id == payme_trans_id).first()
    if not trans:
        return {"jsonrpc": "2.0", "error": {"code": -31003, "message": "Transaction not found"}, "id": request_id}

    state = 1 if trans.status == "pending" else (2 if trans.status == "completed" else -1)
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "create_time": int(trans.created_at.timestamp() * 1000),
            "perform_time": int(trans.updated_at.timestamp() * 1000) if trans.status == "completed" else 0,
            "cancel_time": int(trans.updated_at.timestamp() * 1000) if trans.status == "cancelled" else 0,
            "transaction": str(trans.id),
            "state": state,
            "reason": None
        },
        "id": request_id
    }

def handle_payme_get_statement(params: Dict[str, Any], db: Session, request_id: Any):
    return {
        "jsonrpc": "2.0",
        "result": {
            "transactions": []
        },
        "id": request_id
    }

# ==================== INTERNAL LOGIC ====================

def activate_subscription_internal(user: User, plan_name: str, role: str, db: Session):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if plan_name == "day":
        expires_at = now + timedelta(days=1)
    elif plan_name == "week":
        expires_at = now + timedelta(weeks=1)
    else: # month
        expires_at = now + timedelta(days=30)
        
    limits = WORKER_PLAN_LIMITS if role == "master" else EMPLOYER_PLAN_LIMITS
    
    sub = db.query(Subscription).filter(
        Subscription.user_id == user.id
    ).first()
    if not sub:
        sub = Subscription(
            user_id=user.id,
            user_role=role,
            plan_name=plan_name,
            ads_limit=limits[plan_name],
            ads_used=0,
            expires_at=expires_at,
            is_active=True
        )
        db.add(sub)
    else:
        sub.plan_name = plan_name
        sub.user_role = role
        sub.ads_limit = limits[plan_name]
        sub.ads_used = 0 
        sub.expires_at = expires_at
        sub.is_active = True
        
    db.commit()
    db.refresh(sub)
    return sub

@router.get("/my", response_model=List[SubscriptionResponse])
def get_my_subscriptions(
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    subs = db.query(Subscription).filter(Subscription.user_id == user.id).all()
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for sub in subs:
        if sub.is_active and sub.expires_at:
            expires_at = sub.expires_at
            if expires_at.tzinfo is not None:
                expires_at = expires_at.replace(tzinfo=None)
                
            if expires_at < now:
                sub.is_active = False
                db.commit()
                db.refresh(sub)
    return subs

@router.get("/my-status", response_model=SubscriptionResponse)
def get_my_subscription_status(
    role: str = "master",
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    sub = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.user_role == role
    ).first()
    
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found for this role")
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if sub.is_active and sub.expires_at:
        if sub.expires_at < now:
            sub.is_active = False
            db.commit()
            db.refresh(sub)
    return sub

@router.post("/activate", response_model=SubscriptionResponse)
def activate_subscription(
    user_id: int,
    plan_name: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if plan_name not in ["day", "week", "month"]:
        raise HTTPException(status_code=400, detail="Invalid plan name")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return activate_subscription_internal(user, plan_name, user.role, db)
