from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'llm-gateway'
    app_env: str = 'dev'
    app_host: str = '0.0.0.0'
    app_port: int = 8000
    app_debug: bool = False

    database_url: str = Field(
        default='postgresql+psycopg://gateway:gateway@postgres:5432/gateway'
    )

    # Policy toggle requested by user:
    # False -> free only
    # True  -> free first, then paid fallback
    allow_paid_fallback: bool = False

    default_max_output_tokens: int = 512
    reservation_ttl_seconds: int = 180
    short_cooldown_seconds: int = 60
    long_cooldown_seconds: int = 900

    # Logging / persistence
    save_debug_payloads: bool = False
    payload_log_dir: str = '/app/data/request_payloads'

    # Provider secrets
    gemini_api_key: str | None = None
    cohere_api_key: str | None = None
    hf_api_key: str | None = None
    openrouter_api_key: str | None = None
    openrouter_site_url: str | None = None
    openrouter_app_name: str = 'llm-gateway'


settings = Settings()
