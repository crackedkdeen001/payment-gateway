from typing import Annotated

from pydantic import BaseModel, Field

from .helpers import OrderID, CustomerID, ReceiptID, PositiveAmount, ValidMonth, ValidYear, ValidCurrency


class GenericReceiptRequest(BaseModel):
    order_id: OrderID

class AuthorizeReceiptRequest(GenericReceiptRequest):
    customer_id: CustomerID
    card_number: Annotated[str, Field(min_length=13, max_length=19)]
    card_cvv: Annotated[str, Field(max_length=3)]
    card_expiry_month: ValidMonth
    card_expiry_year: ValidYear
    currency: ValidCurrency
    amount: PositiveAmount
    
class ParamsForReceiptIDDependentEndpoints(GenericReceiptRequest):
    receipt_id: ReceiptID
    
class CaptureReceiptRequest(ParamsForReceiptIDDependentEndpoints):
    amount: PositiveAmount

class VoidReceiptRequest(ParamsForReceiptIDDependentEndpoints):
    pass
    
class RefundReceiptRequest(ParamsForReceiptIDDependentEndpoints):
    amount: PositiveAmount
    
class PaymentHistoryRequest(BaseModel):
    customer_id: CustomerID
    limit: PositiveAmount
    offset: PositiveAmount
    
class BankAuthorizeRequest(BaseModel):
    card_number: str
    cvv: str
    expiry_month: int
    expiry_year: int
    amount: PositiveAmount
    
class ParamsForAuthIDDependentEndpoints(BaseModel):
    authorization_id: str
    
class BankVoidRequest(ParamsForAuthIDDependentEndpoints):
    pass

class BankCaptureRequest(ParamsForAuthIDDependentEndpoints):
    amount: PositiveAmount

class BankRefundRequest(BaseModel):
    capture_id: str
    amount: int
    
