from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.news_ingestor import news_ingestor
from app.core.logger import logger
from app.core.config import settings
from datetime import datetime

scheduler = AsyncIOScheduler()

async def start_scheduler():
    try:
        scheduler.add_job(
            news_ingestor.run,
            trigger=IntervalTrigger(hours=settings.scheduler_news_ingestor_interval_hours),
            id="news_ingestor_task",
            name="News Ingestor Pipeline",
            replace_existing=True,
            next_run_time=datetime.now()
        )

        scheduler.add_job(
            news_ingestor.process_failed_embeddings,
            kwargs={"limit": settings.openai_embedding_concurrent_limit},
            trigger=IntervalTrigger(minutes=settings.scheduler_back_fill_embedding_interval_minutes),
            id="backfill_vectors_task",
            name="Backfill Vectors",
            replace_existing=True,
            next_run_time=datetime.now()
        )

        scheduler.start()
        logger.bind(type="news_ingestor", step="Scheduler").info("Scheduler started. Task scheduled every 12h.")
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
    
async def stop_scheduler():
    try:
        scheduler.shutdown()
        logger.bind(type="news_ingestor", step="Scheduler").info("Scheduler shut down..")
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {str(e)}")
