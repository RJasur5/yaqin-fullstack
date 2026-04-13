import sqlite3
import os

db_path = "findix.db"
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding 'accepted_at' column to 'orders' table...")
    cursor.execute("ALTER TABLE orders ADD COLUMN accepted_at DATETIME")
    conn.commit()
    print("Success!")
except sqlite3.OperationalError:
    print("Column 'accepted_at' already exists.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
