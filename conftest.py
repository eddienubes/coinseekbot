import asyncio
import os

import pytest

from config import config
from container import Container


@pytest.fixture(autouse=True, scope='session')
async def env():
    os.environ['ENV'] = 'test'
    config.env = 'test'


@pytest.fixture(autouse=True, scope='session')
async def event_loop(env):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope='class')
async def container(env):
    container = Container()
    await container.init()
    yield container
    await container.destroy()
