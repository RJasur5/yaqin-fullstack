
import sqlite3
import os

def check_tables():
    db_path = 'findix.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print("Tables in database:", tables)
    
    if 'chat_messages' in tables:
        print("chat_messages table exists.")
        cursor.execute("PRAGMA table_info(chat_messages);")
        columns = cursor.fetchall()
        print("Columns in chat_messages:", columns)
        
        cursor.execute("SELECT COUNT(*) FROM chat_messages")
        count = cursor.fetchone()[0]
        print(f"Total messages: {count}")
    else:
        print("chat_messages table DOES NOT exist.")
        
    cursor.execute("SELECT id, status FROM orders")
    orders = cursor.fetchall()
    print("Orders:", orders)
    
    conn.close()

if __name__ == "__main__":
    check_tables()
