import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from elasticsearch import AsyncElasticsearch

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./products.db")
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

# Render provides postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Initialize async ElasticSearch client
es_client = AsyncElasticsearch(ES_URL)

def run_migrations():
    """Add ai_summary to products if missing."""
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS ai_summary TEXT"))
            conn.commit()
        except Exception:
            conn.rollback()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

