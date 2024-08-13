from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.filters import Command

from crypto.crypto_assets_repo import CryptoAssetsRepo
from crypto.crypto_watches_repo import CryptoWatchesRepo
from crypto.crypto_favourites_repo import CryptoFavouritesRepo
from telegram.tg_chats_repo import TgChatsRepo
from telegram.tg_users_repo import TgUsersRepo
from .states import WatchMenuState

from .. import TelegramBot


@TelegramBot.router()
class BotWatchRouter:
    def __init__(self,
                 chats_repo: TgChatsRepo,
                 assets_repo: CryptoAssetsRepo,
                 crypto_watches_repo: CryptoWatchesRepo,
                 crypto_favourites_repo: CryptoFavouritesRepo,
                 tg_users_repo: TgUsersRepo
                 ):
        self.__chats_repo = chats_repo
        self.__assets_repo = assets_repo
        self.__crypto_watches_repo = crypto_watches_repo
        self.__crypto_favorites_repo = crypto_favourites_repo
        self.__tg_users_repo = tg_users_repo

    @TelegramBot.handle_message(Command('watch'))
    async def watch(self, message: Message, state: FSMContext):
        await state.set_state(WatchMenuState.SHOW_FAVOURITES)

        tg_user = await self.__tg_users_repo.get_by_tg_id_with_chat(
            tg_user_id=message.from_user.id,
            tg_chat_id=message.chat.id
        )

        # If there is no user, that means no crypto favourites
        if not tg_user:
            await message.reply(
                text='Watch command'
            )
            return

        favourites = await self.__crypto_favorites_repo.get_by_tg_user_uuid_with_assets(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=tg_user.chat.uuid
        )

        btns = []

        for fav in favourites.hits:
            if fav.watch:
                postfix = f'- Watching 👀'
            else:
                postfix = ''

            row = [
                InlineKeyboardButton(
                    text=f'{fav.asset.name} {postfix}',
                    callback_data='asdfj'
                )
            ]

            btns.append(row)

        await message.reply(
            text='Watch command with assets',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    *btns
                ]
            )

        )
