from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from postgres import Base
from decimal import *

from utils import faker
from .tg_chats_to_users import TgChatsToUsers

if TYPE_CHECKING:
    from .tg_user import TgUser


class TgChat(Base):
    __tablename__ = 'tg_chats'

    uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=sa.func.gen_random_uuid())

    tg_id: Mapped[int] = mapped_column(sa.BigInteger, unique=True, nullable=False)

    type: Mapped[str] = mapped_column(sa.String, index=True, nullable=False)

    title: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    """Full name of a user in case the chat is private"""

    username: Mapped[str | None] = mapped_column(sa.String, index=True, nullable=True)

    fullname: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    """Full name of a user in case the chat is private"""

    is_forum: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.sql.false())
    """if the supergroup chat is a forum"""

    description: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    """Description, for supergroups and channel chats"""

    bio: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    """Bio of the other party in a private chat"""

    join_by_request: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.sql.false())
    """True, if the chat is a private chat and the other party can join the chat by request"""

    invite_link: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    """Chat invite link, for supergroups and channel chats"""

    users: Mapped[list['TgUser']] = relationship(
        secondary=TgChatsToUsers.__table__,
        back_populates='chats',
        lazy='noload',
        viewonly=True
    )

    @staticmethod
    def random(**kwargs) -> 'TgChat':
        base = TgChat(
            tg_id=faker.pyint(),
            type=faker.pystr(10, 10),
            username=faker.pystr(10, 10),
            fullname=faker.pystr(10, 10),
            is_forum=False,
            description=faker.pystr(10, 10),
            bio=faker.pystr(10, 10),
            join_by_request=False,
            invite_link=faker.url()
        )

        return TgChat(
            **{**base.to_dict(), **kwargs}
        )
