from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.vector_store import store
from app.llm.gemini_client import get_embedding

router = APIRouter(prefix="/api/v1/chatbot/rag", tags=["RAG Document Embeddings (v1)"])

class ProductDoc(BaseModel):
    product_id: int
    text: str

@router.post("/products")
def index_product(doc: ProductDoc):
    """Internal Webhook: Used by Product Service to asynchronously index items into FAISS."""
    emb = get_embedding(doc.text)
    store.add_document(emb, {"product_id": doc.product_id, "text": doc.text})
    return {"status": "indexed", "dimension": len(emb)}

@router.get("/search")
def search_products(query: str, top_k: int = 3):
    emb = get_embedding(query)
    results = store.search(emb, top_k)
    return {"results": results}
