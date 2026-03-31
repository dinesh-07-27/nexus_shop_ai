from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_chat
from app.core import security

router = APIRouter(prefix="/api/v1/chat", tags=["AI Chatbot (v1)"])

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, user_payload: dict = Depends(security.get_current_user_payload)):
    """Secured AI Endpoint: Requires valid standard JWT to consume Gemini inference logic."""
    return await process_chat(request)
