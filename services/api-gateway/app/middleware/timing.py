"""Request timing middleware for tracking total request duration."""

import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from aegis_shared.utils.logging import get_logger
from aegis_shared.utils.tracing import get_correlation_id

logger = get_logger("api_gateway")


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs total request processing time."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            
            # Calculate total time
            total_time_ms = (time.perf_counter() - start_time) * 1000
            
            # Get correlation ID for tracing
            correlation_id = get_correlation_id()
            
            # Log the request timing
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                total_time_ms=round(total_time_ms, 2),
                correlation_id=correlation_id,
            )
            
            # Add timing header to response (optional)
            response.headers["X-Response-Time-Ms"] = str(round(total_time_ms, 2))
            
            return response
            
        except Exception as e:
            # Log failed requests as well
            total_time_ms = (time.perf_counter() - start_time) * 1000
            correlation_id = get_correlation_id()
            
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                total_time_ms=round(total_time_ms, 2),
                error=str(e),
                correlation_id=correlation_id,
            )
            raise