from pydantic_settings import BaseSettings, SettingsConfigDict # otomatis membaca setting dari file .env
from functools import lru_cache # untuk mengatasi problem memoization
from pathlib import Path


class Settings(BaseSettings):
    app_name: str =  "backend_client"
    debug: bool = False
    app_version: str = "1.0.0"

    database_url :str

    secret_key :str
    algorithm :str = "HS256"
    access_token_expire_minutes :int = 30
    cors_origins :list = ["*"]

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent / ".env"),
        case_sensitive=False,
        extra="ignore"
    )
    
@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
