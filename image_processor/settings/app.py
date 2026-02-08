import logging
import os

from dotenv import load_dotenv
from pydantic import AnyUrl
from pydantic_settings import BaseSettings

load_dotenv()


class AppSettings(BaseSettings):
    SERVER_HOST: str = os.getenv("SERVER_HOST", "localhost")

    allowed_cors_origin: set[AnyUrl | str] = ["*"]
    allowed_cors_credentials: bool = True
    TESTING: bool = 0
    LOG_FORMAT_DEBUG: str = "%(levelname)s - %(asctime)s - %(name)s - %(message)s"
    LOG_FORMAT_ERROR: str = (
        "%(asctime)s [%(levelname)s] in %(name)s (%(filename)s:%(lineno)d): %(message)s"
    )
    LOG_FORMAT_INFO: str = "%(levelname)s - %(message)s"
    LOG_LEVEL: int = logging.INFO

    RABBITMQ_URI: str = os.getenv("RABBITMQ_URI")
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT: str = os.getenv("RABBITMQ_PORT")
    RABBITMQ_QUEUE_NAME: str = os.getenv("RABBITMQ_QUEUE_NAME")
