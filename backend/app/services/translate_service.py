import json
import asyncio
from typing import Dict, Any, Optional
from pydantic import ValidationError
from app.core.config import settings
from app.core.prompts import Prompts
from app.models.article import AITranslatedResult
from openai import AsyncOpenAI
from app.core.decorators import monitor_news_ingestor
from app.core.logger import logger

class TranslateService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,

        )
        self.model = settings.gemini_model
        self.temperature = settings.gemini_temperature
        self.sem = asyncio.Semaphore(settings.gemini_concurrent_limit)

    async def translate_and_summarize(
        self, 
        title: str, 
        hn_text: Optional[str]=None, 
        scraped_content: Optional[str]=None
        ) -> Optional[AITranslatedResult]:

        if not title and not hn_text and not scraped_content:
            return None
        
        safe_title = title or "N/A"
        safe_hn_text = hn_text or "N/A"
        safe_scraped_content = scraped_content[:100000] if scraped_content else "N/A"

        combined_input = f"""
        Title: {safe_title}
        Original Post Description: 
        {safe_hn_text}
        ---
        Scraped Article Content:
        {safe_scraped_content}
        """

        system_prompt = Prompts.SUMMARIZE_SYSTEM_Chinese

        try:
            async with self.sem:
                response = await self.client.chat.completions.create(
                    model = self.model,
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": combined_input},
                    ],
                    response_format={"type": "json_object"},
                    temperature=self.temperature,
                )

                result_text = response.choices[0].message.content

                if not result_text:
                    logger.error(f"[TranslateAndSummarizerService] Error: LLM returned empty result")
                    return None
                
                return AITranslatedResult.model_validate_json(result_text)

        except json.JSONDecodeError:
            logger.error(f"[TranslateAndSummarizerService] Error: LLM returned invalid JSON")
            return None
        except ValidationError as e:
            logger.error(f"[TranslateAndSummarizerService] Validation Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"[TranslateAndSummarizerService] Error processing content: {str(e)}")
            return None

    @monitor_news_ingestor(step_name="Translate-Summarize")
    async def translate_and_summarize_batch(
        self, 
        inputs: Dict[int, Dict[str, Any]]
        ) -> Dict[int, Optional[AITranslatedResult]]:
        # concurrently translate and summarize multiple inputs

        ids = list[int](inputs.keys())

        tasks = [
            self.translate_and_summarize(
                title = inputs[i].get("title", ""),
                hn_text = inputs[i].get("hn_text"),
                scraped_content = inputs[i].get("scraped_content"),
                ) for i in ids
            ]

        results = await asyncio.gather(*tasks)

        return dict(zip(ids, results))
        

translate_service = TranslateService()
