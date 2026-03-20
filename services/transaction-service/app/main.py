"""Transaction Service — gRPC server entrypoint."""

import asyncio

from aegis_shared.utils.redis import get_redis
from app.services.transaction_service import TransactionBusinessService
from app.services.idempotency_service import IdempotencyService
from app.grpc.server.servicer import TransactionServicer
from app.queue.sqs_publisher import SQSPublisher
from app.grpc.clients.risk_engine_client import RiskEngineClient

import aegis_shared.generated.common_pb2  # noqa: F401

from app.grpc.channel import create_channel
from app.db.session import engine  
from app.config import settings
from app.grpc.server.setup import create_grpc_server
from aegis_shared.utils.logging import setup_logger
from aegis_shared.generated import transaction_pb2_grpc
from aegis_shared.utils.sqs import init_boto_session
from aegis_shared.utils.redis import init_redis, close_redis

logger = setup_logger("transaction-service", settings.LOG_LEVEL)



async def serve():
    """Start the Transaction gRPC server."""

    try:
        # Initialize AWS and Redis clients before starting server
        await init_boto_session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )


        await init_redis(settings.REDIS_URL)

    except Exception as e:
        logger.error("startup_initialization_failed", error=str(e))
        raise


    redis = get_redis()  # get Redis client for services

    # gRPC client channel
    risk_channel = create_channel(settings.RISK_ENGINE_GRPC_ADDR)
    await asyncio.wait_for(risk_channel.channel_ready(), timeout=5)  # ensure channel is ready before accepting requests

    transaction_service = TransactionBusinessService(
        publisher=SQSPublisher(),
        risk_engine=RiskEngineClient(channel=risk_channel)
    )

    idempotency_service = IdempotencyService(redis_client=redis)

    # Create gRPC server
    server = create_grpc_server()


    # Register servicer
    servicer = TransactionServicer(
        transaction_service, 
        idempotency_service
    )

    transaction_pb2_grpc.add_TransactionServiceServicer_to_server(
        servicer,
        server
    )

    listen_addr = f"0.0.0.0:{settings.TRANSACTION_GRPC_PORT}"
    server.add_insecure_port(listen_addr)

    logger.info("transaction_service_starting", address=listen_addr)

    await server.start()

    logger.info("transaction_service_started", address=listen_addr)

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("transaction_service_keyboard_interrupt_received")
    finally:
        logger.info("transaction_service_shutting_down")
        await server.stop(grace=5)

        try:
            await servicer.transaction_service.risk_engine.close()
        except Exception as e:
            logger.error("error_closing_risk_engine_client", error=str(e))

        await engine.dispose()              # close DB connection pool
        await close_redis()

if __name__ == "__main__":
    asyncio.run(serve())
