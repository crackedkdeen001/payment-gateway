from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from ..models import BaseModel

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
    created_at: datetime
    bank_reference: BankReference
