from typing import List, Dict

from config import config
from redis.asyncio import Redis


class RedisService:
    def __init__(self):
        self.redis = Redis(host=config.redis_host, port=config.redis_port, decode_responses=True)

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ex_s: int = None) -> None:
        return await self.redis.set(key, value, ex=ex_s)

    async def delete(self, key: str) -> None:
        return await self.redis.delete(key)

    async def keys(self) -> List[str]:
        return await self.redis.keys()

    async def flush(self) -> None:
        await self.redis.flushdb()

    async def get_all(self) -> Dict[str, str]:
        keys = await self.keys()
        data = {}
        for key in keys:
            data[key] = await self.get(key)
        return data

    async def set_all(self, data) -> bool:
        for key, value in data.items():
            await self.set(key, value)
        return True

    async def delete_all(self) -> bool:
        keys = await self.keys()
        for key in keys:
            await self.delete(key)
        return True

    async def on_module_init(self):
        await self.redis.initialize()

    async def on_module_destroy(self):
        await self.redis.aclose(close_connection_pool=True)
