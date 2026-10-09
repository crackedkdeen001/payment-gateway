import json
from datetime import datetime

import psycopg
from fastapi import Request, status
from fastapi.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from src.db import get_conn_string
from src.models import IdempotencyKey
from src.core import logger
from src.exceptions import DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY, EMPTY_REQUEST_BODY
from src.repository.idempotency import IdempotencyRepository

class IdempotencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.idempotency_header = "X-Idempotency-Key"
        self.idempotency_store = None

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> JSONResponse | Response:
        with psycopg.connect(get_conn_string()) as conn:
            with conn.transaction():
                self.idempotency_store = IdempotencyRepository(conn)
                
                if request.method not in ["POST", "PATCH"]:
                    return await call_next(request)
                
                bytes_request_body = await request.body()
                # raise an error if request_body is empty
                if not bytes_request_body:
                    return JSONResponse(content={"status":"error", "message": EMPTY_REQUEST_BODY}, status_code=status.HTTP_400_BAD_REQUEST)
                json_request_body = json.loads(bytes_request_body)
                
                idempotency_key = request.headers.get(self.idempotency_header)
                if idempotency_key is not None:
                    logger.info("Attempting to get cached response")
                    existing = self.idempotency_store.get(idempotency_key, request.url.path)
                    
                    # using an idempotency key with the different request bodies
                    # yields an error.
                    if existing is not None:
                        if existing.request_body != json_request_body:
                            return JSONResponse(content={"status":"error", "message": DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY}, status_code=status.HTTP_409_CONFLICT)

                        # return cached response if everything is in order
                        logger.info("Returning cached response from idempotency table")
                        return JSONResponse(content=existing.response_body, headers={"X-Idempotent-Replayed": "true"})
                
                # no need to add exceptions for idempotency key being empty
                # fastapi handles it for us automatically
                response = await call_next(request)
                if should_cache_response(response.status_code):
                    # store response in database if the request was successful
                    json_response_body = [section async for section in response.body_iterator]
                    response_body_dict = json.loads(json_response_body[0])
                    logger.info(f"response_body={json_response_body[0].decode()}")
                    new_record = IdempotencyKey(
                        id = None,
                        idempotency_key=idempotency_key,
                        request_path=request.url.path,
                        request_body=json_request_body,
                        response_body=response_body_dict,
                        response_code=response.status_code,
                        created_at=datetime.now()
                    )
                    self.idempotency_store.create(new_record)
                    
                    return JSONResponse(content=json_request_body, status_code=status.HTTP_200_OK)
                else:
                    return response
        


def should_cache_response(status_code: int) -> bool:
    return 200 <= status_code < 300
