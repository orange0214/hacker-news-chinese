from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
from app.db.supabase import get_supabase
from app.models.article import Article
from app.core.logger import logger
from app.repositories.chunk_repository import chunk_repository

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

        self.supabase = get_supabase()
    
    async def  process_and_store_article(self, article: Article):
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
                records.append({
                    "article_id": getattr(article, "id", None),
                    "content": chunk,
                    "embedding": vectors[i],
                    "metadata": {
                        "source": "combined",
                        "chunk_index": i,
                        "title": article.original_title,
                        "hn_id": article.hn_id
                    }
                })
            
            records = [r for r in records if r["article_id"] is not None]

            if not records:
                logger.warning(f"[VectorService] Skipped saving chunks for {article.hn_id}: Missing article.id")
                return
            
            
        


            

            

        except Exception as e:
            logger.error(f"[VectorService] Error processing article {article.hn_id}: {e}")