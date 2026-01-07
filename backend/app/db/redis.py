from redis.asyncio import Redis, from_url
from app.core.config import settings

_redis_pool = None

def init_redis():
    global _redis_pool
    _redis_pool = from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )

async def get_redis() -> Redis:
    global _redis_pool
    if _redis_pool is None:
        init_redis()
    return _redis_pool

async def close_redis():
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.aclose()