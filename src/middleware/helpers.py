from uuid import UUID

from src.dtos.helpers import order_prefix
from src.exceptions.exception import IDParsingError


def parse_order_id(order_id: str) -> UUID:
    if not order_id.startswith(order_prefix):
        raise IDParsingError(message=None)
    
    try:
        return UUID(order_id.removeprefix(order_prefix))
    except ValueError:
        raise IDParsingError(message=None)
