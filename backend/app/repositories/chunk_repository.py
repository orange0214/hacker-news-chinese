from app.db.supabase import get_supabase
from typing import List, Dict, Any
from app.core.logger import logger

class ChunkRepository:
    def __init__(self):
        self.table_name = "document_chunks"
    
    @property
    def supabase(self):
        return get_supabase()
    
    def add_chunks(self, records: List[Dict[str, Any]]) -> bool:
        try:
            self.supabase.table(self.table_name).insert(records).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding document chunks: {e}")
            return False


chunk_repository = ChunkRepository() 