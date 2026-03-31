import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.db import models, database
from app.api.v1 import users

# 1. Centralized Production Logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] User Service: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2. Database Bootstrap
models.Base.metadata.create_all(bind=database.engine)
database.run_migrations()  # Safely add new columns to existing tables
logger.info("Database schema check and migrations complete.")

# 3. Application Orchestration
app = FastAPI(
    title="NexusShop AI - Auth & User Service",
    description="Amazon-grade Authentication provider with Strict RBAC (Role Based Access Control) Enforcements.",
    version="1.1.0"
)

# 4. Standard Error Interceptors (Resilience)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Crash intercepted on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error", 
            "code": 500, 
            "message": "Internal System Exception. Please check the centralized logs.",
            "path": request.url.path
        }
    )

# 5. Route Registration
app.include_router(users.router)

# 6. Global Health Check
@app.get("/api/v1/health")
def health_check():
    logger.info("Health check ping received.")
    return {"status": "User Service API v1 is fully healthy"}
