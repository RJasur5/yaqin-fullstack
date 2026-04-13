import sqlite3

try:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_reviews';")
    table = cursor.fetchone()
    if table:
        print("Table 'app_reviews' exists.")
        cursor.execute("PRAGMA table_info(app_reviews);")
        print("Columns:", cursor.fetchall())
    else:
        print("Table 'app_reviews' DOES NOT EXIST.")
    conn.close()
except Exception as e:
    print(f"Error checking DB: {e}")
