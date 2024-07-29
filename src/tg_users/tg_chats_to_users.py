from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa

from postgres import Base


class TgChatsToUsers(Base):
    tg_chat: Mapped[sa.UUID] = mapped_column(sa.UUID, sa.ForeignKey('tg_chats.uuid'), primary_key=True)
    tg_user: Mapped[sa.UUID] = mapped_column(sa.UUID, sa.ForeignKey('tg_users.uuid'), primary_key=True)
