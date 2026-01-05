from fastapi import APIRouter, Depends, HTTPException, status, Security
from app.schemas.article import ArticleFilterParams, ArticleListResponse
from app.services.article_service import article_service
from app.schemas.article import ArticleSchema
from app.api.deps import get_current_user_optional
from typing import Optional

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/", response_model=ArticleListResponse)
def list_articles(
    params: ArticleFilterParams = Depends()
):
    try:
        return article_service.get_article_list(params)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")


@router.get("/{article_id}", response_model=ArticleSchema)
def get_article(article_id: int, current_user = Security(get_current_user_optional)):
    try:
        user_id = current_user.id if current_user else None
        return article_service.get_article_detail(article_id, user_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )