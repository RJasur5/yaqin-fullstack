
import sqlite3

def check_db():
    conn = sqlite3.connect('findix.db')
    cursor = conn.cursor()
    
    print("--- ORDERS ---")
    cursor.execute("SELECT id, client_id, master_id, status FROM orders")
    orders = cursor.fetchall()
    for o in orders:
        print(o)
        
    print("\n--- CHAT MESSAGES ---")
    try:
        cursor.execute("SELECT id, order_id, sender_id, text FROM chat_messages")
        messages = cursor.fetchall()
        for m in messages:
            print(m)
    except Exception as e:
        print(f"Error reading chat_messages: {e}")
        
    print("\n--- USERS ---")
    cursor.execute("SELECT id, name, phone, role FROM users")
    users = cursor.fetchall()
    for u in users:
        print(u)
        
    conn.close()

if __name__ == "__main__":
    check_db()
