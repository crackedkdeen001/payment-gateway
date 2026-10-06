from typing import Annotated

from fastapi import Header, status

from src.exceptions import CustomBaseException, IDEMPOTENCY_KEY_TOO_LONG
from  src.core import settings


async def idempotency_header(X_Idempotency_Key: Annotated[str, Header()]):
    if len(X_Idempotency_Key) > settings.IDEMPOTENCY_KEY_LENGTH:
        raise CustomBaseException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=IDEMPOTENCY_KEY_TOO_LONG
        )
    return {"X-Idempotency-Key": X_Idempotency_Key}
