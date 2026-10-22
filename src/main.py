import uvicorn
from fastapi import Depends, FastAPI, Request, status, HTTPException, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.dtos.requests import (
    AuthorizeReceiptRequest,
    CaptureReceiptRequest,
    VoidReceiptRequest,
    RefundReceiptRequest,
)
from src.dependencies import idempotency_header
from src.middleware.route import PaymentRoute


app = FastAPI()


idempotent_endpoints = APIRouter(route_class= PaymentRoute, dependencies= [Depends(idempotency_header)])

@app.exception_handler(RequestValidationError)
def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    message = ""
    for error in exc.errors():
        message += f"Field: {error['loc']}, Error: {error['msg']}"
        
    return JSONResponse(content={"status":"error", "message":message}, status_code=status.HTTP_400_BAD_REQUEST)

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(content={"status":"error", "message":exc.detail}, status_code=exc.status_code)

@idempotent_endpoints.post("/authorize", summary="Authorize a transaction")
async def authorize(idk: AuthorizeReceiptRequest):
    return idk.model_dump()

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
