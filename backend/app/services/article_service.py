import math
from fastapi import HTTPException
from typing import Optional
from app.repositories.article_repository import article_repository
from app.schemas.article import ArticleFilterParams, ArticleSchema, ArticleListResponse
from app.services.interaction_service import interaction_service

class ArticleService:
    def get_article_list(self, params: ArticleFilterParams) -> ArticleListResponse:
        skip = (params.page - 1) * params.size

        data, total = article_repository.get_articles(
            skip=skip,
            limit=params.size,
            sort_by=params.sort_by,
            order=params.order,
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

    def get_article_detail(self, article_id: int, user_id: Optional[str] = None) -> ArticleSchema:
        article = article_repository.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        article_data = article.model_dump()

        article_data["is_favorited"] = False
        article_data["is_read_later"] = False

        if user_id:
            status = interaction_service.get_interaction_status(user_id, article_id)
            article_data.update(status)
        
        return ArticleSchema.model_validate(article_data)
    
    def get_article_context(self, article_id: int) -> dict:
        # get article context from database
        data = article_repository.get_article_by_id(article_id)
        if not data:
            raise HTTPException(status_code=404, detail="Article not found")

        return {
            "original_title": data.original_title,
            "original_text": data.original_text or "(No original text)",
            "raw_content": data.raw_content or "(No raw content)",
            "detailed_analysis": data.detailed_analysis.model_dump_json() if data.detailed_analysis else "(No detailed analysis)",
        }

article_service = ArticleService()