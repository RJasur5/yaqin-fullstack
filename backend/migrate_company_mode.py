import sqlite3
import os

db_path = "findix.db"
if not os.path.exists(db_path):
    print(f"Database {db_path} not found in current directory.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add is_company column to orders table
        cursor.execute("ALTER TABLE orders ADD COLUMN is_company BOOLEAN DEFAULT 0")
        print("Added is_company column to orders table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("is_company column already exists.")
        else:
            print(f"Error adding is_company: {e}")

    conn.commit()
    conn.close()
    print("Database migration finished.")
