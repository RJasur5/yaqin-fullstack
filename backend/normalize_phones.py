from sqlalchemy.orm import sessionmaker
from database import engine
from models import User, JobApplication
import re
import sqlalchemy as sa

Session = sessionmaker(bind=engine)
session = Session()


def normalize_phone_clean(phone: str) -> str:
    """
    Normalize phone to clean +998XXXXXXXXX format (NO spaces, brackets, dashes).
    This is the canonical format for all DB storage.
    Examples:
      +998 (99) 842-65-74  -> +998998426574
      +998998426574        -> +998998426574
      998998426574         -> +998998426574
      998426574            -> +998998426574  (9 digits)
    """
    if not phone:
        return phone
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 12 and digits.startswith('998'):
        return '+' + digits[:12]
    elif len(digits) == 9:
        return '+998' + digits
    elif len(digits) > 9:
        return '+998' + digits[-9:]
    return phone  # fallback - can't normalize


def migrate():
    print("Normalizing user phone numbers to clean +998XXXXXXXXX format...")
    users = session.query(User).all()
    updated = 0
    for user in users:
        old_phone = user.phone
        new_phone = normalize_phone_clean(old_phone)
        if old_phone != new_phone:
            # Check for duplicate
            existing = session.query(User).filter(User.phone == new_phone, User.id != user.id).first()
            if existing:
                print(f"  WARNING: Duplicate found for {new_phone}. Keeping user {existing.id}, skipping user {user.id}")
                continue
            print(f"  Updating user {user.id}: '{old_phone}' -> '{new_phone}'")
            user.phone = new_phone
            try:
                session.commit()
                updated += 1
            except Exception as e:
                session.rollback()
                print(f"  FAILED to update user {user.id}: {e}")

    print(f"Updated {updated} user phone numbers.")

    print("Normalizing job application phone numbers...")
    apps = session.query(JobApplication).all()
    for app in apps:
        if app.phone:
            old_phone = app.phone
            new_phone = normalize_phone_clean(old_phone)
            if old_phone != new_phone:
                print(f"  Updating app {app.id}: '{old_phone}' -> '{new_phone}'")
                app.phone = new_phone
                try:
                    session.commit()
                except Exception:
                    session.rollback()

    print("Migration finished! All phones now in +998XXXXXXXXX format.")


if __name__ == "__main__":
    migrate()
