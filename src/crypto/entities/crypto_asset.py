from sqlalchemy import UUID, func, String
from sqlalchemy.orm import mapped_column, Mapped

from postgres import Base


class CryptoAsset(Base):
    __tablename__ = 'crypto_assets'

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, server_default=func.gen_random_uuid())

    ticker: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, unique=False, nullable=False)

    logo_s3_key: Mapped[str] = mapped_column(String, nullable=False)
    
    
