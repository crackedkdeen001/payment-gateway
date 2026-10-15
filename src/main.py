import pydantic_core
import uvicorn
from fastapi import Depends, FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.middleware.idempotency import IdempotencyMiddleware
from src.middleware.state_machine import StateMachineMiddleware
from src.dtos.requests import ReceiptAuthorize
from src.dependencies import idempotency_header

app = FastAPI(dependencies=[Depends(idempotency_header)])

app.add_middleware(IdempotencyMiddleware)
app.add_middleware(StateMachineMiddleware)


@app.exception_handler(RequestValidationError)
def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    message = ""
    for error in exc.errors():
        message += f"Field: {error['loc']}, Error: {error['msg']}"
        
    return JSONResponse(content={"status":"error", "message":message}, status_code=status.HTTP_400_BAD_REQUEST)

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(content={"status":"error", "message":exc.detail}, status_code=exc.status_code)

@app.post("/authorize", summary="Authorize a transaction")
async def authorize(idk: ReceiptAuthorize):
    return idk.model_dump()

@app.post("/capture", summary="Capture an authorized transaction")
async def capture(idk: ReceiptAuthorize):
    return idk.model_dump()

@app.post("/void", summary="Void an authorized transaction")
async def void(idk: ReceiptAuthorize):
    return idk.model_dump()

@app.post("/refund", summary="Refund a captured transaction")
async def refund(idk: ReceiptAuthorize):
    return idk.model_dump()


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
