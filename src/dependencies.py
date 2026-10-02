from typing import Annotated

from fastapi import Header


async def idempotency_header(X_Idempotency_Key: Annotated[str, Header()]):
    return {"X-Idempotency-Key": X_Idempotency_Key}
