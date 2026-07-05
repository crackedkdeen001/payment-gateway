from enum import StrEnum


class TransactionStates(StrEnum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    VOIDED = "voided"
    CAPTURED = "captured"
    REFUNDED = "refunded"
