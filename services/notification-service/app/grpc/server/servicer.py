"""Notification gRPC servicer — implements all 4 RPCs from notification.proto."""

import uuid

import grpc

from aegis_shared.generated import notification_pb2, notification_pb2_grpc
from aegis_shared.generated.common_pb2 import HealthCheckResponse
from aegis_shared.utils.logging import get_logger
from app.db.session import get_session
from app.repositories.webhook_repo import WebhookRepository
from app.services.webhook_delivery import WebhookDeliveryService

logger = get_logger("notification-servicer")


class NotificationServicer(notification_pb2_grpc.NotificationServiceServicer):

    def __init__(self, delivery_service: WebhookDeliveryService):
        self._delivery = delivery_service

    async def RegisterWebhook(self, request, context):
        if not request.client_id or not request.url:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "client_id and url are required")
            return

        try:
            async with get_session() as session:
                repo = WebhookRepository(session)
                webhook = await repo.create(
                    client_id=request.client_id,
                    url=request.url,
                    events=list(request.events),
                )

            logger.info(
                "webhook_registered",
                webhook_id=str(webhook.webhook_id),
                client_id=request.client_id,
                url=request.url,
            )

            return notification_pb2.RegisterWebhookResponse(
                webhook_id=str(webhook.webhook_id),
                url=webhook.url,
                client_id=webhook.client_id,
                events=webhook.events or [],
                created_at=webhook.created_at.isoformat(),
            )
        except Exception as e:
            logger.error("register_webhook_failed", error=str(e))
            await context.abort(grpc.StatusCode.INTERNAL, "Failed to register webhook")

    async def SendNotification(self, request, context):
        client_id = request.metadata.client_id if request.metadata else ""
        event = request.event

        if not client_id or not event:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "client_id and event are required")
            return

        payload = {
            "transaction_id": request.transaction_id,
            "event": event,
            "risk_score": request.risk_score,
            "risk_level": request.risk_level,
            "triggered_rules": list(request.triggered_rules),
            "explanation_summary": request.explanation_summary,
            "evaluated_at": request.evaluated_at,
        }

        webhooks_triggered = 0
        try:
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

                if success:
                    webhooks_triggered += 1

            return notification_pb2.SendNotificationResponse(
                transaction_id=request.transaction_id,
                webhooks_triggered=webhooks_triggered,
                success=True,
            )
        except Exception as e:
            logger.error(
                "send_notification_failed",
                transaction_id=request.transaction_id,
                error=str(e),
            )
            await context.abort(grpc.StatusCode.INTERNAL, "Failed to send notification")

    async def GetWebhookStatus(self, request, context):
        if not request.webhook_id:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "webhook_id is required")
            return

        try:
            webhook_uuid = uuid.UUID(request.webhook_id)
        except ValueError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid webhook_id format")
            return

        try:
            async with get_session() as session:
                repo = WebhookRepository(session)
                webhook = await repo.get_by_id(webhook_uuid)

            if not webhook:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Webhook not found")
                return

            status = "active" if webhook.is_active else "inactive"
            return notification_pb2.GetWebhookStatusResponse(
                webhook_id=str(webhook.webhook_id),
                url=webhook.url,
                status=status,
                delivery_count=webhook.delivery_count,
                failure_count=webhook.failure_count,
            )
        except Exception as e:
            logger.error("get_webhook_status_failed", error=str(e))
            await context.abort(grpc.StatusCode.INTERNAL, "Failed to get webhook status")

    async def HealthCheck(self, request, context):
        return HealthCheckResponse(status="SERVING")
