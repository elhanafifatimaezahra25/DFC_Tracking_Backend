"""
Middleware for security and logging.
"""
import logging
import time
from fastapi import Request
from fastapi.responses import JSONResponse
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    """Log all requests and responses."""
    request_id = str(uuid.uuid4())[:8]
    
    # Skip sensitive endpoints from full logging
    sensitive_keywords = ['password', 'token', 'secret']
    path_lower = request.url.path.lower()
    is_sensitive = any(keyword in path_lower for keyword in sensitive_keywords)
    
    start_time = time.time()
    
    # Log request (skip full details for sensitive paths)
    user_agent = request.headers.get("user-agent", "Unknown")
    client_ip = request.client.host if request.client else "Unknown"
    if not is_sensitive:
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - IP: {client_ip} - Agent: {user_agent}"
        )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response (skip full details for sensitive paths)
        if not is_sensitive:
            logger.info(
                f"[{request_id}] Response: {response.status_code} - Time: {process_time:.3f}s"
            )
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"[{request_id}] Exception: {str(e)} - Time: {process_time:.3f}s",
            exc_info=True
        )
        raise
