"""SQS Worker — consumes aegis-risk-completed and delivers webhooks."""

import asyncio
import json
import uuid

from aegis_shared.utils.logging import get_logger
from aegis_shared.utils.sqs import get_boto_session
from aegis_shared.utils.tracing import clear_correlation_id, set_correlation_id
from app.config import settings
from app.db.session import get_session
from app.repositories.webhook_repo import WebhookRepository
from app.services.webhook_delivery import WebhookDeliveryService

logger = get_logger("notification-worker")


class NotificationWorker:
    """Polls aegis-risk-completed SQS queue and delivers webhooks to registered clients."""

    def __init__(self, delivery_service: WebhookDeliveryService):
        self._delivery = delivery_service
        self.session = get_boto_session()
        self._queue_url: str | None = None
        self.worker_id = settings.WORKER_ID

    def _client(self):
        return self.session.client(
            "sqs",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_ENDPOINT_URL,
        )

    async def _get_queue_url(self) -> str:
        if self._queue_url:
            return self._queue_url
        try:
            async with self._client() as client:
                response = await client.get_queue_url(
                    QueueName=settings.SQS_RISK_COMPLETED_QUEUE
                )
                self._queue_url = response["QueueUrl"]
                return self._queue_url
        except Exception:
            self._queue_url = (
                f"{settings.AWS_ENDPOINT_URL}/000000000000/{settings.SQS_RISK_COMPLETED_QUEUE}"
            )
            return self._queue_url

    async def run(self, shutdown_event: asyncio.Event) -> None:
        await self._get_queue_url()
        logger.info("notification_worker_started", worker_id=self.worker_id)

        while not shutdown_event.is_set():
            try:
                await self._poll_messages()
            except Exception as e:
                logger.error("notification_worker_poll_error", error=str(e))
            await asyncio.sleep(settings.WORKER_POLL_INTERVAL)

        logger.info("notification_worker_stopped", worker_id=self.worker_id)

    async def _poll_messages(self) -> None:
        async with self._client() as client:
            response = await client.receive_message(
                QueueUrl=self._queue_url,
                MaxNumberOfMessages=settings.WORKER_MAX_MESSAGES,
                VisibilityTimeout=settings.WORKER_VISIBILITY_TIMEOUT,
                WaitTimeSeconds=5,
                MessageAttributeNames=["All"],
            )

        messages = response.get("Messages", [])
        if not messages:
            return

        logger.info("notification_messages_received", count=len(messages))
        await asyncio.gather(
            *[self._process_message(msg) for msg in messages],
            return_exceptions=True,
        )

    async def _process_message(self, message: dict) -> None:
        receipt_handle = message["ReceiptHandle"]
        transaction_id = "unknown"

        try:
            body = json.loads(message["Body"])
            transaction_id = body.get("transaction_id", "unknown")
            correlation_id = body.get("correlation_id", str(uuid.uuid4()))
            client_id = body.get("client_id", "")
            event = "risk.completed"

            set_correlation_id(correlation_id)

            payload = {
                "transaction_id": transaction_id,
                "event": event,
                "decision": body.get("decision"),
                "risk_score": body.get("risk_score"),
                "risk_level": body.get("risk_level"),
                "risk_factors": body.get("risk_factors", []),
                "correlation_id": correlation_id,
            }

            if client_id:
                async with get_session() as session:
                    repo = WebhookRepository(session)
                    webhooks = await repo.get_active_for_client_and_event(client_id, event)

                for webhook in webhooks:
                    success = await self._delivery.deliver(
                        url=webhook.url,
                        event=event,
                        payload=payload,
                    )
                    async with get_session() as session:
                        repo = WebhookRepository(session)
                        await repo.increment_delivery(webhook.webhook_id, success)

                logger.info(
                    "notification_dispatched",
                    transaction_id=transaction_id,
                    webhooks_count=len(webhooks),
                )
            else:
                logger.warning(
                    "notification_skipped_no_client_id",
                    transaction_id=transaction_id,
                )

            # Ack only after all delivery attempts (acks-late)
            async with self._client() as client:
                await client.delete_message(
                    QueueUrl=self._queue_url,
                    ReceiptHandle=receipt_handle,
                )

        except Exception as e:
            logger.error(
                "notification_message_processing_failed",
                transaction_id=transaction_id,
                error=str(e),
                message_id=message.get("MessageId"),
            )
        finally:
            clear_correlation_id()
