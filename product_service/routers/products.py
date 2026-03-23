from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    # 1. Save to PostgreSQL for strict ACID compliance
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # 2. Async Index in ElasticSearch for lightning-fast fuzzy search
    doc = {
        "id": db_product.id,
        "name": db_product.name,
        "description": db_product.description,
        "category": db_product.category,
        "price": db_product.price,
        "stock": db_product.stock
    }
    
    try:
        await database.es_client.index(index="products", id=str(db_product.id), document=doc)
    except Exception as e:
        # Depending on saga/rollback logic, we might queue a retry here.
        print(f"Failed to index to ES: {e}")

    return db_product

@router.get("/search")
@router.get("/search")
async def search_products(query: str, db: Session = Depends(database.get_db)):
    # Perform a fuzzy search across name and description
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "description"],  # Boost name relevance
                "fuzziness": "AUTO"
            }
        }
    }
    try:
        res = await database.es_client.search(index="products", body=body)
        hits = res["hits"]["hits"]
        results = [hit["_source"] for hit in hits]
        return {"results": results}
    except Exception as e:
        print(f"ElasticSearch unavailable, falling back to PostgreSQL: {e}")
        # High Availability Fallback: If ES is down, query the primary DB
        fallback_results = db.query(models.Product).filter(
            models.Product.name.ilike(f"%{query}%") |
            models.Product.description.ilike(f"%{query}%")
        ).all()
        
        results = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "category": p.category,
                "price": p.price,
                "stock": p.stock
            } for p in fallback_results
        ]
        return {"results": results}

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
