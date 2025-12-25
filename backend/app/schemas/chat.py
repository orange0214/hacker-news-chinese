from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(description="role of the message, user or assistant")
    content: str = Field(description="content of the message")

class ChatRequest(BaseModel):
    article_id: int = Field(description="id of the article")
    message: str = Field(description="message from user")
    history: List[ChatMessage] = Field(
        default=[],
        description="history of the conversation"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "article_id": 1,
                    "message": "What is the main idea of the article?",
                    "history": [
                        {"role": "user", "content": "Hello"},
                        {"role": "assistant", "content": "Hello, how can I help you today?"},
                    ]
                }
            ]
        }

class GlobalChatRequest(BaseModel):
    message: str = Field(description="message from user")
    history: List[ChatMessage] = Field(
        default=[],
        description="history of the conversation"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "What are the latest articles about Rust?",
                    "history": [
                        {"role": "user", "content": "Hello"},
                        {"role": "assistant", "content": "Hello, how can I help you today?"},
                    ]
                }
            ]
        }
