import os

from dotenv import load_dotenv
from pydantic import AnyUrl
from pydantic_settings import BaseSettings

load_dotenv()


class AppSettings(BaseSettings):
    SERVER_HOST: str = os.getenv('SERVER_HOST', 'localhost')

    allowed_cors_origin: set[AnyUrl | str] = ['*']
    allowed_cors_credentials: bool = True
    TESTING: bool = 0
