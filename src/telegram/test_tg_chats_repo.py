import pytest

from container import Container
from telegram.tg_chat import TgChat
from telegram.tg_chats_repo import TgChatsRepo
from telegram.tg_user import TgUser


class TesteTgChatsRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container) -> TgChatsRepo:
        yield container.get(TgChatsRepo)

    async def test_add(self, repo: TgChatsRepo):
        chat = TgChat.random()

        added = await repo.add(chat)

        assert added.tg_id == chat.tg_id

    async def test_upsert(self, repo: TgChatsRepo):
        chat = TgChat.random(is_forum=None)
        added = await repo.upsert(chat)

        assert added.tg_id == chat.tg_id

        chat.fullname = 'new fullname'

        updated = await repo.upsert(chat)

        assert updated.fullname == 'new fullname'

    async def test_relations(self, repo: TgChatsRepo):
        chat = TgChat.random()
        user = TgUser.random()

        chat.users.append(user)

        chat = await repo.add(chat)

        assert chat is not None
