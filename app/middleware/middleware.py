import logging
from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """Global error handling middleware."""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
