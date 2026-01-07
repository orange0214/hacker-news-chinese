# Hacker News Chinese

**Hacker News Chinese** is an AI-powered technology news aggregation platform designed to break language barriers. It automatically collects trending articles from Hacker News and leverages large language models (LLMs) to generate Chinese summaries and translations, helping users efficiently access high-quality technical information.

## Core Features

- **Automatic Aggregation**: Periodically fetches Hacker News Top Stories.
- **Intelligent Extraction**: 
    - Uses Jina Reader to extract the core content of web pages.
    - Fully preserves the original text description from Hacker News posts.
- **AI Summarization**: 
    - Analyzes the original title, post text, and page content collectively.
    - Generates a Chinese title, in-depth summary, and original translation.
- **RAG Intelligent Q&A**:
    - **Single Article Chat**: Interactive Q&A based on specific article content.
    - **Global Knowledge Search**: Semantic search and Q&A across the entire article history using vector database.
- **Data Persistence**: Stores article metadata and analysis results in a structured manner to Supabase.

## Tech Stack

- **Backend**: FastAPI (Python 3.12+)
- **Database**: Supabase (PostgreSQL + pgvector), Redis
- **AI/Tools**: Gemini, Jina Reader, uv, Loguru, APScheduler

### Frontend
- **Framework**: Next.js 16 (React 19)
- **Styling**: Tailwind CSS 4, Shadcn UI
- **State**: Zustand

## Quick Start

### 1. Backend Setup
```bash
# 1. Start Redis (Required for Chat Caching)
docker run -d --name hn-redis -p 6379:6379 -v hn_redis_data:/data redis:alpine redis-server --appendonly yes

# 2. Setup Python Environment
cd backend
uv sync
# Configure environment variables in .env
uv run dev
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

- API Docs: `http://localhost:8000/api/docs`
- Frontend: `http://localhost:3000`

## Project Structure

```
.
├── backend/            # FastAPI Application
│   ├── app/
│   │   ├── api/            # API Layer
│   │   │   ├── endpoints/  # Route Handlers (articles, auth, chat, health, news)
│   │   │   ├── deps.py     # Dependencies
│   │   │   └── router.py   # Router Config
│   │   ├── core/           # Core Infrastructure
│   │   │   ├── config.py   # Settings
│   │   │   ├── decorators.py
│   │   │   ├── logger.py
│   │   │   ├── news_ingestor.py # News Aggregation Logic
│   │   │   ├── prompts.py  # AI Prompts
│   │   │   └── scheduler.py# Task Scheduling
│   │   ├── db/             # Database Client (Supabase)
│   │   ├── models/         # Internal Data Models
│   │   ├── repositories/   # Data Access Layer
│   │   ├── schemas/        # Pydantic Schemas (DTOs)
│   │   │   └── external/   # External API Schemas
│   │   ├── services/       # Business Logic Services
│   │   │   ├── contexts/   # Context Management
│   │   │   ├── article_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── extraction_service.py
│   │   │   ├── hn_service.py
│   │   │   ├── translate_service.py
│   │   │   └── vector_service.py
│   │   └── main.py         # Application Entry Point
│   └── tests/              # Test Suite
├── frontend/           # Next.js Application
│   └── src/
│       ├── app/        # App Router Pages
│       ├── components/ # React Components
│       ├── lib/        # Utils & API
│       └── stores/     # State Management
└── db/                 # SQL Schemas
    ├── functions/          # Database Functions
    ├── article.sql
    └── document_chunk.sql
```

## Status

MVP Stage. See [PRD.md](./PRD.md) & [TODO.md](./TODO.md).
