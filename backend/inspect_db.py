from database import SessionLocal
from models import User, MasterProfile, Subcategory, Category

db = SessionLocal()
try:
    print("--- Masters in DB ---")
    masters = db.query(MasterProfile).all()
    for m in masters:
        user = db.query(User).filter(User.id == m.user_id).first()
        sub = db.query(Subcategory).filter(Subcategory.id == m.subcategory_id).first()
        print(f"User: {user.name} ({user.phone}), Subcategory: {sub.name_ru if sub else 'None'}, City: {m.city}")
    
    print("\n--- Online Users (Manager Stat) ---")
    # This might be harder since manager is in memory of the running process.
    # But I can check how many MasterProfiles exist per subcategory.
    from sqlalchemy import func
    counts = db.query(MasterProfile.subcategory_id, func.count(MasterProfile.id)).group_by(MasterProfile.subcategory_id).all()
    for sub_id, count in counts:
        sub = db.query(Subcategory).filter(Subcategory.id == sub_id).first()
        print(f"Subcategory {sub.name_ru if sub else sub_id}: {count} masters")

finally:
    db.close()
