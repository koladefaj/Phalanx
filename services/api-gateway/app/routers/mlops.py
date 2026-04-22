"""MLOps router — endpoints for triggering model retraining.

POST /ml/retrain         → Publish a retrain trigger to SQS (async)
POST /ml/retrain/now     → Run the retrain workflow inline (dev/demo only)
GET  /ml/retrain/status  → Check queue depth to see if retrain is pending
"""

import json
import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from aegis_shared.schemas.auth import AuthUser
from aegis_shared.schemas.common import QueuedResponse
from aegis_shared.utils.logging import get_logger
from app.dependencies import require_admin_role, get_sqs_session
from app.config import settings

logger = get_logger("mlops_router")
router = APIRouter(prefix="/ml", tags=["MLOps"])


class RetrainRequest(BaseModel):
    lookback_days: int = Field(default=7, ge=1, le=30, description="Days of data to analyse")
    trigger: str = Field(default="manual")


# ── POST /ml/retrain ──────────────────────────────────────────────────────────

@router.post(
    "/retrain",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=QueuedResponse,
    summary="Trigger model retraining via SQS",
    description=(
        "Publishes a retrain request to the aegis-model-retrain-requests SQS queue. "
        "The analyst-service picks it up asynchronously, runs the LlamaIndex "
        "RetrainingWorkflow (LLM analysis → XGBoost training → hot-swap), and logs the result."
    ),
)
async def trigger_retrain(
    request: RetrainRequest,
    user: Annotated[AuthUser, Depends(require_admin_role)],
    boto_session=Depends(get_sqs_session),
) -> QueuedResponse:
    """Queue a retraining job. Returns immediately — workflow runs async."""
    correlation_id = str(uuid.uuid4())

    try:
        queue_url = (
            f"{settings.AWS_ENDPOINT_URL}/000000000000/aegis-model-retrain-requests"
        )

        async with boto_session.client(
            "sqs",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_ENDPOINT_URL,
        ) as client:
            await client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({
                    "trigger": request.trigger,
                    "lookback_days": request.lookback_days,
                    "correlation_id": correlation_id,
                }),
            )

        logger.info(
            "retrain_request_queued",
            correlation_id=correlation_id,
            lookback_days=request.lookback_days,
            requested_by=user.sub,
        )

        return {
            "status": "queued",
            "correlation_id": correlation_id,
            "message": (
                "Retrain request queued. The analyst-service will analyse "
                "performance metrics, then retrain if the LLM determines it's necessary."
            ),
        }

    except Exception as e:
        logger.error("retrain_queue_failed", error=str(e), correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to queue retrain request: {str(e)}",
        )
