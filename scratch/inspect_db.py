import sqlite3
import os

db_path = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\findix.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Table Info ---")
cursor.execute("PRAGMA table_info(users)")
for row in cursor.fetchall():
    print(row)

print("\n--- User Info for +998998426574 ---")
cursor.execute("SELECT * FROM users WHERE phone = '+998998426574'")
user = cursor.fetchone()
if user:
    # Get column names
    names = [description[0] for description in cursor.description]
    user_dict = dict(zip(names, user))
    print(user_dict)
else:
    print("User not found")

conn.close()
