import logging
from sqlalchemy import create_engine, MetaData, Table, select, insert, inspect
from sqlalchemy.orm import sessionmaker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migrator")

# Engines
sqlite_url = "sqlite:///old_findix.db"
pg_url = "postgresql://findix_user:findix_pass@db:5432/findix_db"

s_engine = create_engine(sqlite_url)
p_engine = create_engine(pg_url)

def migrate():
    s_meta = MetaData()
    p_meta = MetaData()
    
    # Check what exists in SQLite
    insp = inspect(s_engine)
    existing_sqlite_tables = insp.get_table_names()
    logger.info(f"Existing tables in SQLite: {existing_sqlite_tables}")

    # We must preserve the order of dependencies
    target_tables = ["categories", "subcategories", "users", "master_profiles", "orders", "reviews", "subscriptions", "favorites"]
    
    with p_engine.begin() as p_conn:
        # Clear existing data first in reverse order
        for name in reversed(target_tables):
            logger.info(f"Clearing table {name}...")
            # We use text() to avoid needing MetaData for DELETE
            from sqlalchemy import text
            p_conn.execute(text(f"TRUNCATE TABLE {name} RESTART IDENTITY CASCADE"))
            
        # Copy data
        for name in target_tables:
            if name not in existing_sqlite_tables:
                logger.warning(f"Skipping table {name} (not found in SQLite)")
                continue

            logger.info(f"Migrating table {name}...")
            s_table = Table(name, s_meta, autoload_with=s_engine)
            p_table = Table(name, p_meta, autoload_with=p_engine)
            
            with s_engine.connect() as s_conn:
                rows = s_conn.execute(select(s_table)).mappings().all()
                if rows:
                    data = [dict(row) for row in rows]
                    logger.info(f"Inserting {len(data)} rows into {name}...")
                    p_conn.execute(insert(p_table), data)
                    
            logger.info(f"Done {name}")

if __name__ == '__main__':
    migrate()
