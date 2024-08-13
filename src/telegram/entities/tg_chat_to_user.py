from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa

from postgres import Base


class TgChatToUser(Base):
    __tablename__ = 'tg_chats_to_users'

    chat_uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, sa.ForeignKey('tg_chats.uuid'), primary_key=True)
    user_uuid: Mapped[sa.UUID] = mapped_column(sa.UUID, sa.ForeignKey('tg_users.uuid'), primary_key=True)
