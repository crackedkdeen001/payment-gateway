from fastapi.exceptions import HTTPException
from typing import Annotated

from fastapi import Header, status, Request

from src.exceptions import IDEMPOTENCY_KEY_TOO_LONG
from src.core import settings


async def idempotency_header(X_Idempotency_Key: Annotated[str, Header()]):
    if len(X_Idempotency_Key) > settings.IDEMPOTENCY_KEY_LENGTH:
        raise HTTPException(detail=IDEMPOTENCY_KEY_TOO_LONG, status_code=status.HTTP_400_BAD_REQUEST)
    return {"X-Idempotency-Key": X_Idempotency_Key}


async def get_connection_from_request(request: Request):
    yield request.state.conn


async def get_connection_from_app(request: Request):
    async with request.app.state.pool.connection() as conn:
        yield conn