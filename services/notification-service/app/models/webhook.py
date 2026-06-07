import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from app.db.base import Base


class Webhook(Base):
    __tablename__ = "webhooks"

    webhook_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    client_id = Column(String(128), nullable=False, index=True)
    url = Column(String(512), nullable=False)
    events = Column(ARRAY(String), nullable=False, server_default=text("ARRAY[]::varchar[]"))
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    delivery_count = Column(Integer, nullable=False, default=0, server_default=text("0"))
    failure_count = Column(Integer, nullable=False, default=0, server_default=text("0"))
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )
    last_delivery_at = Column(DateTime(timezone=True), nullable=True)
