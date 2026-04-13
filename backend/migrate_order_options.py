import sqlite3
import os

db_path = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\findix.db'

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding include_lunch column...")
    cursor.execute("ALTER TABLE orders ADD COLUMN include_lunch BOOLEAN DEFAULT 0")
except sqlite3.OperationalError as e:
    print(f"Column include_lunch might already exist: {e}")

try:
    print("Adding include_taxi column...")
    cursor.execute("ALTER TABLE orders ADD COLUMN include_taxi BOOLEAN DEFAULT 0")
except sqlite3.OperationalError as e:
    print(f"Column include_taxi might already exist: {e}")

conn.commit()
conn.close()
print("Migration completed successfully!")
