import pytest

from container import Container
from tg_users.tg_chat import TgChat
from tg_users.tg_chats_repo import TgChatsRepo


class TesteTgChatsRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container) -> TgChatsRepo:
        yield container.get(TgChatsRepo)

    async def test_add(self, repo: TgChatsRepo):
        chat = TgChat.random()

        added = await repo.add(chat)

        assert added.tg_id == chat.tg_id
