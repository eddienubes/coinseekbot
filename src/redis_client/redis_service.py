from config import config
from redis.asyncio import Redis
from redis.asyncio.lock import Lock


class RedisService:
    def __init__(self):
        self.redis = Redis(
            host=config.redis_host,
            port=config.redis_port,
            password=config.redis_password,
            decode_responses=True
        )

    async def get(self, key: str) -> str | None:
        return await self.redis.get(self.__get_key(key))

    async def set(self, key: str, value: str, ex_s: int = None) -> None:
        return await self.redis.set(self.__get_key(key), value, ex=ex_s)

    async def mset(self, data: dict[str, str]) -> None:
        """
        Set multiple keys in Redis. Does not have an expiration time.
        https://stackoverflow.com/a/70270472
        """
        return await self.redis.mset({self.__get_key(k): v for k, v in data.items()})

    async def mget(self, keys: list[str]) -> list[str]:
        return await self.redis.mget([self.__get_key(k) for k in keys])

    async def delete(self, key: str) -> None:
        return await self.redis.delete(self.__get_key(key))

    async def keys(self) -> list[str]:
        return await self.redis.keys()

    async def flush(self) -> None:
        await self.redis.flushdb()

    async def get_all(self) -> dict[str, str]:
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

    def lock(self, key: str, timeout: int = None) -> Lock:
        return self.redis.lock(self.__get_key(key), timeout=timeout)

    async def on_module_init(self):
        await self.redis.initialize()

    async def on_module_destroy(self):
        await self.redis.aclose(close_connection_pool=True)

    def __get_key(self, postfix: str) -> str:
        return f'{config.redis_prefix}:{postfix}'
