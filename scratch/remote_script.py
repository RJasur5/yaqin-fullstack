
import sqlite3
import os

db_path = '/home/yaqingo/yaqin-production/backend/findix.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(users)')
    cols = [r[1] for r in cursor.fetchall()]
    if 'is_trial_used' not in cols:
        print("Adding is_trial_used")
        cursor.execute('ALTER TABLE users ADD COLUMN is_trial_used BOOLEAN DEFAULT 0')
    if 'fcm_token' not in cols:
        print("Adding fcm_token")
        cursor.execute('ALTER TABLE users ADD COLUMN fcm_token VARCHAR(255)')
    conn.commit()
    conn.close()
    print("DB fix applied")
else:
    print(f"DB not found at {db_path}")
