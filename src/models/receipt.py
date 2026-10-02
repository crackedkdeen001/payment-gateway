from datetime import datetime
from uuid import UUID

from src.models import BaseModel

from .card import Card
from .states import PaymentStates
from .bank_reference import BankReference


class Receipt(BaseModel):
    id: int
    order_id: UUID
    customer_id: int
    amount_in_cents: int
    currency: str
    card: Card
    current_state: PaymentStates
    bank_reference: BankReference
    created_at: datetime
