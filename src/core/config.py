import os
from datetime import timedelta, datetime

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), ".env")

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV)
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_URL: str
    
    IDEMPOTENCY_KEY_LENGTH: int = 100
    
settings = Config()