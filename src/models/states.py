from datetime import datetime
from enum import StrEnum

from . import Card
from ..models import BaseModel


# Payment states are stored in the database as an Enum
class PaymentStates(StrEnum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    VOIDED = "voided"
    REFUNDED = "refunded"


# Payment states are represented as types in code
class GenericPayment(BaseModel):
    receipt_id: str
    order_id: str
    card: Card


class PendingPayment(GenericPayment):
    pass


class AuthorizedPayment(GenericPayment):
    authorize_id: str
    authorized_at: datetime


# Both voided and captured states have the ID's of authorized, so,
# we know which authorized payment was voided or captured
class VoidedPayment(GenericPayment):
    authorized_id: str
    voided_id: str
    voided_at: datetime


class CapturedPayment(GenericPayment):
    authorized_id: str
    captured_id: str
    captured_at: datetime


class RefundedPayment(GenericPayment):
    captured_id: str
    refunded_id: str
    refunded_at: datetime

