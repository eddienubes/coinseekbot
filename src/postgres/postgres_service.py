from .pg_engine import pg_engine


class PostgresService:
    async def on_module_destroy(self):
        await pg_engine.dispose()
