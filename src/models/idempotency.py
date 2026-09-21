from datetime import datetime

from ..models import BaseModel


class IdempotencyKeys(BaseModel):
    id: int
    idempotency_key: str
    request_path: str
    request_params: dict
    response_body: dict | None
    response_code: int | None
    receipt_id: int
    created_at: datetime
    
