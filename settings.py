from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    app_env: str = "development"

    postgres_user: str = "agent"
    postgres_password: str = "agent_dev"
    postgres_db: str = "enterprise_agent"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    model_base_url: str | None = None
    model_api_key: str | None = None
    model_name: str | None = None
    
    embedding_model: str = "BAAI/bge-m3"
    embedding_max_tokens: int = 700
    embedding_overlap_tokens: int = 100
    embedding_batch_size: int = 1
    embedding_max_sequence_length: int = 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
