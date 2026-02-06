import logging

from image_processor.settings.app import AppSettings


class LocalAppSettings(AppSettings):
    debug: bool = True

    logging_level: int = logging.DEBUG
