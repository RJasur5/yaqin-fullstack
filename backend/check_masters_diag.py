from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import MasterProfile, User, Subcategory

engine = create_engine("sqlite:///findix.db")
Session = sessionmaker(bind=engine)
db = Session()

print(f"{'UserID':<8} | {'Name':<15} | {'City':<15} | {'Subcategory':<20} | {'District':<15}")
print("-" * 80)

masters = db.query(MasterProfile).all()
for m in masters:
    user_name = m.user.name if m.user else "Unknown"
    city = m.city if m.city else "None"
    sub_name = m.subcategory.name_ru if m.subcategory else "None"
    district = m.district if m.district else "None"
    print(f"{m.user_id:<8} | {user_name:<15} | {city:<15} | {sub_name:<20} | {district:<15}")

db.close()
