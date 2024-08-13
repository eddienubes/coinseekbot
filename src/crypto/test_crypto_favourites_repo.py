from datetime import datetime

import pytest
import uuid

from container import Container
from crypto.crypto_favourites_repo import CryptoFavouritesRepo
from crypto.crypto_watches_repo import CryptoWatchesRepo
from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_favourite import CryptoFavourite
from crypto.entities.crypto_watch import CryptoWatch, WatchInterval
from telegram.entities.tg_chat import TgChat
from telegram.entities.tg_user import TgUser


class TestCryptoWatchesRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container):
        yield container.get(CryptoFavouritesRepo)

    async def test_get_by_tg_user_uuid_with_assets(self, repo: CryptoFavouritesRepo):
        tg_user = TgUser.random()
        asset = CryptoAsset.random()
        tg_chat = TgChat.random()

        asset = await repo.add(asset)
        tg_chat = await repo.add(tg_chat)
        tg_user = await repo.add(tg_user)

        watch = CryptoWatch(
            asset_uuid=asset.uuid,
            tg_chat_uuid=tg_chat.uuid,
            interval=WatchInterval.EVERY_DAY,
            next_execution_at=datetime.now()
        )

        watch = await repo.add(watch)

        favourite = CryptoFavourite(
            asset_uuid=asset.uuid,
            tg_user_uuid=tg_user.uuid
        )

        favourite = await repo.add(favourite)

        result = await repo.get_by_tg_user_uuid_with_assets(
            tg_user_uuid=tg_user.uuid,
            tg_chat_uuid=watch.tg_chat_uuid
        )

        print(result)
