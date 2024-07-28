import asyncio
import logging
import random
from typing import Callable

__logger = logging.getLogger(__name__)


# TODO: Add conditional retry based on exception type
async def retry(func: Callable,
                *args,
                max_retries: int = 3,
                delay: int = 1,
                jitter=False,
                max_jitter: int = 3,
                min_jitter: int = 1, **kwargs):
    """Exponential backoff retry mechanism"""

    for i in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if jitter:
                additional_delay = random.randint(min_jitter, max_jitter)
                delay **= 2
                delay += additional_delay

            __logger.debug(f'Retrying {func.__name__} attempt {i + 1}/{max_retries} in {delay} seconds, error: {e}')
            await asyncio.sleep(delay)

    raise Exception(f'async_utils::retry: Max retries f{max_retries} exceeded for function: {func.__name__}')
