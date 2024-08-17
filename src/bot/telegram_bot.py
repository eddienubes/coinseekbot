import logging
from typing import Callable

from aiogram import Dispatcher, Bot, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from inspect import signature

from aiogram.fsm.storage.redis import RedisStorage
from redis import Redis

from utils import AnyCallable
from .handler import Handler, HandlerType

from config import config


class TelegramBot:
    # For each class, we store a list of handler factories.
    # A factory encloses the handler function with provided Aiogram filters.
    __handlers: dict[str, list[Handler]] = {}
    __routers: dict[str, object] = {}

    def __init__[T: BaseMiddleware](self, redis: Redis, middlewares: list[T] = None):
        self.__dp = Dispatcher(
            storage=RedisStorage(
                redis=redis
            )
        )
        self.bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        if middlewares is not None:
            for m in middlewares:
                self.__dp.update.middleware(m)

    @classmethod
    def router(cls):
        def decorator(decorated_cls):
            def wrapper(*args, **kwargs):
                existing_on_module_init = getattr(decorated_cls, 'on_module_init', None)

                async def on_module_init(self) -> None:
                    cls.__attach_router(self)

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
    def __attach_router(cls, router: object):
        """router is an instance here"""

        router_name = router.__class__.__name__
        cls.__routers[router_name] = router

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

    def _register_handlers(self):

        for router_name, handlers in TelegramBot.__handlers.items():
            router_instance = TelegramBot.__routers[router_name]

            for handler in handlers:
                logging.info(
                    f"Registered handler {handler.type} for router: {router_name}")

                if handler.type == HandlerType.MESSAGE:
                    self.__dp.message.register(handler.factory(router_instance), *handler.filters)
                elif handler.type == HandlerType.INLINE_QUERY:
                    self.__dp.inline_query.register(handler.factory(router_instance), *handler.filters)
                elif handler.type == HandlerType.CHAT_MEMBER:
                    self.__dp.chat_member.register(handler.factory(router_instance), *handler.filters)
                elif handler.type == HandlerType.MY_CHAT_MEMBER:
                    self.__dp.my_chat_member.register(handler.factory(router_instance), *handler.filters)
                elif handler.type == HandlerType.CALLBACK_QUERY:
                    self.__dp.callback_query.register(handler.factory(router_instance), *handler.filters)

    async def start(self, **kwargs) -> None:
        self._register_handlers()

        await self.__dp.start_polling(self.bot, **kwargs)
