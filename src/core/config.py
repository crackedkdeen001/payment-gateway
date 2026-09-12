from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# dynamically sets the file path depending on whether the 
# .env file is read from tests or used normally
base_dir_name = Path.cwd().name
if base_dir_name == "tests":
    env_args = {
    "env_file" : str(Path.cwd().parent / ".env")
    }
else:
    env_args = {
        "env_file" : ".env",
        "env_file_depth" : 3
    }
    
class Config(BaseSettings):
    model_config = SettingsConfigDict(**env_args)
    
    database_url: str
    
settings = Config()