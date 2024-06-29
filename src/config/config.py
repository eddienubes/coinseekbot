import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    bot_token: str = os.getenv('BOT_TOKEN')
