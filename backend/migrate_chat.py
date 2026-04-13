from sqlalchemy import create_engine
from database import DATABASE_URL, Base
from models import ChatMessage  # Important so it knows about the new model

engine = create_engine(DATABASE_URL)

print("Creating chat_messages table...")
ChatMessage.__table__.create(bind=engine, checkfirst=True)
print("Done!")
