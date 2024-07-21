import functools
import logging
from typing import Callable, TypeVar, Any

from utils import ContextFactory
from .pg_engine import PgEngine

P = TypeVar('P', bound=Callable[..., Any])

logger = logging.getLogger('session-decorator')


def session(engine: PgEngine) -> Callable[[P], P]:
    def decorator(func: P) -> P:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.debug(f'Inspecting for {func.__name__}')
            ctx = engine.get_ctx()

            # Some operations are only allowed at the top level.
            # Otherwise, the caller is responsible for committing/reverting/closing the transaction.
            top_level = ctx is None

            async def within_ctx(*args, **kwargs):
                logger.debug(f'Top level: {top_level}, session: {ctx}')

                if top_level:
                    # We don't need to begin a transaction here.
                    # Unit of work will do it for us.
                    db_session = engine.set_ctx(func.__name__).session
                else:
                    db_session = ctx.session

                try:
                    logger.debug(f'About to call {func.__name__}')

                    result = await func(*args, **kwargs, session=db_session)

                    logger.debug(f'Finished calling {func.__name__}')

                    if top_level:
                        logger.debug(f'Committing transaction for {func.__name__}')
                        await db_session.commit()

                    return result
                except Exception as e:
                    logger.error(f'Error in {func.__name__}: {e}')
                    if top_level:
                        logger.debug(f'Rolling back the transaction')
                        await db_session.rollback()
                    raise e
                finally:
                    if top_level:
                        logger.debug(f'Closing session for {func.__name__}')
                        await db_session.close()

            return await ContextFactory().run(within_ctx, *args, **kwargs)

        return wrapper

    return decorator
