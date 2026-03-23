from fastapi import APIRouter
from schemas.chat import ChatRequest, ChatResponse
from services.chat_service import process_chat

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    return await process_chat(request)
