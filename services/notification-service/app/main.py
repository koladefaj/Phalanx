"""Notification Service — gRPC server + SQS worker entrypoint."""

import asyncio

from aegis_shared.generated import notification_pb2_grpc
from aegis_shared.utils.logging import setup_logger
from aegis_shared.utils.sqs import init_boto_session
from app.config import settings
from app.db.session import engine
from app.grpc.server.servicer import NotificationServicer
from app.grpc.server.setup import create_grpc_server
from app.queue.sqs_consumer import NotificationWorker
from app.services.webhook_delivery import WebhookDeliveryService

logger = setup_logger("notification-service", settings.LOG_LEVEL)


async def serve():
    logger.info("Initializing Notification Service...")

    try:
        await init_boto_session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
    except Exception as e:
        logger.error("startup_sqs_init_failed", error=str(e))
        raise

    delivery_service = WebhookDeliveryService()

    server = create_grpc_server()
    servicer = NotificationServicer(delivery_service=delivery_service)
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(servicer, server)

    listen_addr = f"0.0.0.0:{settings.NOTIFICATION_GRPC_PORT}"
    server.add_insecure_port(listen_addr)

    logger.info("notification_service_starting", address=listen_addr)
    await server.start()
    logger.info("notification_service_started", address=listen_addr)

    shutdown_event = asyncio.Event()
    worker = NotificationWorker(delivery_service=delivery_service)

    try:
        await asyncio.gather(
            server.wait_for_termination(),
            worker.run(shutdown_event),
        )
    except KeyboardInterrupt:
        logger.info("notification_service_keyboard_interrupt_received")
    finally:
        logger.info("notification_service_shutting_down")
        shutdown_event.set()
        await server.stop(grace=5)
        await engine.dispose()
        logger.info("notification_service_stopped")


if __name__ == "__main__":
    asyncio.run(serve())
