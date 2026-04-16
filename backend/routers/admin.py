from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Order, MasterProfile
from schemas import (
    UserResponse, OrderResponse, AdminUserUpdate, 
    AdminOrderUpdate, MessageResponse, AdminUserDetailResponse,
    AdminMasterProfileUpdate
)
from sqlalchemy import func
from routers.auth import get_current_admin
from routers.orders import build_order_response
from routers.masters import build_master_card
from models import Order, MasterProfile, Review
from websocket_manager import manager

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get system-wide statistics for the admin dashboard."""
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    online_users = manager.get_active_users_count()
    
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "online_users": online_users
    }

# ==================== USERS ====================

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get all users in the system."""
    return db.query(User).all()

@router.get("/users/{user_id}", response_model=AdminUserDetailResponse)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get full user account (Client + Master info + Stats)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    res = UserResponse.from_orm(user)
    master_card = None
    stats = []
    
    if user.master_profile:
        master_card = build_master_card(user.master_profile)
        # Calculate rating distribution
        counts = db.query(Review.rating, func.count(Review.id))\
            .filter(Review.master_id == user.master_profile.id)\
            .group_by(Review.rating)\
            .all()
        stats = [{"rating": r, "count": c} for r, c in counts]
        
    return AdminUserDetailResponse(
        **res.dict(),
        master_profile=master_card,
        review_stats=stats
    )

@router.put("/users/{user_id}/master", response_model=AdminUserDetailResponse)
def update_master_profile_admin(
    user_id: int,
    data: AdminMasterProfileUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Admin update of master profile data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.master_profile:
        raise HTTPException(status_code=404, detail="Master profile not found")
        
    profile = user.master_profile
    if data.subcategory_id is not None:
        profile.subcategory_id = data.subcategory_id
    if data.description is not None:
        profile.description = data.description
    if data.experience_years is not None:
        profile.experience_years = data.experience_years
    if data.hourly_rate is not None:
        profile.hourly_rate = data.hourly_rate
    if data.city is not None:
        profile.city = data.city
    if data.district is not None:
        profile.district = data.district
    if data.address is not None:
        profile.address = data.address
    if data.skills is not None:
        profile.skills = data.skills
    if data.is_available is not None:
        profile.is_available = data.is_available
        
    db.commit()
    db.refresh(user)
    return get_user_detail(user_id, db, admin)

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_admin(
    user_id: int,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Admin update of any user data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if data.name is not None:
        user.name = data.name
    if data.phone is not None:
        user.phone = data.phone
    if data.role is not None:
        user.role = data.role
    if data.city is not None:
        user.city = data.city
    if data.lang is not None:
        user.lang = data.lang
    if data.is_blocked is not None:
        user.is_blocked = data.is_blocked
        
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Delete a user and their associated profiles (via cascade)."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return MessageResponse(message=f"User {user_id} deleted successfully")

# ==================== ORDERS ====================

@router.get("/orders", response_model=List[OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get all orders in the system."""
    orders = db.query(Order).all()
    return [build_order_response(o) for o in orders]

@router.put("/orders/{order_id}", response_model=OrderResponse)
def update_order_admin(
    order_id: int,
    data: AdminOrderUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Admin update of any order data."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if data.description is not None:
        order.description = data.description
    if data.price is not None:
        order.price = data.price
    if data.status is not None:
        order.status = data.status
        
    db.commit()
    db.refresh(order)
    return build_order_response(order)

@router.delete("/orders/{order_id}", response_model=MessageResponse)
def delete_order_admin(
    order_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Delete an order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
    return MessageResponse(message=f"Order {order_id} deleted successfully")
