from typing import Optional, Tuple, List
from app.db.supabase import get_supabase
from app.models.article import Article
from app.core.logger import logger
from app.schemas.article import SortField, SortOrder

class ArticleRepository:
    def __init__(self):
        self.table_name = "articles"
    
    @property
    def supabase(self):
        return get_supabase()
    
    def has_article(self, hn_id: int) -> bool:
        try:
            result = self.supabase.table(self.table_name)\
                .select("id", count="exact", head=True)\
                .eq("hn_id", hn_id)\
                .execute()
            return result.count is not None and result.count > 0
        except Exception as e:
            logger.error(f"Error checking existence of article with hn_id {hn_id}: {e}")
            return False
    
    def add_article(self, article: Article) -> Optional[Article]:
        try:
            data = article.model_dump(mode="json", exclude={"id"})
            response = self.supabase.table(self.table_name).insert(data).execute()
            if response.data:
                return Article.model_validate(response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error adding article: {e}")
            return None
    
    def get_articles(self, skip: int, limit: int, sort_by: SortField, order: SortOrder) -> Tuple[List[dict], int]:
        try:
            # use count = "exact" to get the total number of articles
            query = self.supabase.table(self.table_name).select("*", count="exact")

            is_desc = (order == SortOrder.DESC)
            if sort_by == SortField.AI_SCORE:
                query = query.order("detailed_analysis->ai_score", desc=is_desc)
            elif sort_by == SortField.SCORE:
                query = query.order("score", desc=is_desc)
            elif sort_by == SortField.POSTED_AT:
                query = query.order("posted_at", desc=is_desc)

            query = query.range(skip, skip + limit - 1)
            result = query.execute()
            return (result.data, result.count if result.count is not None else 0)
            
        except Exception as e:
            logger.error(f"Error getting articles: {e}")
            return ([], 0)

    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        try:
            result = self.supabase.table(self.table_name)\
                .select("hn_id, type, by, posted_at, original_title, original_url, original_text, score, raw_content, detailed_analysis")\
                .eq("id", article_id)\
                .single()\
                .execute()
            return Article.model_validate(result.data) if result.data else None
        except Exception as e:
            logger.error(f"Error getting article by article_id {article_id}: {e}")
            return None

article_repository = ArticleRepository()