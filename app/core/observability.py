import logging
import time
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ledgerlens.agent")

def trace_execution(func):
    """Decorator to trace execution time and log execution flows for observability."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        logger.info(f"Starting execution of {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"{func.__name__} completed in {time.time() - start:.3f}s")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__} after {time.time() - start:.3f}s: {str(e)}")
            raise e
    return wrapper
