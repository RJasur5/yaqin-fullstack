import logging
from sqlalchemy import create_engine, MetaData, Table, select, insert
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
    
    # We must preserve the order of dependencies
    table_names = ["categories", "subcategories", "users", "master_profiles", "orders", "reviews", "subscriptions", "favorites"]
    
    with p_engine.begin() as p_conn:
        # Clear existing data first
        for name in reversed(table_names):
            logger.info(f"Clearing table {name}...")
            p_conn.execute(Table(name, p_meta, autoload_with=p_engine).delete())
            
        # Copy data
        for name in table_names:
            logger.info(f"Migrating table {name}...")
            s_table = Table(name, s_meta, autoload_with=s_engine)
            p_table = Table(name, p_meta, autoload_with=p_engine)
            
            # Select all from SQLite
            with s_engine.connect() as s_conn:
                rows = s_conn.execute(select(s_table)).mappings().all()
                if rows:
                    # Convert to dictionaries
                    data = [dict(row) for row in rows]
                    logger.info(f"Inserting {len(data)} rows into {name}...")
                    p_conn.execute(insert(p_table), data)
                    
            logger.info(f"Done {name}")

if __name__ == '__main__':
    migrate()
