import functools
from typing import Callable, Type

from .repository import Repository
from .postgres_repo import PostgresRepo
from container import Container


def session(repo_type: Type[Repository]) -> Callable:
    def decorator(func: Callable) -> Callable:
        repository: Repository = Container().get(repo_type)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            db_session = repository.get_session()
            top_level = db_session is None

            try:

                if top_level:
                    db_session = repository.create_session()

                result = await func(*args, **kwargs, session=db_session)

                if top_level:
                    await db_session.commit()

                return result
            except Exception as e:
                # Only if we are the top level caller.
                # Otherwise, the caller is responsible for committing the transaction.
                if top_level:
                    await db_session.rollback()
                raise e
            finally:
                if top_level:
                    await db_session.close()

        return wrapper

    return decorator


# Decorator to create a session around current async context
pg_session = session(PostgresRepo)
