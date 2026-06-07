import grpc
from concurrent import futures

from aegis_shared.grpc.interceptors.logging_server import LoggingServerInterceptor
from aegis_shared.utils.logging import get_logger
from app.config import settings


def create_grpc_server() -> grpc.aio.Server:
    logger = get_logger("notification-service")

    interceptors = [
        LoggingServerInterceptor(
            logger=logger,
            correlation_id_header=settings.CORRELATION_ID_HEADER,
        )
    ]

    return grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=interceptors,
        options=[
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
            ("grpc.keepalive_time_ms", 10000),
            ("grpc.keepalive_timeout_ms", 5000),
        ],
    )
