import math
import asyncio
import f

import psycopg
import uvicorn
from uuid import UUID
from fastapi import Depends, FastAPI, Request, Response, status, HTTPException, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from psycopg import Connection

from src.core import logger, settings
from src.dtos.requests import (
    AuthorizeReceiptRequest,
    CaptureReceiptRequest,
    VoidReceiptRequest,
    RefundReceiptRequest,
)
from src.dependencies import idempotency_header
from src.middleware.route import PaymentRoute
from src.dtos.requests import BankAuthorizeRequest
from src.dtos.responses import AuthorizeResponse, BankError
from src.dtos.helpers import (
    create_prefixed_customer_id,
    create_prefixed_order_id,
    create_prefixed_receipt_id,
)
from src.models import PaymentStates, Receipt
from src.repository import ReceiptRepository
from src.services.bank import BankService


app = FastAPI()
retries = 0

# @app.middeware("http")
# async def retry_middleware(request: Request, call_next):
#     try:
#         response: Response = await call_next(request)
#         
#         global retries
#         while True:
#             if response.status_code >= 500:
#                 wait_in_milliseconds = (int((math.pow(2, retries) - 1) * 100) / 1000)  # to milliseconds
#                 logger.info(f"wait: {wait_in_milliseconds}, retry_count: {retries}")
#                 await asyncio.sleep(wait_in_milliseconds)
#                 
#                 if retries == settings.MAX_RETRY:
#                     return response
#                 
#                 retries += 1
#                 continue
#             else:
#                 break
#                 
#         return response
#     except psycopg.Error:
#         retries += 1
#         response: Response = await call_next(request)
#         
#         if retries == settings.MAX_RETRY:
#             return response

        

idempotent_endpoints = APIRouter(route_class= PaymentRoute, dependencies=[Depends(idempotency_header)])

@app.exception_handler(RequestValidationError)
def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    message = []
    for error in exc.errors():
        message.append(f"Field: {error['loc']}, Error: {error['msg']}")
        
    return JSONResponse(content={"status":"error", "message":message}, status_code=status.HTTP_400_BAD_REQUEST)

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(content={"status":"error", "message":exc.detail}, status_code=exc.status_code)

@app.exception_handler(Exception)
def general_exception_handler(request:Request, exc: Exception):
    return JSONResponse({"status":"error", "message":"Internal Server Error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR    )

@idempotent_endpoints.post("/authorize", summary="Authorize a transaction")
async def authorize(authorize_request: AuthorizeReceiptRequest, request: Request):
    conn: Connection = request.state.conn
    repository = ReceiptRepository(connection=conn)
    receipt = repository.create(Receipt(
        id=None,
        order_id=UUID(authorize_request.order_id.removeprefix("orx_")),
        customer_id=int(authorize_request.customer_id.removeprefix("cux_")),
        amount_in_cents=authorize_request.amount,
        currency=authorize_request.currency,
        card_number=authorize_request.card_number,
        card_cvv=authorize_request.card_cvv,
        card_expiry_month=authorize_request.card_expiry_month,
        card_expiry_year=authorize_request.card_expiry_year,
        current_state=PaymentStates.PENDING,
        authorize_id=None,
        authorized_at=None,
        auth_expiry=None,
        capture_id=None,
        captured_at=None,
        void_id=None,
        voided_at=None,
        refund_id=None,
        refunded_at=None,
        created_at=None,
    ))
    repository.create_audit(receipt, "ins")
    repository.commit()
    
    with conn.transaction():
        bank_response = await BankService.authorize(BankAuthorizeRequest(
            card_number=authorize_request.card_number,
            cvv=authorize_request.card_cvv,
            expiry_month=authorize_request.card_expiry_month,
            expiry_year=authorize_request.card_expiry_year,
            amount=authorize_request.amount,
        ))
        if isinstance(bank_response, BankError):
            if bank_response.status_code == status.HTTP_400_BAD_REQUEST:
                return JSONResponse(
                    content={"status": "error", "message": bank_response.message},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            raise HTTPException(status_code=bank_response.status_code, detail=bank_response.message)

        receipt = repository.update(
            receipt,
            current_state=PaymentStates.AUTHORIZED,
            authorize_id=bank_response.authorization_id,
            authorized_at=bank_response.created_at,
            auth_expiry=bank_response.expires_at,
        )
        repository.create_audit(receipt, "upd")
        
    return AuthorizeResponse(
        receipt_id=create_prefixed_receipt_id(receipt.id),
        order_id=create_prefixed_order_id(receipt.order_id),
        customer_id=create_prefixed_customer_id(receipt.customer_id),
        amount=receipt.amount_in_cents,
        status=bank_response.status,
        authorized_at=bank_response.created_at,
        expires_at=bank_response.expires_at,
    )

@idempotent_endpoints.post("/capture", summary="Capture an authorized transaction")
async def capture(idk: CaptureReceiptRequest):
    return idk.model_dump()

@idempotent_endpoints.post("/void", summary="Void an authorized transaction")
async def void(idk: VoidReceiptRequest):
    return idk.model_dump()

@idempotent_endpoints.post("/refund", summary="Refund a captured transaction")
async def refund(idk: RefundReceiptRequest):
    return idk.model_dump()

app.include_router(idempotent_endpoints)


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
