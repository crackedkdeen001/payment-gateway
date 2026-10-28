from .config import Config
from .log import logger

settings = Config()

__all__ = [
    "logger",
    "settings",
]