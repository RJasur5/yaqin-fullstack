from fastapi import APIRouter, Depends, HTTPException, Query, Header, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime, timezone

from database import get_db, SessionLocal
from models import User, MasterProfile, Subcategory, Category, Order, ClientReview, Review, ChatMessage, Subscription, JobApplication, OrderAssignment
from schemas import OrderCreate, OrderResponse, MessageResponse, ClientReviewCreate, ReviewCreate, ChatMessageResponse, ChatMessageCreate, ChatSummaryResponse
from utils.security import mask_phone, filter_description
from utils.regions import normalize_region_name, get_region_variants
from routers.auth import get_current_user_from_header
from websocket_manager import manager
from notification_manager import notification_manager
import asyncio

router = APIRouter(prefix="/api/orders", tags=["Orders"])

async def auto_cancel_company_order(order_id: int):
    """Dynamically monitors the HR announcement and auto-cancels when time expires."""
    import asyncio
    from datetime import datetime, timezone, timedelta
    
    while True:
        db = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order or not order.is_company or order.status != "open":
                return  # Order is already closed or not valid
                
            now = datetime.now(timezone.utc)
            created_at_utc = order.created_at
            if created_at_utc.tzinfo is None:
                created_at_utc = created_at_utc.replace(tzinfo=timezone.utc)
                
            expires_at = created_at_utc + timedelta(minutes=5)
            remaining_seconds = (expires_at - now).total_seconds()
            
            if remaining_seconds <= 0:
                break  # Time is completely up, proceed to cancel!
                
            if remaining_seconds > 120:
                # Sleep until exactly 2 minutes are left
                sleep_time = remaining_seconds - 120
                db.close()
                await asyncio.sleep(sleep_time)
                continue
                
            # If we are exactly at or below 2 minutes left, send a warning
            try:
                await notification_manager.send_notification(
                    order.client_id, "hr_expiry_warning",
                    {
                        "order_id": order.id,
                        "subcategory_name_ru": order.subcategory.name_ru if order.subcategory else "",
                        "subcategory_name_uz": order.subcategory.name_uz if order.subcategory else "",
                        "minutes_left": 2,
                    }
                )
            except Exception as ne:
                print(f"BACKGROUND: Failed to send warning: {ne}")
                
            # Sleep the remaining time
            db.close()
            await asyncio.sleep(remaining_seconds)
            continue  # Loop back to verify time is actually up (in case they extended during the last 2 minutes)
            
        except Exception as e:
            print(f"BACKGROUND ERROR in monitor loop for order {order_id}: {e}")
            return
        finally:
            if 'db' in locals() and getattr(db, 'is_active', False):
                db.close()

    # Outside the loop: TIME IS UP!
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or not order.is_company or order.status != "open":
            return
            
        order.status = "cancelled"
        db.commit()
        
        # Find and close ALL pending child orders for this HR announcement
        pending_children = db.query(Order).filter(
            Order.client_id == order.client_id,
            Order.subcategory_id == order.subcategory_id,
            Order.is_company == True,
            Order.status == "pending",
            Order.id != order.id
        ).all()
        
        for child in pending_children:
            child.status = "vacancy_closed"
            db.commit()
            
            if child.master and child.master.user_id:
                try:
                    await notification_manager.send_notification(
                        child.master.user_id, "vacancy_closed",
                        {
                            "order_id": child.id,
                            "client_name": order.client.name if order.client else "",
                            "subcategory_name_ru": order.subcategory.name_ru if order.subcategory else "",
                            "subcategory_name_uz": order.subcategory.name_uz if order.subcategory else "",
                        }
                    )
                except Exception as ne:
                    pass
                    
        print(f"BACKGROUND: Company order {order_id} auto-cancelled. Closed {len(pending_children)} pending applications.")
        
        # Notify the HR employer via websocket that the vacancy was closed
        try:
            await notification_manager.send_notification(
                order.client_id, "vacancy_closed",
                {
                    "order_id": order.id,
                    "type": "vacancy_closed"
                }
            )
        except:
            pass

    except Exception as e:
        print(f"BACKGROUND ERROR auto-cancelling company order {order_id}: {e}")
    finally:
        db.close()

async def complete_order_after_delay(order_id: int):
    # Wait for 1 minute
    await asyncio.sleep(60)
    
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.status == "accepted":
            order.status = "completed"
            db.commit()
            
            # Notify master
            if order.master and order.master.user_id:
                await notification_manager.send_notification(
                    order.master.user_id, "order_completed",
                    {
                        "order_id": order.id,
                        "subcategory_name_ru": order.subcategory.name_ru,
                        "subcategory_name_uz": order.subcategory.name_uz,
                    }
                )
            
            # Notify client
            await notification_manager.send_notification(
                order.client_id, "order_completed",
                {
                    "order_id": order.id,
                    "subcategory_name_ru": order.subcategory.name_ru,
                    "subcategory_name_uz": order.subcategory.name_uz,
                }
            )
            
            print(f"BACKGROUND: Order {order_id} auto-completed and users notified.")
    except Exception as e:
        print(f"BACKGROUND ERROR auto-completing order {order_id}: {e}")
    finally:
        db.close()

async def auto_reject_company_order_application(order_id: int):
    # Wait for 5 minutes
    await asyncio.sleep(300)
    
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.is_company and order.status == "pending":
            order.status = "vacancy_closed"  # Вакансия закрыта (вместо rejected)
            db.commit()
            
            # Notify master
            if order.master and order.master.user_id:
                await notification_manager.send_notification(
                    order.master.user_id, "vacancy_closed",
                    {
                        "order_id": order.id,
                        "client_name": order.client.name if order.client else "",
                        "subcategory_name_ru": order.subcategory.name_ru if order.subcategory else "",
                        "subcategory_name_uz": order.subcategory.name_uz if order.subcategory else "",
                    }
                )
            print(f"BACKGROUND: Company child order {order_id} auto-closed (vacancy_closed) after 5 minutes.")
    except Exception as e:
        print(f"BACKGROUND ERROR auto-closing company order {order_id}: {e}")
    finally:
        db.close()

def check_subscription(user_id: int, role: str, db: Session) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
        
    # ADMINS ALWAYS HAVE ACCESS
    if user.role == "admin":
        return True

    sub = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).first()
    if not sub:
        return False
    if not sub.is_active:
        return False
        
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expires_at = sub.expires_at
    if expires_at and expires_at.tzinfo is not None:
        expires_at = expires_at.replace(tzinfo=None)
        
    if expires_at < now:
        # SPECIAL LOGIC: If it's a day plan and hasn't been used yet, don't expire it.
        if sub.plan_name == "day" and sub.ads_used == 0:
            pass # Keep it valid
        else:
            # Auto-expire
            sub.is_active = False
            db.commit()
            return False
        
    return True

def can_accept_orders(user_id: int, role: str, db: Session) -> bool:
    if not check_subscription(user_id, role, db):
        return False
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if sub and sub.ads_used >= sub.ads_limit:
        return False
    return True

def build_order_response(order: Order, is_subscribed: bool = True, override_master: Optional[MasterProfile] = None) -> OrderResponse:
    from datetime import timedelta
    # Ensure created_at is timezone-aware UTC
    created_at = order.created_at
    if created_at and created_at.tzinfo is not None:
        created_at = created_at.replace(tzinfo=None)
    
    # For HR announcements, calculate when it expires (5 min after creation)
    expires_at = None
    if order.is_company and order.status == "open" and created_at:
        expires_at = created_at + timedelta(minutes=5)
    
    # Use override_master if provided (for multiple assignments), otherwise use order.master
    m_profile = override_master if override_master else order.master
        
    res = OrderResponse(
        id=order.id,
        client_id=order.client_id,
        client_name=order.client.name,
        client_phone=order.client.phone,
        client_rating=order.client.client_rating,
        client_reviews_count=order.client.client_reviews_count,
        client_avatar=order.client.avatar,
        master_id=m_profile.id if m_profile else None,
        master_name=m_profile.user.name if m_profile else None,
        master_avatar=m_profile.user.avatar if m_profile else None,
        subcategory_id=order.subcategory_id,
        subcategory_name_ru=order.subcategory.name_ru,
        subcategory_name_uz=order.subcategory.name_uz,
        description=order.description,
        city=order.city,
        district=order.district,
        price=order.price,
        status=order.status,
        created_at=created_at,
        is_client_reviewed=order.is_client_reviewed,
        is_master_reviewed=order.is_master_reviewed,
        include_lunch=order.include_lunch,
        include_taxi=order.include_taxi,
        can_chat=is_subscribed,
        is_application=False,
        is_company=order.is_company,
        applicants_count=len(order.assignments) if order.assignments else 0,
        expires_at=expires_at,
    )
    
    if not is_subscribed:
        res.client_phone = mask_phone(res.client_phone or "")
        res.description = filter_description(res.description or "")
        
    return res

def build_application_order_response(app: JobApplication) -> OrderResponse:
    """Maps a JobApplication to an OrderResponse for the 'My Orders' view."""
    created_at = app.created_at
    if created_at and created_at.tzinfo is not None:
        created_at = created_at.replace(tzinfo=None)
        
    return OrderResponse(
        id=app.id,
        client_id=app.employer_id,
        client_name=app.employer.name,
        client_phone=app.phone or app.employer.phone,
        client_rating=app.employer.client_rating,
        client_reviews_count=app.employer.client_reviews_count,
        client_avatar=app.employer.avatar,
        master_id=app.master_id,
        master_name=app.master.user.name,
        master_avatar=app.master.user.avatar,
        subcategory_id=app.master.subcategory_id,
        subcategory_name_ru=app.master.subcategory.name_ru,
        subcategory_name_uz=app.master.subcategory.name_uz,
        description=app.description,
        city=app.city or app.master.city or "",
        district=None,
        price=None,
        status=app.status,
        created_at=created_at,
        is_client_reviewed=False,
        is_master_reviewed=False,
        include_lunch=False,
        include_taxi=False,
        can_chat=False, # Chat only after acceptance
        is_application=True
    )

@router.post("", response_model=OrderResponse)
async def create_order(
    data: OrderCreate,
    background_tasks: BackgroundTasks,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Ваш профиль заблокирован")
    # Note: Employers no longer need a subscription to post ads (free for employers)
    # Only masters need subscriptions (to accept orders)
        
    order = Order(
        client_id=user.id,
        subcategory_id=data.subcategory_id,
        description=data.description,
        city=data.city,
        district=data.district,
        price=data.price,
        include_lunch=data.include_lunch,
        include_taxi=data.include_taxi,
        is_company=data.is_company,
        status="open"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Reload with relations
    order = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.subcategory)
    ).filter(Order.id == order.id).first()

    # --- STRICT NOTIFICATION LOGIC ---
    try:
        online_user_ids = list(manager.active_connections.keys())
        
        # 1. Strict Query for Masters in this subcategory
        # We also join with User to be able to log their names for debugging
        matching_masters = db.query(MasterProfile).filter(
            MasterProfile.subcategory_id == order.subcategory_id,
            MasterProfile.is_blocked == False
        ).all()
        
        all_potential_user_ids = [m.user_id for m in matching_masters]
        
        # 2. Filter by City/District
        targeted_user_ids = []
        for m in matching_masters:
            # Skip if it's the creator
            if m.user_id == user.id:
                continue
            
            # Normalize names to handle Ru/Uz language differences
            order_city_norm = normalize_region_name(order.city) if order.city else ""
            m_city_norm = normalize_region_name(m.city) if m.city else ""
            
            # City filter
            if order_city_norm and m_city_norm and (order_city_norm not in m_city_norm):
                continue
                
            # District filter: if order has a specific district, only notify those in that district 
            # OR those with NO district filter (they work everywhere)
            order_dist_norm = normalize_region_name(order.district) if order.district else ""
            m_dist_norm = normalize_region_name(m.district) if m.district else ""
            
            ALL_DISTRICTS_NORM = ["barcha tumanlar"]
            if order_dist_norm and order_dist_norm not in ALL_DISTRICTS_NORM:
                if m_dist_norm and m_dist_norm not in ALL_DISTRICTS_NORM and (order_dist_norm not in m_dist_norm):
                    continue
            
            targeted_user_ids.append(m.user_id)

        # DEBUG LOGGING (Very strict)
        print(f"NOTIFY DEBUG: Order {order.id} | Subcat: {order.subcategory_id} | City: {order.city} | District: {order.district}")
        print(f"NOTIFY DEBUG: Masters in DB for this subcat: {len(all_potential_user_ids)} {all_potential_user_ids}")
        print(f"NOTIFY DEBUG: Online users: {online_user_ids}")
        print(f"NOTIFY DEBUG: TARGETED FINAL: {targeted_user_ids}")
        
        if targeted_user_ids:
            for master_user_id in targeted_user_ids:
                try:
                    await notification_manager.send_notification(
                        master_user_id, "new_order",
                        {
                            "order_id": order.id,
                            "subcategory_id": order.subcategory_id,
                            "subcategory_name_ru": order.subcategory.name_ru,
                            "subcategory_name_uz": order.subcategory.name_uz,
                            "description": order.description,
                            "city": order.city,
                            "district": order.district,
                            "price": order.price
                        }
                    )
                except Exception as ne:
                    print(f"NOTIFY ERROR for user {master_user_id}: {ne}")
            
    except Exception as e:
        print(f"NOTIFY CRITICAL ERROR: {e}")
    # ---------------------------------

    return build_order_response(order, is_subscribed=True)

@router.get("/available", response_model=List[OrderResponse])
def get_available_orders(
    category_id: Optional[int] = Query(None),
    subcategory_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    
    # Filter out orders older than 30 days
    from datetime import timedelta
    thirty_days_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)

    
    query = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.subcategory),
        joinedload(Order.assignments)
    ).join(Subcategory).filter(
        Order.status == "open",
        Order.created_at >= thirty_days_ago
    )
    
    if category_id:
        query = query.filter(Subcategory.category_id == category_id)
    if subcategory_id:
        query = query.filter(Order.subcategory_id == subcategory_id)
    if city:
        variants = get_region_variants(city)
        if len(variants) > 1:
            from sqlalchemy import or_
            conditions = [Order.city.ilike(f"%{v}%") for v in variants]
            query = query.filter(or_(*conditions))
        else:
            query = query.filter(Order.city.ilike(f"%{city}%"))
    if search:
        query = query.filter(
            (Order.description.ilike(f"%{search}%")) |
            (Subcategory.name_ru.ilike(f"%{search}%")) |
            (Subcategory.name_uz.ilike(f"%{search}%"))
        )
            
    orders = query.order_by(Order.created_at.desc()).all()
    
    # Check if user has master subscription to see full details (phone/description)
    is_subscribed = can_accept_orders(user.id, "master", db)
    return [build_order_response(o, is_subscribed=is_subscribed) for o in orders]


@router.post("/{order_id}/accept", response_model=OrderResponse)
async def accept_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    profile = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=403, detail="Only masters can accept orders")

    order = db.query(Order).options(
        joinedload(Order.assignments)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.is_company:
        # Check if master already accepted this order
        already_accepted = db.query(OrderAssignment).filter(
            OrderAssignment.order_id == order_id,
            OrderAssignment.master_id == profile.id
        ).first()
        if already_accepted:
            raise HTTPException(status_code=400, detail="Вы уже откликнулись на это объявление")
            
        # Companies can hire up to 1000 people (unlimited recruitment)
        if len(order.assignments) >= 1000:
             raise HTTPException(status_code=400, detail="На это объявление уже набрано максимальное количество откликов")

    # --- SUBSCRIPTION CHECK FOR WORKER (Risking money) ---
    if user.role != "admin":
        if not can_accept_orders(user.id, "master", db):
            raise HTTPException(status_code=403, detail="Лимит принятых заказов исчерпан или нет подписки. Пожалуйста, обновите подписку.")
            
        sub = db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()
        if not sub:
            raise HTTPException(status_code=403, detail="Подписка мастера не найдена")
        
        sub.ads_used += 1
    # -------------------------------------

    if order.is_company:
        # This matches the "as usual" behavior (like JobApplication)
        final_order = Order(
            client_id=order.client_id,
            master_id=profile.id,
            subcategory_id=order.subcategory_id,
            description=order.description,
            city=order.city,
            district=order.district,
            price=order.price,
            include_lunch=order.include_lunch,
            include_taxi=order.include_taxi,
            status="pending",
            accepted_at=datetime.now(timezone.utc).replace(tzinfo=None),
            is_company=True # Preserve company flag for UI to show 'Reject' button
        )
        db.add(final_order)
        db.flush() # Get the new ID for notifications

        # Track assignment on the ORIGINAL order for duplicate checking and statistics
        assignment = OrderAssignment(order_id=order.id, master_id=profile.id)
        db.add(assignment)
        
        # For the first master, also mark the original order as "active" but keep it OPEN
        if not order.master_id:
            order.master_id = profile.id
            order.accepted_at = datetime.now(timezone.utc).replace(tzinfo=None)
            # Start 3-minute auto-cancel timer on original announcement
            background_tasks.add_task(auto_cancel_company_order, order.id)
        
        # Start auto-reject timer for the CHILD order (application)
        background_tasks.add_task(auto_reject_company_order_application, final_order.id)
        
    else:
        # Standard logic
        if order.status != "open":
            raise HTTPException(status_code=400, detail="Order already accepted by another master")
            
        order.master_id = profile.id
        order.status = "accepted"
        order.accepted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Also create assignment for consistency
        assignment = OrderAssignment(order_id=order.id, master_id=profile.id)
        db.add(assignment)
        
        # Start auto-completion timer
        background_tasks.add_task(complete_order_after_delay, order.id)
        final_order = order
    
    db.commit()
    db.refresh(final_order)
    
    # --- INSTANT NOTIFICATION TO CLIENT ---
    # IMPORTANT: Using await directly instead of background_tasks.add_task() because
    # background_tasks silently drops async coroutines without executing them.
    notify_data = {
        "order_id": final_order.id,
        "master_name": user.name or user.phone,
        "subcategory_name_ru": final_order.subcategory.name_ru,
        "subcategory_name_uz": final_order.subcategory.name_uz,
        "is_company": str(order.is_company)
    }
    print(f"NOTIFY: Sending order_accepted to client_id={final_order.client_id}, data={notify_data}")
    try:
        await notification_manager.send_notification(
            final_order.client_id, "order_accepted", notify_data
        )
        print(f"NOTIFY: Successfully sent order_accepted to client_id={final_order.client_id}")
    except Exception as e:
        print(f"NOTIFY ERROR: Failed to send notification: {e}")
    # ------------------------------
    return build_order_response(final_order, is_subscribed=True, override_master=profile)

@router.get("/my", response_model=List[OrderResponse])
def get_my_orders(
    type: Optional[str] = Query(None, description="Filter by 'client' or 'master'"),
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """
    Returns orders and applications for the current user, filtered by role.
    - type='client' (My Orders): orders user CREATED + applications user SENT
    - type='master' (Accepted Orders): orders user ACCEPTED as worker + rejected applications FROM employers
    - type=None: everything (backwards compat)
    """
    user = get_current_user_from_header(authorization, db)
    profile = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
    master_id = profile.id if profile else -1
    
    is_subscribed = check_subscription(user.id, "master", db)
    order_responses = []
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # ------------------------------------------------------------------
    # EMPLOYER SIDE: orders I created + applications I sent
    # ------------------------------------------------------------------
    if type != "master":
        employer_orders = db.query(Order).options(
            joinedload(Order.client),
            joinedload(Order.master).joinedload(MasterProfile.user),
            joinedload(Order.subcategory),
            joinedload(Order.assignments).joinedload(OrderAssignment.master).joinedload(MasterProfile.user)
        ).filter(Order.client_id == user.id).order_by(Order.created_at.desc()).all()
        
        for o in employer_orders:
            # Auto-complete logic for standard orders
            if not o.is_company and o.status == "accepted" and o.accepted_at:
                acc_at = o.accepted_at.replace(tzinfo=None) if o.accepted_at.tzinfo else o.accepted_at
                if (now - acc_at).total_seconds() >= 86400:
                    o.status = "completed"
                    db.commit()
            if o.is_company and o.status == "open":
                # For company announcements, show the main entry once.
                # Accepted candidates will show up as separate 'accepted' orders.
                resp = build_order_response(o, is_subscribed=is_subscribed)
                resp.my_role = "employer"
                order_responses.append(resp)
            else:
                # Standard order or accepted child order
                resp = build_order_response(o, is_subscribed=is_subscribed)
                resp.my_role = "employer"
                order_responses.append(resp)
        
        apps_sent = db.query(JobApplication).options(
            joinedload(JobApplication.employer),
            joinedload(JobApplication.master).joinedload(MasterProfile.user),
            joinedload(JobApplication.master).joinedload(MasterProfile.subcategory)
        ).filter(
            JobApplication.employer_id == user.id,
            JobApplication.status.in_(["pending", "viewed", "rejected"])
        ).all()
        for a in apps_sent:
            resp = build_application_order_response(a)
            resp.my_role = "employer"
            order_responses.append(resp)
    
    # ------------------------------------------------------------------
    # WORKER SIDE: orders I accepted + rejected applications from employers
    # ------------------------------------------------------------------
    if type != "client" and profile:
        # 1. Direct orders (new logic: child orders for company announcements)
        direct_master_orders = db.query(Order).options(
            joinedload(Order.client),
            joinedload(Order.subcategory),
            joinedload(Order.assignments)
        ).filter(Order.master_id == profile.id).all()
        
        for o in direct_master_orders:
            # Skip the main company order which was created by someone else and has assignments
            if o.is_company and o.client_id != user.id and len(o.assignments) > 0:
                continue
            
            # Auto-complete check
            if not o.is_company and o.status == "accepted" and o.accepted_at:
                acc_at = o.accepted_at.replace(tzinfo=None) if o.accepted_at.tzinfo else o.accepted_at
                if (now - acc_at).total_seconds() >= 86400:
                    o.status = "completed"
                    db.commit()
            
            resp = build_order_response(o, is_subscribed=is_subscribed, override_master=profile)
            resp.my_role = "worker"
            order_responses.append(resp)
            
        existing_ids_with_master = {(r.id, r.master_id) for r in order_responses}

        # 2. Assignments (old logic and backward compat)
        assignments = db.query(OrderAssignment).options(
            joinedload(OrderAssignment.order).joinedload(Order.client),
            joinedload(OrderAssignment.order).joinedload(Order.subcategory),
            joinedload(OrderAssignment.order).joinedload(Order.assignments)
        ).filter(OrderAssignment.master_id == profile.id).all()
        
        for assign in assignments:
            o = assign.order
            if o.is_company:
                continue
            if (o.id, profile.id) in existing_ids_with_master:
                continue
            
            # Auto-complete check
            if not o.is_company and o.status == "accepted" and o.accepted_at:
                acc_at = o.accepted_at.replace(tzinfo=None) if o.accepted_at.tzinfo else o.accepted_at
                if (now - acc_at).total_seconds() >= 86400:
                    o.status = "completed"
                    db.commit()
            
            resp = build_order_response(o, is_subscribed=is_subscribed, override_master=profile)
            resp.my_role = "worker"
            order_responses.append(resp)
        
        # 3. Rejected job applications
        apps_rejected = db.query(JobApplication).options(
            joinedload(JobApplication.employer),
            joinedload(JobApplication.master).joinedload(MasterProfile.user),
            joinedload(JobApplication.master).joinedload(MasterProfile.subcategory)
        ).filter(
            JobApplication.master_id == profile.id,
            JobApplication.status == "rejected"
        ).all()
        
        for a in apps_rejected:
            # Applications don't have order_id, so we use a different check or just append
            resp = build_application_order_response(a)
            resp.my_role = "worker"
            order_responses.append(resp)

    order_responses.sort(key=lambda x: x.created_at, reverse=True)
    return order_responses

@router.post("/{order_id}/rate_client", response_model=MessageResponse)
def rate_client(
    order_id: int,
    data: ClientReviewCreate,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    profile = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=403, detail="Только мастера могут оценивать клиентов")
        
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.master_id != profile.id:
        raise HTTPException(status_code=403, detail="Вы не являетесь мастером этого заказа")
        
    # Check if 5 minutes passed if it's still 'accepted'
    can_rate = order.status == "completed"
    if order.status == "accepted" and order.accepted_at:
        acc_at = order.accepted_at
        if acc_at.tzinfo is None:
            acc_at = acc_at.replace(tzinfo=timezone.utc)
        if (datetime.now(timezone.utc).replace(tzinfo=None) - acc_at).total_seconds() >= 300:
            can_rate = True
            
    if not can_rate:
        raise HTTPException(status_code=400, detail="Оценить можно только завершенный заказ (через 5 минут после принятия)")
        
    if order.is_client_reviewed:
        raise HTTPException(status_code=400, detail="Вы уже оставили отзыв по этому заказу")
        
    review = ClientReview(
        client_id=order.client_id,
        master_id=profile.id,
        rating=data.rating,
        comment=data.comment
    )
    db.add(review)
    
    # Update order flag
    order.is_client_reviewed = True
    
    db.commit()
    
    # Recalculate client rating
    client_user = db.query(User).filter(User.id == order.client_id).first()
    reviews = db.query(ClientReview).filter(ClientReview.client_id == client_user.id).all()
    if reviews:
        count = len(reviews)
        avg = sum(r.rating for r in reviews) / count
        client_user.client_reviews_count = count
        client_user.client_rating = avg
        
        # Checking logic for a permanent ban (3 reviews <= 2 stars)
        bad_reviews = [r for r in reviews if r.rating <= 2]
        if len(bad_reviews) >= 3:
            client_user.is_blocked = True
            
        db.commit()
    return MessageResponse(message="Отзыв успешно сохранен")

@router.post("/{order_id}/rate_master", response_model=MessageResponse)
def rate_master(
    order_id: int,
    data: ReviewCreate,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.client_id != user.id:
        raise HTTPException(status_code=403, detail="Вы не являетесь владельцем этого заказа")
    if not order.master_id:
        raise HTTPException(status_code=400, detail="У заказа нет мастера")
    if order.is_master_reviewed:
        raise HTTPException(status_code=400, detail="Вы уже оставили отзыв")
        
    review = Review(
        master_id=order.master_id,
        client_id=user.id,
        rating=data.rating,
        comment=data.comment
    )
    db.add(review)
    
    # Update average rating for master
    master = order.master
    all_reviews = db.query(Review).filter(Review.master_id == master.id).all()
    # add current review conceptually
    ratings = [r.rating for r in all_reviews] + [data.rating]
    master.rating = sum(ratings) / len(ratings)
    master.reviews_count = len(ratings)
    
    # Mark order reviewed
    order.is_master_reviewed = True
    
    db.commit()
    return MessageResponse(message="Отзыв мастеру успешно сохранен")

@router.get("/{order_id}/chat", response_model=List[ChatMessageResponse])
def get_chat_history(
    order_id: int,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    
    print(f"DEBUG: get_chat_history for order {order_id}, user {user.id} ({user.name})")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        print(f"DEBUG: Order {order_id} not found")
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    is_client = order.client_id == user.id
    is_master = order.master and order.master.user_id == user.id
    
    # For company orders, also check if user has an assignment
    if not is_master and not is_client:
        profile = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
        if profile:
            assignment = db.query(OrderAssignment).filter(
                OrderAssignment.order_id == order_id,
                OrderAssignment.master_id == profile.id
            ).first()
            if assignment:
                is_master = True
    
    print(f"DEBUG: is_client={is_client}, is_master={is_master}, order_status={order.status}")
    
    if not is_client and not is_master:
        print(f"DEBUG: Access denied for user {user.id} to order {order_id}")
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому чату")
        
    messages = db.query(ChatMessage).filter(ChatMessage.order_id == order_id).order_by(ChatMessage.created_at.asc()).all()
    # Ensure they are aware UTC
    for m in messages:
        if m.created_at and m.created_at.tzinfo is None:
            m.created_at = m.created_at.replace(tzinfo=timezone.utc)
    print(f"DEBUG: Found {len(messages)} messages")
    return messages

@router.get("/chats", response_model=List[ChatSummaryResponse])
async def get_chat_list(
    db: Session = Depends(get_db),
    authorization: str = Header("")
):
    """
    Returns a list of orders the user is participating in, 
    with the latest message and details of the other participant.
    """
    current_user = get_current_user_from_header(authorization, db)
    print(f"DEBUG: get_chat_list for user {current_user.id} ({current_user.name})")
    
    # Find all orders where user is participant and status is relevant for chat
    # We now include 'cancelled' and 'rejected' so users can see the final status/history
    orders = db.query(Order).outerjoin(MasterProfile, Order.master_id == MasterProfile.id).filter(
        ((Order.client_id == current_user.id) | (MasterProfile.user_id == current_user.id)) &
        (Order.status.in_(["accepted", "accepted_hr", "completed", "cancelled", "rejected", "vacancy_closed", "pending"]))
    ).all()
    
    print(f"DEBUG: Found {len(orders)} relevant orders for chat list")
    
    chats = []
    for order in orders:
        # Get last message
        last_msg = db.query(ChatMessage).filter(ChatMessage.order_id == order.id).order_by(ChatMessage.created_at.desc()).first()
        
        # Determine the "other" person
        is_client = current_user.id == order.client_id
        is_master = order.master and current_user.id == order.master.user_id
        
        print(f"DEBUG: Order {order.id}: is_client={is_client}, is_master={is_master}, master_id={order.master_id}")
        other = None
        if is_client:
            # I am client, the other is master
            if order.master:
                other = order.master.user
        elif is_master:
            # I am master, the other is client
            other = order.client
            
        if not other: continue
        
        # Calculate unread count (messages NOT sent by current_user and NOT read)
        unread_count = db.query(ChatMessage).filter(
            ChatMessage.order_id == order.id,
            ChatMessage.sender_id != current_user.id,
            ChatMessage.is_read == False
        ).count()
        
        # Ensure times are aware UTC
        msg_time = last_msg.created_at if last_msg else order.created_at
        if msg_time and msg_time.tzinfo is None:
            msg_time = msg_time.replace(tzinfo=timezone.utc)

        chats.append(ChatSummaryResponse(
            order_id=order.id,
            other_user_id=other.id,
            other_user_name=other.name,
            other_user_avatar=other.avatar,
            other_user_role=other.role,
            other_master_id=order.master.id if is_client and order.master else None,
            last_message=last_msg.text if last_msg else None,
            last_message_time=msg_time,
            subcategory_name_ru=order.subcategory.name_ru,
            subcategory_name_uz=order.subcategory.name_uz,
            unread_count=unread_count
        ))
        
    # Sort by the most recent message or update time
    chats.sort(key=lambda x: x.last_message_time, reverse=True)
    return chats

@router.post("/{order_id}/read", response_model=MessageResponse)
async def mark_chat_as_read(
    order_id: int,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """
    Marks all messages in an order as read for the current user.
    """
    current_user = get_current_user_from_header(authorization, db)
    
    # Mark messages sent by the OTHER person as read
    db.query(ChatMessage).filter(
        ChatMessage.order_id == order_id,
        ChatMessage.sender_id != current_user.id,
        ChatMessage.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    return {"message": "All messages marked as read"}

@router.post("/{order_id}/chat", response_model=ChatMessageResponse)
async def send_chat_message(
    order_id: int,
    data: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    from schemas import ChatMessageCreate, ChatMessageResponse
    user = get_current_user_from_header(authorization, db)
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    # Verify participant
    is_client = order.client_id == user.id
    is_master = order.master and order.master.user_id == user.id
    
    # For company orders, check assignments too
    if not is_master and not is_client:
        profile = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
        if profile:
            assignment = db.query(OrderAssignment).filter(
                OrderAssignment.order_id == order_id,
                OrderAssignment.master_id == profile.id
            ).first()
            if assignment:
                is_master = True
    
    if not is_client and not is_master:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому чату")
        
    msg = ChatMessage(order_id=order_id, sender_id=user.id, text=data.text)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    recipient_id = order.master.user_id if is_client else order.client_id
    
    # Notify recipient in BACKGROUND to keep chat snappy
    # Ensure aware UTC before isoformat
    msg_created_at = msg.created_at
    if msg_created_at and msg_created_at.tzinfo is None:
        msg_created_at = msg_created_at.replace(tzinfo=timezone.utc)

    try:
        await notification_manager.send_notification(
            recipient_id, "chat_message",
            {
                "order_id": order.id,
                "sender_id": user.id,
                "sender_name": user.name,
                "text": data.text,
                "created_at": msg_created_at.isoformat()
            }
        )
    except Exception as e:
        print(f"NOTIFY ERROR chat_message: {e}")
    
    return msg


@router.put("/{order_id}/cancel", response_model=MessageResponse)
async def cancel_order(
    order_id: int,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """
    Client cancels their order. 
    If the order was accepted by a master within the last 5 minutes, 
    the master gets a 'refund' of their ads_used limit.
    """
    user = get_current_user_from_header(authorization, db)
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    if order.client_id != user.id:
        raise HTTPException(status_code=403, detail="Вы не можете отменить чужой заказ")
        
    if order.status == "completed":
        raise HTTPException(status_code=400, detail="Завершенный заказ нельзя отменить")
        
    if order.status == "cancelled":
        return MessageResponse(message="Заказ уже отменен")

    order.status = "cancelled"
    
    # Reject all pending job applications from this employer
    from models import JobApplication
    pending_apps = db.query(JobApplication).filter(
        JobApplication.employer_id == user.id,
        JobApplication.status == "pending"
    ).all()
    for app in pending_apps:
        app.status = "rejected"
        
    # Also find and close ALL pending child orders for this HR announcement
    if order.is_company:
        pending_children = db.query(Order).filter(
            Order.client_id == order.client_id,
            Order.subcategory_id == order.subcategory_id,
            Order.is_company == True,
            Order.status == "pending",
            Order.id != order.id  # Exclude the parent
        ).all()
        for child in pending_children:
            child.status = "vacancy_closed"  # Вакансия закрыта
            db.commit()
            if child.master and child.master.user_id:
                try:
                    await notification_manager.send_notification(
                        child.master.user_id, "vacancy_closed",
                        {
                            "order_id": child.id,
                            "client_name": user.name,
                            "subcategory_name_ru": order.subcategory.name_ru if order.subcategory else "",
                            "subcategory_name_uz": order.subcategory.name_uz if order.subcategory else "",
                        }
                    )
                except Exception:
                    pass

    db.commit()

    # Notify master about cancellation
    if order.master_id and not order.is_company:
        master_user = db.query(User).join(MasterProfile).filter(MasterProfile.id == order.master_id).first()
        if master_user:
            await notification_manager.send_notification(
                master_user.id, "order_cancelled",
                {
                    "order_id": order.id,
                    "client_name": user.name,
                    "status": "cancelled"
                }
            )

    return MessageResponse(message="Заказ успешно отменен")


@router.put("/{order_id}/reject", response_model=MessageResponse)
async def reject_master(
    order_id: int,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """
    Employer rejects a master who accepted their order.
    The order status changes to 'rejected'.
    """
    user = get_current_user_from_header(authorization, db)
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    if order.client_id != user.id:
        raise HTTPException(status_code=403, detail="Вы не можете отклонить мастера в чужом заказе")
        
    if order.status == "completed":
        raise HTTPException(status_code=400, detail="Завершенный заказ нельзя отклонить")
        
    if order.status == "rejected":
        return MessageResponse(message="Мастер уже отклонен")

    order.status = "rejected"
    db.commit()
    
    # Notify master about rejection
    if order.master_id:
        master_user = db.query(User).join(MasterProfile).filter(MasterProfile.id == order.master_id).first()
        if master_user:
            await notification_manager.send_notification(
                master_user.id, "order_rejected",
                {
                    "order_id": order.id,
                    "client_name": user.name,
                    "subcategory_name_ru": order.subcategory.name_ru,
                    "subcategory_name_uz": order.subcategory.name_uz,
                }
            )
            
    return MessageResponse(message="Мастер успешно отклонен")


@router.put("/{order_id}/hr-accept", response_model=MessageResponse)
async def hr_accept_master(
    order_id: int,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """
    Employer formally accepts a master's application to an HR order.
    Sets the child order status to 'accepted' (Принято).
    """
    user = get_current_user_from_header(authorization, db)
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    if order.client_id != user.id:
        raise HTTPException(status_code=403, detail="Вы не можете управлять чужим заказом")
        
    if order.status == "accepted_hr":
        return MessageResponse(message="Мастер уже принят на работу")
        
    if order.status in ("vacancy_closed", "rejected", "cancelled"):
        raise HTTPException(status_code=400, detail="Невозможно принять мастера в этом статусе")

    order.status = "accepted_hr"  # Принято (вместо completed)
    db.commit()
    
    # Notify master about acceptance
    if order.master_id:
        master_user = db.query(User).join(MasterProfile).filter(MasterProfile.id == order.master_id).first()
        if master_user:
            asyncio.create_task(
                notification_manager.send_notification(
                    master_user.id, "hr_accepted",
                    {
                        "order_id": order.id,
                        "client_name": user.name,
                        "subcategory_name_ru": order.subcategory.name_ru,
                        "subcategory_name_uz": order.subcategory.name_uz,
                    }
                )
            )
            
    return MessageResponse(message="Мастер успешно принят на работу")


@router.post("/{order_id}/extend-hr", response_model=MessageResponse)
async def extend_hr_announcement(
    order_id: int,
    background_tasks: BackgroundTasks,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """
    HR employer extends the active announcement by 5 more minutes.
    Can be called after receiving the 'hr_expiry_warning' notification.
    """
    user = get_current_user_from_header(authorization, db)
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    if order.client_id != user.id:
        raise HTTPException(status_code=403, detail="Вы не можете управлять чужим заказом")
    
    if not order.is_company:
        raise HTTPException(status_code=400, detail="Продление возможно только для HR-объявлений")
    
    if order.status != "open":
        raise HTTPException(status_code=400, detail="Объявление уже завершено или закрыто")
    
    # Shift created_at by 5 minutes forward to extend the deadline
    from datetime import timedelta
    if order.created_at:
        order.created_at = order.created_at + timedelta(minutes=5)
        db.commit()

    # The background task is already running in a while loop. 
    # It will automatically detect the new created_at and adjust its sleep time!
    
    print(f"EXTEND: HR announcement {order_id} extended by 5 minutes by user {user.id}")
    return MessageResponse(message="Объявление продлено на 5 минут")


@router.put("/{order_id}/cancel-others", response_model=MessageResponse)
async def cancel_others(
    order_id: int,
    keep_master_id: Optional[int] = Query(None, description="Master ID to keep (optional)"),
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    """
    Employer cancels all other assignments for a company/HR order.
    Optionally keeps one master (keep_master_id).
    If no keep_master_id is given, cancels the entire order.
    """
    user = get_current_user_from_header(authorization, db)
    order = db.query(Order).options(
        joinedload(Order.assignments).joinedload(OrderAssignment.master).joinedload(MasterProfile.user)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.client_id != user.id:
        raise HTTPException(status_code=403, detail="Вы не можете управлять чужим заказом")
    if not order.is_company:
        raise HTTPException(status_code=400, detail="Эта функция только для HR-объявлений")
    
    notified_count = 0
    for assign in order.assignments:
        if keep_master_id and assign.master_id == keep_master_id:
            continue
        # Notify the cancelled master
        master_user = assign.master.user if assign.master else None
        if master_user:
            await notification_manager.send_notification(
                master_user.id, "order_cancelled",
                {"order_id": order.id, "client_name": user.name}
            )
            notified_count += 1
        db.delete(assign)
    
    if keep_master_id:
        # Set order to accepted with the chosen master
        order.master_id = keep_master_id
        order.status = "accepted"
        order.accepted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        # Cancel the entire order
        order.status = "cancelled"
    
    db.commit()
    return MessageResponse(message=f"Отменено {notified_count} откликов")
