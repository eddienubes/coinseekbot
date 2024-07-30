import pytest

from container import Container
from .tg_chat import TgChat

from .tg_chat_to_user import TgChatToUser
from .tg_chats_to_users_repo import TgChatsToUsersRepo
from .tg_user import TgUser


class TestTgChatsToUsersRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container):
        yield container.get(TgChatsToUsersRepo)

    async def test_upsert(self, repo: TgChatsToUsersRepo):
        chat = TgChat.random()
        user = TgUser.random()

        await repo.add_all([chat, user])

        creation = TgChatToUser(
            chat_uuid=chat.uuid,
            user_uuid=user.uuid
        )

        await repo.upsert(creation)

        await repo.upsert(
            creation
        )
