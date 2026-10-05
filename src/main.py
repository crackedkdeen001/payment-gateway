import uvicorn
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.exceptions import INTERNAL_SERVER_ERROR
from src.middleware.idempotency import IdempotencyMiddleware
from src.dependencies import idempotency_header
from src.exceptions import CustomBaseException
from src.models import Card

app = FastAPI(dependencies=[Depends(idempotency_header)])

app.add_middleware(
    IdempotencyMiddleware
)


@app.exception_handler(Exception)
def http_exception_handler(request: Request, exc:Exception):
    if isinstance(exc, CustomBaseException):
        return JSONResponse(content=exc.content(), status_code=exc.status_code)
    return JSONResponse(content={"error":INTERNAL_SERVER_ERROR}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/authorize")
def authorize(card: Card):
    return card

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
