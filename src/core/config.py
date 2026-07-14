from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the project"""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    database_url: str
    

settings = Settings()  # pyright: ignore[reportCallIssue]
    