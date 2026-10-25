from typing import Annotated
from uuid import UUID

from pydantic import BeforeValidator, Field

from src.exceptions.exception import IDParsingError

receipt_prefix = "rex_"
order_prefix = "orx_"
customer_prefix = "cux_"


# --- For responses
def create_prefixed_order_id(order_id):
    return order_prefix + str(order_id)


def create_prefixed_customer_id(customer_id):
    return customer_prefix + str(customer_id)


def create_prefixed_receipt_id(receipt_id):
    return receipt_prefix + str(receipt_id)

def remove_prefix(id: str, prefix:str, name:str):
    if not id.startswith(prefix):
        raise IDParsingError(f"Invalid {name} ID, {prefix} is missing")

    return id.removeprefix(prefix)

# -- for requests 
# check if the id sent has the prefix, we return an error if it doesn't.
# remove the prefix specified in the function parameter and return it back
# if the prefix is "rex_" or "cux_", parse it as an integer, else we parse it as an UUID and return to the sender
def parse_order_id(order_id: str, name: str = "order_id") -> str:
    original_id = remove_prefix(order_id, order_prefix, name=name)
    try:
        test_id = UUID(original_id)
    except ValueError:
        raise IDParsingError("Invalid order ID")
        
    return order_id

def parse_integer_ids(integer_id: str, prefix: str, name: str) -> str:
    original_id = remove_prefix(integer_id, prefix, name)
    try:
        test_id = int(original_id)
    except ValueError:
        raise IDParsingError(f"Invalid {name} ID")

    return integer_id


def parse_customer_id(id: str) -> str:
    return parse_integer_ids(id, prefix=customer_prefix, name="customer")


def parse_receipt_id(id: str) -> str:
    return parse_integer_ids(id, prefix=receipt_prefix, name="receipt")


OrderID = Annotated[str, BeforeValidator(parse_order_id)]
CustomerID = Annotated[str, BeforeValidator(parse_customer_id)]
ReceiptID = Annotated[str, BeforeValidator(parse_receipt_id)]
PositiveAmount = Annotated[int, Field(ge=1)]
