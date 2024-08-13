import pytest

from container import Container
from telegram.entities.tg_user import TgUser
from .entities.tg_chat import TgChat
from .entities.tg_chat_to_user import TgChatToUser

from .tg_users_repo import TgUsersRepo


class TestTgUsersRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container):
        yield container.get(TgUsersRepo)

    async def test_get_by_tg_id_with_chat(self, repo: TgUsersRepo):
        user = TgUser.random()
        chat = TgChat.random()

        user = await repo.add(user)
        chat = await repo.add(chat)

        relation = TgChatToUser(
            chat_uuid=chat.uuid,
            user_uuid=user.uuid
        )

        relation = await repo.add(relation)

        user = await repo.get_by_tg_id_with_chat(
            tg_user_id=user.tg_id,
            tg_chat_id=chat.tg_id
        )

        assert user is not None

    async def test_upsert(self, repo: TgUsersRepo):
        user = TgUser.random(first_name='Pupa')
        added = await repo.upsert(user)

        assert added.tg_id == user.tg_id

        user.first_name = 'Boba'

        updated = await repo.upsert(user)

        assert updated.first_name == 'Boba'
