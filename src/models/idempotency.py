from datetime import datetime

from models import BaseModel


class IdempotencyKeys(BaseModel):
    id: int
    idempotency_key: str
    created_at: datetime

    request_method: str
    request_path: str
    request_params: dict

    response_body: dict
    response_code: int
