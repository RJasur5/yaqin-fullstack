from database import engine, Base
from models import User, Subscription
import logging

def update_db():
    print("Updating database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Done! Tables created/verified.")
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == "__main__":
    update_db()
