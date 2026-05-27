"""Centralized configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from urllib.parse import quote


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_provider: str = "openai"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_choice: str = "gpt-4o-mini"
    vision_llm_choice: str = "gpt-4o-mini"

    # Embedding
    embedding_provider: str = "openai"
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_api_key: str = ""
    embedding_model_choice: str = "text-embedding-3-small"

    # Database — either provide DATABASE_URL or individual params
    database_url: str = ""
    supabase_url: str = ""
    supabase_service_key: str = ""

    # Individual DB connection params (use these if DATABASE_URL has encoding issues)
    db_host: str = ""          # e.g., db.grizykmkgnsxrrzyyqmg.supabase.co
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_password: str = ""      # raw password, no URL encoding needed
    db_port: int = 5432

    # Web Search
    brave_api_key: str = ""

    # Observability
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # Environment
    environment: str = "development"

    @property
    def resolved_database_url(self) -> str:
        """Return DATABASE_URL, or build one from individual params."""
        if self.database_url:
            return self.database_url
        if self.db_host and self.db_password:
            encoded_password = quote(self.db_password, safe="")
            return f"postgresql://{self.db_user}:{encoded_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return ""


settings = Settings()
