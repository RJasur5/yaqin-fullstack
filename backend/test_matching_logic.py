from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from models import MasterProfile, User, Subcategory

engine = create_engine("sqlite:///backend/findix.db")
Session = sessionmaker(bind=engine)
db = Session()

ALL_DISTRICTS = "Все районы (весь город)"

def test_matching(order_city, order_district, sub_id):
    print(f"\n--- Testing Order: {order_city} | {order_district} | SubID: {sub_id} ---")
    
    query = db.query(MasterProfile).filter(
        MasterProfile.subcategory_id == sub_id
    )
    
    if order_city:
        query = query.filter(MasterProfile.city.ilike(f"%{order_city}%"))
        
    if order_district:
        if order_district == ALL_DISTRICTS:
            # All districts - wildcard
            pass
        else:
            query = query.filter(MasterProfile.district.ilike(f"%{order_district}%"))
            
    matches = query.all()
    print(f"Found {len(matches)} matches:")
    for m in matches:
        print(f"  - Master {m.user.name} ({m.district})")

# Sample scenarios
# 53 is "Моторист" ( жасур is Motoriest in Chilonzor)
# 1. Specific District Order (Matches)
test_matching("Toshkent", "Chilonzor", 53)

# 2. Specific District Order (No Match)
test_matching("Toshkent", "Yakkasaroy", 53)

# 3. All Districts Order (Should match all Toshkent Motorists)
test_matching("Toshkent", ALL_DISTRICTS, 53)

db.close()
