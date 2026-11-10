from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from src.dtos.helpers import receipt_prefix, order_prefix, customer_prefix

# added | str for converting it to a prefixed ID
class GeneralResponseFields(BaseModel):
    receipt_id: int | str
    order_id: UUID | str
    customer_id: int | str
    amount: int
    status: str

    def model_post_init(self, context: Any, /) -> None:
        self.receipt_id = receipt_prefix + str(self.receipt_id)
        self.order_id = order_prefix + str(self.order_id)
        self.customer_id = customer_prefix + str(self.customer_id)

class AuthorizeResponse(GeneralResponseFields):
    authorized_at: datetime
    expires_at: datetime

class CaptureResponse(GeneralResponseFields):
    captured_at: datetime

class VoidResponse(GeneralResponseFields):
    voided_at: datetime
    
class RefundResponse(GeneralResponseFields):
    refunded_at: datetime

class PaymentHistoryResponse(BaseModel):
    page: int
    total: int
    receipts: list[GeneralResponseFields]

class BankAuthorizeResponse(BaseModel):
    authorization_id: str
    status: str
    amount: int
    currency: str
    expires_at: datetime
    created_at: datetime
    
class BankCaptureResponse(BaseModel):
    capture_id: str
    authorization_id: str
    status: str
    amount: int
    currency: str
    captured_at: datetime

class BankVoidResponse(BaseModel):
    void_id: str
    authorization_id: str
    status: str
    voided_at: datetime
    
class BankRefundResponse(BaseModel):
    refund_id: str
    capture_id: str
    status: str
    amount: int
    currency: str
    refunded_at: datetime
    
class BankError(BaseModel):
    error: str
    message: str
    status_code: int