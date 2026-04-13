from database import SessionLocal
from models import Subcategory, MasterProfile
db = SessionLocal()
subs = db.query(Subcategory).all()
for s in subs:
    print(f"{s.id}: {s.name_ru}")
db.close()
