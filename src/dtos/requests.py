from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.dtos.helpers import (
    OrderID,
    CustomerID,
    ReceiptID,
    PositiveAmount,
    ValidMonth,
    ValidYear,
    ValidCurrency,
    order_prefix,
    receipt_prefix,
    customer_prefix,
)


class GenericReceiptRequest(BaseModel):
    order_id: OrderID
    
    # converts prefix ID to native type to native type 
    def model_post_init(self, context: Any, /) -> None:
        self.order_id = UUID(self.order_id.removeprefix(order_prefix))
        
        if type(self).model_fields.get("receipt_id", None):
            self.receipt_id = int(self.receipt_id.removeprefix(receipt_prefix))

        if type(self).model_fields.get("customer_id", None):
            self.customer_id = int(self.customer_id.removeprefix(customer_prefix))

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
    
