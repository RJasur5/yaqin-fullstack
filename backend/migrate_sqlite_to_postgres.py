import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    Base, User, Category, Subcategory, MasterProfile, 
    Review, ClientReview, Favorite, Order, ChatMessage, AppReview
)
from dotenv import load_dotenv

# Load local environment
load_dotenv()

# Source database (SQLite)
SQLITE_URL = "sqlite:///findix.db"
# Target database (PostgreSQL) - using environment variables or a placeholder
POSTGRES_URL = os.getenv("DATABASE_URL")

if not POSTGRES_URL or not POSTGRES_URL.startswith("postgresql"):
    print("WARNING: DATABASE_URL is not set to a PostgreSQL connection string.")
    print("Format: postgresql://user:password@host:port/dbname")
    exit(1)

# Set up engines
sqlite_engine = create_engine(SQLITE_URL)
pg_engine = create_engine(POSTGRES_URL)

# Create tables in PostgreSQL
print("Creating tables in PostgreSQL...")
Base.metadata.create_all(pg_engine)

# Create sessions
SqliteSession = sessionmaker(bind=sqlite_engine)
PgSession = sessionmaker(bind=pg_engine)

def migrate_data():
    sqlite_db = SqliteSession()
    pg_db = PgSession()

    try:
        # Tables to migrate in order (dependencies first)
        tables = [
            (Category, "categories"),
            (Subcategory, "subcategories"),
            (User, "users"),
            (MasterProfile, "master_profiles"),
            (Favorite, "favorites"),
            (Order, "orders"),
            (ChatMessage, "chat_messages"),
            (Review, "reviews"),
            (ClientReview, "client_reviews"),
            (AppReview, "app_reviews"),
        ]

        for model, name in tables:
            print(f"Migrating {name}...")
            # Get all records from SQLite
            items = sqlite_db.query(model).all()
            if not items:
                print(f"  No records found in {name}.")
                continue

            # Clear existing data in PG for this table (optional, but safer for re-runs)
            # pg_db.query(model).delete() 

            for item in items:
                # Merge into postgres (handles existing records better than simple add)
                pg_db.merge(item)
            
            pg_db.commit()
            print(f"  Successfully migrated {len(items)} records to {name}.")

        print("\n=== Migration Completed Successfully ===")

    except Exception as e:
        print(f"\nERROR during migration: {e}")
        pg_db.rollback()
    finally:
        sqlite_db.close()
        pg_db.close()

if __name__ == "__main__":
    confirm = input(f"This will migrate data from {SQLITE_URL} to {POSTGRES_URL}. Continue? (y/n): ")
    if confirm.lower() == 'y':
        migrate_data()
    else:
        print("Migration cancelled.")
