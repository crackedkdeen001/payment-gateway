import uuid
from enum import StrEnum

from database.database import metadata_obj
from sqlalchemy import DATETIME, UUID, Column, Enum, Index, Integer, String, Table


class TransactionStates(StrEnum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    VOIDED = "voided"
    CAPTURED = "captured"
    REFUNDED = "refunded"


payment_receipt = Table(
    "payment_receipt",
    metadata_obj,
    Column("id", UUID, primary_key=True, default=uuid.uuid4),
    Column("order_id", Integer, nullable=False, index=True),
    Column("customer_id", Integer, nullable=False, index=True),
    Column("amount_cents", Integer, nullable=False),
    Column("current_state", Enum(TransactionStates), nullable=False),
    Column("authorization_id", String(100), nullable=True),
    Column("capture_id", String(100), nullable=True),
    Column("void_id", String(100), nullable=True),
    Column("refund_id", String(100), nullable=True),
    Column("expires_at", DATETIME(timezone=True), nullable=True),
    Column("captured_at", DATETIME(timezone=True), nullable=True),
    Column("voided_at", DATETIME(timezone=True), nullable=True),
    Column("refunded_at", DATETIME(timezone=True), nullable=True),
    Column("state_transitioned_at", DATETIME(timezone=True)),
    # Composite Index on order and transaction state
    Index("idx_order_id_transaction_state", "order_id", "current_state"),
)
