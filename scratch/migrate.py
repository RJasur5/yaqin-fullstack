
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Subcategory, MasterProfile, Order, Review, Subscription, Favorite

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migrator")

# Engines
# Note: Use the Postgres URL from env or hardcode consistent with docker-compose
sqlite_url = "sqlite:///old_findix.db"
pg_url = "postgresql://findix_user:findix_pass@db:5432/findix_db"

sqlite_engine = create_engine(sqlite_url)
pg_engine = create_engine(pg_url)

SqliteSession = sessionmaker(bind=sqlite_engine)
PgSession = sessionmaker(bind=pg_engine)

def migrate():
    s_db = SqliteSession()
    p_db = PgSession()

    # Clear Postgres first
    logger.info("Dropping and recreating Postgres tables...")
    Base.metadata.drop_all(bind=pg_engine)
    Base.metadata.create_all(bind=pg_engine)

    tables = [Category, Subcategory, User, MasterProfile, Order, Review, Subscription, Favorite]
    
    for model in tables:
        logger.info(f"Migrating {model.__tablename__}...")
        items = s_db.query(model).all()
        for item in items:
            # We use make_transient to allow inserting into a new DB
            s_db.expunge(item)
            # Remove SQLAlchemy internal state
            if hasattr(item, '_sa_instance_state'):
                delattr(item, '_sa_instance_state')
            p_db.add(item)
        
        p_db.commit()
        logger.info(f"Done {model.__tablename__}: {len(items)} rows")

    s_db.close()
    p_db.close()

if __name__ == '__main__':
    migrate()
