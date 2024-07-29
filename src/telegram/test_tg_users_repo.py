import pytest

from container import Container
from telegram.tg_user import TgUser
from telegram.tg_users_repo import TgUsersRepo


class TestTgUsersRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container) -> TgUsersRepo:
        yield container.get(TgUsersRepo)

    async def test_add(self, repo: TgUsersRepo):
        user = TgUser.random()

        added = await repo.add(user)

        assert added.tg_id == user.tg_id
