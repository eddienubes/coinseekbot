import sys
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

path = os.path.abspath(os.path.join(sys.prefix, '..', '.env'))


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=path, extra='allow')
    #
    # App
    #
    env: str
    log_level: str

    #
    # Bot
    #
    bot_token: str
    bot_inline_cache_timeout_sec: int
    bot_inline_hot_cache_timeout_sec: int

    #
    # Redis
    #
    redis_host: str
    redis_port: int
    redis_prefix: str

    #
    # S3
    #
    s3_public_bucket_name: str
    s3_private_bucket_name: str
    s3_access_key_id: str
    s3_access_secret_key: str
    s3_endpoint_url: str

    #
    # Postgres
    #
    postgres_user: str
    postgres_pass: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    def __init__(self, **values):
        super().__init__(**values)
        self.postgres_url = f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_pass}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'


config = Config()
