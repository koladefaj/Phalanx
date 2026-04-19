"""gRPC channel setup for Transaction Service."""

import grpc
from aegis_shared.grpc.interceptors.correlation_client import (
    CorrelationIdClientInterceptor,
)


def create_channel(target: str):
    interceptor = [CorrelationIdClientInterceptor()]

    channel = grpc.aio.insecure_channel(target, interceptors=interceptor)

    return channel