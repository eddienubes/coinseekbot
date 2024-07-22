from aiohttp import ClientSession, ClientResponse


async def fetch(session: ClientSession, url: str) -> ClientResponse:
    async with session.get() as response:
        return response.content
