import logging

from image_processor.settings.app import AppSettings


class ProductionAppSettings(AppSettings):
    LOG_LEVEL: int = logging.ERROR
