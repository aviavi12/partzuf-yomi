import os
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    app_env: str = "development"
    demo_mode: bool = True

    database_url: str = "sqlite+aiosqlite:///./partzuf_yomi.db"

    redis_url: str = "redis://localhost:6379/0"

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_chat_id_global: str = ""
    telegram_chat_id_israel: str = ""

    ai_provider: Literal["openai", "anthropic", "none"] = "none"
    ai_api_key: str = ""
    ai_model: str = "gpt-4o-mini"

    ap_news_url: str = "https://apnews.com/"
    rotter_source_url: str = "https://rotter.net/"

    hourly_collection_enabled: bool = True
    daily_synthesis_hour: int = 18
    timezone: str = "Asia/Jerusalem"

    log_level: str = "INFO"

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8"}


settings = Settings()
