from datetime import datetime
from uuid import UUID

from sqlalchemy import TIMESTAMP, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base
from src.core.state_machine import TransactionStates


class StateHistory(Base):
    __tablename__ = "state_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    previous_state: Mapped[TransactionStates] = mapped_column(Enum(TransactionStates))
    transitioned_state: Mapped[TransactionStates] = mapped_column(
        Enum(TransactionStates)
    )
    transitioned_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    receipt_id: Mapped[UUID] = mapped_column(
        ForeignKey("payment_receipt.id", ondelete="RESTRICT")
    )
