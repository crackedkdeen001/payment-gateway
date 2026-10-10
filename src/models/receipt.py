from datetime import datetime
from uuid import UUID

from src.models import BaseModel

from .states import PaymentStates


class Receipt(BaseModel):
    id: int | None
    order_id: UUID
    customer_id: int
    amount_in_cents: int
    currency: str
    card_number: str
    card_cvv: str
    card_expiry_month: int
    card_expiry_year: int
    current_state: PaymentStates
    authorize_id: str | None
    authorized_at: datetime | None
    auth_expiry : datetime | None
    capture_id: str | None
    captured_at: datetime | None
    void_id: str | None
    voided_at: datetime | None
    refund_id: str | None
    refunded_at: datetime | None
    created_at: datetime
