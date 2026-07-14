from enum import StrEnum


class TransactionStates(StrEnum):
    PENDING = "pending"
    AUTHORIZING = "authorizing"
    AUTHORIZED = "authorized"
    VOIDING = "voiding"
    VOIDED = "voided"
    CAPTURING = "capturing"
    CAPTURED = "captured"
    REFUNDING = "refunding"
    REFUNDED = "refunded"
    FAILED = "failed"


class TransactionEvents(StrEnum):
    AUTHORIZE = "authorize"
    AUTHORIZE_OK = "authorize_ok"
    VOID = "void"
    VOID_OK = "void_ok"
    CAPTURE = "capture"
    CAPTURE_OK = "capture_ok"
    REFUND = "refund"
    REFUND_OK = "refund_ok"
    FAIL ="fail"

TRANSITIONS = {
    (TransactionStates.PENDING, TransactionStates.AUTHORIZING): TransactionEvents.AUTHORIZE,
    (TransactionStates.AUTHORIZING, TransactionStates.FAILED): TransactionEvents.FAIL,
    (TransactionStates.AUTHORIZING, TransactionStates.AUTHORIZED): TransactionEvents.FAIL,
    
}


#TODO Finish up designing the state machine's states, triggers, transition and detstination states.
#TODO also run alembic migrations to update the database transaction states based on the new states