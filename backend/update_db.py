import sqlite3
import os

db_path = 'findix.db'

def update():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add district to master_profiles
    try:
        cursor.execute('ALTER TABLE master_profiles ADD COLUMN district VARCHAR;')
        print('District added to master_profiles')
    except Exception as e:
        print(f'master_profiles: {e}')

    # Add district to orders
    try:
        cursor.execute('ALTER TABLE orders ADD COLUMN district VARCHAR;')
        print('District added to orders')
    except Exception as e:
        print(f'orders: {e}')

    conn.commit()
    conn.close()
    print("Database update process finished.")

if __name__ == "__main__":
    update()
