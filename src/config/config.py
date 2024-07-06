import sys
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

path = os.path.abspath(os.path.join(sys.prefix, '..', '.env'))
print(path)


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=path)

    bot_token: str

    #
    # Redis
    #
    redis_host: str
    redis_port: int

    #
    # S3
    #
    s3_public_bucket_name: str
    s3_private_bucket_name: str
    s3_access_key_id: str
    s3_access_secret_key: str
    s3_endpoint_url: str


config = Config()
