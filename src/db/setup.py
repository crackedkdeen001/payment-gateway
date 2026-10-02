from typing import Annotated

import psycopg
from fastapi import Depends

from src.core.config import settings

def get_conn_string():
    return f"host={settings.POSTGRES_HOST} port={settings.POSTGRES_PORT} dbname={settings.POSTGRES_DB} user={settings.POSTGRES_USER} password={settings.POSTGRES_PASSWORD}"

def get_connection():
    conn_string = get_conn_string()
    with psycopg.connect(conninfo=conn_string, autocommit=True) as conn:
        yield conn


Conn = Annotated[psycopg.Connection, Depends(get_connection)]


