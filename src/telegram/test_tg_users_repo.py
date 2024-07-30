import pytest

from container import Container
from .tg_user import TgUser

from .tg_users_repo import TgUsersRepo


@pytest.fixture(autouse=True, scope='module')
async def repo(container: Container):
    yield container.get(TgUsersRepo)


async def test_upsert(repo: TgUsersRepo):
    user = TgUser.random(first_name='Pupa')
    added = await repo.upsert(user)

    assert added.tg_id == user.tg_id

    user.first_name = 'Boba'

    updated = await repo.upsert(user)

    assert updated.first_name == 'Boba'
