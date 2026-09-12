from datetime import datetime

from models import BaseModel


class BankReference(BaseModel):
    authorized_id: str
    authorized_at: datetime
    captured_id: str
    captured_at: datetime
    voided_id: str
    voided_at: datetime
    refunded_id: str
    refunded_at: datetime

