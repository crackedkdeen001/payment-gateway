import json
from datetime import datetime

from fastapi import Request, status
from fastapi.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from src.middleware.connection import middleware_conn
from src.exceptions.exceptions import IdempotencyException
from src.models import IdempotencyKey
from src.core import logger
from src.exceptions import DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY 
from src.repository.idempotency import IdempotencyRepository

class IdempotencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.idempotency_header = "X-Idempotency-Key"
        self.idempotency_store = IdempotencyRepository(middleware_conn())

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> JSONResponse | Response:
        if request.method in ["POST", "PATCH"]:
            request_body = await request.json()
            idempotency_key = request.headers.get(self.idempotency_header)

            if idempotency_key is not None:
                logger.info("Attempting to get cached response")
                existing = self.idempotency_store.get(idempotency_key, request.url.path)

                if existing is not None:
                    if existing.request_body != request_body:
                        raise IdempotencyException(message=DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY, status_code=status.HTTP_409_CONFLICT)

                    # return cached response if everything is in order
                    logger.info("Returning cached response from idempotency table")
                    return JSONResponse(content=existing.response_body, headers={"X-Idempotent-Replayed": "true"})
            response = await call_next(request)
            if should_cache_response(response.status_code):
                # store response in database if the request was successful
                json_response_body = [section async for section in response.body.iterator]
                response_body_dict = json.loads(json_response_body[0])
                logger.info(f"response_body={json_response_body[0].decode()}")
                new_record = IdempotencyKey(
                    id = None,
                    idempotency_key=idempotency_key,
                    request_path=request.url.path,
                    request_body=request_body,
                    response_body=response_body_dict,
                    response_code=response.status_code,
                    created_at=datetime.now()
                )
                self.idempotency_store.create(new_record)

                return JSONResponse(content=request_body, status_code=status.HTTP_200_OK)
            else:
                return response

        return await call_next(request)

def should_cache_response(status_code: int) -> bool:
    return 200 <= status_code < 300
