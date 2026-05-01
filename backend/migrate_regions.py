from database import SessionLocal
from models import Order, User, MasterProfile

REGION_MAP = {
    'Toshkent': 'Toshkent shahar',
    'Samarqand': 'Samarqand viloyati',
    'Buxoro': 'Buxoro viloyati',
    'Andijon': 'Andijon viloyati',
    'Namangan': 'Namangan viloyati',
    'Farg\'ona': 'Farg\'ona viloyati',
    'Nukus': 'Qoraqalpog\'iston',
    'Navoiy': 'Navoiy viloyati',
    'Urganch': 'Xorazm viloyati',
    'Qarshi': 'Qashqadaryo viloyati',
    'Jizzax': 'Jizzax viloyati',
    'Termiz': 'Surxondaryo viloyati',
    'Xiva': 'Xorazm viloyati',
    'Guliston': 'Sirdaryo viloyati'
}

def migrate_regions():
    db = SessionLocal()
    
    print("Migrating users...")
    users = db.query(User).all()
    updated_users = 0
    for u in users:
        if u.city in REGION_MAP:
            u.city = REGION_MAP[u.city]
            updated_users += 1
    
    print(f"Migrating orders...")
    orders = db.query(Order).all()
    updated_orders = 0
    for o in orders:
        if o.city in REGION_MAP:
            o.city = REGION_MAP[o.city]
            updated_orders += 1
            
    print(f"Migrating master profiles...")
    profiles = db.query(MasterProfile).all()
    updated_profiles = 0
    for p in profiles:
        if p.city in REGION_MAP:
            p.city = REGION_MAP[p.city]
            updated_profiles += 1
            
    db.commit()
    db.close()
    
    print(f"Migration completed:")
    print(f"- Users updated: {updated_users}")
    print(f"- Orders updated: {updated_orders}")
    print(f"- Profiles updated: {updated_profiles}")

if __name__ == "__main__":
    migrate_regions()
