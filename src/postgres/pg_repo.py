from . import pg_engine
from .repo import Repo


class PgRepo(Repo):
    def __init__(self):
        super().__init__(pg_engine)
