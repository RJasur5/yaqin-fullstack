import os
import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
# Add current dir to path to import models and database
sys.path.append(os.getcwd())

from database import Base, engine as pg_engine
from models import User, Category, Subcategory, MasterProfile, Review, ClientReview, Favorite, Order, ChatMessage, AppReview, Subscription

# Source engine (SQLite)
SQLITE_URL = "sqlite:///findix.db"
sqlite_engine = create_engine(SQLITE_URL)
SqliteSession = sessionmaker(bind=sqlite_engine)

# Destination engine (PostgreSQL) - will be passed from env or config
# For the script we assume pg_engine from database.py is already configured for Postgres
# or we create it here if we want to be explicit
PG_URL = os.getenv("DATABASE_URL") # This should be the postgres one during migration

def migrate_data():
    if not PG_URL or not PG_URL.startswith("postgresql"):
        print("ERROR: DATABASE_URL is not set to PostgreSQL. Migration aborted.")
        return

    print(f"Starting migration from SQLite ({SQLITE_URL}) to PostgreSQL...")
    
    # 1. Create tables in PostgreSQL
    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(pg_engine)
    
    # 2. Migration logic
    sqlite_session = SqliteSession()
    pg_session = sessionmaker(bind=pg_engine)()
    
    try:
        # Order of migration is important due to foreign keys
        models = [
            User, Category, Subcategory, MasterProfile, 
            Review, ClientReview, Favorite, Order, 
            ChatMessage, AppReview, Subscription
        ]
        
        for model in models:
            print(f"Migrating {model.__tablename__}...")
            items = sqlite_session.query(model).all()
            print(f"Found {len(items)} records.")
            
            # Use merge to avoid duplicates and handle identity keys
            for item in items:
                # Expunge from sqlite session to move to pg session
                sqlite_session.expunge(item)
                pg_session.merge(item)
            
            pg_session.commit()
            print(f"Finished {model.__tablename__}.")
            
        print("MIGRATION SUCCESSFUL!")
        
    except Exception as e:
        pg_session.rollback()
        print(f"MIGRATION FAILED: {e}")
        raise e
    finally:
        sqlite_session.close()
        pg_session.close()

if __name__ == "__main__":
    migrate_data()
