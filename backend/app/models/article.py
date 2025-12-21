from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class AITranslatedResult(BaseModel):
    # LLM translated and summarized result
    topic: str = Field(description="Article topic label")
    title_cn: str = Field(description="Chinese title")
    summary: str = Field(description="In-depth summary")
    key_points: List[str] = Field(description="Key points", min_items=3, max_items=10)
    tech_stack: List[str] = Field(default_factory=list, description="Tech stack")
    takeaway: str = Field(description="Independent insight")
    ai_score: int = Field(description="AI score", ge=0, le=100)
    original_text_trans: Optional[str] = Field(default=None, description="Original text translation")
    url_content_trans: Optional[str] = Field(default=None, description="URL Full-text translation")

class CommentAnalysis(BaseModel):
    comment_trans: str = Field(description="Full-text translation of the comment")

class Article(BaseModel):
    """
    This Pydantic model represents an enriched HN article, containing:
    1. Basic information returned by the HN API (hn_id, original_title, original_url, score, etc.)
    2. The main article body/content extracted by the crawler (raw_content)
    3. AI-generated results, such as summary, translated_title, detailed_analysis, etc.
    """
    id: Optional[int] = Field(default=None, description="Database primary key")
    hn_id: int
    type: str
    by: Optional[str] = Field(default=None, description="The username of the item's author")
    posted_at: datetime
    
    original_title: str
    original_url: Optional[str]
    original_text: Optional[str]
    score: int

    kids: Optional[List[int]]
    parent: Optional[int]
    poll: Optional[int]
    parts: Optional[List[int]]
    descendants: Optional[int]

    deleted: Optional[bool]
    dead: Optional[bool]

    raw_content: str
    image_urls: Optional[List[str]]

    is_embedded: bool = Field(default=False, description="Article has been vectorized")

    detailed_analysis: Optional[AITranslatedResult]
    comment_analysis: Optional[List[CommentAnalysis]]
    
    class Config:
        # allow reading data from ORM objects (if we use SQLAlchemy in the future)
        from_attributes = True 
        # when saving to the database, let Pydantic automatically convert detailed_analysis to JSON
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }