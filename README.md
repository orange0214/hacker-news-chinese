# Hacker News Chinese

**Hacker News Chinese** is an AI-powered technology news aggregation platform designed to break language barriers. It automatically collects trending articles from Hacker News and leverages large language models (LLMs) to generate Chinese summaries and translations, helping users efficiently access high-quality technical information.

## Core Functions:

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

## Tech Stack:

- **Backend**: FastAPI (Python 3.12+)
- **Database**: Supabase (PostgreSQL + pgvector)
- **AI Services**: Gemini (Summarization), Jina Reader (Extraction)
- **Tooling**: uv (Package Management), Loguru (Logging), APScheduler (Task Scheduling)

## Quick Start

### 1. Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

### 2. Installation

```bash
git clone <repository-url>
cd Hacker_News_Chinese
uv sync
```

### 3. Configuration

Refer to `.env.example`, create a `.env` file, and fill in the configuration:

### 4. Running the Service

```bash
# Development Mode
uv run uvicorn app.main:app --reload
# Or
uv run dev

# Or use Makefile (if available)
make run
```

API Documentation: `http://localhost:8000/api/docs`

## Project Structure

```
.
├── backend/
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
├── db/                     # SQL Scripts & Schemas
│   ├── functions/          # Database Functions
│   ├── article.sql
│   └── document_chunk.sql
└── frontend/               # Frontend Application
```

## Development Status

Currently in MVP development stage. For detailed planning, please refer to [PRD.md](./PRD.md) and [TODO.md](./TODO.md).
