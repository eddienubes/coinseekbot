from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from postgres import Base
from utils import faker
from .tg_chats_to_users import TgChatsToUsers
from decimal import *

if TYPE_CHECKING:
    from .tg_chat import TgChat


class TgUser(Base):
    __tablename__ = 'tg_users'

    uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=sa.func.gen_random_uuid())

    tg_id: Mapped[Decimal] = mapped_column(sa.NUMERIC, unique=True, nullable=False)
    is_bot: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    first_name: Mapped[str] = mapped_column(sa.String, nullable=False)
    last_name: Mapped[str] = mapped_column(sa.String, nullable=True)
    username: Mapped[str] = mapped_column(sa.String, nullable=True)
    language_code: Mapped[str] = mapped_column(sa.String, nullable=True)
    is_premium: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)

    added_to_attachment_menu: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    """If the user has added the bot to the attachment menu"""

    chats: Mapped[list['TgChat']] = relationship(
        secondary=TgChatsToUsers.__table__,
        back_populates='users',
        lazy='noload',
        viewonly=True
    )

    @staticmethod
    def random() -> 'TgUser':
        return TgUser(
            tg_id=faker.pydecimal(left_digits=5, right_digits=5),
            is_bot=faker.boolean(),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            username=faker.user_name(),
            language_code=faker.language_code(),
            is_premium=faker.boolean(),
            added_to_attachment_menu=faker.boolean()
        )
