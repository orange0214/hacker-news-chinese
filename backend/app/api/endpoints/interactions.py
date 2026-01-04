from fastapi import APIRouter, Depends, Query
from app.api.deps import get_current_user
from app.services.interaction_service import interaction_service
from app.schemas.article import ArticleListResponse, ArticleFilterParams
from fastapi import status

router = APIRouter(prefix="/interactions", tags=["interactions"])

@router.post("/favorites/{article_id}", status_code=status.HTTP_201_CREATED)
def add_favorite(article_id: int, current_user: dict = Depends(get_current_user)):
    interaction_service.favorite_article(current_user["id"], article_id)
    return {"message": "Favorite added successfully"}

@router.delete("/favorites/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(article_id: int, current_user: dict = Depends(get_current_user)):
    interaction_service.unfavorite_article(current_user["id"], article_id)
    return {"message": "Favorite removed successfully"}

@router.get("/favorites", response_model=ArticleListResponse)
def get_favorites(current_user: dict = Depends(get_current_user), params: ArticleFilterParams = Depends()):
    return interaction_service.get_my_favorites(current_user["id"], params)

@router.post("/read-later/{article_id}", status_code=status.HTTP_201_CREATED)
def add_read_later(article_id: int, current_user: dict = Depends(get_current_user)):
    interaction_service.read_later_article(current_user["id"], article_id)
    return {"message": "Read later added successfully"}

@router.delete("/read-later/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_read_later(article_id: int, current_user: dict = Depends(get_current_user)):
    interaction_service.unread_later_article(current_user["id"], article_id)
    return {"message": "Read later removed successfully"}

@router.get("/read-later", response_model=ArticleListResponse)
def get_read_laters(current_user: dict = Depends(get_current_user), params: ArticleFilterParams = Depends()):
    return interaction_service.get_my_read_laters(current_user["id"], params)