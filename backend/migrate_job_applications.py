"""
Migration script to create job_applications table.
Run this on the production server to add the new table.
"""
import sys
sys.path.insert(0, '.')

from database import engine, Base
from models import JobApplication  # noqa: F401 - import to register model

def migrate():
    print("Creating job_applications table...")
    Base.metadata.create_all(bind=engine, tables=[JobApplication.__table__])
    print("Done! job_applications table created successfully.")

if __name__ == "__main__":
    migrate()
