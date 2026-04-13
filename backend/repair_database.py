
import sqlite3
import os

def repair():
    db_path = 'findix.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found. Starting with a fresh database would require all tables.")
        # Actually, if main.py runs, it creates all tables anyway.
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Checking for chat_messages table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_messages';")
    if not cursor.fetchone():
        print("Creating chat_messages table...")
        cursor.execute('''
            CREATE TABLE chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (sender_id) REFERENCES users (id)
            )
        ''')
        print("Table created successfully.")
    else:
        print("chat_messages table already exists. Checking for columns...")
        cursor.execute("PRAGMA table_info(chat_messages);")
        chat_columns = [c[1] for c in cursor.fetchall()]
        if 'is_read' not in chat_columns:
            print("Adding is_read column to chat_messages...")
            cursor.execute("ALTER TABLE chat_messages ADD COLUMN is_read BOOLEAN DEFAULT 0;")
            print("Column added.")
        else:
            print("is_read column already exists.")
        
    # Check for accepted_at column in orders just in case it's missing (needed for recent features)
    cursor.execute("PRAGMA table_info(orders);")
    columns = [c[1] for c in cursor.fetchall()]
    if 'accepted_at' not in columns:
        print("Adding accepted_at column to orders...")
        cursor.execute("ALTER TABLE orders ADD COLUMN accepted_at DATETIME;")
        print("Column added.")
        
    if 'is_client_reviewed' not in columns:
        print("Adding is_client_reviewed column to orders...")
        cursor.execute("ALTER TABLE orders ADD COLUMN is_client_reviewed BOOLEAN DEFAULT 0;")
        
    if 'is_master_reviewed' not in columns:
        print("Adding is_master_reviewed column to orders...")
        cursor.execute("ALTER TABLE orders ADD COLUMN is_master_reviewed BOOLEAN DEFAULT 0;")

    conn.commit()
    conn.close()
    print("Repair complete!")

if __name__ == "__main__":
    repair()
