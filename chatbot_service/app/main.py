import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1 import chat, rag

# 1. Centralized Production Logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] Chatbot RAG Service: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2. Application Orchestration
app = FastAPI(
    title="NexusShop AI - Chatbot & RAG Recommendation Service",
    description="Semantic FAISS Vector Search with Gemini LLM inference. Secured by cross-service JWT.",
    version="1.1.0"
)

# 3. Standard Error Interceptors (Resilience)
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

# 4. Route Registration
app.include_router(chat.router)
app.include_router(rag.router)

# 5. Global Health Check
@app.get("/api/v1/health")
def health_check():
    logger.info("Health check ping received.")
    return {"status": "Chatbot RAG Service API v1 is fully healthy"}
