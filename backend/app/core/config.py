from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Logging Configuration
    log_level: str

    # Scheduler Configuration
    scheduler_news_ingestor_interval_hours: int
    scheduler_back_fill_embedding_interval_minutes: int

    # Supabase Configuration
    supabase_url: str
    supabase_api_key: str

    # redis
    redis_url: str

    # Hacker News API endpoints (top/new up to 500 stories, best stories list)
    hn_top_url: str = "https://hacker-news.firebaseio.com/v0/topstories.json"
    hn_new_url: str = "https://hacker-news.firebaseio.com/v0/newstories.json"
    hn_best_url: str = "https://hacker-news.firebaseio.com/v0/beststories.json"
    hn_item_url: str = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
    hn_poll_interval_seconds: int
    hn_story_limit: int
    hn_fetch_concurrent_limit: int

    # OpenAI Configuration
    openai_api_key: str
    openai_embedding_concurrent_limit: int

    # Embedding
    embedding_match_threshold: float

    # Gemini Configuration
    gemini_base_url: str
    gemini_api_key: str
    gemini_model: str
    gemini_temperature: float
    gemini_concurrent_limit: int

    # DeepSeek Configuration
    deepseek_base_url: str
    deepseek_api_key: str
    deepseek_model: str
    deepseek_temperature: float
    deepseek_concurrent_limit: int

    # Jina
    jina_reader_base: str
    jina_api_key: str
    jina_fetch_concurrent_limit: int


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()