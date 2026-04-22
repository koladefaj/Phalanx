"""Common shared schemas for Aegis Risk."""

from uuid import UUID
from pydantic import BaseModel, Field


class QueuedResponse(BaseModel):
    """Generic response for asynchronously queued tasks."""
    status: str = Field(..., example="queued")
    message: str = Field(..., example="Task has been queued successfully.")
    correlation_id: str | None = Field(None, example="550e8400-e29b-41d4-a716-446655440000")


class ReinvestigationResponse(QueuedResponse):
    """Specific response for manual AI re-investigations."""
    transaction_id: UUID
