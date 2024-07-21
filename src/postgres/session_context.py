import functools
import logging
from contextvars import ContextVar
from typing import Callable, TypeVar, Any, ParamSpec

from utils import IsolatedContext
from .database_context import DatabaseContext
from .pg_engine import PgEngine


class SessionContext:
    """A factory for creating session scopes."""

    __RV = TypeVar('__RV', bound=Any)
    __P = ParamSpec('__P')

    def __init__(self, engine: PgEngine):
        self.__engine = engine
        self.__ctx: ContextVar[DatabaseContext | None] = ContextVar('pg_ctx', default=None)
        self.__logger = logging.getLogger(SessionContext.__name__)

    def get_or_create_ctx(self) -> DatabaseContext:
        """Gets or creates a database context."""
        ctx = self.get_ctx()

        if ctx is None:
            return self.set_ctx()

        return ctx

    def get_ctx(self) -> DatabaseContext | None:
        """Gets current database context."""
        db_ctx = self.__ctx.get()
        return db_ctx

    def try_get_ctx(self) -> DatabaseContext:
        """Tries to get current database context."""
        ctx = self.get_ctx()

        if ctx is None:
            raise ValueError('You are executing a database operation outside of a session context.')

        return ctx

    def set_ctx(self, fn_name: str = None) -> DatabaseContext:
        """Creates and returns database execution context."""
        session = self.__engine.create_session()

        ctx = DatabaseContext(session=session)

        self.__ctx.set(DatabaseContext(session=session, fn_name=fn_name))

        return ctx

    def delete_session(self) -> None:
        """Deletes session from the context."""
        self.__ctx.set(None)

    def run(self, func: Callable[..., __RV], *args, **kwargs) -> __RV:
        wrapped = self.wrap(func)
        return wrapped(*args, **kwargs)

    def wrap(self, func: Callable[__P, __RV]) -> Callable[__P, __RV]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            self.__logger.debug(f'Inspect method: {func.__name__}')
            ctx = self.get_ctx()

            # Some operations are only allowed at the top level.
            # Otherwise, the caller is responsible for committing/reverting/closing the transaction.
            top_level = ctx is None

            @functools.wraps(func)
            async def within_ctx(*args, **kwargs):
                self.__logger.debug(f'Top level: {top_level}, session: {ctx}')

                if top_level:
                    # We don't need to begin a transaction here.
                    # Unit of work will do it for us.
                    db_session = self.set_ctx(func.__name__).session
                else:
                    db_session = ctx.session

                try:
                    self.__logger.debug(f'About to call {func.__name__}')

                    result = await func(*args, **kwargs)

                    self.__logger.debug(f'Finished calling {func.__name__}')

                    if top_level:
                        self.__logger.debug(f'Committing transaction for {func.__name__}')
                        await db_session.commit()

                    return result
                except Exception as e:
                    self.__logger.error(f'Error in {func.__name__}: {e}')
                    if top_level:
                        self.__logger.debug(f'Rolling back the transaction')
                        await db_session.rollback()
                    raise e
                finally:
                    if top_level:
                        self.__logger.debug(f'Closing session for {func.__name__}')
                        await db_session.close()

            # If top level, create a new isolated context
            if top_level:
                return await IsolatedContext().run(within_ctx, *args, **kwargs)

            # Otherwise, keep using existing context and its session
            return await within_ctx(*args, **kwargs)

        return wrapper


P = TypeVar('P', bound=Callable[..., Any])


def session(scope: SessionContext) -> Callable[[P], P]:
    """A decorator that wraps a function in a session scope."""

    def decorator(func: P) -> P:
        return scope.wrap(func)

    return decorator
