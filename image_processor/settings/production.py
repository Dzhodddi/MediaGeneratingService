import logging

from image_processor.settings.app import AppSettings


class ProductionAppSettings(AppSettings):
    logging_level: int = logging.INFO