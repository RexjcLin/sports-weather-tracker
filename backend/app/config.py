"""Application settings loaded from environment variables and .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CWB_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./sports_weather.db"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()