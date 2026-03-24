import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default to localhost for local dev outside a container
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nexus_admin:nex_password@localhost:5432/nexus_db")

engine = create_engine(DATABASE_URL, pool_size=2, max_overflow=3, pool_recycle=300)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
