# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import asyncio
import functools
from utils.logger import get_mcp_logger

logger = get_mcp_logger()


def retry_async(max_retries=3, base_delay=1.0, exponential_base=2.0, retriable_exceptions=None):
    """Retry decorator for async functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        retriable_exceptions: Tuple of exception types that should trigger retry.
                             If None, retries on all exceptions.
    
    Usage:
        @retry_async(max_retries=3, base_delay=1.0)
        async def my_function():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if retriable_exceptions is not None and not isinstance(e, retriable_exceptions):
                        raise
                    
                    if attempt < max_retries:
                        delay = base_delay * (exponential_base ** attempt)
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after {delay:.1f}s: {type(e).__name__}: {e}"
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries} retries exhausted for {func.__name__}: "
                            f"{type(e).__name__}: {e}"
                        )
            raise last_exception
        return wrapper
    return decorator
