from typing import Callable, Any, Awaitable, Tuple

from dataclasses import dataclass

from utils import AnyCallable


@dataclass
class Handler:
    # The handler factory function.
    # Requires self to be passed as the first argument.
    factory: Callable[[object], Callable[[..., Any], Awaitable[None]]]
    filters: Tuple[AnyCallable, ...]
