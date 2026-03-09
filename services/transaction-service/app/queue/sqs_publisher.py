"""SQS message publisher for transaction events."""

import json
import aioboto3
from app.config import settings
from aegis_shared.utils.logging import get_logger

logger = get_logger("sqs_publisher")


class SQSPublisher:
    """Publishes transaction events to AWS SQS.

    Uses aioboto3 with configurable endpoint URL to support
    LocalStack in development and real SQS in production.
    """

    def __init__(self):
        self.session = aioboto3.Session()
        # queue_url resolved lazily on first publish
        self._queue_url: str | None = None

    def _client(self):
        """Return a configured async SQS client context manager."""
        return self.session.client(
            "sqs",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_ENDPOINT_URL,
        )

    async def _get_queue_url(self) -> str:
        """Resolve and cache the SQS queue URL from the queue name."""
        if self._queue_url:
            return self._queue_url

        try:
            async with self._client() as client:
                response = await client.get_queue_url(
                    QueueName=settings.SQS_TRANSACTION_QUEUE
                )
                self._queue_url = response["QueueUrl"]
                return self._queue_url
        except Exception as e:
            logger.warning("sqs_queue_url_resolution_failed", error=str(e))
            # Fallback to constructed URL for LocalStack
            fallback = (
                f"{settings.AWS_ENDPOINT_URL}/000000000000/"
                f"{settings.SQS_TRANSACTION_QUEUE}"
            )
            self._queue_url = fallback
            return fallback

    async def publish_transaction_queued(self, payload: dict) -> str | None:
        """Publish a TransactionQueued event to SQS.

        Args:
            payload: Transaction event data.

        Returns:
            SQS MessageId or None on failure.
        """
        try:
            queue_url = await self._get_queue_url()

            async with self._client() as client:
                response = await client.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(payload, default=str),
                    MessageAttributes={
                        "EventType": {
                            "DataType": "String",
                            "StringValue": "TransactionQueued",
                        },
                        "TransactionId": {
                            "DataType": "String",
                            "StringValue": payload.get("transaction_id", ""),
                        },
                    },
                )

            message_id = response.get("MessageId")
            logger.info(
                "sqs_message_published",
                message_id=message_id,
                transaction_id=payload.get("transaction_id"),
                queue=settings.SQS_TRANSACTION_QUEUE,
            )
            return message_id

        except Exception as e:
            logger.error(
                "sqs_publish_failed",
                error=str(e),
                transaction_id=payload.get("transaction_id"),
            )
            raise