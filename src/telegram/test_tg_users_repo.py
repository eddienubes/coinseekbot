import pytest

from container import Container
from .tg_user import TgUser

from .tg_users_repo import TgUsersRepo


class TestTgUsersRepo:
    @pytest.fixture(autouse=True, scope='class')
    async def repo(self, container: Container):
        yield container.get(TgUsersRepo)

    async def test_upsert(self, repo: TgUsersRepo):
        user = TgUser.random(first_name='Pupa')
        added = await repo.upsert(user)

        assert added.tg_id == user.tg_id

        user.first_name = 'Boba'

        updated = await repo.upsert(user)

        assert updated.first_name == 'Boba'
