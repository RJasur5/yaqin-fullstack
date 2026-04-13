from database import SessionLocal
from models import User

def promote_to_admin(phone: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone == phone).first()
        if user:
            user.role = "admin"
            db.commit()
            print(f"User {phone} promoted to admin successfully!")
        else:
            print(f"User with phone {phone} not found.")
    finally:
        db.close()

if __name__ == "__main__":
    promote_to_admin("+998998426574")
