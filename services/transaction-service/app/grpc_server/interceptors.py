"""gRPC interceptors for logging and authentication."""

import time
import uuid
import grpc
from grpc import HandlerCallDetails, RpcMethodHandler
from grpc.aio import ServerInterceptor

from aegis_shared.utils.logging import get_logger
from aegis_shared.utils.tracing import set_correlation_id, clear_correlation_id

logger = get_logger("grpc_interceptor")


class LoggingInterceptor(ServerInterceptor):
    """gRPC server interceptor that logs all incoming requests with timing."""

    async def intercept_service(
        self,
        continuation,
        handler_call_details: HandlerCallDetails,
    ) -> RpcMethodHandler:
        
        handler = await continuation(handler_call_details)

        if handler is None:
            return handler

        method = handler_call_details.method

        # wrap the actual handler function
        original_fn = handler.unary_unary or handler.unary_stream or \
                      handler.stream_unary or handler.stream_stream

        if original_fn is None:
            return handler

        async def wrapper(request, context):
            start_time = time.perf_counter()
            correlation_id = str(uuid.uuid4())
            set_correlation_id(correlation_id)

            logger.info(
                "grpc_request_started",
                method=method,
                correlation_id=correlation_id,
            )

            try:
                response = await original_fn(request, context)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.info(
                    "grpc_request_completed",
                    method=method,
                    duration_ms=round(elapsed_ms, 2),
                    correlation_id=correlation_id,
                )
                return response
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.error(
                    "grpc_request_failed",
                    method=method,
                    duration_ms=round(elapsed_ms, 2),
                    error=str(e),
                    correlation_id=correlation_id,
                )
                raise
            finally:
                clear_correlation_id()

        # return new handler with wrapped function, preserving all other attributes
        return handler._replace(unary_unary=wrapper) if handler.unary_unary else \
               handler._replace(unary_stream=wrapper) if handler.unary_stream else \
               handler._replace(stream_unary=wrapper) if handler.stream_unary else \
               handler._replace(stream_stream=wrapper)