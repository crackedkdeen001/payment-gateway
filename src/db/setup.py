from pathlib import Path
from typing import Annotated

import psycopg
from fastapi import Depends
from psycopg import Connection

from src.core.config import settings

def get_dsn():
    if Path.cwd().name == "tests":
        return f"host={settings.TEST_POSTGRES_HOST} port={settings.TEST_POSTGRES_PORT} dbname={settings.TEST_POSTGRES_DB} user={settings.TEST_POSTGRES_USER} password={settings.TEST_POSTGRES_PASSWORD}"

    return f"host={settings.POSTGRES_HOST} port={settings.POSTGRES_PORT} dbname={settings.POSTGRES_DB} user={settings.POSTGRES_USER} password={settings.POSTGRES_PASSWORD}"


async def get_connection():
    with psycopg.connect(get_dsn()) as conn:
        yield conn

