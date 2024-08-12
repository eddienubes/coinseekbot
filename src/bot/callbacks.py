import json
import uuid
from typing import Type, get_type_hints, Self

from aiogram.filters.callback_data import CallbackData
from pydantic import Field

from redis_client import RedisService


class DummyCb(CallbackData, prefix='DummyCb'):
    pass


class RedisCb[T](CallbackData, prefix='R'):
    id: str | None = None

    __prefix = 'R'
    __redis_prefix = 'cb'

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        hints = get_type_hints(cls)
        for field, field_type in hints.items():
            if not hasattr(cls, field):
                # Make field optional and set default to None
                setattr(cls, field, Field(default=None))

    def model_dump_json(self, *args, **kwargs) -> str:
        return json.dumps({'id': self.id})

    def pack(self) -> str:
        return f'{self.__prefix__}::{self.id}'

    @classmethod
    def unpack(cls: Type[T], value: str) -> T:
        return cls(id=value.split('::')[1])

    async def save(self) -> str:
        """Create a callback data, saves it to redis and returns the id to use as callback data"""
        from container import Container
        container = Container()

        redis_service = container.get(RedisService)

        id = str(uuid.uuid4())

        json_str = self.model_dump_json()

        # store callbacks in redis for 30 days
        await redis_service.set(f'{self.__class__.__redis_prefix}:{id}', json_str, ex_s=60 * 60 * 24 * 30)

        self.id = id

        # Return cb data key
        return self.pack()

    async def load(self) -> Self:
        """Loads dataclass from redis"""
        if not self.id:
            raise ValueError('Callback data id is not set you shortbus')

        from container import Container
        container = Container()

        redis_service = container.get(RedisService)

        data_str = await redis_service.get(f'{self.__class__.__redis_prefix}:{self.id}')

        data = json.loads(data_str)

        for key, value in data.items():
            setattr(self, key, value)

        return self
