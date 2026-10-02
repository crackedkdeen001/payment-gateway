import uvicorn
from fastapi import Depends, FastAPI

from src.middleware.idempotency import IdempotencyMiddleware
from src.dependencies import idempotency_header
from src.models import Card

app = FastAPI(dependencies=[Depends(idempotency_header)])

app.add_middleware(
    IdempotencyMiddleware
)

@app.post("/authorize")
def authorize(card: Card):
    return card

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)