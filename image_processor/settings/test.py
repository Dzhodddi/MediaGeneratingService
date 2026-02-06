import logging

from image_processor.settings.app import AppSettings


class TestAppSettings(AppSettings):
    debug: bool = True

    logging_level: int = logging.DEBUG
