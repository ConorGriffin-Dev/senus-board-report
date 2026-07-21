"""Application settings, loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = (
        "postgresql+asyncpg://senus:senus_dev_password@localhost:5432/senus_board_report"
    )
    environment: str = "development"
    backend_cors_origins: str = "http://localhost:5173"

    # Not used in normal operation. The extraction and insight services read
    # cached fixtures rather than calling a live API. Present only so the
    # documented swap point in those services has somewhere to read a key from.
    anthropic_api_key: str = ""

    @property
    def sync_database_url(self) -> str:
        """Alembic runs migrations synchronously."""
        return self.database_url.replace("+asyncpg", "")


settings = Settings()
