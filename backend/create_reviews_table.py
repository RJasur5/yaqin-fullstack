from database import engine, Base
from models import AppReview

print("Attempting to create tables explicitly...")
try:
    AppReview.__table__.create(bind=engine, checkfirst=True)
    print("Table 'app_reviews' created/verified successfully.")
except Exception as e:
    print(f"Error creating table: {e}")
