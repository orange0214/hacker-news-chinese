from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(description="role of the message, user or assistant")
    content: str = Field(description="content of the message")

class ChatRequest(BaseModel):
    article_id: int = Field(description="id of the article")
    message: str = Field(description="message from user")
    conversation_id: Optional[str] = Field(
        default=None,
        description="id of the conversation, if None, a new conversation will be created"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "article_id": 1,
                    "message": "What is the main idea of the article?",
                    "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }

class GlobalChatRequest(BaseModel):
    message: str = Field(description="message from user")
    conversation_id: Optional[str] = Field(
        default=None,
        description="id of the conversation, if None, a new conversation will be created"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "What are the latest articles about Rust?",
                    "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }
