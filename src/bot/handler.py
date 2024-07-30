from enum import Enum
from typing import Callable, Any, Awaitable

from dataclasses import dataclass

from utils import AnyCallable


class HandlerType(Enum):
    MESSAGE = 'MESSAGE'
    INLINE_QUERY = 'INLINE_QUERY'
    CHAT_MEMBER = 'CHAT_MEMBER'
    MY_CHAT_MEMBER = 'MY_CHAT_MEMBER'
    CALLBACK_QUERY = 'CALLBACK_QUERY'


@dataclass
class Handler:
    # The handler factory function.
    # Requires self to be passed as the first argument.
    factory: Callable[[object], Callable[[..., Any], Awaitable[None]]]
    filters: tuple[AnyCallable, ...]
    type: HandlerType
