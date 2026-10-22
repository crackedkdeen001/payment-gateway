from uuid import UUID

from psycopg import Connection
from starlette.responses import JSONResponse, Response

from src.exceptions import RECEIPT_DOES_NOT_EXIST
from src.models import PaymentStates
from src.repository import ReceiptRepository

# the endpoints that are allowed for each state
VALID_ENDPOINTS = {
    PaymentStates.PENDING: ["/authorize"],
    PaymentStates.AUTHORIZED: ["/capture", "/void"],
    PaymentStates.CAPTURED: ["/refund"],
}


class StateMachine:
    def __init__(self, connection: Connection):
        self.receipt_repo = ReceiptRepository(connection=connection)

    def check(self, path: str, order_id: UUID) -> Response | None:
        """None when the request may continue, an error response when it may not."""
        receipt = self.receipt_repo.get_by_order_id(order_id=order_id)

        # new payments are only allowed on the /authorize endpoint
        if receipt is None:
            if path == "/authorize":
                return None
            return JSONResponse(content={"status": "error", "message": RECEIPT_DOES_NOT_EXIST},
                                status_code=404)

        state = receipt.current_state

        # voided and refunded are terminal states
        if state in (PaymentStates.VOIDED, PaymentStates.REFUNDED):
            return invalid_transition_response(state)

        if path not in VALID_ENDPOINTS[state]:
            return invalid_transition_response(state)

        return None


def invalid_transition_response(state: PaymentStates) -> JSONResponse:
    endpoints = ", ".join(VALID_ENDPOINTS.get(state, []))
    message = "request can't be processed at this endpoint"
    if endpoints:
        message = f"{message}. Try sending it to {endpoints}"
    return JSONResponse(content={"status": "error", "message": message},
                        status_code=400)
