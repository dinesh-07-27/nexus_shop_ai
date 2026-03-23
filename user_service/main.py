from fastapi import FastAPI
from database import Base, engine
import models
from routers import users

# Automatically create all tables in the database (for dev only, use Alembic in prod)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NexusShop AI - User Service",
    description="Handles user authentication, profiles, and JWTs",
    version="1.0.0"
)

app.include_router(users.router)

@app.get("/health")
def health_check():
    return {"status": "User Service is healthy"}
