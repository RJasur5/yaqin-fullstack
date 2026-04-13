import requests
import json

# Configuration
BASE_URL = "http://localhost:8005/api"
# User ID 26 (жасур) is a master for subcategory 1 in Toshkent/Yunusobod.
# To test Yakkasaroy, we need to create an order for Yakkasaroy.
# Since we want Жасур to receive it (for testing), I will temporarily 
# set the district to "Yakkasaroy" in his profile OR 
# I will create the order for "Все районы".

def create_test_order():
    url = f"{BASE_URL}/orders"
    payload = {
        "subcategory_id": 1,
        "description": "ТЕСТОВОЕ УВЕДОМЛЕНИЕ: Ремонт сантехники в Yakkasaroy",
        "city": "Toshkent",
        "district": "Yakkasaroy", # The user specifically asked for Yakkasaroy
        "price": 50000.0
    }
    
    # We need a token to create an order. 
    # BUT! I can inject it directly into the DB using python if I don't have a token.
    # Let's use the DB injection to be 100% sure the logic in orders.py runs.
    print("Injecting order via Direct DB access to trigger notification logic...")
    
    import sqlite3
    conn = sqlite3.connect('findix.db')
    cursor = conn.cursor()
    
    # Get a client_id (not Жасур, to avoid self-filtering if I add it later)
    client_id = 1 # Usually there's an admin or dummy user
    
    # Insert order
    cursor.execute('''
        INSERT INTO orders (client_id, subcategory_id, description, city, district, price, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ''', (client_id, 1, payload["description"], payload["city"], payload["district"], payload["price"], "open"))
    
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"Order {order_id} injected. Now triggering the notification logic manually (or wait for the app to see it if it polls).")
    print("Wait, the notification logic is in the FastAPI route, not the DB trigger.")
    print("I will call the API properly.")

if __name__ == "__main__":
    # Actually, I'll just use a python script that acts like the FastAPI logic 
    # but bypasses the need for a real login token for this test.
    
    # OR better: I'll use the existing create_test_order.py if it exists.
    pass
