"""Central settings. Everything configurable lives in backend/.env, never in code."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Absolute so the env file loads no matter where uvicorn is started from.
ENV_FILE = Path(__file__).parents[2] / ".env"
# Single source of truth for pipeline output. Pipeline writes, backend serves, frontend fetches.
DATA_DIR = Path(__file__).parents[3] / "data"


class Settings(BaseSettings):
    """LLM + job config, loaded from backend/.env."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    llm_api_key: str = ""
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_model: str = "gemini-3.8-flash"
    apify_token: str = ""
    healthchecks_uuid_fetch: str = ""
    healthchecks_uuid_digest: str = ""
    healthchecks_uuid_archive: str = ""
    # popular tag: topic engagement must be in this top fraction of the day's distribution.
    popular_top_fraction: float = 0.1


settings = Settings()
