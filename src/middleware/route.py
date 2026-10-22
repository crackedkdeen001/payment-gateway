import json
from collections.abc import Callable

import psycopg
from fastapi import Request, Response, HTTPException
from fastapi.routing import APIRoute
from starlette import status
from starlette.responses import JSONResponse

from middleware.helpers import parse_order_id
from src.exceptions.exception import IDParsingError

from src.db import get_dsn
from src.exceptions import EMPTY_REQUEST_BODY
from src.middleware.idempotency import IDEMPOTENCY_HEADER, Idempotency
from src.middleware.state_machine import StateMachine

# Route as middleware
# To make sure everything error that gets propagated can be handled by the FastAPI exception Handlers
class PaymentRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            body = await read_body(request)
            
            # one connection (and one transaction) for the whole request
            with psycopg.connect(get_dsn()) as conn:
                request.state.conn = conn

                # 1. state machine: is this request allowed to touch the receipt?
                state_machine = StateMachine(conn)
                try:
                    order_id = parse_order_id(body["order_id"])
                except (IDParsingError, KeyError, TypeError, AttributeError):
                    raise HTTPException(detail="Invalid order ID", status_code=status.HTTP_400_BAD_REQUEST)

                error = state_machine.check(request.url.path, order_id)
                if error is not None:
                    return error

                # 2. idempotency: replay the cached response or run the request
                idempotency = Idempotency(conn)
                key = request.headers.get(IDEMPOTENCY_HEADER)
                
                cached = idempotency.replay(key, request.url.path, body)
                if cached is not None:
                    return cached

                response = await original_route_handler(request)

                # 3. cache the response so the same key can be replayed
                idempotency.store(key, request.url.path, body, response)
                return response

        return custom_route_handler


async def read_body(request: Request) -> dict:
    raw = await request.body()
    if not raw:
        raise HTTPException(detail=EMPTY_REQUEST_BODY, status_code=status.HTTP_400_BAD_REQUEST)

    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(detail="Malformed JSON body", status_code=status.HTTP_400_BAD_REQUEST)

    if not isinstance(body, dict):
        raise HTTPException(detail="Malformed JSON body", status_code=status.HTTP_400_BAD_REQUEST)

    return body


