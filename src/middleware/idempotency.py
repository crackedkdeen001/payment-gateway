from datetime import datetime

import psycopg
from psycopg._enums import IsolationLevel
from fastapi import HTTPException
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from core import toJsonb
from src.models import IdempotencyKey
from src.dependencies import Conn
from src.core import logger, settings
from src.exceptions import ErrorMessages
from repository.idempotency import IdempotencyRepository

"""
Checks if a request has been seen before using the idempotency key provided
If it has, it should return the response stored in the postgres database.
If it hasn't, then it should forward the request to the appropriate route function to handle it.
The middleware should also only work with particular endpoints that require idempotency

edge cases:
no idempotency header is seen
If the same idempotency key is used on the same path but with different request parameters, we return a conflict error
saying that the idempotency key has been used before.
the request sent is currently in progress 
"""

def atomic_phase(conn: Conn, idempotency_key: IdempotencyKey | None, callback):
    conn.isolation_level = IsolationLevel.SERIALIZABLE
    error = False
    repository = IdempotencyRepository(conn)

    try:
        with Conn.transaction():
            ret = callback()

            if isinstance(ret, (NoOp, RecoveryPoint, Response)):
                ret.call(key)
            else:
                raise Exception
    except psycopg.errors.SerializationFailure:
        error = True
        raise HTTPException(status.HTTP_409_CONFLICT, ErrorMessages.)
    except Exception:
        error = True
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorMessages.)
    finally:
        if error and idempotency_key is not None:
            try:
                
        

class IdempotencyMiddleWare(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, conn= Conn):
        super().__init__(app)
        self.header = "X-Idempotency-Key" 
        self.conn = conn
        self.repository = IdempotencyRepository(self.conn)
        self.allowed_methods = ["POST", "PATCH"]
        
        self.conn.isolation_level = IsolationLevel.SERIALIZABLE
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method in self.allowed_methods:
            idempotency_key_val = request.headers.get(self.header)
            # if no key is provided, raise an exception
            if idempotency_key_val is None:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.IDEMPOTENCY_KEY_NOT_FOUND)
            else:
                key = self.repository.get(idempotency_key_val, request.url.path)
                if key is not None:
                   # if the idempotency_keys are the same but the request parameters are different,
                   # we assume it's an invalid request and raise an exception 
                   if key.request_params != request.path_params:
                       raise HTTPException(status.HTTP_409_CONFLICT, detail=ErrorMessages.DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY)
                   
                   # if the same request is sent while it's still being processed
                   # we raise an exception
                   request_start_time = datetime.now() - settings.IDEMPOTENCY_KEY_LOCK_TIMEOUT
                   if key.locked_at and key.locked_at > request_start_time:
                       err_message = ErrorMessages.REQUEST_IN_PROGRESS + f" {request_start_time.microsecond}"
                       raise HTTPException(status.HTTP_409_CONFLICT, detail=err_message)
                
                   
                else:
                   # create a new idempotency record if the has not been seen before
                   key = IdempotencyKey(
                        id = None,
                        idempotency_key=idempotency_key_val,
                        request_path=request.url.path,
                        request_params=toJsonb(request.path_params),
                        response_body=None,
                        response_code=None,
                        recovery_point=,
                        locked_at=datetime.now(),
                        expires_at=settings.IDEMPOTENCY_KEY_EXPIRY_TIME,
                        created_at=datetime.now()
                   )
                   self.repository.create(key)
             

class NoOp:
    def __init__(self):
        pass
    
class RecoveryPoint:
    def __init__(self, name: str):
        self.name = name
        
    def call(self, key: IdempotencyKey):
        key.recovery_point = self.name
        

class CustomResponse(Response):
    def call
