from uuid import UUID

import psycopg
import pydantic_core
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.dtos.requests import ReceiptAuthorize
from src.repository import ReceiptRepository
from src.db import get_conn_string
from src.middleware.helpers import get_request_body, valid_endpoints, invalid_state_transition_response
from src.models import Receipt, PaymentStates


class StateMachineMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.receipt_repo = None
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        with psycopg.connect(get_conn_string()) as conn:
            with conn.transaction():
                if request.method != "POST":
                    return await call_next(request)
                
                self.receipt_repo = ReceiptRepository(connection=conn)
                
                request_body = await get_request_body(request)
                if isinstance(request_body, JSONResponse):
                    return request_body
                
                try:
                    request_model = ReceiptAuthorize(**request_body)
                except pydantic_core.ValidationError as exc:
                    fields = []
                    for err in exc.errors():
                        loc = [p for p in err["loc"] if p not in ("body", "path", "query")]
                        fields.append(
                            {
                                "detail": f"{"".join((map(str, loc)))}: {err["msg"]}"
                            }
                        )
                    return JSONResponse(content={"status":"error", "message":fields}, status_code=status.HTTP_400_BAD_REQUEST)
                
                receipt = self.receipt_repo.get_by_order_id(order_id=UUID(request_model.order_id))
                # set receipt state to pending if it has never been seen before
                if receipt is None:
                    new_receipt = Receipt(
                        id = None,
                        customer_id=int(request_model.customer_id),
                        order_id=UUID(request_model.order_id),
                        amount_in_cents=request_body["amount"],
                        currency=request_body["currency"],
                        card_number=request_body["card_number"],
                        card_cvv=request_body["card_cvv"],
                        card_expiry_month=request_body["card_expiry_month"],
                        card_expiry_year=request_body["card_expiry_year"],
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
                        created_at=None
                    )
                    new_receipt = self.receipt_repo.create(new_receipt)
                    
                
                state = receipt.current_state if receipt else new_receipt.current_state
                match state:
                    case PaymentStates.PENDING:
                        if request.url.path not in valid_endpoints[PaymentStates.PENDING]:
                            return invalid_state_transition_response(PaymentStates.PENDING)
                    case PaymentStates.AUTHORIZED:
                        if request.url.path not in valid_endpoints[PaymentStates.AUTHORIZED]:
                            return invalid_state_transition_response(PaymentStates.AUTHORIZED)
                    case PaymentStates.CAPTURED:
                        if request.url.path not in valid_endpoints[PaymentStates.AUTHORIZED]:
                            return invalid_state_transition_response(PaymentStates.CAPTURED)
                    case PaymentStates.VOIDED | PaymentStates.REFUNDED:
                        return invalid_state_transition_response(state=None)
                    
                return await call_next(request)
