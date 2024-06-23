import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    bot_token: str = os.getenv('BOT_TOKEN')
    inline_query_cache_time: int = int(os.getenv('INLINE_QUERY_CACHE_TIME'))
