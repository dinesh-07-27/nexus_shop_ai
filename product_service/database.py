import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from elasticsearch import AsyncElasticsearch

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nexus_admin:nex_password@localhost:5432/nexus_db")
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

engine = create_engine(DATABASE_URL, pool_size=1, max_overflow=1, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Initialize async ElasticSearch client
es_client = AsyncElasticsearch(ES_URL)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
