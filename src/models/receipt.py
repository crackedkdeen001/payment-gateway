from datetime import datetime
from uuid import UUID

from models import BankReference, BaseModel, Card, PaymentStates


class Receipt(BaseModel):
    id: int 
    order_id: UUID
    customer_id: int
    card: Card
    current_state: PaymentStates
    created_at: datetime
    bank_reference: BankReference
    