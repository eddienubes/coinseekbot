import asyncio
import logging
import random
from typing import Callable, Coroutine

__logger = logging.getLogger(__name__)


# TODO: Add conditional retry based on exception type
async def retry(func: Callable,
                *args,
                max_retries: int = 3,
                delay: float = 2,
                jitter=False,
                max_jitter: int = 3,
                min_jitter: int = 1,
                backoff: float = 1.2,
                **kwargs):
    """
    Exponential backoff retry mechanism

    :param delay: should be > 1, otherwise it will be a constant delay, not exponential
    """

    error = None

    for i in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error = e

            if i != 0:
                delay **= backoff

            jitter_delay = random.randint(min_jitter, max_jitter)

            if jitter:
                sleep = delay + jitter_delay
            else:
                sleep = delay

            __logger.info(
                f'Retrying {func.__name__} attempt {i + 1}/{max_retries} in {round(sleep, 2)} seconds, error: {e}')

            await asyncio.sleep(sleep)

    raise Exception(
        f'async_utils::retry: Max retries {max_retries} exceeded for function: {func.__name__} with error: {error}')


def dispatch(coro: Coroutine):
    """
    Dispatch coroutine without awaiting it
    """
    asyncio.create_task(coro)
