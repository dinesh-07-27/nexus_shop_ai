from fastapi import APIRouter
from pydantic import BaseModel
from rag.vector_store import store
from llm.gemini_client import get_embedding

router = APIRouter(prefix="/rag", tags=["RAG"])

class ProductDoc(BaseModel):
    product_id: int
    text: str

@router.post("/products")
def index_product(doc: ProductDoc):
    emb = get_embedding(doc.text)
    store.add_document(emb, {"product_id": doc.product_id, "text": doc.text})
    return {"status": "indexed", "dimension": len(emb)}

@router.get("/search")
def search_products(query: str, top_k: int = 3):
    emb = get_embedding(query)
    results = store.search(emb, top_k)
    return {"results": results}
