import json

from fastapi import Request
from starlette import status
from starlette.responses import JSONResponse

from src.models import PaymentStates
from src.exceptions import EMPTY_REQUEST_BODY


async def get_request_body(request: Request) -> JSONResponse | dict:
    bytes_request_body = await request.body()
    # return an error if request_body is empty
    if not bytes_request_body:
        return JSONResponse(content={"status": "error", "message": EMPTY_REQUEST_BODY},
                            status_code=status.HTTP_400_BAD_REQUEST)

    return json.loads(bytes_request_body)


valid_endpoints = {
    PaymentStates.PENDING:["/authorize"],
    PaymentStates.AUTHORIZED: ["/capture", "/void"],
    PaymentStates.CAPTURED: ["/refund"],
}


def invalid_state_transition_response(state: PaymentStates | None):
    if not state:
        return JSONResponse(
            content={"state": "error", "message": "request can't be processed at this endpoint"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    endpoints = "".join(valid_endpoints[state])
    return JSONResponse(
        content=
        {
            "state": "error",
            "message": f"request can't be processed at this endpoint. Try sending it to {endpoints}"
        },
        status_code=status.HTTP_400_BAD_REQUEST
    )
