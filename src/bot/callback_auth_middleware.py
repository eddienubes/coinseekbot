import asyncio
from collections.abc import Callable
from typing import Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

from telegram.tg_service import TgService
from utils import dispatch


class CallbackAuthMiddleware(BaseMiddleware):
    """Simple middleware to track user engagement."""

    def __init__(self,
                 tg_service: TgService
                 ):
        self.__tg_service = tg_service

    async def __call__(self,
                       handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
                       update: Update,
                       data: dict[str, Any]):
        print(update)

        return await handler(update, data)
