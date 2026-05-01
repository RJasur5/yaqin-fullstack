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
from services.paynet_service import paynet_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

PLAN_PRICES = {
    "master": {
        "day": 5000.0,
        "week": 40000.0,
        "2_weeks": 100000.0,
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
    "2_weeks": 30,
    "month": 50      
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
    # We pass both user_id and plan_name, as configured in the user's Payme dashboard
    account = {
        "user_id": user.id,
        "plan_name": plan_name
    }
    
    url = payme_service.generate_payment_url(amount, account)
    return {"url": url}

@router.get("/paynet-url")
def get_paynet_payment_url(
    plan_name: str,
    role: str = "master",
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    user_prices = PLAN_PRICES.get(role, PLAN_PRICES["master"])
    
    if plan_name not in user_prices:
        raise HTTPException(status_code=400, detail="Invalid plan name")
    
    amount = int(user_prices[plan_name] * 100)
    service_id = settings.PAYNET_SERVICE_ID
    
    # Paynet App deeplink format
    url = f"https://paynet.uz/pay/{service_id}?client_id={user.id}&amount={amount}"
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
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Payme Webhook JSON Error: {e}")
        return {"error": {"code": -32700, "message": "Parse error"}, "id": None}
        
    method = data.get("method")
    params = data.get("params", {})
    request_id = data.get("id")

    auth_header = request.headers.get("Authorization")
    if not payme_service.verify_auth(auth_header):
        logger.warning(f"Payme Auth Failed. Header: {auth_header}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32504,
                "message": {
                    "ru": "Недостаточно привилегий для выполнения метода.",
                    "uz": "Metodni bajarish uchun imtiyozlar yetarli emas.",
                    "en": "Insufficient privileges to perform the method."
                }
            },
            "id": request_id
        }

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

# ==================== PAYNET HANDLERS ====================

@router.post("/webhook/paynet")
async def paynet_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Paynet Webhook JSON Error: {e}")
        return {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}
        
    method = data.get("method")
    params = data.get("params", {})
    request_id = data.get("id")

    auth_header = request.headers.get("Authorization")
    if not paynet_service.verify_auth(auth_header):
        logger.warning(f"Paynet Auth Failed. Header: {auth_header}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": 412, "message": "Неверный логин или пароль"},
            "id": request_id
        }

    logger.info(f"Paynet Webhook Received: Method={method}, Params={params}")
    
    response = {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": request_id
    }
    
    if method == "GetInformation":
        response = handle_paynet_get_information(params, db, request_id)
    elif method == "PerformTransaction":
        response = handle_paynet_perform_transaction(params, db, request_id)
    elif method == "CheckTransaction":
        response = handle_paynet_check_transaction(params, db, request_id)
    elif method == "CancelTransaction":
        response = handle_paynet_cancel_transaction(params, db, request_id)
    elif method == "GetStatement":
        response = handle_paynet_get_statement(params, db, request_id)
    elif method == "ChangePassword":
        response = handle_paynet_change_password(params, request_id)
        
    logger.info(f"Paynet Response: {response}")
    from fastapi.responses import JSONResponse
    return JSONResponse(content=response)

def get_plan_by_amount(amount: float, role: str = "master"):
    prices = PLAN_PRICES.get(role, PLAN_PRICES["master"])
    for plan_name, price in prices.items():
        if abs(price - amount) < 0.01:
            return plan_name
    return None

def find_user_by_client_id(client_id: str, db: Session):
    try:
        user_id = int(client_id)
        user = db.query(User).filter(User.id == user_id).first()
        if user: return user
    except:
        pass
        
    import re
    digits = re.sub(r'\D', '', str(client_id))
    if digits:
        # Match phone if it ends with these digits
        user = db.query(User).filter(User.phone.like(f"%{digits}")).first()
        if user: return user
    return None

def handle_paynet_get_information(params: Dict[str, Any], db: Session, request_id: Any):
    fields = params.get("fields", {})
    client_id = fields.get("client_id")
    
    if not client_id:
        return {"jsonrpc": "2.0", "error": {"code": 411, "message": "client_id is required"}, "id": request_id}
        
    user = find_user_by_client_id(str(client_id), db)
    if not user:
        return {"jsonrpc": "2.0", "error": {"code": 302, "message": "Клиент не найден"}, "id": request_id}
        
    return {
        "jsonrpc": "2.0",
        "result": {
            "status": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fields": {
                "name": user.name,
                "role": user.role
            }
        },
        "id": request_id
    }

def handle_paynet_perform_transaction(params: Dict[str, Any], db: Session, request_id: Any):
    amount = float(params.get("amount", 0)) / 100.0
    paynet_trans_id = params.get("transactionId")
    fields = params.get("fields", {})
    client_id = fields.get("client_id")
    
    if not client_id or not paynet_trans_id:
        return {"jsonrpc": "2.0", "error": {"code": 411, "message": "Missing params"}, "id": request_id}
        
    user = find_user_by_client_id(str(client_id), db)
    if not user:
        return {"jsonrpc": "2.0", "error": {"code": 302, "message": "Клиент не найден"}, "id": request_id}
        
    role = user.role
    plan_name = get_plan_by_amount(amount, role)
    if not plan_name:
        return {"jsonrpc": "2.0", "error": {"code": 415, "message": "Сумма превышает максимальный лимит"}, "id": request_id}
        
    existing = db.query(PaymentTransaction).filter(
        PaymentTransaction.provider == "paynet",
        PaymentTransaction.provider_trans_id == str(paynet_trans_id)
    ).first()
    
    if existing:
        if existing.status == "completed":
            return {"jsonrpc": "2.0", "error": {"code": 201, "message": "Транзакция уже существует"}, "id": request_id}
        return {"jsonrpc": "2.0", "error": {"code": 102, "message": "System error"}, "id": request_id}

    trans = PaymentTransaction(
        user_id=user.id,
        provider="paynet",
        provider_trans_id=str(paynet_trans_id),
        amount=amount,
        plan_name=plan_name,
        role=role,
        status="completed",
        completed_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    db.add(trans)
    
    activate_subscription_internal(user, plan_name, role, db)
    db.commit()
    db.refresh(trans)
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "providerTrnId": trans.id,
            "timestamp": trans.completed_at.strftime("%Y-%m-%d %H:%M:%S"),
            "fields": {
                "client_id": client_id
            }
        },
        "id": request_id
    }

def handle_paynet_check_transaction(params: Dict[str, Any], db: Session, request_id: Any):
    paynet_trans_id = params.get("transactionId")
    trans = db.query(PaymentTransaction).filter(
        PaymentTransaction.provider == "paynet",
        PaymentTransaction.provider_trans_id == str(paynet_trans_id)
    ).first()
    
    if not trans:
        return {"jsonrpc": "2.0", "error": {"code": 203, "message": "Транзакция не найдена"}, "id": request_id}
        
    if trans.status == "completed":
        state = 1
    elif trans.status == "cancelled":
        state = 2
    else:
        state = 3
        
    return {
        "jsonrpc": "2.0",
        "result": {
            "providerTrnId": trans.id,
            "timestamp": (trans.completed_at or trans.created_at).strftime("%a %b %d %H:%M:%S UZT %Y"),
            "transactionState": state
        },
        "id": request_id
    }

def handle_paynet_cancel_transaction(params: Dict[str, Any], db: Session, request_id: Any):
    paynet_trans_id = params.get("transactionId")
    trans = db.query(PaymentTransaction).filter(
        PaymentTransaction.provider == "paynet",
        PaymentTransaction.provider_trans_id == str(paynet_trans_id)
    ).first()
    
    if not trans:
        return {"jsonrpc": "2.0", "error": {"code": 203, "message": "Транзакция не найдена"}, "id": request_id}
        
    if trans.status == "cancelled":
        return {"jsonrpc": "2.0", "error": {"code": 202, "message": "Транзакция уже отменена"}, "id": request_id}
        
    trans.status = "cancelled"
    trans.cancel_time = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(trans)
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "providerTrnId": trans.id,
            "timestamp": trans.cancel_time.strftime("%Y-%m-%d %H:%M:%S"),
            "transactionState": 2
        },
        "id": request_id
    }

def handle_paynet_get_statement(params: Dict[str, Any], db: Session, request_id: Any):
    date_from_str = params.get("dateFrom")
    date_to_str = params.get("dateTo")
    
    try:
        date_from = datetime.strptime(date_from_str, "%Y-%m-%d %H:%M:%S")
        date_to = datetime.strptime(date_to_str, "%Y-%m-%d %H:%M:%S")
    except:
        return {"jsonrpc": "2.0", "error": {"code": 414, "message": "Invalid date format"}, "id": request_id}
        
    transactions = db.query(PaymentTransaction).filter(
        PaymentTransaction.provider == "paynet",
        PaymentTransaction.completed_at >= date_from,
        PaymentTransaction.completed_at <= date_to
    ).all()
    
    statements = []
    for trans in transactions:
        statements.append({
            "amount": int(trans.amount * 100),
            "providerTrnId": trans.id,
            "transactionId": int(trans.provider_trans_id),
            "timestamp": trans.completed_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    return {
        "jsonrpc": "2.0",
        "result": {
            "statements": statements
        },
        "id": request_id
    }

def handle_paynet_change_password(params: Dict[str, Any], request_id: Any):
    # we don't handle password change dynamically here, usually we'd save to env or DB.
    # For now return success or simply "not supported"
    return {
        "jsonrpc": "2.0",
        "result": "success",
        "id": request_id
    }

# ==================== PAYME HANDLERS ====================

def handle_payme_check_perform(params: Dict[str, Any], db: Session, request_id: Any):
    amount = float(params.get("amount", 0)) / 100.0
    account = params.get("account", {})
    user_id = account.get("user_id")

    if not user_id:
        return {"jsonrpc": "2.0", "error": {"code": -31050, "message": "Invalid account: missing user_id"}, "id": request_id}

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return {"jsonrpc": "2.0", "error": {"code": -31050, "message": "User not found"}, "id": request_id}

    role = user.role
    plan_name = get_plan_by_amount(amount, role)
    
    if not plan_name:
        return {"jsonrpc": "2.0", "error": {"code": -31001, "message": "Invalid amount for the user's role"}, "id": request_id}

    amount_tiyin = int(amount * 100)
    detail = {
        "receipt_type": 0,
        "items": [
            {
                "title": f"Подписка на тариф {plan_name}",
                "price": amount_tiyin,
                "count": 1,
                "code": "10305010001000000",
                "units": 242,  # 242 - штуки (услуги)
                "vat_percent": 0,
                "package_code": "123456"
            }
        ]
    }

    return {"jsonrpc": "2.0", "result": {"allow": True, "detail": detail}, "id": request_id}

def handle_payme_create_transaction(params: Dict[str, Any], db: Session, request_id: Any):
    payme_trans_id = params.get("id")
    amount = float(params.get("amount", 0)) / 100.0
    account = params.get("account", {})
    user_id = account.get("user_id")

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

    user = db.query(User).filter(User.id == user_id).first()
    role = user.role if user else "master"
    plan_name = get_plan_by_amount(amount, role)

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
                "perform_time": int(trans.completed_at.timestamp() * 1000) if trans.completed_at else int(time.time()*1000),
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
    trans.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()

    return {
        "jsonrpc": "2.0",
        "result": {
            "transaction": str(trans.id),
            "perform_time": int(trans.completed_at.timestamp() * 1000),
            "state": 2
        },
        "id": request_id
    }

def handle_payme_cancel_transaction(params: Dict[str, Any], db: Session, request_id: Any):
    payme_trans_id = params.get("id")
    reason = params.get("reason")
    
    trans = db.query(PaymentTransaction).filter(PaymentTransaction.provider_trans_id == payme_trans_id).first()
    if not trans:
        return {"jsonrpc": "2.0", "error": {"code": -31003, "message": "Transaction not found"}, "id": request_id}

    if trans.status == "cancelled":
        return {
            "jsonrpc": "2.0",
            "result": {
                "transaction": str(trans.id),
                "cancel_time": int(trans.cancel_time.timestamp() * 1000) if trans.cancel_time else int(time.time()*1000),
                "state": -1 if not trans.completed_at else -2
            },
            "id": request_id
        }

    state = -1 if trans.status == "pending" else -2
    trans.status = "cancelled"
    trans.cancel_reason = reason
    trans.cancel_time = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()

    return {
        "jsonrpc": "2.0",
        "result": {
            "transaction": str(trans.id),
            "cancel_time": int(trans.cancel_time.timestamp() * 1000),
            "state": state
        },
        "id": request_id
    }

def handle_payme_check_transaction(params: Dict[str, Any], db: Session, request_id: Any):
    payme_trans_id = params.get("id")
    
    trans = db.query(PaymentTransaction).filter(PaymentTransaction.provider_trans_id == payme_trans_id).first()
    if not trans:
        return {"jsonrpc": "2.0", "error": {"code": -31003, "message": "Transaction not found"}, "id": request_id}

    if trans.status == "pending":
        state = 1
    elif trans.status == "completed":
        state = 2
    else: # cancelled
        state = -2 if trans.completed_at else -1
        
    return {
        "jsonrpc": "2.0",
        "result": {
            "create_time": int(trans.created_at.timestamp() * 1000),
            "perform_time": int(trans.completed_at.timestamp() * 1000) if trans.completed_at else 0,
            "cancel_time": int(trans.cancel_time.timestamp() * 1000) if trans.cancel_time else 0,
            "transaction": str(trans.id),
            "state": state,
            "reason": trans.cancel_reason if trans.status == "cancelled" else None
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
    elif plan_name == "2_weeks":
        expires_at = now + timedelta(weeks=2)
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
    if plan_name not in ["day", "week", "2_weeks", "month"]:
        raise HTTPException(status_code=400, detail="Invalid plan name")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return activate_subscription_internal(user, plan_name, user.role, db)
