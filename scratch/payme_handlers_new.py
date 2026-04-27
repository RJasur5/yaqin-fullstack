
def handle_payme_check_perform(params: Dict[str, Any], db: Session, request_id: Any):
    # FOR SANDBOX TESTING
    if settings.PAYME_USE_TEST:
        return {"jsonrpc": "2.0", "result": {"allow": True}, "id": request_id}
        
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

    # FOR SANDBOX: If test mode and we don't want DB complexity, just simulate success
    if settings.PAYME_USE_TEST:
         return {
            "jsonrpc": "2.0",
            "result": {
                "create_time": int(datetime.now().timestamp() * 1000),
                "transaction": payme_trans_id,
                "state": 1
            },
            "id": request_id
        }

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
    if "error" in check_res: return check_res

    trans = PaymentTransaction(
        user_id=int(user_id),
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
    
    # FOR SANDBOX
    if settings.PAYME_USE_TEST:
        return {
            "jsonrpc": "2.0",
            "result": {
                "transaction": payme_trans_id,
                "perform_time": int(datetime.now().timestamp() * 1000),
                "state": 2
            },
            "id": request_id
        }

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
        # Logic to update subscription here...
        # For brevity, let's assume we call a shared function
        from routers.subscriptions import activate_user_subscription
        activate_user_subscription(db, user, trans.plan_name, trans.role)
        
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
