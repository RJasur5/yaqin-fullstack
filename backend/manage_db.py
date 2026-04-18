import os
import sys
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, Order, Subscription, MasterProfile, Category, Subcategory

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    print("\n" + "="*50)
    print(f" {text} ".center(50, "="))
    print("="*50)

def list_users(db: Session):
    print_header("USERS LIST")
    users = db.query(User).all()
    print(f"{'ID':<3} | {'Name':<20} | {'Phone':<15} | {'Role':<10} | {'Blocked':<7}")
    print("-" * 65)
    for u in users:
        print(f"{u.id:<3} | {u.name[:20]:<20} | {u.phone:<15} | {u.role:<10} | {u.is_blocked}")

def list_orders(db: Session):
    print_header("LATEST ORDERS")
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
    print(f"{'ID':<3} | {'Client':<15} | {'Subcat':<20} | {'Status':<10} | {'Price':<10}")
    print("-" * 65)
    for o in orders:
        client_name = o.client.name if o.client else "Unknown"
        subcat_name = o.subcategory.name_ru if o.subcategory else "Unknown"
        print(f"{o.id:<3} | {client_name[:15]:<15} | {subcat_name[:20]:<20} | {o.status:<10} | {o.price or 0}")

def view_subscriptions(db: Session):
    print_header("ACTIVE SUBSCRIPTIONS")
    subs = db.query(Subscription).filter(Subscription.is_active == True).all()
    print(f"{'UID':<3} | {'Plan':<10} | {'Limit':<6} | {'Used':<6} | {'Expires'}")
    print("-" * 65)
    for s in subs:
        expires = s.expires_at.strftime("%Y-%m-%d %H:%M") if s.expires_at else "NEVER"
        print(f"{s.user_id:<3} | {s.plan_name:<10} | {s.ads_limit:<6} | {s.ads_used:<6} | {expires}")

def activate_sub(db: Session):
    uid = input("Enter User ID: ")
    plan = input("Enter Plan (day/week/month): ").lower()
    
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        print("❌ User not found!")
        return
        
    # Import limits from router to stay consistent
    from routers.subscriptions import WORKER_PLAN_LIMITS, EMPLOYER_PLAN_LIMITS
    limits = WORKER_PLAN_LIMITS if user.role == "master" else EMPLOYER_PLAN_LIMITS
    
    if plan not in limits:
        print("❌ Invalid plan!")
        return

    now = datetime.now(timezone.utc)
    if plan == "day": expires = now + timedelta(days=1)
    elif plan == "week": expires = now + timedelta(weeks=1)
    else: expires = now + timedelta(days=30)
    
    sub = db.query(Subscription).filter(Subscription.user_id == uid).first()
    if not sub:
        sub = Subscription(user_id=uid, user_role=user.role, plan_name=plan, ads_limit=limits[plan], ads_used=0, expires_at=expires, is_active=True)
        db.add(sub)
    else:
        sub.plan_name = plan
        sub.ads_limit = limits[plan]
        sub.ads_used = 0
        sub.expires_at = expires
        sub.is_active = True
        
    db.commit()
    print(f"✅ Subscription '{plan}' activated for {user.name}")

def promote_admin(db: Session):
    uid = input("Enter User ID to make ADMIN: ")
    user = db.query(User).filter(User.id == uid).first()
    if user:
        user.role = "admin"
        db.commit()
        print(f"✅ {user.name} is now an ADMIN")
    else:
        print("❌ User not found")

def main():
    db = SessionLocal()
    while True:
        clear_screen()
        print_header("FINDIX DATABASE MANAGER")
        db_path = os.path.abspath("findix.db")
        print(f"📍 Database path: {db_path}")
        print("\n1. List Users")
        print("2. List Orders")
        print("3. View Subscriptions")
        print("4. Activate Subscription for User")
        print("5. Promote User to Admin")
        print("0. Exit")
        
        choice = input("\nSelect option: ")
        
        if choice == "1": list_users(db)
        elif choice == "2": list_orders(db)
        elif choice == "3": view_subscriptions(db)
        elif choice == "4": activate_sub(db)
        elif choice == "5": promote_admin(db)
        elif choice == "0": break
        
        input("\nPress Enter to continue...")
    
    db.close()

if __name__ == "__main__":
    main()
