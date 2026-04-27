import sqlite3
import datetime

def fix_db():
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting TRULY TOTAL database schema fix...")
    conn = sqlite3.connect('findix.db')
    cursor = conn.cursor()

    # Define tables and their required columns (based on server models.py)
    schema = {
        "users": [
            ("id", "INTEGER PRIMARY KEY"),
            ("phone", "TEXT UNIQUE"),
            ("full_name", "TEXT"),
            ("password_hash", "TEXT"),
            ("is_active", "BOOLEAN DEFAULT 1"),
            ("is_master", "BOOLEAN DEFAULT 0"),
            ("is_trial_used", "BOOLEAN DEFAULT 0"),
            ("created_at", "DATETIME")
        ],
        "categories": [
            ("id", "INTEGER PRIMARY KEY"),
            ("name_ru", "TEXT"),
            ("name_uz", "TEXT"),
            ("icon", "TEXT"),
            ("color", "TEXT"),
            ("order_index", "INTEGER DEFAULT 0")
        ],
        "subcategories": [
            ("id", "INTEGER PRIMARY KEY"),
            ("category_id", "INTEGER"),
            ("name_ru", "TEXT"),
            ("name_uz", "TEXT")
        ],
        "master_profiles": [
            ("id", "INTEGER PRIMARY KEY"),
            ("user_id", "INTEGER"),
            ("subcategory_id", "INTEGER"),
            ("description", "TEXT"),
            ("experience_years", "INTEGER DEFAULT 0"),
            ("hourly_rate", "FLOAT"),
            ("city", "TEXT"),
            ("district", "TEXT"),
            ("address", "TEXT"),
            ("skills", "JSON"),
            ("rating", "FLOAT DEFAULT 0.0"),
            ("reviews_count", "INTEGER DEFAULT 0"),
            ("is_available", "BOOLEAN DEFAULT 1"),
            ("is_blocked", "BOOLEAN DEFAULT 0"),
            ("portfolio_images", "JSON")
        ],
        "orders": [
            ("id", "INTEGER PRIMARY KEY"),
            ("client_id", "INTEGER"),
            ("master_id", "INTEGER"),
            ("subcategory_id", "INTEGER"),
            ("description", "TEXT"),
            ("city", "TEXT"),
            ("district", "TEXT"),
            ("price", "FLOAT"),
            ("status", "TEXT DEFAULT 'open'"),
            ("created_at", "DATETIME"),
            ("accepted_at", "DATETIME")
        ],
        "reviews": [
            ("id", "INTEGER PRIMARY KEY"),
            ("master_id", "INTEGER"),
            ("client_id", "INTEGER"),
            ("rating", "INTEGER"),
            ("comment", "TEXT"),
            ("created_at", "DATETIME")
        ],
        "client_reviews": [
            ("id", "INTEGER PRIMARY KEY"),
            ("client_id", "INTEGER"),
            ("master_id", "INTEGER"),
            ("rating", "INTEGER"),
            ("comment", "TEXT"),
            ("created_at", "DATETIME")
        ],
        "subscriptions": [
            ("id", "INTEGER PRIMARY KEY"),
            ("user_id", "INTEGER"),
            ("user_role", "TEXT"),
            ("plan_name", "TEXT"),
            ("ads_limit", "INTEGER DEFAULT 0"),
            ("ads_used", "INTEGER DEFAULT 0"),
            ("expires_at", "DATETIME"),
            ("is_active", "BOOLEAN DEFAULT 1")
        ],
        "app_reviews": [
            ("id", "INTEGER PRIMARY KEY"),
            ("user_id", "INTEGER"),
            ("rating", "INTEGER"),
            ("comment", "TEXT"),
            ("created_at", "DATETIME")
        ]
    }

    for table, columns in schema.items():
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Table '{table}' missing! Creating it...")
            cols_str = ", ".join([f"{name} {dtype}" for name, dtype in columns])
            cursor.execute(f"CREATE TABLE {table} ({cols_str})")
        else:
            # Table exists, check columns
            cursor.execute(f"PRAGMA table_info({table})")
            existing_cols = [row[1] for row in cursor.fetchall()]
            for col_name, col_type in columns:
                if col_name not in existing_cols:
                    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Adding column '{col_name}' to table '{table}'...")
                    # Simplified column addition to avoid complex type parsing
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type.split('PRIMARY KEY')[0]}")

    conn.commit()
    conn.close()
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Database schema is now TRULY up to date!")

if __name__ == "__main__":
    fix_db()
