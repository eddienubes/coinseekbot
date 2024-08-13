from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from postgres import Base
from utils import faker
from telegram.entities.tg_chat_to_user import TgChatToUser

if TYPE_CHECKING:
    from telegram.entities.tg_chat import TgChat


class TgUser(Base):
    __tablename__ = 'tg_users'

    uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=sa.func.gen_random_uuid())

    tg_id: Mapped[int] = mapped_column(sa.BigInteger, unique=True, nullable=False)
    is_bot: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.sql.false())
    first_name: Mapped[str] = mapped_column(sa.String, nullable=False)
    last_name: Mapped[str] = mapped_column(sa.String, nullable=True)
    username: Mapped[str] = mapped_column(sa.String, nullable=True)
    language_code: Mapped[str] = mapped_column(sa.String, nullable=True)
    is_premium: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.sql.false())

    added_to_attachment_menu: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.sql.false())
    """If the user has added the bot to the attachment menu"""

    chats: Mapped[list['TgChat']] = relationship(
        secondary=TgChatToUser.__table__,
        back_populates='users',
        lazy='noload',
        # User middle table repo to create a relationship
        viewonly=True
    )

    chat: Mapped['TgChat'] = relationship(
        secondary=TgChatToUser.__table__,
        lazy='joined',
        uselist=False
    )

    @staticmethod
    def random(**kwargs) -> 'TgUser':
        base = TgUser(
            tg_id=faker.pyint(),
            is_bot=faker.boolean(),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            username=faker.user_name(),
            language_code=faker.language_code(),
            is_premium=faker.boolean(),
            added_to_attachment_menu=faker.boolean()
        )

        return TgUser(
            **{**base.to_dict(), **kwargs}
        )
