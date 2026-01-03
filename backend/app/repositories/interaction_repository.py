from typing import List, Tuple, Optional
from app.db.supabase import get_supabase
from app.core.logger import logger

class InteractionRepository:
    def __init__(self):
        self.favorites_table = "favorites"
        self.read_laters_table = "read_laters"
    
    @property
    def supabase(self):
        return get_supabase()

    # --- Favorites ---
    def add_favorite(self, user_id: str, article_id: int) -> bool:
        try:
            self.supabase.table(self.favorites_table).insert({
                "user_id": user_id,
                "article_id": article_id
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            return False
    
    def remove_favorite(self, user_id: str, article_id: int) -> bool:
        try:
            self.supabase.table(self.favorites_table).delete().match({
                "user_id": user_id,
                "article_id": article_id
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error removing favorite: {e}")
            return False
    
    def check_is_favorite(self, user_id: str, article_id: int) -> bool:
        try:
            res = self.supabase.table(self.favorites_table)\
                .select("article_id", count="exact", head=True)\
                .eq("user_id", user_id)\
                .eq("article_id", article_id)\
                .execute()
            return res.count is not None and res.count > 0
        except Exception as e:
            return False
    
    def get_user_favorites(self, user_id: str, skip: int = 0, limit: int = 20) -> Tuple[List[dict], int]:
        try:
            # Join query with articles table
            result = self.supabase.table(self.favorites_table)\
                .select("*, article:articles(*)", count="exact")\
                .eq("user_id", user_id)\
                .range(skip, skip + limit - 1)\
                .order("created_at", desc=True)\
                .execute()
            
            # Extract article data, ignoring cases where the associated article may have been physically deleted
            articles = [item['article'] for item in result.data if item.get('article')]
            return (articles, result.count if result.count else 0)
        except Exception as e:
            logger.error(f"Error getting user favorites: {e}")
            return ([], 0)
    
    # --- Read Later ---
    def add_read_later(self, user_id: str, article_id: int) -> bool:
        try:
            self.supabase.table(self.read_laters_table).insert({
                "user_id": user_id,
                "article_id": article_id
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding read later: {e}")
            return False
    
    def remove_read_later(self, user_id: str, article_id: int) -> bool:
        try:
            self.supabase.table(self.read_laters_table).delete().match({
                "user_id": user_id,
                "article_id": article_id
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error removing read later: {e}")
            return False
    
    def check_is_read_later(self, user_id: str, article_id: int) -> bool:
        try:
            res = self.supabase.table(self.read_laters_table)\
                .select("article_id", count="exact", head=True)\
                .eq("user_id", user_id)\
                .eq("article_id", article_id)\
                .execute()
            return res.count is not None and res.count > 0
        except Exception:
            return False
    
    def get_user_read_laters(self, user_id: str, skip: int = 0, limit: int = 20) -> Tuple[List[dict], int]:
        try:
            result = self.supabase.table(self.read_laters_table)\
                .select("*, article:articles(*)", count="exact")\
                .eq("user_id", user_id)\
                .range(skip, skip + limit - 1)\
                .order("created_at", desc=True)\
                .execute()
            
            articles = [item['article'] for item in result.data if item.get('article')]
            return (articles, result.count if result.count else 0)
        except Exception as e:
            logger.error(f"Error getting user read laters: {e}")
            return ([], 0)

interaction_repository = InteractionRepository()