import asyncio
import logging
from contextvars import Context
from typing import Callable, TypeVar, Any


class IsolatedContext:
    """A factory for creating isolated contexts."""

    __RV = TypeVar('__RV', bound=Any)
    __logger = logging.getLogger('context-factory')

    @staticmethod
    def run(fn: Callable[..., __RV], *args, **kwargs) -> __RV:
        """Runs a function within a new context."""

        # Turns out each task propagates existing context to the child task.
        # So, in order to isolate the context, we need to create a new task.
        if asyncio.iscoroutinefunction(fn):
            return asyncio.create_task(fn(*args, **kwargs))

        # Context isolation works differently for synchronous functions.
        # We can simply run it within the current context.
        return Context().run(fn, *args, **kwargs)
