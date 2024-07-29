from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from postgres import Base
from .tg_chats_to_users import TgChatsToUsers
from decimal import *

if TYPE_CHECKING:
    from .tg_chat import TgChat


class TgUser(Base):
    __tablename__ = 'tg_users'

    uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, primary_key=True, server_default=sa.func.gen_random_uuid())

    tg_id: Mapped[Decimal] = mapped_column(sa.DECIMAL, unique=True, nullable=False)
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
