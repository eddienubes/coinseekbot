import functools
from typing import Callable

from .pg_engine import PgEngine


def session(engine: PgEngine) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            db_session = engine.get_session()

            # Some operations are only allowed at the top level.
            # Otherwise, the caller is responsible for committing/reverting/closing the transaction.
            top_level = db_session is None

            try:
                if top_level:
                    db_session = engine.create_session()

                result = await func(*args, **kwargs, session=db_session)

                if top_level:
                    await db_session.commit()

                return result
            except Exception as e:
                if top_level:
                    await db_session.rollback()
                raise e
            finally:
                if top_level:
                    await db_session.close()

        return wrapper

    return decorator
