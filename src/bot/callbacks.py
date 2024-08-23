import json
import uuid
from typing import Type, get_type_hints, Self, ClassVar

from aiogram.filters.callback_data import CallbackData
from pydantic import Field

from redis_client import RedisService


class DummyCb(CallbackData, prefix='DummyCb'):
    pass


class BaseCb(CallbackData, prefix='CB'):
    tg_user_id: int


class RedisCb[T](BaseCb, prefix='R'):
    id: str | None = None

    redis_prefix: ClassVar = 'cb'

    def __init_subclass__(cls, **kwargs):
        hints = get_type_hints(cls)
        for field, field_type in hints.items():
            if not hasattr(cls, field):
                # Make field optional and set default to None
                setattr(cls, field, Field(default=None))

        super().__init_subclass__(**kwargs)

    def model_dump_json(self, *args, **kwargs) -> str:
        return json.dumps({'id': self.id})

    def pack(self) -> str:
        if not self.id:
            raise ValueError('Use .save() method to save callback data to redis and get the id')

        return f'{self.__prefix__}::{self.id}'

    @classmethod
    def unpack(cls: Type[T], value: str) -> T:
        try:
            prefix, *data = value.split('::')

            if prefix != cls.__prefix__:
                raise ValueError('Invalid prefix')
        except Exception as e:
            raise ValueError('Invalid callback data, supposedly prefix is missing, error: {e}')

        try:
            redis_id = data[0]

            return cls(id=redis_id)
        except Exception as e:
            raise ValueError(f'Unable to unpack callback data: {value}, error: {e}')

    async def save(self) -> str:
        """Create a callback data, saves it to redis and returns the id to use as callback data"""
        from container import Container
        container = Container()

        redis_service = container.get(RedisService)

        self.id = str(uuid.uuid4())

        hm = dict()

        for key in self.model_fields:
            hm[key] = getattr(self, key)

        json_str = json.dumps(hm)

        # store callbacks in redis for 30 days
        await redis_service.set(f'{self.__class__.redis_prefix}:{self.id}', json_str, ex_s=60 * 60 * 24 * 30)

        # Return cb data key
        return self.pack()

    async def load(self) -> Self:
        """Loads dataclass from redis"""
        if not self.id:
            raise ValueError('Callback data id is not set you shortbus')

        from container import Container
        container = Container()

        redis_service = container.get(RedisService)

        data_str = await redis_service.get(f'{self.__class__.redis_prefix}:{self.id}')

        if not data_str:
            raise ValueError('Callback data not found in redis, save to redis first, you fool')

        data = json.loads(data_str)

        for key in self.model_fields:
            setattr(self, key, data[key])

        return self
