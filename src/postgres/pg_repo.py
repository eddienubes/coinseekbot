from .pg_session import pg_session_ctx
from .repo import Repo


class PgRepo(Repo):
    def __init__(self):
        super().__init__(pg_session_ctx)
