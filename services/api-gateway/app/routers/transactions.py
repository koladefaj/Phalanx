"""Transaction API routes."""

import json
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies import get_current_user, get_transaction_client, get_sqs_session, AuthUser, require_analyst_role, require_admin_role
from app.grpc.clients.transaction_client import TransactionGRPCClient
from app.config import settings
from aegis_shared.schemas.transaction import TransactionCreate, TransactionAccepted, TransactionResponse
from aegis_shared.schemas.common import ReinvestigationResponse
from aegis_shared.utils.logging import get_logger

logger = get_logger("transactions_router")
router = APIRouter(prefix="/transactions", tags=["Transactions"])



@router.post(
    "",
    response_model=TransactionAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a transaction for risk evaluation",
)
async def create_transaction(
    transaction: TransactionCreate,
    request: Request,
    user: Annotated[AuthUser, Depends(get_current_user)],               
    client: Annotated[TransactionGRPCClient, Depends(get_transaction_client)],  
) -> TransactionAccepted:
    """
    Submit a transaction for fraud risk evaluation.
    """

    logger.info(
        "transaction_submission_received",
        idempotency_key=transaction.idempotency_key,
    )

    return await client.create_transaction(
        transaction=transaction,
        client_id=user.tenant_id,         
        request=request,
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get transaction details",
)
async def get_transaction(
    transaction_id: uuid.UUID,
    request: Request,
    user: Annotated[AuthUser, Depends(require_analyst_role)],
    client: Annotated[TransactionGRPCClient, Depends(get_transaction_client)],
) -> TransactionResponse:
    """Retrieve a transaction by ID."""
    
    result = await client.get_transaction(
        transaction_id=transaction_id,
        client_id=user.tenant_id,
        request=request,
    )

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return result


@router.post(
    "/{transaction_id}/reinvestigate",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ReinvestigationResponse,
    summary="Trigger a fresh agent investigation for a transaction",
    response_description="Investigation queued successfully",
)
async def reinvestigate_transaction(
    transaction_id: uuid.UUID,
    request: Request,
    user: Annotated[AuthUser, Depends(require_analyst_role)],
    txn_client: Annotated[TransactionGRPCClient, Depends(get_transaction_client)],
    boto_session=Depends(get_sqs_session),
) -> ReinvestigationResponse:
    """Re-trigger the Agentic AI investigation for a transaction.

    Useful when the original investigation failed (e.g. Ollama was down)
    or when a fraud analyst wants a fresh deep-dive report.

    The existing `agent_summary` is NOT cleared — the new investigation will
    overwrite it once completed.
    """
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

    # Verify transaction exists and get sender_id
    txn = await txn_client.get_transaction(
        transaction_id=transaction_id,
        client_id=user.tenant_id,
        request=request,
    )
    if txn is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    payload = {
        "transaction_id": str(transaction_id),
        "sender_id": txn.sender_id,
        "correlation_id": correlation_id,
    }

    try:
        queue_url = (
            f"{settings.AWS_ENDPOINT_URL}/000000000000/"
            f"{settings.SQS_AGENT_INVESTIGATIONS_QUEUE}"
        )
        async with boto_session.client(
            "sqs",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_ENDPOINT_URL,
        ) as sqs:
            await sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(payload),
                MessageAttributes={
                    "EventType": {
                        "DataType": "String",
                        "StringValue": "ManualReinvestigation",
                    },
                    "RequestedBy": {
                        "DataType": "String",
                        "StringValue": user.sub,
                    },
                },
            )
    except Exception as e:
        logger.error("reinvestigate_publish_failed", transaction_id=str(transaction_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to queue reinvestigation. Please retry.",
        )

    logger.info(
        "reinvestigation_queued",
        transaction_id=str(transaction_id),
        requested_by=user.sub,
    )

    return {
        "message": "Reinvestigation queued successfully.",
        "transaction_id": str(transaction_id),
        "status": "QUEUED",
    }
