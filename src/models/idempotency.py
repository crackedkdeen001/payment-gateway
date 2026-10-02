from datetime import datetime

from src.models import BaseModel


class IdempotencyKey(BaseModel):
    id: int | None
    idempotency_key: str
    request_path: str
    request_body: dict
    response_body: dict | None
    response_code: int | None
    created_at: datetime | None
    
