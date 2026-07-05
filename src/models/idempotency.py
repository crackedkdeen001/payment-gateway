from datetime import datetime

from sqlalchemy import JSON, TIMESTAMP, UUID, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class IdempotencyKeys(Base):
    __tablename__ = "idempotency_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now()
    )
    idempotency_key: Mapped[str] = mapped_column(String(100))
    last_run_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now()
    )
    locked_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now()
    )
    # parameters for the incoming request
    request_method: Mapped[str] = mapped_column(String(10))
    request_params: Mapped[dict] = mapped_column(JSON)
    request_path: Mapped[str] = mapped_column(String(100))

    # for finished request
    response_code: Mapped[int | None]
    response_body: Mapped[dict | None] = mapped_column(JSON)
    recovery_point: Mapped[str] = mapped_column(String(50))

    receipt_id: Mapped[UUID] = mapped_column(
        ForeignKey("payment_receipt.id"), onupdate="RESTRICT"
    )
