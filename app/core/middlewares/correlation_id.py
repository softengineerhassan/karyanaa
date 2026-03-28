
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging_config import correlation_id_var




class CorrelationIdMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Extract or generate correlation ID
        corr_id = request.headers.get("X-Correlation-ID")
        if not corr_id:
            corr_id = str(uuid.uuid4())
        
        # Set correlation ID in context for logging
        correlation_id_var.set(corr_id)

        
        # Add to request state for access in endpoints
        request.state.correlation_id = corr_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = corr_id
        
        return response
