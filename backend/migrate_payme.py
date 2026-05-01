import sqlite3

def upgrade():
    conn = sqlite3.connect('findix.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE payment_transactions ADD COLUMN cancel_reason INTEGER;")
        print("Added cancel_reason")
    except sqlite3.OperationalError as e:
        print(f"cancel_reason already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE payment_transactions ADD COLUMN cancel_time DATETIME;")
        print("Added cancel_time")
    except sqlite3.OperationalError as e:
        print(f"cancel_time already exists or error: {e}")

    conn.commit()
    conn.close()
    print("Migration finished!")

if __name__ == '__main__':
    upgrade()
