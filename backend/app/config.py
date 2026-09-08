"""
Central configuration for SearchLens AI.

All values can be overridden with environment variables (see .env.example
in the repo root). The app is designed to run fully in "demo mode" with
no external credentials at all, so a new contributor can clone the repo
and see real-looking data within a few minutes.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # General
    APP_NAME: str = "SearchLens AI"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Database. Defaults to a local SQLite file so the API runs with zero
    # setup. Point this at Postgres for anything beyond local development,
    # e.g. postgresql+psycopg2://searchlens:searchlens@db:5432/searchlens
    DATABASE_URL: str = "sqlite:///./searchlens.db"

    # Google integrations (optional). If these are not set, GSC/GA4 routes
    # automatically fall back to a deterministic demo data generator so the
    # dashboard still works.
    GOOGLE_SERVICE_ACCOUNT_JSON: str | None = None
    GA4_PROPERTY_ID: str | None = None

    # AI / GEO providers (optional). Any subset can be configured; providers
    # without a key are skipped and, if none are configured at all, the GEO
    # module runs in demo mode.
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    PERPLEXITY_API_KEY: str | None = None

    # Demo mode can also be forced on explicitly, which is useful for
    # screenshots, interviews or portfolio walkthroughs.
    FORCE_DEMO_MODE: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
