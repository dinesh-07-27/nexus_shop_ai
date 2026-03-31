import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.db import models, database
from app.api.v1 import products

# 1. Centralized Production Logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] Product Catalog Service: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2. Database Bootstrap
models.Base.metadata.create_all(bind=database.engine)
database.run_migrations()  # Safely add any missing columns like ai_summary
logger.info("Product database schema check and migrations complete.")

# 3. Application Orchestration
app = FastAPI(
    title="NexusShop AI - Product Service",
    description="Scalable Catalog Management, Elasticsearch Sync, and Role-Based Administration.",
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

# 5. Connect ElasticSearch on Startup
@app.on_event("startup")
async def startup_event():
    try:
        exists = await database.es_client.indices.exists(index="products")
        if not exists:
            await database.es_client.indices.create(index="products")
            logger.info("Created 'products' index in Elastic Cloud.")
    except Exception as e:
        logger.warning(f"Could not connect to ElasticSearch on startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Closing Elastic Cloud connection pools...")
    await database.es_client.close()

# 6. Route Registration
app.include_router(products.router)

# 7. Global Health Check
@app.get("/api/v1/health")
def health_check():
    logger.info("Health check ping received via /api/v1/health.")
    return {"status": "Product Service API v1 is fully healthy"}
