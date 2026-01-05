from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
from app.models.article import AITranslatedResult

class SortField(str, Enum):
    POSTED_AT = "posted_at"
    SCORE = "score"
    AI_SCORE = "ai_score"

class SortOrder(str, Enum):
    DESC = "desc"
    ASC = "asc"

# --- Request Models (Query Params) ---
class ArticleFilterParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    sort_by: SortField = Field(default=SortField.POSTED_AT, description="Sort field")
    order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")

# --- Response Models (DTOs) ---
class ArticleSchema(BaseModel):
    id: int = Field(description="Database ID")
    hn_id: int = Field(description="Hacker News ID")
    original_title: str = Field(description="Original English Title")
    original_url: Optional[str] = Field(default=None, description="Original URL")
    original_text: Optional[str] = Field(default=None, description="Original English Text")
    score: int = Field(description="Hacker News Score")
    posted_at: datetime = Field(description="Posted At")
    by: Optional[str] = Field(default=None, description="Author")
    type: str = Field(description="Article Type")

    detailed_analysis: Optional[AITranslatedResult] = Field(default=None, description="AI Analysis Result")

    # Statistics
    descendants: Optional[int] = Field(default=None, description="In the case of stories or polls, the total comment count")

    favorites_count: int = Field(description="number of favorites")

    is_favorited: bool = Field(default=False, description="true if the article is favorited by the user")
    is_read_later: bool = Field(default=False, description="true if the article is read later by the user")

    # Status
    deleted: Optional[bool] = Field(default=False, description="true if the item is deleted")
    dead: Optional[bool] = Field(default=False, description="true if the item is dead")

    class Config:
        from_attributes = True

class ArticleListResponse(BaseModel):
    items: List[ArticleSchema]
    total: int
    page: int
    size: int
    total_pages: int

