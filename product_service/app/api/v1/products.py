import os
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import google.generativeai as genai
import httpx

from app.db import models, database
from app.schemas import product as schemas
from app.core import security

router = APIRouter(prefix="/api/v1/products", tags=["Products (v1)"])

genai.configure(api_key=os.getenv("GEMINI_API_KEY", "dummy"))
genai_model = genai.GenerativeModel('gemini-2.5-flash')

@router.get("/", response_model=list[schemas.ProductResponse])
def list_products(db: Session = Depends(database.get_db)):
    """Publicly accessible: List all products in the catalog."""
    return db.query(models.Product).all()


@router.post("/", response_model=schemas.ProductResponse)
async def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(database.get_db),
    admin_payload: dict = Depends(security.require_admin_role)
):
    """Admin-Only: Create a new product and sync to ElasticSearch/FAISS."""
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
        print(f"Failed to index to ES: {e}")

    # 3. Async Index in FAISS (Chatbot RAG)
    try:
        async with httpx.AsyncClient() as client:
            rag_payload = {
                "product_id": db_product.id,
                "text": f"{db_product.name} - {db_product.description}. Category: {db_product.category}"
            }
            await client.post("https://nexus-shop-ai-3.onrender.com/api/v1/chatbot/rag/products", json=rag_payload, timeout=2.0)
    except Exception as e:
        print(f"Failed to update Semantic Search vector: {e}")

    return db_product

@router.get("/search")
async def search_products(query: str, db: Session = Depends(database.get_db)):
    """Publicly accessible fuzzy search"""
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "description"],
                "fuzziness": "AUTO"
            }
        }
    }
    try:
        res = await database.es_client.search(index="products", body=body)
        hits = res["hits"]["hits"]
        return {"results": [hit["_source"] for hit in hits]}
    except Exception as e:
        print(f"ElasticSearch unavailable, falling back to PostgreSQL: {e}")
        fallback_results = db.query(models.Product).filter(
            models.Product.name.ilike(f"%{query}%") |
            models.Product.description.ilike(f"%{query}%")
        ).all()
        return {"results": [{"id": p.id, "name": p.name, "description": p.description, "category": p.category, "price": p.price, "stock": p.stock} for p in fallback_results]}

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

def summarize_reviews(product_id: int):
    db = database.SessionLocal()
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product: return
        reviews = db.query(models.Review).filter(models.Review.product_id == product_id).all()
        if not reviews: return
        
        review_texts = [f"Rating: {r.rating}/5 - {r.text}" for r in reviews]
        prompt = f"Analyze customer reviews for '{product.name}'. Write a single short sentence summarizing overall sentiment:\n" + "\n".join(review_texts)
        
        response = genai_model.generate_content(prompt)
        product.ai_summary = response.text.strip()
        db.commit()
    except Exception as e:
        print(f"AI Review Summarization failed: {e}")
    finally:
        db.close()

@router.post("/{product_id}/reviews", response_model=schemas.ReviewResponse)
def add_review(
    product_id: int, 
    review: schemas.ReviewCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(database.get_db),
    user_payload: dict = Depends(security.get_current_user_payload)
):
    """Requires standard user authentication JWT to add a review."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    new_review = models.Review(**review.dict(), product_id=product_id)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    background_tasks.add_task(summarize_reviews, product_id)
    return new_review

@router.get("/{product_id}/reviews")
def get_reviews(product_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Review).filter(models.Review.product_id == product_id).all()
