from datetime import datetime

import pytest

from container import Container
from crypto.crypto_watches_repo import CryptoWatchRepo
from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_watch import CryptoWatch, WatchInterval
from telegram.tg_chat import TgChat


class TestCryptoWatchesRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container):
        yield container.get(CryptoWatchRepo)

    async def test_get_with_joins(self, repo: CryptoWatchRepo):
        asset = CryptoAsset.random()
        tg_chat = TgChat.random()

        asset = await repo.add(asset)
        tg_chat = await repo.add(tg_chat)

        watch = CryptoWatch(
            asset_uuid=asset.uuid,
            tg_chat_uuid=tg_chat.uuid,
            interval=WatchInterval.EVERY_WEEK,
            next_execution_at=datetime.now()
        )

        watch = await repo.add(watch)

        hit = await repo.get_with_joins(
            asset_uuid=watch.asset_uuid,
            tg_chat_uuid=watch.tg_chat_uuid
        )

        assert hit.interval == WatchInterval.EVERY_WEEK
        assert hit.asset.uuid == asset.uuid
        assert hit.tg_chat.uuid == tg_chat.uuid
