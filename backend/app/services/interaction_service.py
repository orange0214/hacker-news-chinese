import math
from fastapi import HTTPException
from app.repositories.interaction_repository import interaction_repository
from app.schemas.article import ArticleSchema, ArticleListResponse

class InteractionService:
    # --- Favorites ---
    def favorite_article(self, user_id: str, article_id: int):
        success = interaction_repository.add_favorite(user_id, article_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to favorite article")

    def unfavorite_article(self, user_id: str, article_id: int):
        pass

    def get_my_favorites(self, user_id: str, article_id: int):
        pass
    
    # --- Read Later ---
    def read_later_article(self, user_id: str, article_id: int):
        pass

    def unread_later_article(self, user_id: str, article_id: int):
        pass

    def get_my_read_laters(self, user_id: str, article_id: int):
        pass
    
    # --- Helper for Article Service ---
    def get_interaction_status(self, user_id: str, article_id: int) -> dict:
        return {
            "is_favorited": interaction_repository.check_is_favorite(user_id, article_id),
            "is_read_later": interaction_repository.check_is_read_later(user_id, article_id)
        }