import logging
from typing import Callable, List, Dict

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from inspect import signature

from utils import AnyCallable
from .handler import Handler

from config import Config


class TelegramBot:
    __dp = Dispatcher()
    # For each class, we store a list of handler factories.
    # A factory encloses the handler function with provided Aiogram filters.
    __message_handlers: Dict[str, List[Handler]] = {}
    __inline_query_handlers: Dict[str, List[Handler]] = {}

    @classmethod
    def router(cls):
        def decorator(decorated_cls):
            def wrapper(*args, **kwargs):
                existing_on_module_init = getattr(decorated_cls, 'on_module_init', None)

                async def on_module_init(self) -> None:
                    message_handlers = cls.__message_handlers.get(decorated_cls.__name__, [])
                    inline_query_handlers = cls.__inline_query_handlers.get(decorated_cls.__name__, [])

                    for handler in message_handlers:
                        logging.info(
                            f"Registering message handlers for router: {decorated_cls.__name__}")
                        cls.__dp.message.register(handler.factory(self), *handler.filters)

                    for handler in inline_query_handlers:
                        logging.info(
                            f"Registering inline query handlers for router: {decorated_cls.__name__}")
                        cls.__dp.inline_query.register(handler.factory(self), *handler.filters)

                    if existing_on_module_init:
                        await existing_on_module_init(self)

                setattr(decorated_cls, 'on_module_init', on_module_init)

                return decorated_cls(*args, **kwargs)

            return wrapper

        return decorator

    @classmethod
    def handle_message(cls, *filters: AnyCallable) -> Callable:
        return cls.__attach_handler(*filters, handlers_dict=cls.__message_handlers)

    @classmethod
    def handle_inline_query(cls, *filters: AnyCallable) -> Callable:
        return cls.__attach_handler(*filters, handlers_dict=cls.__inline_query_handlers)

    @classmethod
    def __attach_handler(cls, *filters: AnyCallable, handlers_dict: Dict[str, List[Handler]]):
        def decorator(fn):
            cls_name = fn.__qualname__.split('.')[0]

            handlers = handlers_dict.get(cls_name, [])

            def factory(self):
                async def handler(*args, **kwargs):
                    sig = signature(fn)
                    filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
                    # Strip away unnecessary arguments
                    await fn(self, *args, **filtered_kwargs)

                return handler

            handlers.append(Handler(
                factory=factory,
                filters=filters
            ))

            handlers_dict[cls_name] = handlers

            return fn

        return decorator

    async def start(self, **kwargs) -> None:
        bot = Bot(token=Config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await TelegramBot.__dp.start_polling(bot, **kwargs)
