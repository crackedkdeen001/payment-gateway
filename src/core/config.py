import os
from datetime import timedelta, datetime

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), ".env")

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV, extra='forbid')
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_URL: PostgresDsn
    
    TEST_POSTGRES_USER: str
    TEST_POSTGRES_PASSWORD: str
    TEST_POSTGRES_DB: str
    TEST_POSTGRES_HOST: str
    TEST_POSTGRES_PORT: int
    
    BANK_API_URL: str

    IDEMPOTENCY_KEY_LENGTH: int = 100

settings = Config()