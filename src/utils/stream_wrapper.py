import asyncio
from abc import ABC
from typing import IO


class StreamWrapper(IO, ABC):
    def __init__(self, stream: asyncio.StreamReader):
        self.__stream = stream

    async def read(self, __n=-1) -> bytes:
        return await self.__stream.read(__n)
