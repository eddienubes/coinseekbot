import logging

from .pg_engine import pg_engine


class PostgresService:
    def __init__(self):
        self.__logger = logging.getLogger(PostgresService.__name__)

    async def on_module_destroy(self):
        self.__logger.info('Disposing postgres engine')
        await pg_engine.dispose()
