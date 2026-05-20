from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration backed by environment variables."""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    # App settings
    APP_NAME: str = "AW Client Report Portal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_PATH: str = "./clients.db"
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS settings
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Auth settings (simple team-only access)
    AUTH_ENABLED: bool = False
    AUTH_TOKEN: str = "default-insecure-token"

    @field_validator("DEBUG", "AUTH_ENABLED", mode="before")
    @classmethod
    def parse_bool_env(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "on", "debug", "dev", "development"}:
                return True
            if normalized in {"false", "0", "no", "off", "release", "prod", "production"}:
                return False
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

config = Config()
