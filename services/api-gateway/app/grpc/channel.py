"""gRPC channel setup for API Gateway."""

import grpc
from aegis_shared.grpc.interceptors.correlation_client import (
    CorrelationIdClientInterceptor,
)


def create_channel(target: str):
    interceptor = [CorrelationIdClientInterceptor()]

    channel = grpc.aio.insecure_channel(target, interceptors=interceptor)

    return channel