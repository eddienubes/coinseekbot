import asyncio
from collections.abc import Callable
from typing import Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

from telegram.tg_service import TgService
from utils import dispatch


class EngagementMiddleware(BaseMiddleware):
    """Simple middleware to track user engagement."""

    def __init__(self,
                 tg_service: TgService
                 ):
        self.__tg_service = tg_service

    async def __call__(self,
                       handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
                       update: Update,
                       data: dict[str, Any]):
        dispatch(self.__tg_service.upsert_user_in_chat_from_update(update))

        return await handler(update, data)
