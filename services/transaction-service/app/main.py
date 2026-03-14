"""Transaction Service — gRPC server entrypoint."""

import asyncio
from concurrent import futures

import grpc

# Pre-load common protobuf descriptors before any service/mapper 
# imports transaction_pb2, which depends on common.proto. 
import aegis_shared.generated.common_pb2  # noqa: F401

from app.config import settings
from app.grpc_server.servicer import TransactionServicer
from app.grpc_server.interceptors import LoggingInterceptor
from aegis_shared.utils.logging import setup_logger
from aegis_shared.generated import transaction_pb2_grpc

from aegis_shared.utils.redis import init_redis

logger = setup_logger("transaction-service", settings.LOG_LEVEL)


async def serve():
    """Start the Transaction gRPC server."""

    # Initialize Redis before starting services
    await init_redis(settings.REDIS_URL)

    # Create gRPC server
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[LoggingInterceptor()],
    )

    # Register servicer
    servicer = TransactionServicer()
    transaction_pb2_grpc.add_TransactionServiceServicer_to_server(servicer, server)

    listen_addr = f"0.0.0.0:{settings.TRANSACTION_GRPC_PORT}"
    server.add_insecure_port(listen_addr)

    logger.info("transaction_service_starting", address=listen_addr)
    await server.start()
    logger.info("transaction_service_started", address=listen_addr)

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("transaction_service_shutting_down")
        await server.stop(grace=5)

if __name__ == "__main__":
    asyncio.run(serve())
