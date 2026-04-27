import sqlite3
import os

db_path = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\findix.db'

def fix_users_table():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking users table columns...")
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    missing_columns = {
        "is_trial_used": "BOOLEAN DEFAULT 0",
        "fcm_token": "VARCHAR(255)"
    }

    for col, definition in missing_columns.items():
        if col not in columns:
            print(f"Adding column '{col}' to 'users' table...")
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
                print(f"Column '{col}' added successfully.")
            except Exception as e:
                print(f"Error adding column '{col}': {e}")
        else:
            print(f"Column '{col}' already exists.")

    conn.commit()
    conn.close()
    print("Database fix complete.")

if __name__ == "__main__":
    fix_users_table()
