from datetime import datetime
from enum import StrEnum

from src.models import BaseModel


# Payment states are stored in the database as an Enum
class PaymentStates(StrEnum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    VOIDED = "voided"
    REFUNDED = "refunded"
