import sqlite3
import os
import sys

# Add backend to path to import models
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from models import Base
from database import engine

def sync_schema():
    db_path = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\findix.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables from SQLAlchemy models
    for table_name, table in Base.metadata.tables.items():
        print(f"Checking table '{table_name}'...")
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            print(f"Table '{table_name}' missing. Skipping (should be created by create_all).")
            continue

        # Check for missing columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        for column in table.columns:
            if column.name not in existing_columns:
                print(f"Adding missing column '{column.name}' to table '{table_name}'...")
                
                # Determine type
                col_type = str(column.type)
                if 'VARCHAR' in col_type:
                    col_type = 'VARCHAR(255)'
                elif 'INTEGER' in col_type:
                    col_type = 'INTEGER'
                elif 'FLOAT' in col_type:
                    col_type = 'FLOAT'
                elif 'BOOLEAN' in col_type:
                    col_type = 'BOOLEAN'
                elif 'DATETIME' in col_type:
                    col_type = 'DATETIME'
                elif 'TEXT' in col_type:
                    col_type = 'TEXT'
                elif 'JSON' in col_type:
                    col_type = 'JSON'
                
                # Handle defaults
                default_clause = ""
                if column.default is not None:
                    if hasattr(column.default, 'arg'):
                        arg = column.default.arg
                        if isinstance(arg, bool):
                            default_clause = f" DEFAULT {1 if arg else 0}"
                        elif isinstance(arg, (int, float)):
                            default_clause = f" DEFAULT {arg}"
                        elif isinstance(arg, str):
                            default_clause = f" DEFAULT '{arg}'"

                try:
                    query = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}{default_clause}"
                    print(f"Running: {query}")
                    cursor.execute(query)
                    print(f"Column '{column.name}' added.")
                except Exception as e:
                    print(f"Error adding column '{column.name}': {e}")

    conn.commit()
    conn.close()
    print("Schema synchronization complete.")

if __name__ == "__main__":
    sync_schema()
