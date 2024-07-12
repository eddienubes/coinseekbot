import aiohttp
import pytest
import pytest_asyncio

from config import config
from .s3_service import S3Service


class TestS3Service:
    @pytest_asyncio.fixture(autouse=True, scope='class')
    async def service(self):
        service = S3Service(config.s3_public_bucket_name)
        await service.on_module_init()
        yield service
        await service.on_module_destroy()

    @pytest.mark.asyncio
    async def test_stream_file_upload(self, service):
        file_url = 'https://bin.bnbstatic.com/image/admin_mgs_image_upload/20230505/298aecf1-31ac-4439-81d1-21d89d746e9a'

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as res:
                assert res.status == 200
                file_stream = res.content
                file_path = await service.upload_file_stream('test_file.png', file_stream)
                assert file_path == 'test_file.png'
