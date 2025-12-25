import asyncio
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
from app.models.article import Article
from app.models.chunk import DocumentChunk, DocumentChunkMetadata
from app.core.logger import logger
from app.repositories.vector_repository import vector_repository
from app.repositories.article_repository import article_repository
from app.core.config import settings
from app.core.decorators import monitor_news_ingestor

class VectorService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model = "text-embedding-3-small",
            openai_api_key=settings.openai_api_key
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1200,
            chunk_overlap = 300,
            length_function = lambda x: len(x.encode("utf-8")),
            separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""]
        )
        
        self.sem = asyncio.Semaphore(settings.openai_embedding_concurrent_limit)

    async def process_and_store_article(self, article: Article):
        async with self.sem:
            try:
                parts = []

                # (Part A: original description in HN)
                if article.original_text:
                    parts.append(f"=== Hacker News Description ===\n{article.original_text}")
                
                # (Part B: raw content from url)
                if article.raw_content:
                    parts.append(f"=== Article Content ===\n{article.raw_content}")
                
                # (Part C: detailed analysis from LLM)
                if article.detailed_analysis:
                    analysis = article.detailed_analysis
                    analysis_text = f"""
                    === AI Analysis Report ===
                    Topic: {analysis.topic}
                    Chinese Title: {analysis.title_cn}
                    Summary: {analysis.summary}
                    Key Points: {chr(10).join(analysis.key_points)}
                    Takeaway: {analysis.takeaway}
                    """
                    parts.append(analysis_text)
                
                full_text = "\n\n".join(parts)

                if not full_text or len(full_text) < 50:
                    logger.info(f"[VectorService] Article {article.hn_id} content too short, skipping.")
                    return
                
                chunks = self.text_splitter.split_text(full_text)

                records = []
                vectors = await self.embeddings.aembed_documents(chunks)

                for i, chunk in enumerate(chunks):
                    doc_chunk = DocumentChunk(
                        article_id=article.id,
                        content=chunk,
                        embedding=vectors[i],
                        metadata=DocumentChunkMetadata(
                            chunk_index=i,
                            title=article.original_title,
                            hn_id=article.hn_id
                        )
                    )
                    records.append(doc_chunk)
                
                if not records:
                    logger.warning(f"[VectorService] Skipped saving chunks for {article.hn_id}: Missing article.id")
                    return False
                
                success = vector_repository.add_chunks(records)
                if success:
                    mark_success = article_repository.mark_article_embedded(article.id)
                    if mark_success:
                         logger.info(f"[VectorService] Stored {len(records)} chunks & marked embedded for {article.hn_id}")
                    else:
                         logger.warning(f"[VectorService] Stored chunks but FAILED to mark embedded for {article.hn_id}")
                    return True

            except Exception as e:
                logger.error(f"[VectorService] Error processing article {article.hn_id}: {e}")
                return False

    @monitor_news_ingestor(step_name="Vectorization-Batch")
    async def process_and_store_articles_batch(self, articles: List[Article]):
        """
        Batch process vectorization tasks for multiple articles
        """
        if not articles:
            return

        tasks = [self.process_and_store_article(article) for article in articles]
        
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            query_embedding = await self.embeddings.aembed_query(query)

            results = vector_repository.search_similar(
                query_embedding=query_embedding,
                match_threshold=settings.embedding_match_threshold,
                match_count=limit
            )

            return results

        except Exception as e:
            logger.error(f"[VectorService] Search error: {e}")

vector_service = VectorService()