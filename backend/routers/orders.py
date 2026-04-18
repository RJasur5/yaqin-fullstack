from fastapi import APIRouter, Depends, HTTPException, Query, Header, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime, timezone

from database import get_db, SessionLocal
from models import User, MasterProfile, Subcategory, Category, Order, ClientReview, Review, ChatMessage, Subscription
from schemas import OrderCreate, OrderResponse, MessageResponse, ClientReviewCreate, ReviewCreate, ChatMessageResponse, ChatMessageCreate, ChatSummaryResponse
from utils.security import mask_phone, filter_description
from routers.auth import get_current_user_from_header
from websocket_manager import manager
from notification_manager import notification_manager
import asyncio

router = APIRouter(prefix="/api/orders", tags=["Orders"])

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

def check_subscription(user_id: int, db: Session) -> bool:
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not sub:
        return False
    if not sub.is_active:
        return False
    if sub.expires_at < datetime.now(timezone.utc):
        sub.is_active = False
        db.commit()
        return False
    return True

def build_order_response(order: Order, is_subscribed: bool = True) -> OrderResponse:
    # Ensure created_at is timezone-aware UTC
    created_at = order.created_at
    if created_at and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
        
    res = OrderResponse(
        id=order.id,
        client_id=order.client_id,
        client_name=order.client.name,
        client_phone=order.client.phone,
        client_rating=order.client.client_rating,
        client_reviews_count=order.client.client_reviews_count,
        client_avatar=order.client.avatar,
        master_id=order.master_id,
        master_name=order.master.user.name if order.master else None,
        master_avatar=order.master.user.avatar if order.master else None,
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
        can_chat=is_subscribed
    )
    
    if not is_subscribed:
        res.client_phone = mask_phone(res.client_phone or "")
        res.description = filter_description(res.description or "")
        
    return res

@router.post("", response_model=OrderResponse)
def create_order(
    data: OrderCreate,
    background_tasks: BackgroundTasks,
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Ваш профиль заблокирован")
    
    # Check Subscription
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub or not sub.is_active or sub.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Для размещения объявлений требуется активная подписка")
    
    if sub.ads_used >= sub.ads_limit:
        raise HTTPException(status_code=403, detail=f"Лимит объявлений ({sub.ads_limit}) исчерпан")
        
    order = Order(
        client_id=user.id,
        subcategory_id=data.subcategory_id,
        description=data.description,
        city=data.city,
        district=data.district,
        price=data.price,
        include_lunch=data.include_lunch,
        include_taxi=data.include_taxi,
        status="open"
    )
    db.add(order)
    
    # Increment ads used
    sub.ads_used += 1
    
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
                
            # Skip if not online
            if m.user_id not in online_user_ids:
                continue
            
            # City filter
            if order.city and m.city and (order.city.lower() not in m.city.lower()):
                continue
                
            # District filter: if order has a specific district, only notify those in that district 
            # OR those with NO district filter (they work everywhere)
            ALL_DISTRICTS = "Все районы (весь город)"
            if order.district and order.district != ALL_DISTRICTS:
                if m.district and m.district != ALL_DISTRICTS and (order.district.lower() not in m.district.lower()):
                    continue
            
            targeted_user_ids.append(m.user_id)

        # DEBUG LOGGING (Very strict)
        print(f"NOTIFY DEBUG: Order {order.id} | Subcat: {order.subcategory_id} | City: {order.city} | District: {order.district}")
        print(f"NOTIFY DEBUG: Masters in DB for this subcat: {len(all_potential_user_ids)} {all_potential_user_ids}")
        print(f"NOTIFY DEBUG: Online users: {online_user_ids}")
        print(f"NOTIFY DEBUG: TARGETED FINAL: {targeted_user_ids}")
        
        if targeted_user_ids:
            for master_user_id in targeted_user_ids:
                background_tasks.add_task(
                    notification_manager.send_notification,
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
    
    query = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.subcategory)
    ).join(Subcategory).filter(Order.status == "open")
    
    if category_id:
        query = query.filter(Subcategory.category_id == category_id)
    if subcategory_id:
        query = query.filter(Order.subcategory_id == subcategory_id)
    if city:
        query = query.filter(Order.city.ilike(f"%{city}%"))
    if search:
        query = query.filter(
            (Order.description.ilike(f"%{search}%")) |
            (Subcategory.name_ru.ilike(f"%{search}%")) |
            (Subcategory.name_uz.ilike(f"%{search}%"))
        )
            
    orders = query.order_by(Order.created_at.desc()).all()
    
    is_subscribed = check_subscription(user.id, db)
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
        
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "open":
        raise HTTPException(status_code=400, detail="Order already accepted by another master")

        
    order.master_id = profile.id
    order.status = "accepted"
    order.accepted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(order)
    
    # Start auto-completion timer
    background_tasks.add_task(complete_order_after_delay, order.id)
    
    # --- INSTANT NOTIFICATION TO CLIENT ---
    try:
        await notification_manager.send_notification(
            order.client_id, "order_accepted",
            {
                "order_id": order.id,
                "master_name": order.master.user.name or order.master.user.phone,
                "subcategory_name_ru": order.subcategory.name_ru,
                "subcategory_name_uz": order.subcategory.name_uz,
            }
        )
    except Exception as e:
        print(f"NOTIFY ERROR in acceptance: {e}")
    # ------------------------------
    return build_order_response(order, is_subscribed=True)

    return build_order_response(order)

@router.get("/my", response_model=List[OrderResponse])
def get_my_orders(
    type: Optional[str] = Query(None, description="Filter by 'client' or 'master'"),
    authorization: str = Header(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    profile = db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
    master_id = profile.id if profile else -1
    
    query = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.master).joinedload(MasterProfile.user),
        joinedload(Order.subcategory)
    )
    
    if type == "client":
        query = query.filter(Order.client_id == user.id)
    elif type == "master":
        query = query.filter(Order.master_id == master_id)
    else:
        # Default: both
        query = query.filter((Order.client_id == user.id) | (Order.master_id == master_id))
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    # Auto-completion logic: if accepted > 5 mins ago, mark as completed
    now = datetime.now(timezone.utc)
    updated = False
    for o in orders:
        if o.status == "accepted" and o.accepted_at:
            # Ensure o.accepted_at has timezone info if it doesn't (SQLite sometimes has issues)
            acc_at = o.accepted_at
            if acc_at.tzinfo is None:
                acc_at = acc_at.replace(tzinfo=timezone.utc)
                
            diff = now - acc_at
            if diff.total_seconds() >= 60: # 1 minute for testing
                o.status = "completed"
                updated = True
    
    if updated:
        db.commit()
        # No need to refresh everything, just return the updated list
        
    is_subscribed = check_subscription(user.id, db)
    return [build_order_response(o, is_subscribed=is_subscribed) for o in orders]

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
        if (datetime.now(timezone.utc) - acc_at).total_seconds() >= 300:
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
    
    # Find all accepted or completed orders where user is participant
    orders = db.query(Order).outerjoin(MasterProfile, Order.master_id == MasterProfile.id).filter(
        ((Order.client_id == current_user.id) | (MasterProfile.user_id == current_user.id)) &
        (Order.status.in_(["accepted", "completed"]))
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
    if not is_client and not is_master:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому чату")
        
    msg = ChatMessage(order_id=order_id, sender_id=user.id, text=data.text)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    recipient_id = order.master.user_id if is_client else order.client_id
    
    # Notify recipient INSTANTLY
    try:
        # Ensure aware UTC before isoformat
        msg_created_at = msg.created_at
        if msg_created_at and msg_created_at.tzinfo is None:
            msg_created_at = msg_created_at.replace(tzinfo=timezone.utc)

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
        print(f"NOTIFY ERROR in chat: {e}")
    
    return msg

