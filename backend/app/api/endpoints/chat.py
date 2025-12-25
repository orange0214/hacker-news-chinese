from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.chat_service import chat_service
from app.schemas.chat import ChatRequest, GlobalChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message")
async def chat(request: ChatRequest):
    return StreamingResponse(
        chat_service.stream_chat(
            request.article_id, 
            request.message, 
            request.history
        ),
        media_type="text/event-stream"
    )

@router.post("/global")
async def global_chat(request: GlobalChatRequest):
    return StreamingResponse(
        chat_service.stream_global_chat(
            request.message,
            request.history
        ),
        media_type="text/event-stream"
    )