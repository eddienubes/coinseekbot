import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    bot_token: str = os.getenv('BOT_TOKEN')

    #
    # Redis
    #
    redis_host: str = os.getenv('REDIS_HOST')
    redis_port: int = int(os.getenv('REDIS_PORT'))
