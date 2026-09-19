from datetime import datetime

from ..models import BaseModel


class BankReference(BaseModel):
    authorize_id: str | None 
    authorized_at: datetime | None
    capture_id: str | None
    captured_at: datetime | None
    void_id: str | None
    voided_at: datetime | None
    refund_id: str | None
    refunded_at: datetime | None

