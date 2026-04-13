import sqlite3
from datetime import datetime, timezone

def create_test_order():
    conn = sqlite3.connect('findix.db')
    cursor = conn.cursor()
    
    # Get the first client user ID
    cursor.execute("SELECT id FROM users LIMIT 1")
    user_row = cursor.fetchone()
    if not user_row:
        print("Error: No users found in database.")
        return
    user_id = user_row[0]
    
    # Check if subcategory 13 exists
    cursor.execute("SELECT name_ru FROM subcategories WHERE id = 13")
    sub_row = cursor.fetchone()
    if not sub_row:
        print("Error: Subcategory 13 (Web) not found.")
        return
    
    now = datetime.now(timezone.utc)
    # Using 'price' instead of 'budget', and adding 'city'
    cursor.execute("""
        INSERT INTO orders (client_id, subcategory_id, description, city, district, price, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, 13, "Нужен сайт визитка (ТЕСТ)", "Toshkent", "Toshkent", 500000.0, "open", now))
    
    conn.commit()
    print(f"Test order created in DB with subcategory 13 and district 'Toshkent'")
    conn.close()

if __name__ == "__main__":
    create_test_order()
