"""Transaction business logic service."""

import uuid
from decimal import Decimal
from datetime import datetime, timezone

from app.repo.transaction_repo import TransactionRepository
from app.queue.sqs_publisher import SQSPublisher
from aegis_shared.enums import TransactionStatus
from aegis_shared.utils.logging import get_logger

logger = get_logger("transaction_business_service")


class TransactionBusinessService:
    """Core business logic for transaction operations.

    Orchestrates persistence, state management, and event publishing.
    """

    def __init__(self):
        self.repo = TransactionRepository()
        self.publisher = SQSPublisher()

    async def create(
        self,
        idempotency_key: str,
        amount: Decimal,
        currency: str,
        sender_id: str,
        receiver_id: str,
        sender_country: str,
        receiver_country: str,
        device_fingerprint: str = "",
        ip_address: str = "",
        channel: str = "web",
        correlation_id: str = "",
    ) -> dict:
        """Create a new transaction.

        1. Check for existing transaction with same idempotency key.
        2. Persist transaction with status=RECEIVED.
        3. Publish TransactionQueued event to SQS.

        Args:
            All transaction fields.

        Returns:
            Dict with created transaction details.
        """
        # Check if already exists (belt-and-suspenders with idempotency service)
        existing = await self.repo.find_by_idempotency_key(idempotency_key)
        if existing:
            logger.info("duplicate_transaction_found", idempotency_key=idempotency_key)
            return existing

        now = datetime.now(timezone.utc)

        transaction_data = {
            "idempotency_key": idempotency_key,
            "amount": amount,
            "currency": currency,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "sender_country": sender_country,
            "receiver_country": receiver_country,
            "device_fingerprint": device_fingerprint,
            "ip_address": ip_address,
            "channel": channel,
            "status": TransactionStatus.RECEIVED.value,
            "created_at": now,
        }

        # Persist to DB
        txn = await self.repo.create(transaction_data)
        transaction_id = str(txn.transaction_id)
        logger.info("transaction_persisted", transaction_id=transaction_id)

        # Publish to SQS
        event_payload = {
            "transaction_id": transaction_id,
            "idempotency_key": idempotency_key,
            "amount": amount,
            "currency": currency,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "sender_country": sender_country,
            "receiver_country": receiver_country,
            "device_fingerprint": device_fingerprint,
            "ip_address": ip_address,
            "channel": channel,
            "created_at": now.isoformat(),
            "correlation_id": correlation_id,
        }

        await self.publisher.publish_transaction_queued(event_payload)
        logger.info("transaction_event_published", transaction_id=transaction_id)

        return {
            "transaction_id": transaction_id,
            "idempotency_key": idempotency_key,
            "amount": amount,
            "currency": currency,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "status": TransactionStatus.RECEIVED.value,
            "created_at": now.isoformat(),
            "already_existed": False,
        }

    async def get_by_id(self, transaction_id: str) -> dict | None:
        """Retrieve a transaction by its ID.

        Args:
            transaction_id: Transaction UUID.

        Returns:
            Transaction dict or None.
        """
        return await self.repo.find_by_id(transaction_id)

    async def update_status(
        self,
        transaction_id: str,
        new_status: str,
        reason: str = "",
    ) -> dict:
        """Update transaction status atomically.

        Args:
            transaction_id: Transaction UUID.
            new_status: Target status.
            reason: Reason for state transition.

        Returns:
            Dict with previous and new status.

        Raises:
            ValueError: If transaction not found or invalid transition.
        """
        return await self.repo.update_status(transaction_id, new_status, reason)
