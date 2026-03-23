from fastapi import FastAPI
from database import Base, engine, es_client
import models
from routers import products

# Auto-create tables (Dev only)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NexusShop AI - Product Catalog Service",
    description="Manages product catalog and ElasticSearch indexing for fuzzy search",
    version="1.0.0"
)

app.include_router(products.router)

@app.on_event("startup")
async def startup_event():
    # Ensure ElasticSearch 'products' index exists
    try:
        exists = await es_client.indices.exists(index="products")
        if not exists:
            await es_client.indices.create(index="products")
            print("Created 'products' index in ElasticSearch.")
    except Exception as e:
        print(f"Warning: Could not connect to ElasticSearch on startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await es_client.close()

@app.get("/health")
def health_check():
    return {"status": "Product Service is running smoothly"}
