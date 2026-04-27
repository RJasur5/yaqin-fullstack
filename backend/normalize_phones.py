from sqlalchemy.orm import sessionmaker
from database import engine
from models import User, JobApplication
from utils.phone_formatter import format_phone
import sqlalchemy as sa

Session = sessionmaker(bind=engine)
session = Session()

def migrate():
    print("Normalizing user phone numbers...")
    users = session.query(User).all()
    for user in users:
        old_phone = user.phone
        new_phone = format_phone(old_phone)
        if old_phone != new_phone:
            # Check if this new phone already exists in the DB (for another user)
            existing = session.query(User).filter(User.phone == new_phone, User.id != user.id).first()
            if existing:
                print(f"  WARNING: Duplicate found for {new_phone}. Keeping user {existing.id}, skipping user {user.id}")
                continue
            
            print(f"  Updating user {user.id}: {old_phone} -> {new_phone}")
            user.phone = new_phone
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"  FAILED to update user {user.id}: {e}")
    
    print("Normalizing job application phone numbers...")
    apps = session.query(JobApplication).all()
    for app in apps:
        if app.phone:
            old_phone = app.phone
            new_phone = format_phone(old_phone)
            if old_phone != new_phone:
                print(f"  Updating app {app.id}: {old_phone} -> {new_phone}")
                app.phone = new_phone
                try:
                    session.commit()
                except:
                    session.rollback()

    print("Migration finished!")

if __name__ == "__main__":
    migrate()
