"""Transaction Service — gRPC server entrypoint."""

import asyncio
from concurrent import futures

import grpc

from app.config import settings
from app.grpc_server.servicer import TransactionServicer
from app.grpc_server.interceptors import LoggingInterceptor
from aegis_shared.utils.logging import setup_logger
from aegis_shared.generated import transaction_pb2_grpc

logger = setup_logger("transaction-service", settings.LOG_LEVEL)


async def serve():
    """Start the Transaction gRPC server."""

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
