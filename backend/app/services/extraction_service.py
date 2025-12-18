import asyncio
import httpx
from typing import Optional, List, Dict
from app.core.config import settings
from app.core.decorators import monitor_news_ingestor
from app.core.logger import logger

class ExtractionService:
    def __init__(self):
        self.jina_reader_base = settings.jina_reader_base
        self.headers = {
            "X-Retain-Images": "none" 
        }
        if settings.jina_api_key:
            self.headers["Authorization"] = f"Bearer {settings.jina_api_key}"
        
        self.sem = asyncio.Semaphore(settings.jina_fetch_concurrent_limit)

    async def extract_url(self, url: str) -> Optional[str]:
        if not url:
            return None

        target_url = f"{self.jina_reader_base}{url}"

        try:
            async with self.sem:
                # Use a fresh client for each request to avoid connection pooling issues
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.get(target_url, headers=self.headers)
                    if response.status_code != 200:
                        logger.error(f"[ExtractionService] [Jina Error] Status: {response.status_code} for URL: {url}")
                        return None
                    return response.text
        except httpx.TimeoutException:
            logger.error(f"[ExtractionService] [Timeout] Extracting {url} took too long (>60s).")
            return None
        except Exception as e:
            logger.error(f"[ExtractionService] Error extracting URL {url}: {str(e)}")
            return None

    @monitor_news_ingestor(step_name="Extract-Jina")
    async def extract_batch(self, urls: List[str]) -> Optional[Dict[str, Optional[str]]]:
        tasks = [self.extract_url(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return dict(zip(urls, results))

extraction_service = ExtractionService()