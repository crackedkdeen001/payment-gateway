import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base
from src.core.state_machine import TransactionStates


class PaymentReceipt(Base):
    __tablename__ = "payment_receipt"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[int] = mapped_column(index=True)
    customer_id: Mapped[int] = mapped_column(index=True)
    amount_cents: Mapped[int]
    current_state: Mapped[TransactionStates] = mapped_column(
        Enum(TransactionStates), default=TransactionStates.PENDING
    )
    authorization_id: Mapped[str | None] = mapped_column(String(100))
    capture_id: Mapped[str | None] = mapped_column(String(100))
    void_id: Mapped[str | None] = mapped_column(String(100))
    refund_id: Mapped[str | None] = mapped_column(String(100))
    expires_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    captured_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    voided_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    refunded_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    state_transitioned_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    __table_args__ = (
        Index("idx_order_id_transaction_state", "order_id", "current_state"),
        Index("idx_customer_id", "customer_id"),
    )
