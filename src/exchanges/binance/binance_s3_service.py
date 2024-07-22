import asyncio

from aws import S3PublicService


class BinanceS3Service(S3PublicService):
    async def upload_asset_logo(self, stream: asyncio.StreamReader, ticker: str) -> str:
        return await self.upload_file_stream(f'assets/{ticker}.png', stream)
