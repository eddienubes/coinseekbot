import asyncio

import pytest


@pytest.fixture(autouse=True, scope='session')
async def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
