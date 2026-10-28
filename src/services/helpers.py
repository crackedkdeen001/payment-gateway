from datetime import datetime

from src.models import Receipt


def is_authorization_expired(receipt: Receipt) -> bool:
    """True when the receipt has no authorization expiry, or it is in the past."""
    if receipt.auth_expiry is None:
        return True

    return receipt.auth_expiry <= datetime.now(receipt.auth_expiry.tzinfo)
