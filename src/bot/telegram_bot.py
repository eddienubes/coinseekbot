import logging
from typing import Callable, TypeVar

from aiogram import Dispatcher, Bot, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from inspect import signature

from utils import AnyCallable
from .handler import Handler, HandlerType

from config import config


class TelegramBot:
    _T = TypeVar('_T', bound=BaseMiddleware)

    __dp = Dispatcher()
    # For each class, we store a list of handler factories.
    # A factory encloses the handler function with provided Aiogram filters.
    __handlers: dict[str, list[Handler]] = {}

    def __init__(self, middlewares: list[_T] = None):
        if middlewares is not None:
            for m in middlewares:
                self.__dp.update.middleware(m)

    @classmethod
    def router(cls):
        def decorator(decorated_cls):
            def wrapper(*args, **kwargs):
                existing_on_module_init = getattr(decorated_cls, 'on_module_init', None)

                async def on_module_init(self) -> None:
                    handlers = cls.__handlers.get(decorated_cls.__name__, [])

                    for handler in handlers:
                        logging.info(
                            f"Registering handler {handler.type} for router: {decorated_cls.__name__}")

                        if handler.type == HandlerType.MESSAGE:
                            cls.__dp.message.register(handler.factory(self), *handler.filters)
                        elif handler.type == HandlerType.INLINE_QUERY:
                            cls.__dp.inline_query.register(handler.factory(self), *handler.filters)
                        elif handler.type == HandlerType.CHAT_MEMBER:
                            cls.__dp.chat_member.register(handler.factory(self), *handler.filters)
                        elif handler.type == HandlerType.MY_CHAT_MEMBER:
                            cls.__dp.my_chat_member.register(handler.factory(self), *handler.filters)
                        elif handler.type == HandlerType.CALLBACK_QUERY:
                            cls.__dp.callback_query.register(handler.factory(self), *handler.filters)

                    if existing_on_module_init:
                        await existing_on_module_init(self)

                setattr(decorated_cls, 'on_module_init', on_module_init)

                return decorated_cls(*args, **kwargs)

            return wrapper

        return decorator

    @classmethod
    def handle_my_chat_member(cls, *filters: AnyCallable) -> Callable:
        return cls.__attach_handler(*filters, type=HandlerType.MY_CHAT_MEMBER)

    @classmethod
    def handle_chat_member(cls, *filters: AnyCallable) -> Callable:
        return cls.__attach_handler(*filters, type=HandlerType.CHAT_MEMBER)

    @classmethod
    def handle_message(cls, *filters: AnyCallable) -> Callable:
        return cls.__attach_handler(*filters, type=HandlerType.MESSAGE)

    @classmethod
    def handle_inline_query(cls, *filters: AnyCallable) -> Callable:
        return cls.__attach_handler(*filters, type=HandlerType.INLINE_QUERY)

    @classmethod
    def handle_callback_query(cls, *filters: AnyCallable) -> Callable:
        return cls.__attach_handler(*filters, type=HandlerType.CALLBACK_QUERY)

    @classmethod
    def __attach_handler(cls, *filters: AnyCallable, type: HandlerType):
        def decorator(fn):
            cls_name = fn.__qualname__.split('.')[0]

            handlers = cls.__handlers.get(cls_name, [])

            def factory(self):
                async def handler(*args, **kwargs):
                    sig = signature(fn)
                    filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
                    # Strip away unnecessary arguments
                    await fn(self, *args, **filtered_kwargs)

                return handler

            handlers.append(Handler(
                factory=factory,
                filters=filters,
                type=type
            ))

            cls.__handlers[cls_name] = handlers

            return fn

        return decorator

    async def start(self, **kwargs) -> None:
        bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        await TelegramBot.__dp.start_polling(bot, **kwargs)
