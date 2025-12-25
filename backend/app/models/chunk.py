from pydantic import BaseModel, Field
from typing import List, Dict, Any

class DocumentChunkMetadata(BaseModel):
    source: str = "combined"
    chunk_index: int
    title: str
    hn_id: int

class DocumentChunk(BaseModel):
    article_id: int
    content: str
    embedding: List[float]
    metadata: DocumentChunkMetadata

