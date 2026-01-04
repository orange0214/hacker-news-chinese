"""
Main API router
"""
from fastapi import APIRouter, Security
from app.api.deps import get_current_user

from app.api.endpoints.health import router as health_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.news import router as news_router
from app.api.endpoints.articles import router as articles_router
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.interactions import router as interactions_router

api_router = APIRouter(prefix="/api")

# Health endpoint
api_router.include_router(health_router)

# Auth endpoints
api_router.include_router(auth_router)

# News endpoints
api_router.include_router(news_router, dependencies=[Security(get_current_user)])

# Articles endpoints
api_router.include_router(articles_router)

# Chat endpoints
api_router.include_router(chat_router)

# Interactions endpoints
api_router.include_router(interactions_router)