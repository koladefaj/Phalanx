"""gRPC client interceptor to inject correlation ID into outgoing calls."""

import grpc
from grpc.aio import (
    UnaryUnaryClientInterceptor,
    UnaryStreamClientInterceptor,
    StreamUnaryClientInterceptor,
    StreamStreamClientInterceptor,
)

from aegis_shared.utils.tracing import get_correlation_id


class _ClientCallDetails(grpc.aio.ClientCallDetails):
    def __init__(
        self,
        method,
        timeout,
        metadata,
        credentials,
        wait_for_ready,
    ):
        self._method = method
        self._timeout = timeout
        self._metadata = metadata
        self._credentials = credentials
        self._wait_for_ready = wait_for_ready

    @property
    def method(self):
        return self._method

    @property
    def timeout(self):
        return self._timeout

    @property
    def metadata(self):
        return self._metadata

    @property
    def credentials(self):
        return self._credentials

    @property
    def wait_for_ready(self):
        return self._wait_for_ready


class CorrelationIdClientInterceptor(
    UnaryUnaryClientInterceptor,
    UnaryStreamClientInterceptor,
    StreamUnaryClientInterceptor,
    StreamStreamClientInterceptor,
):
    """Inject correlation ID into all outgoing gRPC calls."""

    def _inject_metadata(self, client_call_details):
        correlation_id = get_correlation_id()

        metadata = []
        if client_call_details.metadata:
            metadata = list(client_call_details.metadata)

        if correlation_id:
            metadata.append(("x-correlation-id", correlation_id))

        return _ClientCallDetails(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            metadata=metadata,
            credentials=client_call_details.credentials,
            wait_for_ready=client_call_details.wait_for_ready,
        )

    # 🔹 unary -> unary
    async def intercept_unary_unary(
        self, continuation, client_call_details, request
    ):
        new_details = self._inject_metadata(client_call_details)
        return await continuation(new_details, request)

    # 🔹 unary -> stream
    async def intercept_unary_stream(
        self, continuation, client_call_details, request
    ):
        new_details = self._inject_metadata(client_call_details)
        return await continuation(new_details, request)

    # 🔹 stream -> unary
    async def intercept_stream_unary(
        self, continuation, client_call_details, request_iterator
    ):
        new_details = self._inject_metadata(client_call_details)
        return await continuation(new_details, request_iterator)

    # 🔹 stream -> stream
    async def intercept_stream_stream(
        self, continuation, client_call_details, request_iterator
    ):
        new_details = self._inject_metadata(client_call_details)
        return await continuation(new_details, request_iterator)