import json
from datetime import datetime

import psycopg
from fastapi import HTTPException, Request,status
from fastapi.responses import Response, JSONResponse
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from src.models import IdempotencyKey
from src.core import logger
from src.db.setup import get_conn_string
from src.exceptions import ErrorMessages
from src.repository.idempotency import IdempotencyRepository


# dependency can't be passed to the middleware, so doing random bs
conn = psycopg.connect(get_conn_string()) 

class IdempotencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.idempotency_header = "X-Idempotency-Key"
        self.idempotency_store = IdempotencyRepository(conn) 
   
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response | None:
        request_body = await request.json()
        if request.method in ["POST", "PATCH"]: 
            idempotency_key = request.headers.get(self.idempotency_header)
            
            if idempotency_key is not None:
                logger.info("Attempting to get cached response")
                existing = self.idempotency_store.get(idempotency_key, request.url.path)
                
                if existing is not None:
                    if existing.request_body != request_body:
                        raise HTTPException(status.HTTP_409_CONFLICT, detail=ErrorMessages.DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY)
                    
                    # return cached response if everything is in order
                    logger.info("Returning cached response from idempotency table")
                    return JSONResponse(content=existing.response_body, headers={"X-Idempotent-Replayed": "true"})
                # else:
                #     logger.warn("Idempotency record not found, creating a new one")
                #     # create a new idempotency record if the has not been seen before
                #     new_record = IdempotencyKey(
                #         id = None,
                #         idempotency_key=idempotency_key,
                #         request_path=request.url.path,
                #         request_body=request_body,
                #         response_body=None,
                #         response_code=None,
                #         created_at=datetime.now()
                #     )
                #     idempotency_store.create(new_record)
             
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
                    request_body=request_body,
                    response_body=response_body_dict,
                    response_code=response.status_code,
                    created_at=datetime.now()
                )
                self.idempotency_store.create(new_record)
                
                return response
        
        return await call_next(request)
        
def should_cache_response(status_code: int) -> bool:
    return 200 <= status_code < 300
