import sqlite3
import os

db_path = "findix.db"
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding 'is_client_reviewed' and 'is_master_reviewed' columns to 'orders' table...")
    # SQL Lite doesn't support multiple columns in one ALTER TABLE, adding one by one
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN is_client_reviewed BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        print("Column 'is_client_reviewed' already exists.")
        
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN is_master_reviewed BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        print("Column 'is_master_reviewed' already exists.")
        
    conn.commit()
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
