from fastapi import FastAPI
from routers import chat, rag

app = FastAPI(
    title="NexusShop AI - Chatbot Service", 
    description="Intelligent Customer Support via FAISS RAG and Gemini LLM Agents", 
    version="1.0.0"
)

app.include_router(chat.router)
app.include_router(rag.router)

@app.get("/health")
def health_check():
    return {"status": "AI Chatbot Service is completely active"}
