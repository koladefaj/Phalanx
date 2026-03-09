from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.transaction import Transaction
from aegis_shared.enums import TransactionStatus
from aegis_shared.utils.logging import get_logger

logger = get_logger("transaction_repo")

# Valid state transitions
VALID_TRANSITIONS = {
    TransactionStatus.RECEIVED: [TransactionStatus.PROCESSING, TransactionStatus.DEAD_LETTERED],
    TransactionStatus.PROCESSING: [TransactionStatus.COMPLETED, TransactionStatus.FAILED],
    TransactionStatus.FAILED: [TransactionStatus.RECEIVED],  # Retry
    TransactionStatus.COMPLETED: [],  # Terminal state
    TransactionStatus.DEAD_LETTERED: [],  # Terminal state
}


class TransactionRepository:
    """Database operations for Transaction model.

    All operations use atomic transactions with proper error handling.
    """

    async def create(self, data: dict) -> Transaction:
        """Insert a new transaction.

        Args:
            data: Transaction data dict.

        Returns:
            Created Transaction ORM instance.
        """
        async with get_session() as session:
            txn = Transaction(**data)
            session.add(txn)
            await session.commit()
            await session.refresh(txn)
            logger.info("transaction_created", transaction_id=str(txn.transaction_id))
            return txn

    async def find_by_id(self, transaction_id: str) -> dict | None:
        """Find a transaction by ID.

        Args:
            transaction_id: Transaction UUID.

        Returns:
            Transaction dict or None.
        """
        async with get_session() as session:
            stmt = select(Transaction).where(Transaction.id == transaction_id)
            result = await session.execute(stmt)
            txn = result.scalar_one_or_none()

            if txn is None:
                return None

            return {
                "transaction_id": str(txn.transaction_id),
                "idempotency_key": txn.idempotency_key,
                "amount": str(txn.amount),
                "currency": txn.currency,
                "sender_id": txn.sender_id,
                "receiver_id": txn.receiver_id,
                "sender_country": txn.sender_country,
                "receiver_country": txn.receiver_country,
                "status": txn.status,
                "created_at": txn.created_at.isoformat() if txn.created_at else None,
                "updated_at": txn.updated_at.isoformat() if txn.updated_at else None,
            }

    async def find_by_idempotency_key(self, idempotency_key: str) -> dict | None:
        """Find a transaction by idempotency key.

        Args:
            idempotency_key: Client-provided unique key.

        Returns:
            Transaction dict or None.
        """
        async with get_session() as session:
            stmt = select(Transaction).where(
                Transaction.idempotency_key == idempotency_key
            )
            result = await session.execute(stmt)
            txn = result.scalar_one_or_none()

            if txn is None:
                return None

            return {
                "transaction_id": txn.id,
                "idempotency_key": txn.idempotency_key,
                "amount": float(txn.amount),
                "currency": txn.currency,
                "sender_id": txn.sender_id,
                "receiver_id": txn.receiver_id,
                "sender_country": txn.sender_country,
                "receiver_country": txn.receiver_country,
                "status": txn.status,
                "created_at": txn.created_at.isoformat() if txn.created_at else None,
                "already_existed": True,
            }

    async def update_status(
        self,
        transaction_id: str,
        new_status: str,
        reason: str = "",
    ) -> dict:
        """Atomically update transaction status with validation.

        Uses SELECT FOR UPDATE to prevent concurrent modifications.

        Args:
            transaction_id: Transaction UUID.
            new_status: Target status string.
            reason: Reason for transition.

        Returns:
            Dict with previous and new status.

        Raises:
            ValueError: If transition is invalid.
        """
        async with get_session() as session:
            # Lock the row for update
            stmt = (
                select(Transaction)
                .where(Transaction.id == transaction_id)
                .with_for_update()
            )
            result = await session.execute(stmt)
            txn = result.scalar_one_or_none()

            if txn is None:
                raise ValueError(f"Transaction {transaction_id} not found")

            current_status = TransactionStatus(txn.status)
            target_status = TransactionStatus(new_status)

            # Validate transition
            if target_status not in VALID_TRANSITIONS.get(current_status, []):
                raise ValueError(
                    f"Invalid transition from {current_status.value} to {target_status.value}"
                )

            previous_status = txn.status
            txn.status = target_status.value

            await session.commit()

            logger.info(
                "transaction_status_updated",
                transaction_id=transaction_id,
                previous_status=previous_status,
                new_status=target_status.value,
            )

            return {
                "transaction_id": transaction_id,
                "previous_status": previous_status,
                "new_status": target_status.value,
                "success": True,
            }
