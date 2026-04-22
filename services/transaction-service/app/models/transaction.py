""" Sqlalchemy Transaction Model. """

from datetime import datetime
import uuid
from sqlalchemy import DateTime, Numeric, Index, String, func, text
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID, JSONB
from decimal import Decimal

from app.db.base import Base


class Transaction(Base):
    """Transaction database model.

    Stores all submitted transactions with their current processing state.
    Uses idempotency_key as a unique constraint to prevent duplicates.
    """

    __tablename__ = "transactions"

    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    ) 

    idempotency_key: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )

    client_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        default="legacy",
        server_default=text("'legacy'"),
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )
    sender_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True
    )

    receiver_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    sender_country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    receiver_country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="TRANSFER",
        server_default=text("'TRANSFER'"),
    )

    device_fingerprint: Mapped[str] = mapped_column(
        String(256),
        nullable=True,
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=True
    )

    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="web",
        server_default=text("'web'")
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="RECEIVED",
        index=True
    )

    transaction_metadata: Mapped[dict] = mapped_column(
        JSONB, 
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_transactions_sender_status", "sender_id", "status"),
        Index("ix_transactions_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, status={self.status}, amount={self.amount})>"
