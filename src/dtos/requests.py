from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator

from src.dtos.helpers import parse_customer_id, parse_order_id

# --- For responses


# -- for requests 
# check if the id sent has the prefix, we return an error if it doesn't.
# remove the prefix specified in the function parameter and return it back
# if the prefix is "rex_" or "cux_", parse it as an integer, else we parse it as an UUID and return to the sender


order_id = Annotated[str, BeforeValidator(parse_order_id)]
customer_id = Annotated[str, BeforeValidator(parse_customer_id)]

class ReceiptAuthorize(BaseModel):
    customer_id: customer_id
    order_id: order_id
    card_number: str
    card_cvv: Annotated[str, Field(max_length=3)]
    card_expiry_month: Annotated[int, Field(ge=1, le=12)]
    card_expiry_year: Annotated[int, Field(ge=1800)]
    amount: Annotated[int, Field(ge=1)]
    currency: Annotated[str, Field(max_length=3)]