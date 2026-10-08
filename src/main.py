import uvicorn
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.middleware.idempotency import IdempotencyMiddleware
from src.dependencies import idempotency_header
from src.models import Card

app = FastAPI(dependencies=[Depends(idempotency_header)])

app.add_middleware(
    IdempotencyMiddleware
)


@app.exception_handler(RequestValidationError)
def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    message = ""
    for error in exc.errors():
        message += f"Field: {error['loc']}, Error: {error['msg']}"
        
    return JSONResponse(content={"status":"error", "message":message}, status_code=status.HTTP_400_BAD_REQUEST)

@app.post("/authorize")
async def authorize(card: Card):
    return card

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
