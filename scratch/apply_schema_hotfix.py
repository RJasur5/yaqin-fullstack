import sqlite3

def run_hotfix():
    db_path = "/home/yaqingo/project/backend/findix.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Applying schema hotfix to {db_path}...")
    
    # 1. Add missing columns to 'users'
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_trial_used BOOLEAN DEFAULT 0;")
        print("Added 'is_trial_used' to 'users'.")
    except sqlite3.OperationalError as e:
        print(f"Skipping 'is_trial_used': {e}")

    # 2. Add missing columns to 'orders'
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN include_lunch BOOLEAN DEFAULT 0;")
        print("Added 'include_lunch' to 'orders'.")
    except sqlite3.OperationalError as e:
        print(f"Skipping 'include_lunch': {e}")
        
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN include_taxi BOOLEAN DEFAULT 0;")
        print("Added 'include_taxi' to 'orders'.")
    except sqlite3.OperationalError as e:
        print(f"Skipping 'include_taxi': {e}")

    # 3. Create missing tables (subscriptions, app_reviews, client_reviews)
    # I'll let SQLAlchemy handle table creation by running a small script inside the container
    
    conn.commit()
    conn.close()
    print("SQLite column hotfix complete.")

if __name__ == "__main__":
    run_hotfix()
