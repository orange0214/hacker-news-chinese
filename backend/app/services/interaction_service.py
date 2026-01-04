import math
from fastapi import HTTPException
from app.repositories.interaction_repository import interaction_repository
from app.schemas.article import ArticleSchema, ArticleListResponse, ArticleFilterParams

class InteractionService:
    # --- Favorites ---
    def favorite_article(self, user_id: str, article_id: int):
        success = interaction_repository.add_favorite(user_id, article_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to favorite article")

    def unfavorite_article(self, user_id: str, article_id: int):
        success = interaction_repository.remove_favorite(user_id, article_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to unfavorite article")

    def get_my_favorites(self, user_id: str, params: ArticleFilterParams):
        skip = (params.page - 1) * params.size
        data, total = interaction_repository.get_user_favorites(
            user_id=user_id,
            skip=skip,
            limit=params.size,
        )

        items = [ArticleSchema.model_validate(item) for item in data]
        total_pages = math.ceil(total / params.size) if params.size > 0 else 0
        return ArticleListResponse(
            items=items,
            total=total,
            page=params.page,
            size=params.size,
            total_pages=total_pages,
        )
    
    # --- Read Later ---
    def read_later_article(self, user_id: str, article_id: int):
        success = interaction_repository.add_read_later(user_id, article_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to read later article")

    def unread_later_article(self, user_id: str, article_id: int):
        success = interaction_repository.remove_read_later(user_id, article_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to unread later article")

    def get_my_read_laters(self, user_id: str, params: ArticleFilterParams):
        skip = (params.page - 1) * params.size
        data, total = interaction_repository.get_user_read_laters(
            user_id=user_id,
            skip=skip,
            limit=params.size,
        )

        items = [ArticleSchema.model_validate(item) for item in data]
        total_pages = math.ceil(total / params.size) if params.size > 0 else 0
        return ArticleListResponse(
            items=items,
            total=total,
            page=params.page,
            size=params.size,
            total_pages=total_pages,
        )
    
    # --- Helper for Article Service ---
    def get_interaction_status(self, user_id: str, article_id: int) -> dict:
        return {
            "is_favorited": interaction_repository.check_is_favorite(user_id, article_id),
            "is_read_later": interaction_repository.check_is_read_later(user_id, article_id)
        }

interaction_service = InteractionService()