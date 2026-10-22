import json
from datetime import datetime

from psycopg import Connection
from starlette.responses import JSONResponse, Response

from src.core import logger
from src.exceptions import DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY
from src.models import IdempotencyKey
from src.repository.idempotency import IdempotencyRepository

IDEMPOTENCY_HEADER = "X-Idempotency-Key"


class Idempotency:
    def __init__(self, connection: Connection):
        self.repo = IdempotencyRepository(connection=connection)

    def replay(self, key: str, path: str, body: dict) -> Response | None:
        if not key:
            return None

        # if it hasn't been seen before, it is a new request
        existing = self.repo.get(key, path)
        if existing is None:
            return None

        # the same key with a different body is a client error
        if existing.request_body != body:
            return JSONResponse(
                content={"status": "error", "message": DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY},
                status_code=409)

        logger.info("Returning cached response from idempotency table")
        return JSONResponse(content=existing.response_body,
                            headers={"X-Idempotent-Replayed": "true"})

    def store(self, key: str, path: str, body: dict, response: Response):
        if not key:
            return
        if not 200 <= response.status_code < 300:
            return

        self.repo.create(IdempotencyKey(
            id=None,
            idempotency_key=key,
            request_path=path,
            request_body=body,
            response_body=json.loads(response.body),
            response_code=response.status_code,
            created_at=datetime.now(),
        ))
