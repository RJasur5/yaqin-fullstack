import sqlite3
import os

# Connect to the database
# Based on database.py: os.path.join(BASE_DIR, 'findix.db')
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'findix.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Migrating users table...")
    # Add client_rating
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN client_rating FLOAT DEFAULT 0.0")
        print("Added column client_rating")
    except sqlite3.OperationalError:
        print("Column client_rating already exists")

    # Add client_reviews_count
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN client_reviews_count INTEGER DEFAULT 0")
        print("Added column client_reviews_count")
    except sqlite3.OperationalError:
        print("Column client_reviews_count already exists")

    # Add is_blocked
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_blocked BOOLEAN DEFAULT 0")
        print("Added column is_blocked")
    except sqlite3.OperationalError:
        print("Column is_blocked already exists")

    conn.commit()
    print("Migration successful!")
except Exception as e:
    print(f"Migration error: {e}")
finally:
    conn.close()
