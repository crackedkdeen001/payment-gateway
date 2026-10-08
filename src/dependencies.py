from typing import Annotated

from fastapi import Header, status
from fastapi.responses import JSONResponse

from src.exceptions import IDEMPOTENCY_KEY_TOO_LONG
from  src.core import settings


async def idempotency_header(X_Idempotency_Key: Annotated[str, Header()]):
    if len(X_Idempotency_Key) > settings.IDEMPOTENCY_KEY_LENGTH:
        return JSONResponse(
            content={"status":"error", "message":IDEMPOTENCY_KEY_TOO_LONG},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return {"X-Idempotency-Key": X_Idempotency_Key}
