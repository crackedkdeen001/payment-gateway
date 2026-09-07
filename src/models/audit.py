from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.setup import Base
from src.models.idempotency import IdempotencyKeys
from src.models.receipt import Receipt
from src.models.states import PaymentStates

"""
Module containing audit tables
The "action" column signifies action taken e.g created, deleted, updated
"""


class ReceiptAudit(Base):
    __tablename__ = "receipt_audit"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    # columns of receipt table
    order_id: Mapped[UUID] = mapped_column(Uuid, default=uuid4)
    customer_id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    card_number: Mapped[str] = mapped_column(String(40))
    card_cvv: Mapped[str] = mapped_column(String(3))
    card_expiry_month: Mapped[int] = mapped_column(Integer)
    card_expiry_year: Mapped[int] = mapped_column(Integer)
    current_state: Mapped[PaymentStates] = mapped_column(
        Enum(
            PaymentStates, 
            values_callable= lambda e : [state.value for state in e]
        ),
        default=PaymentStates.PENDING,
    )
    authorize_id: Mapped[str | None] = mapped_column(String)
    capture_id: Mapped[str | None] = mapped_column(String)
    voided_id: Mapped[str | None] = mapped_column(String)
    refund_id: Mapped[str | None] = mapped_column(String)
    authorized_at: Mapped[datetime | None] = mapped_column(DateTime)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime)

    # A receipt can have multiple idempotency_keys (one to many)
    idempotency_keys: Mapped[list["IdempotencyKeys"]] = relationship(
        back_populates="receipt"
    )

    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipt.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    action: Mapped[str] = mapped_column(String(50))

class IdempotencyAudit(Base):
    __tablename__ = "idempotency_audit"

    id: Mapped[int] = mapped_column(primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(100))

    request_method: Mapped[str] = mapped_column(String(10))
    request_params: Mapped[dict] = mapped_column(JSON)
    request_path: Mapped[str] = mapped_column(String(100))

    response_code: Mapped[int | None] = mapped_column(Integer)
    response_body: Mapped[dict | None] = mapped_column(JSON)

    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipt.id"))
    receipt: Mapped["Receipt"] = relationship(back_populates="idempotency_keys")

    idempotency_id: Mapped[int] = mapped_column(ForeignKey("idempotency_keys.id", ondelete="RESTRICT"))
    action: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
