from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.receipt import Receipt
from src.db.setup import Base


class IdempotencyKeys(Base):
    __table_name__ = "idempotency_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(100))

    request_method: Mapped[str] = mapped_column(String(10))
    request_params: Mapped[dict] = mapped_column(JSON)
    request_path: Mapped[str] = mapped_column(String(100))

    response_code: Mapped[int | None] = mapped_column(Integer)
    response_body: Mapped[dict | None] = mapped_column(JSON)

    # Many idempotency keys can only reference one receipt (Many--to--One)
    # relationship is used to make a connection between python objects.``
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipt.id"))
    receipt: Mapped["Receipt"] = relationship(back_populates="idempotency_keys")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    