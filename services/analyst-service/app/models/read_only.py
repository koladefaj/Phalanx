"""Read-only SQLAlchemy models for the Agent AI Service.

These are lightweight projections of tables owned by the Transaction
and Risk Engine services.  The agent never writes to them — it only
reads to build its "World View" before reasoning about fraud.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Any

from sqlalchemy import (
    String, Integer, Float, Numeric, Boolean,
    DateTime, BigInteger, Text, JSON, func, text,
)
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY


class Base(DeclarativeBase):
    pass


# ── Transaction (owned by transaction-service) ────────────────────────────────

class TransactionReadOnly(Base):
    """Read-only projection of the `transactions` table."""

    __tablename__ = "transactions"

    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
    )
    idempotency_key: Mapped[str] = mapped_column(String(128))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3))
    sender_id: Mapped[str] = mapped_column(String(64), index=True)
    receiver_id: Mapped[str] = mapped_column(String(64))
    sender_country: Mapped[str] = mapped_column(String(2))
    receiver_country: Mapped[str] = mapped_column(String(2))
    transaction_type: Mapped[str] = mapped_column(String(20))
    device_fingerprint: Mapped[Optional[str]] = mapped_column(String(256))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    channel: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    transaction_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


# ── Account Profile (owned by risk-engine-service) ────────────────────────────

class AccountProfileReadOnly(Base):
    """Read-only projection of the `account_profiles` table."""

    __tablename__ = "account_profiles"

    account_id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Lifetime counters
    total_txn_count: Mapped[int] = mapped_column(BigInteger)
    total_volume_lifetime: Mapped[Decimal] = mapped_column(Numeric(20, 2))

    # Rolling windows
    total_volume_30d: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    txn_count_30d: Mapped[int] = mapped_column(Integer)
    total_volume_24h: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    txn_count_24h: Mapped[int] = mapped_column(Integer)
    txn_count_1h: Mapped[int] = mapped_column(Integer)
    total_volume_1h: Mapped[Decimal] = mapped_column(Numeric(20, 2))

    # Amount statistics
    avg_txn_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    max_txn_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    last_txn_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))

    # Behavioural flags
    is_high_risk: Mapped[bool] = mapped_column(Boolean)
    fraud_txn_count: Mapped[int] = mapped_column(Integer)
    blocked_txn_count: Mapped[int] = mapped_column(Integer)
    review_txn_count: Mapped[int] = mapped_column(Integer)

    # Network features
    unique_receiver_count: Mapped[int] = mapped_column(Integer)
    unique_device_count: Mapped[int] = mapped_column(Integer)
    unique_country_count: Mapped[int] = mapped_column(Integer)

    # Timestamps
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    @property
    def fraud_rate(self) -> float:
        if self.total_txn_count == 0:
            return 0.0
        return (self.fraud_txn_count / self.total_txn_count) * 100


# ── Risk Result (owned by risk-engine-service) ────────────────────────────────

class RiskResultReadOnly(Base):
    """Read-only projection of the `risk_results` table."""

    __tablename__ = "risk_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    # Denormalized transaction data
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(3))
    sender_id: Mapped[Optional[str]] = mapped_column(String(64))
    receiver_id: Mapped[Optional[str]] = mapped_column(String(64))

    # Core risk scores
    risk_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(20))
    decision: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[str] = mapped_column(String(10))

    # Rule engine
    rule_score: Mapped[float] = mapped_column(Float)
    triggered_rules: Mapped[Optional[list]] = mapped_column(JSON)
    rule_flags: Mapped[Optional[dict]] = mapped_column(JSON)

    # ML scoring
    ml_anomaly_score: Mapped[Optional[float]] = mapped_column(Float)
    ml_model_version: Mapped[Optional[str]] = mapped_column(String(50))
    ml_fallback_used: Mapped[bool] = mapped_column(Boolean)

    # Agent analysis
    agent_summary: Mapped[Optional[str]] = mapped_column("agent_summary", Text)
    agent_risk_factors: Mapped[Optional[list]] = mapped_column("agent_risk_factors", JSON)
    agent_recommendation: Mapped[Optional[str]] = mapped_column("agent_recommendation", String(100))
    agent_confidence: Mapped[Optional[float]] = mapped_column("agent_confidence", Float)
    agent_model: Mapped[Optional[str]] = mapped_column("agent_model", String(50))
    agent_fallback_used: Mapped[bool] = mapped_column("agent_fallback_used", Boolean, default=False)
    agent_latency_ms: Mapped[Optional[float]] = mapped_column("agent_latency_ms", Float)

    # Timestamps
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, default=1)
