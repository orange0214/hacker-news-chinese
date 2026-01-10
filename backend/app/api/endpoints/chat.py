from fastapi import APIRouter, Security
from fastapi.responses import StreamingResponse
from app.services.chat_service import chat_service
from app.schemas.chat import ChatRequest, GlobalChatRequest
from app.api.deps import get_current_user
from app.schemas.chat import ConversationSchema, ConversationMessageSchema
from typing import List, Optional
from fastapi import Depends, HTTPException

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message")
async def chat(request: ChatRequest, current_user = Security(get_current_user)):
    return StreamingResponse(
        chat_service.stream_chat(
            current_user["id"],
            request.article_id, 
            request.message, 
            request.conversation_id
        ),
        media_type="text/event-stream"
    )

@router.post("/global")
async def global_chat(request: GlobalChatRequest, current_user = Security(get_current_user)):
    return StreamingResponse(
        chat_service.stream_global_chat(
            current_user["id"],
            request.message,
            request.conversation_id
        ),
        media_type="text/event-stream"
    )

@router.get("/sessions", response_model=List[ConversationSchema])
async def get_sessions(
    skip: int = 0, 
    limit: int = 20, 
    article_id: Optional[int] = None,
    current_user = Security(get_current_user)
):
    return await chat_service.get_user_conversations(current_user["id"], article_id, skip, limit)

@router.get("/sessions/{conversation_id}", response_model=ConversationMessageSchema)
async def get_session_detail(
    conversation_id: str,
    current_user = Security(get_current_user)
):
    result = await chat_service.get_conversation_messages_by_id(current_user["id"], conversation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result