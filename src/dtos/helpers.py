from typing import Annotated
from uuid import UUID

from pydantic import Field

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

def remove_prefix(id: str, prefix:str):
    if not id.startswith(prefix):
        raise ValueError(f"{id} is an invalid ID, it should start with {order_prefix}")

    return id.removeprefix(prefix)

# -- for requests 
# check if the id sent has the prefix, we return an error if it doesn't.
# remove the prefix specified in the function parameter and return it back
# if the prefix is "rex_" or "cux_", parse it as an integer, else we parse it as an UUID and return to the sender
def parse_order_id(uuid_id: str) -> str:
    original_id = remove_prefix(uuid_id, order_prefix)
    try:
        try_id = UUID(original_id)
    except ValueError:
        raise ValueError(f"{uuid_id} is an invalid ID, it must be a UUID with {order_prefix} at the beginning")
        
    return original_id

def parse_integer_ids(integer_id: str, prefix: str):
    original_id = remove_prefix(integer_id, prefix)
    try:
        try_id = int(original_id)
    except ValueError:
        raise ValueError(f"{integer_id} is an invalid ID, it must be an number with {prefix} at the beginning")

    return original_id


def parse_customer_id(id: str) -> str:
    return parse_integer_ids(id, prefix=customer_prefix)


def parse_receipt_id(id: str) -> str:
    return parse_integer_ids(id, prefix=receipt_prefix)


currency = Annotated[str, Field(min_length=3, max_length=3)]