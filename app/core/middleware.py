import logging
import time

from fastapi import Request

logger = logging.getLogger("api")


async def logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        duration = time.perf_counter() - start
        log_dict = {
            "url": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration": duration,
        }
        logger.info(log_dict)
        return response
    except Exception:
        logger.exception(
            "Unhandled error: %s %s",
            request.method,
            request.url.path,
        )
        raise
