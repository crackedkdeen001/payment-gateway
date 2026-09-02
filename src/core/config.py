from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_depth="3")
    
    database_url: str = Field(alias="DATABASE_URL")
    
    
settings = Config()