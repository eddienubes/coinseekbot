import pytest

from container import Container
from tg_users.tg_user import TgUser
from tg_users.tg_users_repo import TgUsersRepo


class TestTgUsersRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container) -> TgUsersRepo:
        yield container.get(TgUsersRepo)

    async def test_add(self, repo: TgUsersRepo):
        user = TgUser.random()

        added = await repo.add(user)

        assert added.tg_id == user.tg_id
