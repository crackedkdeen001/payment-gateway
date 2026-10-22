from typing import Annotated

from pydantic import BaseModel, Field

from .helpers import OrderID, CustomerID, ReceiptID, PositiveAmount


# --- For responses


# -- for requests 
# check if the id sent has the prefix, we return an error if it doesn't.
# remove the prefix specified in the function parameter and return it back
# if the prefix is "rex_" or "cux_", parse it as an integer, else we parse it as an UUID and return to the sender


class GenericReceiptRequest(BaseModel):
    order_id: OrderID

class AuthorizeReceiptRequest(GenericReceiptRequest):
    customer_id: CustomerID
    card_number: Annotated[str, Field(min_length=13, max_length=19)]
    card_cvv: Annotated[str, Field(max_length=3)]
    card_expiry_month: Annotated[int, Field(ge=1, le=12)]
    card_expiry_year: Annotated[int, Field(ge=1800)]
    currency: Annotated[str, Field(max_length=3)]
    amount: PositiveAmount
    
class ParamsForReceiptIDDependentEndpoints(GenericReceiptRequest):
    receipt_id: ReceiptID
    
class CaptureReceiptRequest(ParamsForReceiptIDDependentEndpoints):
    amount: PositiveAmount

class VoidReceiptRequest(ParamsForReceiptIDDependentEndpoints):
    pass
    
class RefundReceiptRequest(ParamsForReceiptIDDependentEndpoints):
    amount: PositiveAmount
    
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
    pass

class BankRefundRequest(BaseModel):
    capture_id: str
    amount: int
    
