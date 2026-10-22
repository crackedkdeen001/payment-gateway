from uuid import UUID

from dtos.helpers import order_prefix
from exceptions.exception import IDParsingError


def parse_order_id(order_id: str) -> UUID:
    if not order_id.startswith(order_prefix):
        raise IDParsingError()
    
    try:
        return UUID(order_id.removeprefix(order_prefix))
    except ValueError:
        raise IDParsingError()
