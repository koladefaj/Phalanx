"""Transaction gRPC servicer — implements TransactionService RPCs."""

import uuid
import grpc

from app.services.transaction_service import TransactionBusinessService
from app.services.idempotency_service import IdempotencyService
from aegis_shared.generated.transaction_pb2 import (
    CreateTransactionResponse,
    GetTransactionResponse,
    UpdateStatusResponse,
)
from aegis_shared.generated.common_pb2 import HealthCheckResponse
from aegis_shared.utils.logging import get_logger

logger = get_logger("transaction_servicer")


class TransactionServicer:
    """gRPC servicer implementing the TransactionService."""

    def __init__(self):
        self.transaction_service = TransactionBusinessService()
        self.idempotency_service = IdempotencyService()

    async def CreateTransaction(self, request, context):
        """Create a new transaction with idempotency check."""
        correlation_id = (
            request.metadata.correlation_id
            if request.metadata
            else str(uuid.uuid4())
        )
        idempotency_key = request.idempotency_key

        logger.info(
            "create_transaction_rpc",
            idempotency_key=idempotency_key,
            amount=request.amount,
            correlation_id=correlation_id,
        )

        # Check for duplicate
        cached = await self.idempotency_service.check(idempotency_key)
        if cached:
            logger.info("idempotent_duplicate_detected", idempotency_key=idempotency_key)
            return CreateTransactionResponse(**cached)  # proto object not raw dict

        try:
            result = await self.transaction_service.create(
                idempotency_key=idempotency_key,
                amount=request.amount,
                currency=request.currency,
                sender_id=request.sender_id,
                receiver_id=request.receiver_id,
                sender_country=request.sender_country,
                receiver_country=request.receiver_country,
                device_fingerprint=request.device_fingerprint,
                ip_address=request.ip_address,
                channel=request.channel,
                correlation_id=correlation_id,
            )

            await self.idempotency_service.store(idempotency_key, result)

            return CreateTransactionResponse(**result)  #wrap in proto response

        except Exception as e:
            logger.error("create_transaction_failed", error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    async def GetTransaction(self, request, context):
        """Retrieve a transaction by ID."""
        transaction_id = request.transaction_id
        logger.info("get_transaction_rpc", transaction_id=transaction_id)

        try:
            result = await self.transaction_service.get_by_id(transaction_id)
            if result is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Transaction {transaction_id} not found")
                return GetTransactionResponse()  # empty proto, not None

            return GetTransactionResponse(**result)  # wrap in proto response

        except Exception as e:
            logger.error("get_transaction_failed", error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    async def UpdateTransactionStatus(self, request, context):
        """Update a transaction's status atomically."""
        logger.info(
            "update_status_rpc",
            transaction_id=request.transaction_id,
            new_status=request.new_status,
        )

        try:
            result = await self.transaction_service.update_status(
                transaction_id=request.transaction_id,
                new_status=request.new_status,
                reason=request.reason,
            )
            return UpdateStatusResponse(**result)  # wrap in proto response

        except ValueError as e:
            # Invalid transition — client error, not server error
            logger.warning("invalid_status_transition", error=str(e))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return UpdateStatusResponse()

        except Exception as e:
            logger.error("update_status_failed", error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    async def HealthCheck(self, request, context):
        """Health check endpoint."""
        return HealthCheckResponse(
            status="ok",
            service_name="transaction-service",
            version="1.0.0",
        )