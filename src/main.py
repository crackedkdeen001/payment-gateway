from typing import Annotated
from contextlib import asynccontextmanager

import psycopg
import uvicorn
from uuid import UUID
from fastapi import Depends, FastAPI, Request, Response, status, HTTPException, APIRouter, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.exceptions.exception import IDParsingError
from src.db.setup import get_dsn
from src.dtos.requests import (
    AuthorizeReceiptRequest,
    CaptureReceiptRequest,
    VoidReceiptRequest,
    RefundReceiptRequest,
    BankAuthorizeRequest,
    BankCaptureRequest,
    BankVoidRequest,
    BankRefundRequest,
    PaymentHistoryRequest
)
from src.dtos.responses import AuthorizeResponse, BankError, CaptureResponse, VoidResponse, RefundResponse, GeneralResponseFields, PaymentHistoryResponse
from src.dtos.helpers import (
    create_prefixed_customer_id,
    create_prefixed_order_id,
    create_prefixed_receipt_id,
    OrderID,
    ReceiptID
)
from src.dependencies import idempotency_header, get_connection
from src.middleware.route import PaymentRoute
from src.models import PaymentStates, Receipt
from src.repository import ReceiptRepository
from src.services.bank import BankService
from src.services.helpers import is_authorization_expired
from src.exceptions import (
    AMOUNT_MISMATCH,
    AUTHORIZATION_EXPIRED,
    RECEIPT_DOES_NOT_EXIST
)

app = FastAPI()

idempotent_endpoints = APIRouter(route_class=PaymentRoute, dependencies=[Depends(idempotency_header)])


@app.exception_handler(RequestValidationError)
def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    message = []
    for error in exc.errors():
        message.append(f"Field: {error['loc']}, Error: {error['msg']}")

    return JSONResponse(content={"status": "error", "message": message}, status_code=status.HTTP_400_BAD_REQUEST)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(content={"status": "error", "message": exc.detail}, status_code=exc.status_code)


@app.exception_handler(IDParsingError)
def http_exception_handler(request: Request, exc: IDParsingError):
    return JSONResponse(content={"status": "error", "message": exc.message}, status_code=status.HTTP_400_BAD_REQUEST)

@app.exception_handler(Exception)
def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse({"status": "error", "message": "Internal Server Error"},
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# noinspection unresolved-references,bad-argument-type
@idempotent_endpoints.post("/authorize", summary="Authorize a transaction")
async def authorize(authorize_request: AuthorizeReceiptRequest, request: Request):
    conn: psycopg.AsyncConnection = request.state.conn
    repository = ReceiptRepository(connection=conn)

    async with conn.transaction():
        receipt = await repository.create(
            Receipt(
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
            )
        )
        
        # If the receipt is none, it means it already exists in the database, 
        # so we check whether it is retryable, if not, we return an error
        if receipt is None:
            receipt = await repository.get_by_order_id(order_id=UUID(authorize_request.order_id.removeprefix("orx_")))
            if receipt.current_state != PaymentStates.PENDING:
                raise HTTPException(detail="Receipt has already been authorized", status_code=status.HTTP_400_BAD_REQUEST)
        else:
            await repository.create_audit(receipt, "ins")
        

    async with conn.transaction():
        bank_response = await BankService.authorize(
            BankAuthorizeRequest(
                card_number=authorize_request.card_number,
                cvv=authorize_request.card_cvv,
                expiry_month=authorize_request.card_expiry_month,
                expiry_year=authorize_request.card_expiry_year,
                amount=authorize_request.amount,
            ),
            idempotency_key=authorize_request.order_id
        )

        if isinstance(bank_response, BankError):
            if bank_response.status_code == status.HTTP_400_BAD_REQUEST:
                return JSONResponse(
                    content={"status": "error", "message": bank_response.message},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            raise HTTPException(status_code=bank_response.status_code, detail=bank_response.message)

    async with conn.transaction():
        receipt = await repository.update(
            receipt,
            current_state=PaymentStates.AUTHORIZED,
            authorize_id=bank_response.authorization_id,
            authorized_at=bank_response.created_at,
            auth_expiry=bank_response.expires_at,
        )
        await repository.create_audit(receipt, "upd")

        return AuthorizeResponse(
            receipt_id=create_prefixed_receipt_id(receipt.id),
            order_id=create_prefixed_order_id(receipt.order_id),
            customer_id=create_prefixed_customer_id(receipt.customer_id),
            amount=receipt.amount_in_cents,
            status=bank_response.status,
            authorized_at=bank_response.created_at,
            expires_at=bank_response.expires_at,
        )


# noinspection unresolved-references,bad-argument-type
@idempotent_endpoints.post("/capture", summary="Capture an authorized transaction")
async def capture(capture_request: CaptureReceiptRequest, request: Request):
    conn: psycopg.AsyncConnection = request.state.conn
    repository = ReceiptRepository(connection=conn)

    async with conn.transaction():
        receipt = await repository.get_by_id(receipt_id=int(capture_request.receipt_id.removeprefix("rex_")))

        if is_authorization_expired(receipt):
            raise HTTPException(detail=AUTHORIZATION_EXPIRED, status_code=status.HTTP_410_GONE)

        if receipt.amount_in_cents != capture_request.amount:
            raise HTTPException(detail=AMOUNT_MISMATCH, status_code=status.HTTP_400_BAD_REQUEST)

        authorization_id = receipt.authorize_id
        amount = receipt.amount_in_cents

    async with conn.transaction():
        bank_response = await BankService.capture(
            BankCaptureRequest(authorization_id=authorization_id, amount=amount),
            idempotency_key=capture_request.order_id,
        )

        if isinstance(bank_response, BankError):
            raise HTTPException(status_code=bank_response.status_code, detail=bank_response.message)
    
    async with conn.transaction():
        receipt = await repository.update(
            receipt,
            current_state=PaymentStates.CAPTURED,
            capture_id=bank_response.capture_id,
            captured_at=bank_response.captured_at,
        )
        await repository.create_audit(receipt, "upd")

        return CaptureResponse(
            receipt_id=create_prefixed_receipt_id(receipt.id),
            order_id=create_prefixed_order_id(receipt.order_id),
            customer_id=create_prefixed_customer_id(receipt.customer_id),
            amount=receipt.amount_in_cents,
            status=bank_response.status,
            captured_at=bank_response.captured_at,
        )


# noinspection bad-argument-type,unresolved-references
@idempotent_endpoints.post("/void", summary="Void an authorized transaction")
async def void(void_request: VoidReceiptRequest, request: Request):
    conn: psycopg.AsyncConnection = request.state.conn
    repository = ReceiptRepository(connection=conn)
    
    async with conn.transaction():
        receipt = await repository.get_by_id(int(void_request.receipt_id.removeprefix("rex_")))
        
        if is_authorization_expired(receipt):
            raise HTTPException(detail=AUTHORIZATION_EXPIRED, status_code=status.HTTP_410_GONE)

        authorization_id = receipt.authorize_id
        
    async with conn.transaction():
        bank_response = await BankService.void(
            BankVoidRequest(
                authorization_id=authorization_id
            ),
            idempotency_key=void_request.order_id
        )
        
        if isinstance(bank_response, BankError):
            raise HTTPException(detail=bank_response.message, status_code=bank_response.status_code)
    
    async with conn.transaction():
        await repository.update(receipt,
            current_state=PaymentStates.VOIDED,
            void_id=bank_response.void_id,
            voided_at=bank_response.voided_at
        )
        await repository.create_audit(receipt, "upd")
        
        return VoidResponse(
            receipt_id=create_prefixed_receipt_id(receipt.id),
            order_id=create_prefixed_order_id(receipt.order_id),
            customer_id=create_prefixed_customer_id(receipt.customer_id),
            amount=receipt.amount_in_cents,
            voided_at=bank_response.voided_at,
            status=bank_response.status
        )


# noinspection unresolved-references,bad-argument-type
@idempotent_endpoints.post("/refund", summary="Refund a captured transaction")
async def refund(request: Request, refund_request: RefundReceiptRequest):
    conn: psycopg.AsyncConnection = request.state.conn
    repository = ReceiptRepository(connection=conn)

    async with conn.transaction():
        receipt = await repository.get_by_id(int(refund_request.receipt_id.removeprefix("rex_")))
        
        if receipt.amount_in_cents != refund_request.amount:
            raise HTTPException(detail=AMOUNT_MISMATCH, status_code=status.HTTP_400_BAD_REQUEST)

        capture_id = receipt.capture_id

    async with conn.transaction():
        bank_response = await BankService.refund(
            BankRefundRequest(
                capture_id=capture_id,
                amount=refund_request.amount
            ),
            idempotency_key=refund_request.order_id
        )

        if isinstance(bank_response, BankError):
            raise HTTPException(detail=bank_response.message, status_code=bank_response.status_code)

    async with conn.transaction():
        await repository.update(receipt,
                          current_state=PaymentStates.REFUNDED,
                          refund_id=bank_response.refund_id,
                          refunded_at=bank_response.refunded_at
                          )
        await repository.create_audit(receipt, "upd")

        return RefundResponse(
            receipt_id=create_prefixed_receipt_id(receipt.id),
            order_id=create_prefixed_order_id(receipt.order_id),
            customer_id=create_prefixed_customer_id(receipt.customer_id),
            amount=receipt.amount_in_cents,
            refunded_at=bank_response.refunded_at,
            status=bank_response.status
        )

@app.get("/status", summary="Get payment status of a receipt")
async def get_payment_status(order_id:Annotated[OrderID, Query()]):
   async with await psycopg.AsyncConnection.connect(get_dsn()) as conn: 
        repository = ReceiptRepository(connection=conn)
        receipt = await repository.get_by_order_id(UUID(order_id.removeprefix("orx_")))

        if receipt is None:
            raise HTTPException(detail=RECEIPT_DOES_NOT_EXIST, status_code=status.HTTP_404_NOT_FOUND)
        
        return GeneralResponseFields(
            receipt_id=create_prefixed_receipt_id(receipt.id),
            order_id=create_prefixed_order_id(receipt.order_id),
            customer_id=create_prefixed_customer_id(receipt.customer_id),
            status=receipt.current_state,
            amount=receipt.amount_in_cents
        )
   
@app.get("/history", summary="Get the payment history of a customer")
async def get_customer_history(payment_history_params:Annotated[PaymentHistoryRequest, Query()]):
    async with await psycopg.AsyncConnection.connect(get_dsn()) as conn:
        repository = ReceiptRepository(connection=conn)
        
        customer_id = int(payment_history_params.customer_id.removeprefix("cux_"))
        
        receipts = await repository.get_history_by_customer_id(
            customer_id,
            payment_history_params.limit,
            payment_history_params.offset
        )
        
        if not receipts:
            return JSONResponse(content={"detail":"No history found"}, status_code=status.HTTP_404_NOT_FOUND)
        
        processed_receipts = []
        for receipt in receipts:
            processed_receipts.append(
                GeneralResponseFields(
                    receipt_id=create_prefixed_receipt_id(receipt.id),
                    order_id=create_prefixed_order_id(receipt.order_id),
                    customer_id=create_prefixed_customer_id(receipt.customer_id),
                    status=receipt.current_state,
                    amount=receipt.amount_in_cents
                )
            )
        
        return PaymentHistoryResponse(
            total=len(processed_receipts),
            page=payment_history_params.offset,
            receipts=processed_receipts
        )            
            
@app.get("/verify", summary="Verify goods have been paid for before shipping")
async def verify_goods(receipt_id: ReceiptID):
    async with await psycopg.AsyncConnection.connect(get_dsn()) as conn:
        repository = ReceiptRepository(connection=conn)
        
        receipt = await repository.get_by_id(int(receipt_id.removeprefix("rex_")))
        
        if receipt is None:
            raise HTTPException(detail=RECEIPT_DOES_NOT_EXIST, status_code=status.HTTP_404_NOT_FOUND)
        
        if receipt.current_state == PaymentStates.CAPTURED:
            return JSONResponse(content={"status":"Eligible for shipping"})
        else:
            return JSONResponse(content={"status":"Not eligible for shipping"})


app.include_router(idempotent_endpoints)

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True, port=9000)
