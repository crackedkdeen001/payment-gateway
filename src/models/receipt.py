from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Index

from src.db.custom_types import MyRefID
from src.db.setup import Base

# prevents circular imports
if TYPE_CHECKING:
    from src.models.idempotency import IdempotencyKeys
    
from src.models.states import PaymentStates


class Receipt(Base):
    __tablename__ = "receipt"
    __table_args__ = (
        Index("idx_order_id_current_state", "order_id", "current_state"),
        Index("idx_customer_id", "customer_id"),
    )

    id: Mapped[int] = mapped_column(MyRefID, primary_key=True)
    order_id: Mapped[UUID] = mapped_column(Uuid, default=uuid4)
    customer_id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    
    card_number: Mapped[str] = mapped_column(String(40))
    card_cvv: Mapped[str] = mapped_column(String(3))
    card_expiry_month: Mapped[int] = mapped_column(Integer)
    card_expiry_year: Mapped[int] = mapped_column(Integer)
    current_state: Mapped[PaymentStates] = mapped_column(
        Enum(
            PaymentStates,
            values_callable=lambda states: [state.value for state in states],
        ),
        default=PaymentStates.PENDING,
    )
    # Bank references
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    