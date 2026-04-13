from database import SessionLocal
from models import MasterProfile, User, Subcategory

db = SessionLocal()
try:
    masters = db.query(MasterProfile).all()
    print(f"{'UserID':<8} | {'Name':<15} | {'SubID':<6} | {'SubName (RU)':<25} | {'City':<15} | {'District'}")
    print("-" * 100)
    for m in masters:
        user = db.query(User).filter(User.id == m.user_id).first()
        sub = db.query(Subcategory).filter(Subcategory.id == m.subcategory_id).first()
        print(f"{m.user_id:<8} | {user.name[:15]:<15} | {m.subcategory_id:<6} | {sub.name_ru[:25]:<25} | {m.city:<15} | {m.district}")
finally:
    db.close()
