from app.db.supabase import get_supabase
from typing import List, Dict, Any
from app.core.logger import logger
from app.models.chunk import DocumentChunk

class VectorRepository:
    def __init__(self):
        self.table_name = "document_chunks"
    
    @property
    def supabase(self):
        return get_supabase()
    
    def add_chunks(self, chunks: List[DocumentChunk]) -> bool:
        try:
            # Convert Pydantic models to list of dicts for Supabase insertion
            records = [chunk.model_dump() for chunk in chunks]
            self.supabase.table(self.table_name).insert(records).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding document chunks: {e}")
            return False

    def search_similar(
        self,
        query_embedding: List[float],
        match_threshold: float = 0.5,
        match_count: int = 5
    ) -> List[Dict[str, Any]]:
        try:
            params = {
                "query_embedding": query_embedding,
                "match_threshold": match_threshold,
                "match_count": match_count,
                "filter": {}
            }

            response = self.supabase.rpc("match_documents", params).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"[ChunkRepository] Error searching documents: {e}")
            return []


vector_repository = VectorRepository() 