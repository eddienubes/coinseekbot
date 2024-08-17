import asyncio
import contextlib

import aioboto3
from types_aiobotocore_s3.service_resource import Bucket

from config import config
from utils import StreamWrapper


class S3Service:
    def __init__(self, bucket_name: str):
        self.__bucket_name = bucket_name
        self.__ctx = contextlib.AsyncExitStack()
        self.__s3: Bucket | None = None

    async def upload_file_stream(self, file_path: str, stream: asyncio.StreamReader) -> str:
        wrapper = StreamWrapper(stream)

        await self.__s3.upload_fileobj(wrapper, file_path)
        return file_path

    async def on_module_init(self):
        pass
        # session = aioboto3.Session(
        #     aws_access_key_id=config.s3_access_key_id,
        #     aws_secret_access_key=config.s3_access_secret_key,
        # )
        # 
        # # noinspection PyTypeChecker
        # resource = await self.__ctx.enter_async_context(
        #     session.resource(
        #         's3',
        #         endpoint_url=config.s3_endpoint_url,
        #     )
        # )
        # 
        # self.__s3 = await resource.Bucket(self.__bucket_name)

    async def on_module_destroy(self):
        pass
        # await self.__ctx.aclose()
