"""gRPC server setup for Risk Engine Service."""

import grpc
from concurrent import futures
from aegis_shared.grpc.interceptors.logging_server import LoggingServerInterceptor
from aegis_shared.utils.logging import get_logger
from app.config import settings


def create_grpc_server():
    logger = get_logger("ml-service")

    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[
            LoggingServerInterceptor(
                logger=logger,
                correlation_id_header=settings.CORRELATION_ID_HEADER,
            )
        ],
        options=[
            ("grpc.keepalive_time_ms", 10000),
            ("grpc.keepalive_timeout_ms", 5000),
            ("grpc.http2.max_pings_without_data", 0),
            ("grpc.keepalive_permit_without_calls", 1),
        ],

    )

    return server