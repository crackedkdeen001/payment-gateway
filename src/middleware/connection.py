import psycopg
from src.db.setup import get_conn_string

# TODO make the connections for middleware handle errors

# BaseHTTPMiddlewares can't access fastapi dependencies
# So they have their own connection to the database.
def middleware_conn():
    conn = psycopg.connect(get_conn_string())
    return conn
