from datetime import datetime

from sqlalchemy import JSON, TIMESTAMP, UUID, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class ReceiptAudit(Base):
    __tablename__ = "receipt_audit"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    data: Mapped[dict] = mapped_column(JSON)
    receipt_id: Mapped[UUID] = mapped_column(
        ForeignKey("payment_receipt.id", ondelete="RESTRICT")
    )


class IdempotencyAudit(Base):
    __tablename__ = "idempotency_audit"
    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now()
    )
    idempotency_id: Mapped[int] = mapped_column(
        ForeignKey("idempotency_keys.id", ondelete="RESTRICT")
    )
