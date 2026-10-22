from datetime import datetime

from pydantic import BaseModel

from .helpers import ReceiptID, OrderID, CustomerID, PositiveAmount

class GeneralResponseFields(BaseModel):
    receipt_id: ReceiptID
    order_id: OrderID
    customer_id: CustomerID
    amount: PositiveAmount
    status: str

class AuthorizeResponse(GeneralResponseFields):
    authorized_at: datetime
    expires_at: datetime

class CaptureResponse(GeneralResponseFields):
    captured_at: datetime

class VoidResponse(GeneralResponseFields):
    voided_at: datetime
    
class RefundResponse(GeneralResponseFields):
    refunded_at: datetime

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
    amount: str
    currency: str
    refunded_at: datetime
    
class BankError(BaseModel):
    error: str
    message: str
    status_code: int