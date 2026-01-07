import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.router import api_router
from app.db.supabase import init_supabase
from app.core.scheduler import start_scheduler, stop_scheduler
from app.db.redis import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    supabase = init_supabase()
    app.state.supabase = supabase
    init_redis()
    await start_scheduler()
    try:
        yield
    finally:
        await stop_scheduler()
        await close_redis()
        app.state.supabase = None

app = FastAPI(
    title="Hacker News Chinese", 
    version="1.0.0",
    docs_url="/api/docs",
    lifespan=lifespan,
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API router
app.include_router(api_router)


def main():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

