from datetime import datetime, timedelta

import pytest
import uuid

from container import Container
from crypto.crypto_watches_repo import CryptoWatchesRepo
from crypto.entities.crypto_asset import CryptoAsset
from crypto.entities.crypto_asset_quote import CryptoAssetQuote
from crypto.entities.crypto_favourite import CryptoFavourite, CryptoFavouriteStatus
from crypto.entities.crypto_watch import CryptoWatch, WatchInterval
from telegram.entities.tg_chat import TgChat
from telegram.entities.tg_user import TgUser


class TestCryptoWatchesRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container):
        yield container.get(CryptoWatchesRepo)

    async def test_get_watchlist(self, repo: CryptoWatchesRepo):
        tg_user = TgUser.random()
        tg_user = await repo.add(tg_user)

        asset = CryptoAsset.random()
        tg_chat = TgChat.random()

        asset = await repo.add(asset)
        tg_chat = await repo.add(tg_chat)

        favourite = CryptoFavourite(
            asset_uuid=asset.uuid,
            tg_user_uuid=tg_user.uuid,
            status=CryptoFavouriteStatus.ACTIVE
        )
        favourite = await repo.add(favourite)

        watch = CryptoWatch(
            asset_uuid=asset.uuid,
            tg_chat_uuid=tg_chat.uuid,
            interval=WatchInterval.EVERY_DAY,
            next_execution_at=datetime.now()
        )

        watch = await repo.add(watch)

        watchlist = await repo.get_watchlist(
            tg_chat_uuid=tg_chat.uuid,
            tg_user_uuid=tg_user.uuid
        )

        assert len(watchlist.hits) == 1
        assert watchlist.total == 1
        assert watchlist.limit == 5
        assert watchlist.offset == 0

        hit = watchlist.hits[0]
        watch, asset, favourite = hit
        assert watch.asset_uuid == asset.uuid
        assert watch.tg_chat_uuid == tg_chat.uuid

        assert asset.uuid == favourite.asset_uuid
        assert favourite.asset_uuid == asset.uuid

    async def test_quote_hash(self):
        quote1 = CryptoAssetQuote.random(
            asset_uuid=uuid.uuid4()
        )
        quote2 = CryptoAssetQuote.random(**quote1.to_dict())

        quote3 = CryptoAssetQuote.random(asset_uuid=uuid.uuid4())

        assert hash(quote1) == hash(quote2)

        assert hash(quote1) != hash(quote3)
        assert hash(quote2) != hash(quote3)

    async def test_upsert(self, repo: CryptoWatchesRepo):
        asset = CryptoAsset.random()
        tg_chat = TgChat.random()

        asset = await repo.add(asset)
        tg_chat = await repo.add(tg_chat)

        watch = CryptoWatch(
            asset_uuid=asset.uuid,
            tg_chat_uuid=tg_chat.uuid,
            interval=WatchInterval.EVERY_DAY,
            next_execution_at=datetime.now()
        )

        upserted_watch = await repo.upsert(watch)

        assert upserted_watch.asset_uuid == asset.uuid
        assert upserted_watch.tg_chat_uuid == tg_chat.uuid
        assert upserted_watch.interval == WatchInterval.EVERY_DAY

        watch = CryptoWatch(
            asset_uuid=asset.uuid,
            tg_chat_uuid=tg_chat.uuid,
            interval=WatchInterval.EVERY_3_HOURS,
            next_execution_at=datetime.now()
        )

        upserted_watch = await repo.upsert(watch)

        assert upserted_watch.asset_uuid == asset.uuid
        assert upserted_watch.tg_chat_uuid == tg_chat.uuid
        assert upserted_watch.interval == WatchInterval.EVERY_3_HOURS

    async def test_get_with_joins(self, repo: CryptoWatchesRepo):
        asset = CryptoAsset.random()
        tg_chat = TgChat.random()

        asset = await repo.add(asset)
        tg_chat = await repo.add(tg_chat)

        watch = CryptoWatch(
            asset_uuid=asset.uuid,
            tg_chat_uuid=tg_chat.uuid,
            interval=WatchInterval.EVERY_DAY,
            next_execution_at=datetime.now()
        )

        watch = await repo.add(watch)

        hits = (await repo.get_with_joins_by_chat(
            tg_chat_uuid=watch.tg_chat_uuid
        )).hits

        assert hits[0].interval == WatchInterval.EVERY_DAY
        assert hits[0].asset.uuid == asset.uuid
        assert hits[0].tg_chat.uuid == tg_chat.uuid

    async def test_get_watches_to_notify(self, repo: CryptoWatchesRepo):
        asset = CryptoAsset.random()
        tg_chat = TgChat.random(
            is_removed=False
        )

        asset = await repo.add(asset)
        tg_chat = await repo.add(tg_chat)
        quote = CryptoAssetQuote.random(
            asset_uuid=asset.uuid
        )
        quote = await repo.add(quote)

        watch = CryptoWatch(
            asset_uuid=asset.uuid,
            tg_chat_uuid=tg_chat.uuid,
            interval=WatchInterval.EVERY_DAY,
            # Eligible for notification
            next_execution_at=datetime.now() - timedelta(days=1)
        )

        watch = await repo.add(watch)

        watches = await repo.get_watches_to_notify()

        assert len(watches) >= 1
        assert watches[0].asset is not None
        assert watches[0].asset.latest_quote is not None
        assert watches[0].tg_chat is not None
